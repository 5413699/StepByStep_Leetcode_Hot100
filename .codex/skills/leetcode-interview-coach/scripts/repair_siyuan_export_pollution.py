#!/usr/bin/env python3
"""Repair SiYuan pages polluted by exportMdContent footnotes/frontmatter."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from siyuan_client import DEFAULT_CONFIG, get_block_kramdown, load_config, normalize_hpath, open_client_from_config, update_doc
from sync_leetcode_to_siyuan import CATEGORY_DESCRIPTIONS, CATEGORY_ORDER, own_doc_markdown, strip_block_markdown


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_ROOT = "/算法题/面试手撕训练系统"
POLLUTION_PATTERNS = [
    re.compile(r"(?m)^(title|date|lastmod):\s*"),
    re.compile(r"\[\^\d+\]"),
    re.compile(r"(?m)^##\s+知识链接\s*$"),
    re.compile(r"(?m)^##\s+题干\s*$"),
    re.compile(r"(?m)^##\s+第一反应\s*$"),
    re.compile(r"(?m)^##\s+卡壳点\s*$"),
]


def list_doc_rows(client: Any, root: str) -> list[dict[str, Any]]:
    escaped_root = root.replace("'", "''")
    sql = (
        "select id, hpath, content from blocks "
        f"where type='d' and (hpath = '{escaped_root}' or hpath like '{escaped_root}/%') "
        "order by hpath"
    )
    return client.data("/api/query/sql", {"stmt": sql}) or []


def has_pollution(markdown: str) -> bool:
    return any(pattern.search(markdown) for pattern in POLLUTION_PATTERNS)


def remove_export_footnote_refs(markdown: str) -> str:
    return re.sub(r"\[\^\d+\]", "", markdown)


def remove_export_footnote_definitions(markdown: str) -> str:
    return re.sub(r"(?ms)(?:^|\n)\[\^\d+\]:\s*#\s+.*?(?=\n##\s+|\Z)", "\n", markdown)


def remove_problem_export_sections(markdown: str) -> str:
    first_problem_heading = re.search(r"(?m)^##\s+(知识链接|题干|第一反应|卡壳点|关键突破|思考过程|面试版思路|最终题解|复杂度|易错点|面试表达|掌握状态|复习建议|同步记录)\s*$", markdown)
    if not first_problem_heading:
        return markdown
    return markdown[: first_problem_heading.start()].rstrip() + "\n"


def base_clean(markdown: str) -> str:
    text = strip_block_markdown(markdown)
    text = remove_export_footnote_definitions(text)
    text = remove_export_footnote_refs(text)
    text = remove_problem_export_sections(text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def ensure_heading(markdown: str, heading: str, default_body: str = "") -> str:
    if re.search(rf"(?m)^##\s+{re.escape(heading)}\s*$", markdown):
        return markdown
    if markdown.strip().startswith("- "):
        return f"## {heading}\n\n{markdown.strip()}"
    addition = f"## {heading}\n\n{default_body.strip()}\n" if default_body.strip() else f"## {heading}\n"
    return (markdown.rstrip() + "\n\n" + addition).strip()


def default_concept_markdown(title: str) -> str:
    return "\n".join(
        [
            "## 简介",
            "",
            f"TODO：为 `{title}` 补充基于本地知识库或网络开源资料的具体介绍。不要使用通用套话创建知识点页。",
            "",
            "## 什么时候想到它",
            "",
            "- TODO：补充该知识点在题目中的具体识别信号。",
            "",
            "## 常见代码结构",
            "",
            "```java",
            "// TODO: 补充该知识点的真实代码结构",
            "```",
            "",
            "## 高频易错点",
            "",
            "- TODO：补充该知识点的真实易错点。",
            "",
            "## 题集",
        ]
    )


def clean_concept_page(markdown: str, title: str) -> str:
    text = base_clean(markdown)
    if not text:
        text = default_concept_markdown(title)
    text = ensure_heading(text, "题集")
    return text.strip() + "\n"


def clean_category_page(markdown: str) -> str:
    text = base_clean(markdown)
    text = ensure_heading(text, "知识点")
    return text.strip() + "\n"


def default_root_home() -> str:
    return "\n".join(
        [
            "## 今日入口",
            "",
            "- 题集：按题号复习已经整理过的 Hot100 题目。",
            "- 知识点：按数据结构、方法、模式、常用函数复习。",
            "- 错题与复习：按掌握状态安排二刷和表达训练。",
            "- 面试表达：沉淀面试中可直接说出口的解题表达。",
            "- Codex 同步日志：审阅自动同步、修复和迁移记录。",
            "",
            "## 最近同步",
        ]
    )


def clean_home_page(markdown: str, title: str) -> str:
    text = base_clean(markdown)
    if text:
        return text.strip() + "\n"
    if title == "面试手撕训练系统":
        return default_root_home().strip() + "\n"
    if title == "题集":
        return "## 题目列表\n\n这里按题号汇总已完成整理的题目页。\n"
    if title == "知识点":
        lines = ["## 分类入口", ""]
        lines.extend([f"- {category}：{CATEGORY_DESCRIPTIONS[category]}" for category in CATEGORY_ORDER])
        lines.extend(["", "## 最近关联知识点"])
        return "\n".join(lines).strip() + "\n"
    if title == "错题与复习":
        return "## 复习原则\n\n这里只保留需要复盘的真实题目入口。\n\n## 当前复习入口\n\n- 暂无自动归档题目。\n"
    if title == "面试表达":
        return "## 思路表达模板\n\n- 先说明题型识别信号。\n- 再说明核心状态、辅助函数或遍历结构。\n- 然后说明为什么这样更新答案，以及复杂度。\n\n## 最近可练表达题\n"
    return f"## 说明\n\n{title} 页面用于承接面试手撕训练系统的自动同步内容。\n"


def clean_review_page(markdown: str, title: str) -> str:
    text = base_clean(markdown)
    if not text:
        text = f"## 说明\n\n{title} 用于跟踪需要复习的题目。\n"
    text = ensure_heading(text, "题集")
    return text.strip() + "\n"


def page_kind(root: str, hpath: str) -> str:
    rel = hpath.removeprefix(root).strip("/")
    parts = rel.split("/") if rel else []
    if not parts:
        return "root"
    if parts[0] == "题集":
        return "problem" if len(parts) > 1 else "home"
    if parts[0] == "知识点":
        if len(parts) == 1:
            return "home"
        if len(parts) == 2 and parts[1] in CATEGORY_ORDER:
            return "category"
        if len(parts) >= 3 and parts[1] in CATEGORY_ORDER:
            return "concept"
        return "home"
    if parts[0] == "错题与复习":
        return "review" if len(parts) > 1 else "home"
    if parts[0] in {"面试表达", "Codex 同步日志"}:
        return "home"
    return "home"


def short_preview(markdown: str) -> str:
    text = re.sub(r"\s+", " ", markdown).strip()
    return text[:180]


def repair_page(client: Any, root: str, hpath: str, doc_id: str, title: str, dry_run: bool) -> tuple[bool, str, str, str]:
    kind = page_kind(root, hpath)
    if kind == "problem":
        return False, kind, "", ""
    raw = get_block_kramdown(client, doc_id)
    current = own_doc_markdown(client, doc_id)
    raw_has_pollution = has_pollution(raw)
    if not raw_has_pollution and not has_pollution(current):
        return False, kind, "", ""
    if kind == "concept":
        repaired = clean_concept_page(raw, title)
    elif kind == "category":
        repaired = clean_category_page(raw)
    elif kind == "review":
        repaired = clean_review_page(raw, title)
    else:
        repaired = clean_home_page(raw, title)
    if repaired == current and not raw_has_pollution:
        return False, kind, "", ""
    if not dry_run:
        update_doc(client, doc_id, repaired)
    return True, kind, short_preview(raw), short_preview(repaired)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--root", default=DEFAULT_ROOT)
    parser.add_argument("--apply", action="store_true", help="write repairs to SiYuan; without this flag the script only prints a dry-run plan")
    args = parser.parse_args()
    dry_run = not args.apply

    config = load_config(Path(args.config))
    client, resolved = open_client_from_config(config, config_path=Path(args.config), update_config=args.apply)
    root = normalize_hpath(args.root)

    repaired: list[dict[str, str]] = []
    for row in list_doc_rows(client, root):
        hpath = row.get("hpath") or ""
        doc_id = str(row["id"])
        title = str(row.get("content") or hpath.rsplit("/", 1)[-1])
        changed, kind, before, after = repair_page(client, root, hpath, doc_id, title, dry_run)
        if changed:
            repaired.append({"id": doc_id, "hPath": hpath, "title": title, "kind": kind, "beforePreview": before, "afterPreview": after})

    if repaired and not dry_run:
        client.data("/api/sqlite/flushTransaction", {})
        client.push_message(f"已修复 {len(repaired)} 个思源导出污染页面")

    print(json.dumps({"dryRun": dry_run, "repaired": repaired}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
