#!/usr/bin/env python3
"""Build SiYuan sync payloads with UTF-8 JSON handling."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: str | None, fallback: Any) -> Any:
    if not path:
        return fallback
    return json.loads(Path(path).read_text(encoding="utf-8"))


def as_list(values: list[str] | None) -> list[str]:
    return [value for value in values or [] if value]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--metadata-json")
    parser.add_argument("--problem-title", default="")
    parser.add_argument("--thinking", default="")
    parser.add_argument("--commit", default="")
    parser.add_argument("--statement-markdown", default="")
    parser.add_argument("--process-markdown", default="")
    parser.add_argument("--solution-java", default="")
    parser.add_argument("--complexity-markdown", default="")
    parser.add_argument("--pitfall", action="append", default=[])
    parser.add_argument("--tag-plan-json")
    parser.add_argument("--readiness-json")
    parser.add_argument("--conversation-digest-json")
    args = parser.parse_args()

    metadata = load_json(args.metadata_json, {})
    tag_plan = load_json(args.tag_plan_json, {})
    readiness = load_json(args.readiness_json, {})
    conversation_digest = load_json(args.conversation_digest_json, {})

    problem_title = args.problem_title or metadata.get("problemTitle", "")
    thinking = args.thinking or metadata.get("thinking", "")
    commit = args.commit or metadata.get("commit", "")
    if not problem_title:
        parser.error("--problem-title or metadataJson.problemTitle is required")
    if not thinking:
        parser.error("--thinking or metadataJson.thinking is required")
    if not commit:
        parser.error("--commit or metadataJson.commit is required")

    payload = {
        "problemTitle": problem_title,
        "statementMarkdown": args.statement_markdown or metadata.get("statementMarkdown", ""),
        "thinkingMarkdown": thinking,
        "processMarkdown": args.process_markdown or metadata.get("processMarkdown", ""),
        "solutionJava": args.solution_java or metadata.get("solutionJava", ""),
        "complexityMarkdown": args.complexity_markdown or metadata.get("complexityMarkdown", ""),
        "pitfalls": as_list(args.pitfall or metadata.get("pitfalls", [])),
        "tags": tag_plan.get("tags", {}),
        "tagEvidence": tag_plan.get("tagEvidence", {}),
        "conceptKnowledge": tag_plan.get("conceptKnowledge", {}),
        "readiness": readiness,
        "conversationDigest": conversation_digest,
        "git": {
            "commit": commit,
        },
    }

    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
