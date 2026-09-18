#!/usr/bin/env python3
"""Check a persisted closeout report without rerunning Git or publishing writes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def payload_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def java_tokens(code: str) -> list[str]:
    pattern = r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_$][\w$]*|\d+|[^\s]'
    tokens = [token for token in re.findall(pattern, code) if not token.startswith(("//", "/*"))]
    # A copyable LeetCode answer can wrap the same methods in class Solution.
    while tokens and tokens[0] in ("package", "import") and ";" in tokens:
        tokens = tokens[tokens.index(";") + 1:]
    class_index = next((index for index in range(min(4, len(tokens))) if tokens[index] == "class"), None)
    if class_index is not None and all(token in ("public", "final", "static") for token in tokens[:class_index]):
        if len(tokens) > class_index + 3 and tokens[class_index + 2] == "{" and tokens[-1] == "}":
            tokens = tokens[class_index + 3:-1]
    return tokens


def validate_learning_record(record: dict[str, Any], java_path: Path | None = None) -> list[str]:
    """New closeouts require source material or an explicit missing-history note.

    This does not change legacy renderer/provider payload compatibility.
    """
    errors = []
    if not str(record.get("solutionJava") or "").strip():
        errors.append("solutionJava is empty")
    variants = record.get("solutionVariants")
    if isinstance(variants, list) and variants:
        finals = [variant for variant in variants if isinstance(variant, dict) and variant.get("isFinal") is True]
        if len(finals) != 1:
            errors.append("solutionVariants must contain exactly one final answer")
        else:
            final = finals[0]
            if str(final.get("language") or "java").lower() == "java" and java_tokens(str(final.get("code") or "")) != java_tokens(str(record.get("solutionJava") or "")):
                errors.append("The rendered final Java variant differs from solutionJava")
    if java_path:
        java = java_path.read_text(encoding="utf-8-sig")
        region = re.search(r"// region LeetCode solution\s*([\s\S]*?)// endregion", java)
        if not region:
            errors.append("Java solution region is missing; cannot verify the payload matches the compiled solution")
        elif java_tokens(region.group(1)) != java_tokens(str(record.get("solutionJava") or "")):
            errors.append("Java solution region differs from solutionJava; integrate the final answer before publishing")
    transcript = record.get("teachingTranscript")
    metadata = record.get("sourceMetadata") or {}
    missing = metadata.get("missingTeachingHistory") if isinstance(metadata, dict) else None
    if not transcript and not missing:
        errors.append("teachingTranscript is missing; recover real history or explicitly describe sourceMetadata.missingTeachingHistory")
    if missing:
        from render_learning_note import render_markdown
        notes = missing if isinstance(missing, list) else [missing]
        try:
            visible = render_markdown(record)
            if any(not isinstance(note, str) or not note.strip() or note.strip() not in visible for note in notes):
                errors.append("Every missingTeachingHistory explanation must also appear in the rendered teaching record")
        except (ValueError, TypeError) as exc:
            errors.append(f"Learning record cannot be rendered: {exc}")
    return errors


def validate_target_evidence(report: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    provider = evidence.get("provider")
    target = (report.get("providers") or {}).get(provider)
    if provider != "yuque" or not target or not target.get("enabled"):
        raise ValueError("Verification evidence must name an enabled YuQue provider")
    for key in ("workflowId", "payloadSha256"):
        if not report.get(key) or evidence.get(key) != report[key]:
            raise ValueError(f"Verification evidence does not match this closeout's {key}")
    if not target.get("url") or evidence.get("url") != target["url"]:
        raise ValueError("Verification evidence URL differs from the published target")
    checked_at = datetime.fromisoformat(str(evidence.get("checkedAt") or "").replace("Z", "+00:00"))
    if checked_at.tzinfo is None:
        raise ValueError("checkedAt must include a timezone")
    if not str(evidence.get("observation") or "").strip():
        raise ValueError("Verification evidence needs a concrete observation")
    paths = evidence.get("evidencePaths")
    if not isinstance(paths, list) or not paths or any(not Path(path).is_file() for path in paths):
        raise ValueError("Verification evidence must link saved API or UI observations that exist")
    return target


def add_browser_evidence(report: dict[str, Any], evidence: dict[str, Any]) -> None:
    target = validate_target_evidence(report, evidence)
    required_checks = ("nativeCollapse", "codeBlockNames", "codeHighlight", "quotesLinksBold", "finalAnswerVisible")
    if any((evidence.get("checks") or {}).get(key) is not True for key in required_checks):
        raise ValueError("Browser evidence must confirm every visual/interaction check")
    target["stages"]["browser"] = {"status": "passed", "evidence": evidence}


def add_verification_evidence(report: dict[str, Any], evidence: dict[str, Any]) -> None:
    """Record a later read-only recovery without replaying any provider writes."""
    target = validate_target_evidence(report, evidence)
    stages = evidence.get("verifiedStages")
    if not isinstance(stages, list) or not stages or any(stage not in ("write", "directory", "readback") for stage in stages):
        raise ValueError("verifiedStages must name only write, directory or readback")
    if evidence.get("readOnly") is not True:
        raise ValueError("Recovery evidence must come from read-only checks")
    for stage in stages:
        previous = target["stages"].get(stage)
        target.setdefault("recoveryHistory", []).append({"stage": stage, "previous": previous, "evidence": evidence})
        target["stages"][stage] = {"status": "passed", "evidence": evidence}


def evaluate(report: dict[str, Any]) -> dict[str, Any]:
    """Recompute completion; neither exit code 0 nor 'written' proves verification."""
    incomplete = []
    for name in ("configuration", "record", "local", "commit", "push"):
        stage = (report.get("stages") or {}).get(name) or {}
        if stage.get("status") != "passed" or not stage.get("evidence"):
            incomplete.append(f"{name}: {stage.get('status', 'missing')}")
    providers = report.get("providers") or {}
    for name in ("siyuan", "yuque"):
        if name not in providers or not isinstance(providers[name].get("enabled"), bool):
            incomplete.append(f"{name}: explicit enabled/disabled decision is missing")
    for name, provider in providers.items():
        if not provider.get("enabled"):
            continue
        required = ("dryRun", "write", "directory", "readback")
        if name == "yuque":
            required += ("browser",)
        for step in required:
            stage = (provider.get("stages") or {}).get(step) or {}
            if stage.get("status") != "passed" or not stage.get("evidence"):
                incomplete.append(f"{name}.{step}: {stage.get('status', 'missing')}")
            elif step == "browser":
                try:
                    add_browser_evidence(report, stage["evidence"])
                except (OSError, ValueError, TypeError) as exc:
                    incomplete.append(f"{name}.browser: invalid evidence ({exc})")
    path = Path(report.get("payloadPath") or "__missing_payload__")
    if not path.is_file() or not report.get("payloadSha256") or payload_digest(path) != report["payloadSha256"]:
        incomplete.append("learning record: missing or changed since publication")
    # failures is retained diagnostic history. Current stage evidence determines
    # whether a subsequent read-only recovery actually resolved the failure.
    if report.get("fatalError"):
        incomplete.append(str(report["fatalError"]))
    report["incomplete"] = incomplete
    report["complete"] = not incomplete
    report["status"] = "complete" if not incomplete else "incomplete"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--browser-evidence", type=Path)
    parser.add_argument("--verification-evidence", type=Path)
    parser.add_argument("--validate-record", type=Path)
    parser.add_argument("--java-path", type=Path)
    args = parser.parse_args()
    try:
        if args.validate_record:
            errors = validate_learning_record(load_json(args.validate_record), args.java_path)
            print(json.dumps({"passed": not errors, "errors": errors}, ensure_ascii=False))
            return 2 if errors else 0
        if not args.report:
            parser.error("--report or --validate-record is required")
        report = load_json(args.report)
        if args.verification_evidence:
            add_verification_evidence(report, load_json(args.verification_evidence))
        if args.browser_evidence:
            add_browser_evidence(report, load_json(args.browser_evidence))
        evaluate(report)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["complete"] else 2
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"complete": False, "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
