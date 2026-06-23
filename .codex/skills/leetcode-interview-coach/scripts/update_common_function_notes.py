#!/usr/bin/env python3
"""Create or update repository notes for Java common-function usage."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from common_function_usage import detect_function_usages, note_path_for_usage, render_function_note


def load_json(path: str | None) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--java-path", required=True)
    parser.add_argument("--workflow-metadata-json")
    parser.add_argument("--problem-title", default="")
    parser.add_argument("--problem-note", default="")
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    repo_root = Path.cwd()
    java_path = repo_root / args.java_path
    solution_java = java_path.read_text(encoding="utf-8")
    metadata = load_json(args.workflow_metadata_json)
    problem_title = args.problem_title or metadata.get("problemTitle", "")
    usages = detect_function_usages(
        solution_java,
        problem_title=problem_title,
        problem_note_path=args.problem_note,
    )

    updated_paths: list[str] = []
    for usage in usages:
        note_path = note_path_for_usage(repo_root, usage)
        existing = note_path.read_text(encoding="utf-8") if note_path.exists() else ""
        updated = render_function_note(usage, existing)
        if updated != existing:
            note_path.parent.mkdir(parents=True, exist_ok=True)
            note_path.write_text(updated, encoding="utf-8")
        updated_paths.append(str(note_path.relative_to(repo_root)).replace("/", "\\"))

    output = {
        "updatedPaths": updated_paths,
        "usages": usages,
    }
    Path(args.output_json).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
