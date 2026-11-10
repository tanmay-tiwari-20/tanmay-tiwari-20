#!/usr/bin/env python3
"""Losslessly package licensed local TTF fonts as WOFF 1.0 using stdlib only.

Usage: python scripts/prepare_fonts.py path/to/Poppins-Regular.ttf \
           path/to/Poppins-SemiBold.ttf

No subsetting, glyph modification, downloads, or font installation occurs.
Specification: https://www.w3.org/TR/WOFF/
"""

from __future__ import annotations

import argparse
from pathlib import Path
import struct
import zlib


ROOT = Path(__file__).resolve().parents[1]
CHECKSUM_MAGIC = 0xB1B0AFBA
WOFF_HEADER = struct.Struct(">4sIIHHIHHIIIII")
SFNT_HEADER = struct.Struct(">IHHHH")
SFNT_ENTRY = struct.Struct(">4sIII")
WOFF_ENTRY = struct.Struct(">4sIIII")


def padded(data: bytes) -> bytes:
    return data + b"\0" * (-len(data) % 4)


def checksum(data: bytes) -> int:
    block = padded(data)
    return sum(struct.unpack(f">{len(block) // 4}I", block)) & 0xFFFFFFFF


def search_fields(count: int) -> tuple[int, int, int]:
    selector = count.bit_length() - 1
    search_range = 16 * (1 << selector)
    return search_range, selector, count * 16 - search_range


def read_sfnt(source: bytes) -> tuple[int, list[dict]]:
    if len(source) < 12:
        raise ValueError("Truncated font header")
    flavor, count, search_range, selector, range_shift = SFNT_HEADER.unpack_from(source)
    if flavor not in (0x00010000, 0x4F54544F, 0x74727565) or not 1 <= count <= 4095:
        raise ValueError("Expected one TrueType/OpenType sfnt font")
    if len(source) < 12 + 16 * count:
        raise ValueError("Truncated font table directory")
    if (search_range, selector, range_shift) != search_fields(count):
        raise ValueError("Incorrect sfnt search fields")
    tables = []
    for index in range(count):
        tag, original_checksum, offset, length = SFNT_ENTRY.unpack_from(source, 12 + 16 * index)
        if offset % 4 or offset + length > len(source):
            raise ValueError(f"Invalid {tag!r} table bounds")
        data = source[offset:offset + length]
        checked = data[:8] + b"\0\0\0\0" + data[12:] if tag == b"head" else data
        if checksum(checked) != original_checksum:
            raise ValueError(f"Invalid {tag!r} table checksum")
        tables.append({"tag": tag, "offset": offset, "length": length,
                       "checksum": original_checksum, "data": data})
    tags = [table["tag"] for table in tables]
    if tags != sorted(set(tags)):
        raise ValueError("Table tags must be unique and sorted")
    cursor = 12 + 16 * count
    for table in sorted(tables, key=lambda table: table["offset"]):
        if table["offset"] != cursor:
            raise ValueError("Overlapping tables or non-font data prevent lossless packaging")
        end = cursor + table["length"]
        next_offset = (end + 3) & ~3
        if source[end:next_offset] != b"\0" * (next_offset - end):
            raise ValueError("Font table padding must be zero")
        cursor = next_offset
    if cursor != len(source):
        raise ValueError("Unexpected data after font tables")
    if checksum(source) != CHECKSUM_MAGIC:
        raise ValueError("Invalid overall sfnt checksum")
    return flavor, tables


def font_names(tables: list[dict]) -> dict[int, str]:
    name_table = next((t["data"] for t in tables if t["tag"] == b"name"), None)
    if name_table is None or len(name_table) < 6:
        return {}
    _, count, strings = struct.unpack_from(">HHH", name_table)
    names = {}
    for index in range(count):
        platform, _, language, name_id, length, offset = struct.unpack_from(">HHHHHH", name_table, 6 + 12 * index)
        if platform not in (0, 1, 3) or name_id not in (0, 1, 2, 4, 6, 13, 14):
            continue
        raw = name_table[strings + offset:strings + offset + length]
        value = raw.decode("utf-16-be" if platform in (0, 3) else "mac_roman")
        if name_id not in names or (platform == 3 and language == 0x409):
            names[name_id] = value
    return names


