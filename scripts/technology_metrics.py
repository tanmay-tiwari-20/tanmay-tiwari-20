"""Aggregate auditable repository coverage, never proficiency or code share.

One technology is counted at most once per eligible repository, including
repositories with no manifests in the denominator. Aliases preserve every
declared package identifier in the result.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import PurePosixPath
import json
import re
import tomllib
from urllib.parse import unquote, urlsplit


EXCLUDED_DIRECTORIES = frozenset({
    '.git', 'node_modules', 'vendor', 'dist', 'build', '.next', '.venv', 'venv',
    'coverage', 'bower_components', '.vite', '.cache', '.output', '.turbo', 'out',
})
LANGUAGE_EXTENSIONS = {
    '.js': 'JavaScript', '.jsx': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript',
    '.ts': 'TypeScript', '.tsx': 'TypeScript', '.mts': 'TypeScript', '.cts': 'TypeScript',
    '.html': 'HTML', '.htm': 'HTML', '.css': 'CSS', '.scss': 'SCSS', '.sass': 'Sass',
    '.less': 'Less', '.py': 'Python', '.ipynb': 'Jupyter Notebook', '.ejs': 'EJS',
    '.sh': 'Shell', '.bash': 'Shell', '.ps1': 'PowerShell', '.psm1': 'PowerShell',
    '.c': 'C', '.cpp': 'C++', '.cc': 'C++', '.cxx': 'C++', '.hpp': 'C++',
    '.java': 'Java', '.go': 'Go', '.rs': 'Rust', '.rb': 'Ruby', '.php': 'PHP',
    '.sql': 'SQL', '.sol': 'Solidity', '.vue': 'Vue', '.svelte': 'Svelte',
    '.swift': 'Swift', '.kt': 'Kotlin', '.kts': 'Kotlin', '.dart': 'Dart',
    '.glsl': 'GLSL', '.vert': 'GLSL', '.frag': 'GLSL',
}


# Clear technology families are grouped; arbitrary libraries remain separate.
FAMILIES = [
    ('React', 'UI framework', {'react', 'react-dom'}),
    ('Motion / Framer Motion', 'Animation', {'motion', 'framer-motion'}),
    ('GSAP', 'Animation', {'gsap', '@gsap/react'}),
    ('Socket.IO', 'Realtime', {'socket.io', 'socket.io-client', '@socket.io/redis-adapter'}),
    ('React Router', 'Routing', {'react-router', 'react-router-dom', '@react-router/dev', '@react-router/node', '@react-router/serve'}),
    ('Passport', 'Authentication', {'passport', 'passport-local', 'passport-local-mongoose'}),
    ('Sanity', 'Content management', {'sanity', 'next-sanity', 'sanity-plugin-markdown', '@sanity/image-url', '@sanity/vision'}),
    ('Redux', 'State management', {'@reduxjs/toolkit', 'react-redux', 'redux'}),
    ('TypeChain', 'Web3 tooling', {'typechain', '@typechain/ethers-v6', '@typechain/hardhat'}),
    ('Drizzle', 'Database', {'drizzle-kit', 'drizzle-orm'}),
]
NAMES = {
    'next': ('Next.js', 'Web framework'),
    'typescript': ('TypeScript', 'Language tooling'),
    'three': ('Three.js', '3D graphics'),
    '@react-three/fiber': ('React Three Fiber', '3D graphics'),
    '@react-three/drei': ('Drei', '3D graphics'),
    '@react-three/postprocessing': ('React Three Postprocessing', '3D graphics'),
    '@react-three/rapier': ('React Three Rapier', '3D physics'),
    '@dimforge/rapier3d-compat': ('Rapier', '3D physics'),
    '@react-spring/three': ('React Spring Three', 'Animation'),
    'express': ('Express', 'Backend framework'),
    'mongoose': ('Mongoose', 'Database'),
    'mongodb': ('MongoDB driver', 'Database'),
    'ioredis': ('ioredis', 'Database'),
    'postgres': ('Postgres.js', 'Database'),
    '@neondatabase/serverless': ('Neon', 'Database'),
    'postcss': ('PostCSS', 'Build tooling'),
    'autoprefixer': ('Autoprefixer', 'Build tooling'),
    'lucide-react': ('Lucide React', 'Icons'),
    'react-icons': ('React Icons', 'Icons'),
    'remixicon': ('Remix Icon', 'Icons'),
    'font-awesome': ('Font Awesome', 'Icons'),
    'react-hook-form': ('React Hook Form', 'Forms'),
    '@hookform/resolvers': ('Hook Form resolvers', 'Forms'),
    'zod': ('Zod', 'Validation'),
    'recharts': ('Recharts', 'Charts'),
    'chart.js': ('Chart.js', 'Charts'),
    'react-chartjs-2': ('React Chart.js', 'Charts'),
    'locomotive-scroll': ('Locomotive Scroll', 'Animation'),
    'lenis': ('Lenis', 'Animation'),
    'animejs': ('Anime.js', 'Animation'),
    'animate.css': ('Animate.css', 'Animation'),
    'sheryjs': ('Shery.js', 'Animation'),
    'textillate': ('Textillate', 'Animation'),
    'cdn:lettering.js': ('Lettering.js', 'Typography'),
    'cdn:controlkit.js': ('ControlKit', 'UI controls'),
    'cdn:google-fonts': ('Google Fonts', 'Typography'),
    'tsparticles': ('tsParticles', 'Animation'),
    'jquery': ('jQuery', 'UI library'),
    'bootstrap': ('Bootstrap', 'UI framework'),
    'materialize-css': ('Materialize', 'UI framework'),
    'styled-components': ('Styled Components', 'Styling'),
    'tailwind-merge': ('Tailwind Merge', 'Styling'),
    'tailwindcss-animate': ('Tailwind CSS Animate', 'Animation'),
    'tw-animate-css': ('TW Animate CSS', 'Animation'),
    'clsx': ('clsx', 'Styling utility'),
    'classnames': ('classnames', 'Styling utility'),
    'class-variance-authority': ('Class Variance Authority', 'Styling utility'),
    'zustand': ('Zustand', 'State management'),
    'valtio': ('Valtio', 'State management'),
    'recoil': ('Recoil', 'State management'),
    '@clerk/nextjs': ('Clerk', 'Authentication'),
    'next-auth': ('NextAuth.js', 'Authentication'),
    'jsonwebtoken': ('JSON Web Token', 'Authentication'),
    'jose': ('JOSE', 'Authentication'),
    'bcrypt': ('bcrypt', 'Authentication'),
    'bcryptjs': ('bcryptjs', 'Authentication'),
    'ejs': ('EJS', 'Templating'),
    'axios': ('Axios', 'HTTP client'),
    'cloudinary': ('Cloudinary', 'Media service'),
    '@vercel/analytics': ('Vercel Analytics', 'Analytics'),
    '@emailjs/browser': ('EmailJS', 'Email'),
    'resend': ('Resend', 'Email'),
    'nodemailer': ('Nodemailer', 'Email'),
    '@google/generative-ai': ('Google Generative AI SDK', 'AI'),
    'pdfjs-dist': ('PDF.js', 'Documents'),
    'vitest': ('Vitest', 'Testing'),
    'prettier': ('Prettier', 'Development tooling'),
    'react-scripts': ('Create React App', 'Build tooling'),
    'nodemon': ('Nodemon', 'Development tooling'),
    'tsx': ('tsx', 'Language tooling'),
    'ts-node-dev': ('ts-node-dev', 'Language tooling'),
    'hardhat': ('Hardhat', 'Web3 tooling'),
    'hardhat-gas-reporter': ('Hardhat', 'Web3 tooling'),
    'solidity-coverage': ('Solidity Coverage', 'Web3 tooling'),
    'ethers': ('ethers.js', 'Web3'),
    'viem': ('Viem', 'Web3'),
    '@openzeppelin/contracts': ('OpenZeppelin Contracts', 'Web3'),
    '@chainlink/contracts': ('Chainlink Contracts', 'Web3'),
    '@layerzerolabs/lz-evm-oapp-v2': ('LayerZero', 'Web3'),
    '@lit-protocol/lit-node-client': ('Lit Protocol', 'Web3'),
    '@ethsign/sp-sdk': ('Sign Protocol', 'Web3'),
    'leaflet': ('Leaflet', 'Maps'),
    'react-leaflet': ('React Leaflet', 'Maps'),
    '@react-google-maps/api': ('React Google Maps', 'Maps'),
    'backend': ('Workspace package: backend', 'Project dependency'),
}


def canonical_package(package):
    for name, category, packages in FAMILIES:
        if package in packages:
            return name, category
    if package == 'tailwindcss' or package.startswith('@tailwindcss/'):
        return 'Tailwind CSS', 'Styling'
    if package == 'eslint' or package.startswith(('eslint-', '@eslint/')):
        return 'ESLint', 'Development tooling'
    if package == 'vite' or package.startswith(('@vitejs/', 'vite-')):
        return 'Vite', 'Build tooling'
    if package.startswith('@types/'):
        return 'TypeScript type definitions', 'Type definitions'
    for prefix, name, category in (
        ('@radix-ui/', 'Radix UI', 'UI primitives'),
        ('@chakra-ui/', 'Chakra UI', 'UI framework'),
        ('@emotion/', 'Emotion', 'Styling'),
        ('@stream-io/', 'Stream', 'Video and realtime'),
        ('@testing-library/', 'Testing Library', 'Testing'),
        ('@nomicfoundation/', 'Hardhat', 'Web3 tooling'),
        ('@web3auth/', 'Web3Auth', 'Authentication'),
        ('workbox-', 'Workbox', 'Progressive web apps'),
    ):
        if package.startswith(prefix):
            return name, category
    return NAMES.get(package, (package, 'Library'))


def is_first_party_path(path):
    path = PurePosixPath(path)
    return not any(part.lower() in EXCLUDED_DIRECTORIES for part in path.parts)


def source_language(path):
    if not is_first_party_path(path) or re.search(r'\.min\.(?:js|css)$', path, re.IGNORECASE):
        return None
    return LANGUAGE_EXTENSIONS.get(PurePosixPath(path).suffix.lower())


def python_requirement(value):
    value = value.strip()
    if not value or value.startswith('#'):
        return None
    if value.startswith(('-r ', '--requirement ', '-c ', '--constraint ', '--index-url', '--extra-index-url')):
        return None
    egg = re.search(r'[#&]egg=([A-Za-z0-9_.-]+)', value)
    match = egg or re.match(r'^([A-Za-z0-9][A-Za-z0-9_.-]*)\s*(?:\[|[<>=!~;@ ]|$)', value)
    if not match:
        raise ValueError('Unrecognized Python requirement: ' + value[:120])
    return re.sub(r'[-_.]+', '-', match.group(1)).lower()


def manifest_dependencies(manifest):
    path, content = manifest['path'], manifest['content']
    result = []
    if PurePosixPath(path).name == 'package.json':
        data = json.loads(content)
        for section in ('dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies'):
            values = data.get(section, {})
            if not isinstance(values, dict):
                raise ValueError(f'{path}: {section} must be an object')
            for package, version in values.items():
                if not isinstance(package, str) or not isinstance(version, str):
                    raise ValueError(f'{path}: invalid dependency declaration')
                result.append({'package': package, 'section': section, 'version': version})
    elif PurePosixPath(path).name == 'pyproject.toml':
        data = tomllib.loads(content)
        project = data.get('project', {})
        groups = [('project.dependencies', project.get('dependencies', []))]
        groups.extend(('project.optional-dependencies.' + key, value) for key, value in project.get('optional-dependencies', {}).items())
        groups.extend(('dependency-groups.' + key, [v for v in value if isinstance(v, str)]) for key, value in data.get('dependency-groups', {}).items())
        for section, values in groups:
            for value in values:
                package = python_requirement(value)
                if package:
                    result.append({'package': package, 'section': section, 'version': value})
        poetry = data.get('tool', {}).get('poetry', {})
        poetry_groups = [('tool.poetry.dependencies', poetry.get('dependencies', {}))]
        poetry_groups.extend(('tool.poetry.group.' + key, value.get('dependencies', {})) for key, value in poetry.get('group', {}).items())
        for section, values in poetry_groups:
            for package, version in values.items():
                if package != 'python':
                    result.append({'package': re.sub(r'[-_.]+', '-', package).lower(), 'section': section, 'version': str(version)})
    else:
        for value in content.splitlines():
            package = python_requirement(value)
            if package:
                result.append({'package': package, 'section': 'requirements', 'version': value.strip()})
    return result


class CdnParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        candidate = attrs.get('src') if tag == 'script' else attrs.get('href') if tag == 'link' and attrs.get('rel') == 'stylesheet' else None
        if candidate and candidate.startswith(('http://', 'https://', '//')):
            self.urls.append(candidate)


def cdn_package(url):
    parsed = urlsplit(url if not url.startswith('//') else 'https:' + url)
    host, path = parsed.hostname, unquote(parsed.path)
    if host == 'fonts.googleapis.com':
        return 'cdn:google-fonts'
    if host == 'cdn.tailwindcss.com':
        return 'tailwindcss'
    if host == 'code.jquery.com' and path.startswith('/jquery-'):
        return 'jquery'
    if host == 'cdnjs.cloudflare.com':
        match = re.match(r'/ajax/libs/([^/]+)/', path)
        if match:
            package = match.group(1)
            return {'three.js': 'three', 'lettering.js': 'cdn:lettering.js'}.get(package, package)
    if host == 'cdn.jsdelivr.net' and path.startswith('/gh/automat/controlkit.js@'):
        return 'cdn:controlkit.js'
    if host == 'cdn.jsdelivr.net' and path.startswith('/npm/'):
        path = path[5:]
    elif host == 'unpkg.com':
        path = path.lstrip('/')
    else:
        return None
    if path.startswith('@'):
        match = re.match(r'(@[^/]+/[^/@]+)', path)
    else:
        match = re.match(r'([^/@]+)', path)
    return match.group(1) if match else None


def aggregate_technologies(raw, metrics):
    if raw.get('failures'):
        raise ValueError('Technology audit is incomplete')
    eligible = {repo['name'] for repo in metrics['repositories']}
    denominator = metrics['repository_count']
    records = raw['repositories']
    if not denominator or len(eligible) != denominator or {r['name'] for r in records} != eligible or len(records) != denominator:
        raise ValueError('Technology denominator and complete repository coverage must agree')
    technologies = {}
    languages = {}
    sources, unclassified = set(), []
    manifest_repositories, cdn_repositories = [], []
    manifest_count = 0
    for repo in records:
        if repo.get('status') != 'scanned':
            raise ValueError('Unscanned repository: ' + repo['name'])
        name = repo['name']
        sources.add(repo['tree_url'])
        if repo['manifests']:
            manifest_repositories.append(name)
        if repo['cdn_html']:
            cdn_repositories.append(name)
        dependencies = []
        for manifest in repo['manifests']:
            if not is_first_party_path(manifest['path']):
                raise ValueError('Vendored manifest included in audit')
            manifest_count += 1
            sources.add(manifest['url'])
            declarations = manifest_dependencies(manifest)
            manifest['declarations'] = declarations
            dependencies.extend(item['package'] for item in declarations)
        for html in repo['cdn_html']:
            sources.add(html['url'])
            parser = CdnParser()
            parser.feed(html['content'])
            evidence = []
            for url in dict.fromkeys(parser.urls):
                package = cdn_package(url)
                if package:
                    dependencies.append(package)
                    evidence.append({'package': package, 'url': url})
                else:
                    unclassified.append({'repository': name, 'path': html['path'], 'url': url})
            html['cdn_dependencies'] = evidence
        repo['detected_packages'] = sorted(set(dependencies), key=str.casefold)
        for package in set(dependencies):
            title, category = canonical_package(package)
            item = technologies.setdefault(title, {'name': title, 'category': category, 'package_names': set(), 'repositories': set()})
            item['package_names'].add(package)
            item['repositories'].add(name)
        repo['language_files'] = []
        for file in repo['source_files']:
            language = source_language(file['path'])
            if language:
                item = languages.setdefault(language, {'name': language, 'extensions_present': set(), 'repositories': set()})
                item['extensions_present'].add(PurePosixPath(file['path']).suffix.lower())
                item['repositories'].add(name)
                repo['language_files'].append({'path': file['path'], 'sha': file['sha'], 'language': language})
    def finalize(items):
        rows = []
        for item in items.values():
            row = {key: sorted(value, key=str.casefold) if isinstance(value, set) else value for key, value in item.items()}
            row['count'] = len(row['repositories'])
            row['percent'] = round(row['count'] * 100 / denominator, 2)
            rows.append(row)
        return sorted(rows, key=lambda row: (-row['count'], row['name'].casefold()))
    rows = finalize(technologies)
    return {
        'username': metrics['username'], 'as_of': metrics['as_of'],
        'scope': 'Current default branches of public non-fork repositories, excluding the profile repository. Explicit package dependencies, devDependencies, optionalDependencies and peerDependencies; plus script/stylesheet CDN references in root or one-level HTML only where no package/Python manifest exists.',
        'percentage_basis': 'Repository coverage: repositories with each technology / all eligible repositories. Each technology counts once per repository. Categories overlap; percentages do not sum to 100. These are declared dependencies and references, not proficiency, runtime adoption, code bytes or complete historical usage.',
        'repository_count': denominator,
        'scanned_repositories': len(records),
        'manifest_repositories': len(manifest_repositories),
        'manifest_count': manifest_count,
        'cdn_scanned_repositories': len(cdn_repositories),
        'repositories_scanned': sorted(eligible, key=str.casefold),
        'repositories_with_manifests': sorted(manifest_repositories, key=str.casefold),
        'technology_count': len(rows),
        'package_identifier_count': len({package for row in rows for package in row['package_names']}),
        'technologies': rows,
        'language_presence_basis': 'Extension-based presence in current first-party source/config/test files; generated/vendor directories and .min.js/.min.css files excluded. Data formats and assets are excluded. Languages overlap. This is not GitHub Linguist byte usage, not historical totals, and embedded languages inside HTML are not inferred.',
        'language_presence': finalize(languages),
        'source_urls': sorted(sources), 'failures': [],
        'unclassified_cdn_urls': unclassified,
    }
