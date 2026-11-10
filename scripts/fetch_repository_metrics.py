#!/usr/bin/env python3
"""Refresh public repository metadata and observed technology declarations.

The audit covers current default branches of owned, public, non-fork repos.
Any incomplete tree, failed blob, or invalid aggregation aborts before outputs
are replaced. No packages or repository code are installed or executed.
"""

from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
USERNAME = "tanmay-tiwari-20"
API = "https://api.github.com"
INDIA = timezone(timedelta(hours=5, minutes=30), name="Asia/Kolkata")
EXCLUDED_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".next", ".venv", "venv",
                 "coverage", "bower_components", ".vite", ".cache", ".output", ".turbo", "out"}


class GitHubAPIError(RuntimeError):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(f"GitHub API returned HTTP {status}")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("GitHub API redirects are not followed")


class GitHubClient:
    def __init__(self, token=None, opener=None):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.opener = opener or build_opener(NoRedirect())

    def get_json(self, path):
        # Never send the token to a URL supplied by repository contents.
        parsed = urlsplit(path)
        if not path.startswith("/") or path.startswith("//") or parsed.scheme or parsed.netloc:
            raise ValueError("Only relative GitHub API paths are allowed")
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-technology-audit/1.0",
                   "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        request = Request(API + path, headers=headers)
        for attempt in range(3):
            try:
                with self.opener.open(request, timeout=30) as response:
                    origin = urlsplit(response.geturl())
                    if origin.scheme != "https" or origin.netloc != "api.github.com":
                        raise ValueError("Unexpected GitHub API response origin")
                    body = response.read(15_000_001)
                    if len(body) > 15_000_000:
                        raise ValueError("GitHub API response exceeded the audit size limit")
                    return json.loads(body.decode("utf-8"))
            except HTTPError as exc:
                message = ""
                try:
                    message = str(json.loads(exc.read(4096)).get("message", ""))
                except (ValueError, UnicodeDecodeError):
                    pass
                if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                    raise GitHubAPIError(exc.code, message) from None
            except (URLError, TimeoutError):
                if attempt == 2:
                    raise RuntimeError("GitHub API connection failed; existing audit retained") from None
            time.sleep(2 ** attempt)
        raise RuntimeError("GitHub API request failed")


def valid_username(username):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", username):
        raise ValueError("Invalid GitHub username")


def list_public_repositories(client, username=USERNAME):
    valid_username(username)
    repositories, pages, seen = [], [], set()
    page = 1
    while True:
        path = f"/users/{username}/repos?" + urlencode({"type": "owner", "per_page": 100, "page": page})
        values = client.get_json(path)
        if not isinstance(values, list):
            raise ValueError("GitHub repository listing was not an array")
        pages.append({"url": API + path, "count": len(values)})
        for repo in values:
            full_name = repo.get("full_name")
            if not isinstance(full_name, str) or full_name.casefold() in seen:
                raise ValueError("Repository listing contains a missing or duplicate identity")
            seen.add(full_name.casefold())
            repositories.append({**repo, "_source_url": API + path})
        if len(values) < 100:
            break
        page += 1
    return repositories, pages


def eligible_repositories(repositories, username=USERNAME):
    eligible, excluded = [], []
    for repo in repositories:
        if repo.get("owner", {}).get("login", "").casefold() != username.casefold():
            excluded.append({"name": repo.get("name"), "reason": "not owned by requested user"})
            continue
        if type(repo.get("private")) is not bool or type(repo.get("fork")) is not bool:
            raise ValueError("Repository visibility/fork metadata is missing")
        reason = ("private repository" if repo["private"] else "fork repository" if repo["fork"] else
                  "profile repository" if repo.get("name", "").casefold() == username.casefold() else None)
        if reason:
            # Do not copy a private repository name into a public output.
            excluded.append({"reason": reason} if repo["private"] else {"name": repo["name"], "reason": reason})
        else:
            if repo.get("full_name", "").casefold() != f"{username}/{repo['name']}".casefold():
                raise ValueError("Repository owner and full name disagree")
            eligible.append(repo)
    return sorted(eligible, key=lambda item: item["name"].casefold()), excluded


