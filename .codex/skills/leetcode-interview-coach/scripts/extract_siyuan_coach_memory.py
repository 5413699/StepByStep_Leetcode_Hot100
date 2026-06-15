#!/usr/bin/env python3
"""Extract compact SiYuan coach memory for LeetCode interview practice."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from siyuan_client import (
    DEFAULT_CONFIG,
    SiyuanError,
    get_block_kramdown,
    load_config,
    normalize_hpath,
    open_client_from_config,
)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


SIYUAN_INLINE_MARKERS = "\u200b\u200c\u200d\ufeff"
SECTION_PATTERN = re.compile(r"(?m)^##\s+(.+?)\s*$")
CORRUPTION_MARKERS = ["????", "\ufffd", "\u951f\u65a4\u62f7"]


def clean_markdown(text: str, *, keep_block_refs: bool = False) -> str:
    text = text or ""
    text = re.sub(f"[{SIYUAN_INLINE_MARKERS}]", "", text)
    text = re.sub(r"\{:\s+[^}]*\}", "", text)
    if not keep_block_refs:
        text = re.sub(r"\(\([0-9a-z-]+\s+\"([^\"]+)\"\)\)", r"\1", text)
    return text.strip()


def section(markdown: str, heading: str) -> str:
    matches = list(SECTION_PATTERN.finditer(markdown))
    for index, match in enumerate(matches):
        if match.group(1).strip() != heading:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        return markdown[start:end].strip()
    return ""


def bullet_lines(markdown: str) -> list[str]:
    result: list[str] = []
    for raw in markdown.splitlines():
        line = raw.strip()
        if not line.startswith("- "):
            continue
        text = line[2:].strip()
        if text and text not in result:
            result.append(text)
    return result


def is_corrupted(text: str) -> bool:
    return any(marker in text for marker in CORRUPTION_MARKERS)


def concept_hpath(root: str, concept: str) -> list[str]:
    categories = ["数据结构", "解题方法", "解题模式", "常用函数"]
    return [normalize_hpath(root, "知识点", category, concept) for category in categories]


def read_first_existing_concept(client: Any, notebook: str, root: str, concept: str) -> tuple[str, str] | None:
    for hpath in concept_hpath(root, concept):
        ids = client.data("/api/filetree/getIDsByHPath", {"notebook": notebook, "path": hpath}) or []
        if not ids:
            continue
        block_id = ids[0]
        markdown = clean_markdown(get_block_kramdown(client, block_id), keep_block_refs=True)
        return block_id, markdown
    return None


def extract_problem_title(line: str) -> str:
    match = re.search(r"M\d{3}-[^：:]+", line)
    return match.group(0) if match else ""


def extract_problem_ref(line: str) -> tuple[str, str] | None:
    match = re.search(r"\(\(([0-9a-z-]+)\s+\"(M\d{3}-[^\"]+)\"\)\)", line)
    if match:
        return match.group(2), f"siyuan://blocks/{match.group(1)}"
    title = extract_problem_title(line)
    if title:
        return title, ""
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concept", action="append", default=[], help="Concept name to inspect.")
    parser.add_argument("--max-bullets", type=int, default=8)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_config(config_path)
    if not (config.get("siyuan") or {}).get("enabled", False):
        print(json.dumps({"enabled": False, "memoryBullets": [], "relatedProblems": [], "reviewWarnings": [], "sourceLinks": []}, ensure_ascii=False, indent=2))
        return 0

    concepts = [item.strip() for item in args.concept if item and item.strip()]
    if not concepts:
        print(json.dumps({"enabled": True, "memoryBullets": [], "relatedProblems": [], "reviewWarnings": [], "sourceLinks": []}, ensure_ascii=False, indent=2))
        return 0

    try:
        client, resolved = open_client_from_config(config, config_path=config_path, update_config=True)
        notebook = resolved.get("notebookId")
        root = (config.get("wikiPolicy") or {}).get("systemRootHPath", "/算法题/面试手撕训练系统")
        if not notebook:
            raise SiyuanError("配置缺少 notebookId。")

        memory: list[str] = []
        warnings: list[str] = []
        related: dict[str, dict[str, str]] = {}
        links: list[str] = []

        for concept in concepts:
            data = read_first_existing_concept(client, notebook, root, concept)
            if not data:
                continue
            block_id, markdown = data
            links.append(f"siyuan://blocks/{block_id}")
            coach = bullet_lines(section(markdown, "教练摘要"))
            learning = bullet_lines(section(markdown, "来自题目的理解"))
            pitfalls = bullet_lines(section(markdown, "高频易错点"))

            for line in coach or learning:
                if len(memory) >= args.max_bullets:
                    break
                if is_corrupted(line):
                    continue
                display_line = clean_markdown(line)
                memory.append(f"{concept}：{display_line}")
                problem_ref_data = extract_problem_ref(line)
                if problem_ref_data:
                    title, url = problem_ref_data
                    if title and title not in related:
                        related[title] = {"title": title, "url": url or f"siyuan://blocks/{block_id}"}

            for line in pitfalls[:2]:
                if is_corrupted(line):
                    continue
                item = f"{concept}：{line}"
                if item not in warnings:
                    warnings.append(item)

        output = {
            "enabled": True,
            "memoryBullets": memory[: args.max_bullets],
            "relatedProblems": list(related.values())[:3],
            "reviewWarnings": warnings[:5],
            "sourceLinks": links,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        output = {
            "enabled": False,
            "error": str(exc),
            "memoryBullets": [],
            "relatedProblems": [],
            "reviewWarnings": [],
            "sourceLinks": [],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
