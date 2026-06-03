#!/usr/bin/env python3
"""Audit the current SiYuan interview-training system pages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COACH_SCRIPTS = ROOT / "leetcode-interview-coach" / "scripts"
sys.path.insert(0, str(COACH_SCRIPTS))

from siyuan_client import (  # noqa: E402
    DEFAULT_CONFIG,
    get_block_kramdown,
    load_config,
    normalize_hpath,
    open_client_from_config,
)


CATEGORY_ORDER = ["数据结构", "解题方法", "解题模式", "常用函数"]
SECTIONS = ["题集", "知识点", "错题与复习", "面试表达", "Codex 同步日志"]
FORBIDDEN = [
    "<a href=",
    "## 来源索引",
    "## 迁移记录",
    "## 旧笔记内容",
    "## 迁移补充",
    "## 旧笔记重组补充",
    "<!-- codex-",
    "????",
    "\ufffd",
]
AUDIT_RETENTION_DAYS = 7


def strip_kramdown_attrs(text: str) -> str:
    return re.sub(r"\{:\s+[^}]*\}", "", text)


def audit_log_dates(text: str) -> list[str]:
    cleaned = strip_kramdown_attrs(text)
    return re.findall(r"(?m)^##\s*(\d{4}-\d{2}-\d{2})\s+\d{2}:\d{2}", cleaned)


def doc_ids(client, notebook: str, hpath: str) -> list[str]:
    return client.data("/api/filetree/getIDsByHPath", {"notebook": notebook, "path": hpath}) or []


def audit(config_path: Path) -> dict:
    config = load_config(config_path)
    client, resolved = open_client_from_config(config, config_path=config_path, update_config=True)
    notebook = resolved.get("notebookId")
    root = (config.get("wikiPolicy") or {}).get("systemRootHPath", "/算法题/面试手撕训练系统")
    errors: list[str] = []
    pages: list[dict] = []

    hpaths = [normalize_hpath(root)]
    hpaths.extend(normalize_hpath(root, name) for name in SECTIONS)
    hpaths.extend(normalize_hpath(root, "知识点", category) for category in CATEGORY_ORDER)

    for hpath in hpaths:
        ids = doc_ids(client, notebook, hpath)
        if not ids:
            errors.append(f"missing page: {hpath}")
            continue
        text = get_block_kramdown(client, str(ids[0]))
        visible_text = strip_kramdown_attrs(text)
        forbidden = [marker for marker in FORBIDDEN if marker in text]
        page = {
            "hPath": hpath,
            "id": ids[0],
            "length": len(visible_text),
            "bulletCount": visible_text.count("\n- "),
            "forbidden": forbidden,
            "containsKramdownAttrs": "{:" in text,
        }
        pages.append(page)
        if len(visible_text.strip()) < 80:
            errors.append(f"page looks empty: {hpath}")
        if forbidden:
            errors.append(f"forbidden markers in {hpath}: {forbidden}")
        if hpath.rsplit("/", 1)[-1] in CATEGORY_ORDER and "（暂无知识点）" in visible_text:
            errors.append(f"category page still empty: {hpath}")
        if hpath.endswith("/错题与复习"):
            if visible_text.count("\n- ") > 5:
                errors.append("review home has too many generic bullets")
        if hpath.endswith("/Codex 同步日志"):
            dates = [datetime.strptime(value, "%Y-%m-%d") for value in audit_log_dates(text)]
            if dates and dates != sorted(dates, reverse=True):
                errors.append("audit log is not newest-first")
            cutoff = datetime.now() - timedelta(days=AUDIT_RETENTION_DAYS)
            if any(date < cutoff for date in dates):
                errors.append("audit log contains entries older than retention window")

    sql_root = root.replace("'", "''")
    stmt = (
        "select id, content, hpath from blocks "
        "where type='d' "
        f"and hpath like '{sql_root}/知识点/%' "
        "order by hpath asc"
    )
    concepts: list[dict] = []
    signal_sets: dict[tuple[str, ...], list[str]] = {}
    for row in client.data("/api/query/sql", {"stmt": stmt}) or []:
        hpath = row.get("hpath") or ""
        title = row.get("content") or hpath.rstrip("/").split("/")[-1]
        if title in {"知识点", *CATEGORY_ORDER}:
            continue
        text = get_block_kramdown(client, row["id"])
        match = re.search(r"(?ms)^##\s*什么时候想到它\s*\n(.*?)(?=^##\s+|\Z)", text)
        signals = tuple(
            line.strip()
            for line in (match.group(1).splitlines() if match else [])
            if line.strip().startswith("- ")
        )
        concept_forbidden = [marker for marker in FORBIDDEN if marker in text]
        has_problem_links = "## 题集" in text and "((" in text
        concepts.append(
            {
                "title": title,
                "hPath": hpath,
                "signalCount": len(signals),
                "signals": list(signals[:3]),
                "hasProblemLinks": has_problem_links,
                "forbidden": concept_forbidden,
            }
        )
        signal_sets.setdefault(signals, []).append(title)
        if not signals:
            errors.append(f"missing concept signals: {hpath}")
        if not has_problem_links:
            errors.append(f"missing concept problem links: {hpath}")
        if concept_forbidden:
            errors.append(f"forbidden markers in concept {hpath}: {concept_forbidden}")

    reused_signal_groups = [
        {"signals": list(signals), "concepts": names}
        for signals, names in signal_sets.items()
        if signals and len(names) >= 4
    ]
    if reused_signal_groups:
        errors.append("too many concepts share identical '什么时候想到它' content")

    problem_stmt = (
        "select id, content, hpath from blocks "
        "where type='d' "
        f"and hpath like '{sql_root}/题集/%' "
        "order by hpath asc"
    )
    problems: list[dict] = []
    required_problem_sections = ["## 知识链接", "## 题干", "## 面试版思路", "## 最终题解", "## 复杂度"]
    for row in client.data("/api/query/sql", {"stmt": problem_stmt}) or []:
        hpath = row.get("hpath") or ""
        title = row.get("content") or hpath.rstrip("/").split("/")[-1]
        text = get_block_kramdown(client, row["id"])
        problem_forbidden = [marker for marker in FORBIDDEN if marker in text]
        missing_sections = [section for section in required_problem_sections if section not in text]
        has_concept_refs = "((" in text and "## 知识链接" in text
        problems.append(
            {
                "title": title,
                "hPath": hpath,
                "length": len(text),
                "missingSections": missing_sections,
                "hasConceptRefs": has_concept_refs,
                "forbidden": problem_forbidden,
            }
        )
        if len(text.strip()) < 200:
            errors.append(f"problem page looks empty: {hpath}")
        if missing_sections:
            errors.append(f"missing problem sections in {hpath}: {missing_sections}")
        if not has_concept_refs:
            errors.append(f"missing concept refs in problem: {hpath}")
        if problem_forbidden:
            errors.append(f"forbidden markers in problem {hpath}: {problem_forbidden}")

    return {
        "api": {"url": resolved.get("url"), "notebookId": notebook},
        "root": root,
        "pages": pages,
        "problemCount": len(problems),
        "problems": problems,
        "conceptCount": len(concepts),
        "concepts": concepts,
        "reusedSignalGroupsOver3": reused_signal_groups,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--output")
    args = parser.parse_args()
    result = audit(Path(args.config))
    if args.output:
        Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
