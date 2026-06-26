#!/usr/bin/env python3
"""Write workflow metadata JSON without routing Chinese text through PowerShell."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


CORRUPTION_MARKERS = ["????", "\ufffd", "\u951f\u65a4\u62f7", "\u00ef\u00bf\u00bd"]
METADATA_KEYS_REJECTING_QUESTION_MARK = {
    "problemTitle",
    "title",
    "hPath",
    "systemRootHPath",
    "concept",
    "conceptName",
    "tag",
    "label",
    "reviewLabel",
}


def parse_assignment(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise ValueError(f"Expected key=value assignment, got: {value}")
    key, raw = value.split("=", 1)
    key = key.strip()
    if not key:
        raise ValueError(f"Empty key in assignment: {value}")
    return key, raw


def read_utf8(path: str) -> str:
    return Path(path).read_text(encoding="utf-8-sig")


def load_json(path: str) -> dict[str, Any]:
    data = json.loads(read_utf8(path))
    if not isinstance(data, dict):
        raise ValueError(f"Base JSON must be an object: {path}")
    return data


def load_source_dir(path: str) -> dict[str, Any]:
    source_dir = Path(path)
    if not source_dir.is_dir():
        raise ValueError(f"Source directory does not exist: {path}")

    payload: dict[str, Any] = {}
    for item in sorted(source_dir.iterdir()):
        if not item.is_file():
            continue
        name = item.name
        if name.endswith(".list.txt"):
            key = name[: -len(".list.txt")]
            payload[key] = [line for line in read_utf8(str(item)).splitlines() if line.strip()]
        elif name.endswith(".txt"):
            key = name[: -len(".txt")]
            payload[key] = read_utf8(str(item))
    return payload


def ensure_cli_value_is_ascii(key: str, value: str) -> None:
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError(
            f"Non-ASCII CLI value for {key!r} is refused. "
            "Write the text to a UTF-8 file and pass it with --field-file instead."
        ) from exc


def scan_text(path: str, key: str, text: str, *, metadata: bool) -> list[str]:
    errors: list[str] = []
    for marker in CORRUPTION_MARKERS:
        if marker in text:
            errors.append(f"{path}.{key}: contains corruption marker {marker!r}")
    if re.search(r"\?{2,}", text):
        errors.append(f"{path}.{key}: contains repeated ASCII '?' characters")
    if metadata and "?" in text:
        errors.append(f"{path}.{key}: metadata field contains ASCII '?'")
    return errors


def scan_value(path: str, key: str, value: Any) -> list[str]:
    metadata = key in METADATA_KEYS_REJECTING_QUESTION_MARK
    if isinstance(value, str):
        return scan_text(path, key, value, metadata=metadata)
    if isinstance(value, list):
        errors: list[str] = []
        for index, item in enumerate(value):
            errors.extend(scan_value(path, f"{key}[{index}]", item))
        return errors
    if isinstance(value, dict):
        errors: list[str] = []
        for child_key, item in value.items():
            errors.extend(scan_value(path, f"{key}.{child_key}", item))
        return errors
    return []


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build UTF-8 metadata JSON from UTF-8 source files."
    )
    parser.add_argument("--kind", choices=["commit", "workflow", "generic"], default="generic")
    parser.add_argument("--output", required=True)
    parser.add_argument("--base-json")
    parser.add_argument(
        "--source-dir",
        help=(
            "ASCII temp directory containing UTF-8 files such as problemTitle.txt, "
            "thinking.txt, solutionJava.txt, and pitfalls.list.txt."
        ),
    )
    parser.add_argument(
        "--field",
        action="append",
        default=[],
        help="ASCII-only key=value. Use --field-file for Chinese or multi-line text.",
    )
    parser.add_argument(
        "--field-file",
        action="append",
        default=[],
        help="key=path; read the value from a strict UTF-8 text file.",
    )
    parser.add_argument(
        "--list-field-file",
        action="append",
        default=[],
        help="key=path; read a UTF-8 text file as non-empty lines.",
    )
    parser.add_argument(
        "--json-field-file",
        action="append",
        default=[],
        help="key=path; read a UTF-8 JSON value from the file.",
    )
    parser.add_argument(
        "--set-field",
        action="append",
        default=[],
        help="ASCII-only key=value override; intended for generated ASCII fields such as commit hashes.",
    )
    parser.add_argument(
        "--set-field-file",
        action="append",
        default=[],
        help="key=path; override the field with strict UTF-8 text read from a file.",
    )
    parser.add_argument(
        "--set-json-field-file",
        action="append",
        default=[],
        help="key=path; override the field with a UTF-8 JSON value read from a file.",
    )
    parser.add_argument("--require", action="append", default=[])
    args = parser.parse_args()

    payload: dict[str, Any] = load_json(args.base_json) if args.base_json else {}
    if args.source_dir:
        payload.update(load_source_dir(args.source_dir))

    for assignment in args.field:
        key, value = parse_assignment(assignment)
        ensure_cli_value_is_ascii(key, value)
        payload[key] = value

    for assignment in args.field_file:
        key, path = parse_assignment(assignment)
        payload[key] = read_utf8(path)

    for assignment in args.list_field_file:
        key, path = parse_assignment(assignment)
        payload[key] = [line for line in read_utf8(path).splitlines() if line.strip()]

    for assignment in args.json_field_file:
        key, path = parse_assignment(assignment)
        payload[key] = json.loads(read_utf8(path))

    for assignment in args.set_field:
        key, value = parse_assignment(assignment)
        ensure_cli_value_is_ascii(key, value)
        payload[key] = value

    for assignment in args.set_field_file:
        key, path = parse_assignment(assignment)
        payload[key] = read_utf8(path)

    for assignment in args.set_json_field_file:
        key, path = parse_assignment(assignment)
        payload[key] = json.loads(read_utf8(path))

    required = list(args.require)
    if args.kind in {"commit", "workflow"}:
        required.extend(["problemTitle", "thinking"])
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError(f"Missing required metadata field(s): {', '.join(missing)}")

    errors: list[str] = []
    for key, value in payload.items():
        errors.extend(scan_value("metadata", key, value))
    if errors:
        raise ValueError("Metadata validation failed:\n" + "\n".join(errors))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"write_utf8_metadata failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