def first_party(path):
    parts = PurePosixPath(path).parts
    return bool(parts) and not path.startswith("/") and ".." not in parts and not any(part.lower() in EXCLUDED_DIRS for part in parts[:-1])


def manifest_kind(path):
    name = PurePosixPath(path).name.lower()
    if name == "package.json":
        return "package.json"
    if name == "pyproject.toml":
        return "pyproject.toml"
    if re.fullmatch(r"requirements[^/]*\.txt", name):
        return "requirements.txt"
    return None


def validate_sha(sha):
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", sha):
        raise ValueError("Invalid Git tree/blob SHA")


def scan_repository(client, repo):
    full_name, branch = repo["full_name"], repo["default_branch"]
    if not branch:
        raise ValueError("Repository default branch is missing")
    base = "/repos/" + "/".join(quote(part, safe="") for part in full_name.split("/"))
    tree_path = base + "/git/trees/" + quote(branch, safe="") + "?recursive=1"
    result = {"name": repo["name"], "full_name": full_name, "default_branch": branch,
              "tree_sha": None, "tree_url": API + tree_path, "source_files": [],
              "manifests": [], "cdn_html": [], "status": "scanned"}
    try:
        tree = client.get_json(tree_path)
    except GitHubAPIError as exc:
        if exc.status == 409 and "git repository is empty" in exc.message.lower():
            result["empty"] = True
            return result
        raise
    if tree.get("truncated") is not False or not isinstance(tree.get("tree"), list):
        raise ValueError(f"Incomplete or truncated recursive tree: {full_name}")
    validate_sha(tree.get("sha"))
    result["tree_sha"] = tree["sha"]
    result["tree_url"] = API + base + "/git/trees/" + tree["sha"]
    paths = set()
    for item in tree["tree"]:
        if item.get("type") != "blob" or not first_party(item.get("path", "")):
            continue
        if item["path"] in paths:
            raise ValueError("Duplicate path in Git tree")
        paths.add(item["path"])
        validate_sha(item.get("sha"))
        result["source_files"].append({"path": item["path"], "sha": item["sha"]})
    result["source_files"].sort(key=lambda value: value["path"])
    manifests = [item for item in result["source_files"] if manifest_kind(item["path"])]
    html = [] if manifests else [item for item in result["source_files"] if len(PurePosixPath(item["path"]).parts) <= 2 and PurePosixPath(item["path"]).suffix.lower() in (".html", ".htm")]
    for collection, files in (("manifests", manifests), ("cdn_html", html)):
        for item in files:
            blob = client.get_json(base + "/git/blobs/" + item["sha"])
            if blob.get("encoding") != "base64" or blob.get("sha") != item["sha"]:
                raise ValueError("Blob encoding or snapshot identity is invalid")
            binary = base64.b64decode("".join(blob["content"].split()), validate=True)
            if len(binary) != blob.get("size"):
                raise ValueError("Blob length does not match its metadata")
            record = {"path": item["path"], "url": f"https://github.com/{full_name}/blob/{quote(branch, safe='')}/{quote(item['path'], safe='/')}",
                      "kind": manifest_kind(item["path"]) or "html", "blob_sha": item["sha"], "content": binary.decode("utf-8-sig")}
            result[collection].append(record)
    return result