def encode_woff(source: bytes) -> bytes:
    flavor, tables = read_sfnt(source)
    cursor = 44 + 20 * len(tables)
    payload = bytearray()
    records = {}
    # Preserve physical table order so decoding can recover the original bytes.
    for table in sorted(tables, key=lambda table: table["offset"]):
        compressed = zlib.compress(table["data"], level=9)
        encoded = compressed if len(compressed) < table["length"] else table["data"]
        records[table["tag"]] = WOFF_ENTRY.pack(
            table["tag"], cursor, len(encoded), table["length"], table["checksum"])
        block = padded(encoded)
        payload.extend(block)
        cursor += len(block)
    header = WOFF_HEADER.pack(b"wOFF", flavor, cursor, len(tables), 0,
                              len(source), 1, 0, 0, 0, 0, 0, 0)
    return header + b"".join(records[tag] for tag in sorted(records)) + payload


def decode_woff(encoded: bytes) -> bytes:
    if len(encoded) < 44:
        raise ValueError("Truncated WOFF header")
    signature, flavor, length, count, reserved, sfnt_size, _, _, *optional = WOFF_HEADER.unpack_from(encoded)
    if signature != b"wOFF" or length != len(encoded) or reserved or any(optional):
        raise ValueError("Invalid or unsupported WOFF header")
    if not 1 <= count <= 4095 or len(encoded) < 44 + 20 * count:
        raise ValueError("Invalid WOFF table directory")
    tables = []
    for index in range(count):
        tag, offset, compressed_length, original_length, original_checksum = WOFF_ENTRY.unpack_from(encoded, 44 + 20 * index)
        if compressed_length > original_length or offset % 4 or offset + compressed_length > len(encoded):
            raise ValueError("Invalid WOFF table bounds")
        packed = encoded[offset:offset + compressed_length]
        data = zlib.decompress(packed) if compressed_length < original_length else packed
        if len(data) != original_length:
            raise ValueError("WOFF decompressed length mismatch")
        tables.append({"tag": tag, "offset": offset, "packed_length": compressed_length,
                       "length": original_length, "checksum": original_checksum, "data": data})
    tags = [table["tag"] for table in tables]
    if tags != sorted(set(tags)):
        raise ValueError("WOFF table tags must be unique and sorted")
    payload = bytearray()
    records = {}
    cursor = 12 + count * 16
    woff_cursor = 44 + count * 20
    for table in sorted(tables, key=lambda table: table["offset"]):
        if table["offset"] != woff_cursor:
            raise ValueError("Unexpected gaps or overlap in WOFF tables")
        end = woff_cursor + table["packed_length"]
        next_offset = (end + 3) & ~3
        if encoded[end:next_offset] != b"\0" * (next_offset - end):
            raise ValueError("Invalid WOFF padding")
        woff_cursor = next_offset
        records[table["tag"]] = SFNT_ENTRY.pack(table["tag"], table["checksum"], cursor, table["length"])
        block = padded(table["data"])
        payload.extend(block)
        cursor += len(block)
    if woff_cursor != len(encoded) or cursor != sfnt_size:
        raise ValueError("WOFF total size mismatch")
    result = SFNT_HEADER.pack(flavor, count, *search_fields(count))
    result += b"".join(records[tag] for tag in sorted(records)) + payload
    read_sfnt(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fonts", nargs="+", type=Path, help="Licensed local TTF/OTF source files")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets" / "fonts")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for path in args.fonts:
        source = path.read_bytes()
        _, tables = read_sfnt(source)
        names = font_names(tables)
        encoded = encode_woff(source)
        reconstructed = decode_woff(encoded)
        if reconstructed != source:
            raise ValueError(f"Lossless round-trip failed for {path.name}")
        destination = args.output_dir / f"{path.stem}.woff"
        destination.write_bytes(encoded)
        print(f"{destination.name}: {len(source):,} -> {len(encoded):,} bytes; "
              f"{len(tables)} tables verified; {names.get(4, names.get(1, 'unnamed font'))}; "
              "byte-exact round trip and all checksums valid")


if __name__ == "__main__":
    main()