def build_metrics(repositories, username, as_of, pages):
    eligible, excluded = eligible_repositories(repositories, username)
    normalized, language_repos, created = [], defaultdict(list), Counter()
    for repo in eligible:
        created_at = datetime.fromisoformat(repo["created_at"].replace("Z", "+00:00"))
        if created_at.date() > as_of:
            raise ValueError("Repository was created after the requested as-of date")
        created[created_at.strftime("%Y-%m")] += 1
        language = repo.get("language")
        if language:
            language_repos[language].append(repo["name"])
        for count in ("stargazers_count", "forks_count"):
            if type(repo.get(count)) is not int or repo[count] < 0:
                raise ValueError("Invalid repository count metadata")
        normalized.append({"name": repo["name"], "full_name": repo["full_name"], "html_url": repo["html_url"],
                           "fork": False, "archived": repo.get("archived", False), "default_branch": repo["default_branch"],
                           "stargazers_count": repo["stargazers_count"], "forks_count": repo["forks_count"],
                           "created_at": repo["created_at"], "pushed_at": repo.get("pushed_at"), "visibility": "public",
                           "primary_language": language, "languages": None, "language_bytes_available": False,
                           "sources": [repo["_source_url"]]})
    language_count = sum(map(len, language_repos.values()))
    languages = [{"name": name, "repository_count": len(names), "percent": round(len(names) * 100 / language_count, 2),
                  "repository_names": names} for name, names in sorted(language_repos.items(), key=lambda item: (-len(item[1]), item[0]))]
    timeline, cumulative = [], 0
    if created:
        year, month = map(int, min(created).split("-"))
        while (year, month) <= (as_of.year, as_of.month):
            key = f"{year:04d}-{month:02d}"
            cumulative += created[key]
            timeline.append({"month": key, "repository_count": created[key], "cumulative_repositories": cumulative})
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return {"username": username, "as_of": as_of.isoformat(), "scope": "public non-fork repositories, excluding profile repo",
            "repository_count": len(eligible), "stars": sum(repo["stargazers_count"] for repo in eligible),
            "forks": sum(repo["forks_count"] for repo in eligible), "language_total_bytes": None,
            "language_bytes_available": False, "language_repositories": language_count,
            "language_percentage_basis": "primary language by repository count; denominator is eligible repositories with a non-null GitHub primary language",
            "language_data_source": "GitHub repository metadata language field; this is not byte usage or framework proficiency",
            "languages": languages, "creation_timeline": timeline,
            "creation_timeline_basis": "Repository created_at month in UTC; counts repositories created, not commits or contributions",
            "repositories": normalized, "excluded": excluded,
            "completeness": {"endpoint": f"/users/{username}/repos?type=owner", "per_page": 100,
                             "page_counts": [page["count"] for page in pages], "metadata_verified_count": len(repositories)},
            "source_urls": [page["url"] for page in pages]}


def write_outputs(outputs):
    # Serialize every output and stage every file before replacing saved data.
    encoded = [(path, json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n") for path, payload in outputs]
    staged = []
    try:
        for path, content in encoded:
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
                handle.write(content)
                staged.append((Path(handle.name), path))
        for temporary, destination in staged:
            os.replace(temporary, destination)
    finally:
        for temporary, _ in staged:
            if temporary.exists():
                temporary.unlink()


def refresh(client, output_dir=ROOT / "data", as_of=None, username=USERNAME, aggregate_fn=None, raw_output=None):
    as_of = as_of or datetime.now(INDIA).date()
    repositories, pages = list_public_repositories(client, username)
    metrics = build_metrics(repositories, username, as_of, pages)
    eligible, _ = eligible_repositories(repositories, username)
    raw = {"repositories": [scan_repository(client, repo) for repo in eligible], "failures": []}
    if aggregate_fn is None:
        from technology_metrics import aggregate_technologies
        aggregate_fn = aggregate_technologies
    technologies = aggregate_fn(raw, metrics)
    if technologies.get("username") != username or technologies.get("as_of") != as_of.isoformat() or technologies.get("repository_count") != len(eligible) or technologies.get("failures"):
        raise ValueError("Technology aggregation identity, denominator or completeness is invalid")
    outputs = [(Path(output_dir) / "repository-metrics.json", metrics), (Path(output_dir) / "technologies.json", technologies)]
    if raw_output is not None:
        outputs.append((Path(raw_output), raw))
    write_outputs(outputs)
    return metrics, technologies, raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default=USERNAME)
    parser.add_argument("--as-of", type=date.fromisoformat, default=datetime.now(INDIA).date())
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--raw-output", type=Path)
    args = parser.parse_args()
    metrics, technologies, _ = refresh(GitHubClient(), args.output_dir, args.as_of, args.username, raw_output=args.raw_output)
    print(f"Refreshed {metrics['repository_count']} public non-fork repositories and {len(technologies['technologies'])} detected technologies.")


if __name__ == "__main__":
    main()
