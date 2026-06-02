#!/usr/bin/env python3
"""Dry-run/apply migration into the LeetCode interview-training SiYuan system."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COACH_SCRIPTS = ROOT / "leetcode-interview-coach" / "scripts"
sys.path.insert(0, str(COACH_SCRIPTS))

from siyuan_client import (  # noqa: E402
    DEFAULT_CONFIG,
    SiyuanClient,
    SiyuanError,
    ensure_doc,
    export_doc,
    load_config,
    normalize_hpath,
    open_client_from_config,
    update_doc,
)


LEGACY_ROOTS = [
    "/算法题/LeetCode Hot100",
    "/算法题/按数据结构分类",
    "/算法题/按方法分类",
    "/算法题/常用函数",
]

PROBLEM_RE = re.compile(r"^[EMH]?\d{2,4}[-.．、]")

HOT100_KNOWLEDGE_CATEGORY = {
    "DFS": "解题方法",
    "BFS": "解题方法",
    "深度优先搜索": "解题方法",
    "广度优先搜索": "解题方法",
    "递归": "解题方法",
    "递归法": "解题方法",
    "回溯": "解题方法",
    "前缀和": "解题方法",
    "层序遍历": "解题方法",
    "中序遍历": "解题方法",
    "后序递归": "解题方法",
    "Flood Fill": "解题模式",
    "网格搜索": "解题模式",
    "连通块": "解题模式",
    "二叉树": "数据结构",
    "二叉搜索树": "数据结构",
    "图论": "数据结构",
    "矩阵": "数据结构",
    "数组": "数据结构",
    "哈希表": "数据结构",
    "链表": "数据结构",
    "栈": "数据结构",
    "队列": "数据结构",
}


def sql_quote(value: str) -> str:
    return value.replace("'", "''")


def clean_exported_markdown(markdown: str, title: str) -> str:
    text = markdown.replace("\r\n", "\n").replace("\r", "\n").strip()
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end >= 0:
            text = text[end + len("\n---") :].lstrip()
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].strip() == f"# {title}":
        lines.pop(0)
    text = "\n".join(lines).strip()
    text = re.sub(r"<!--\s*codex-[^>]*-->", "", text).strip()
    return text or "（源页面无正文内容）"


def query_documents(client: SiyuanClient, roots: list[str], target_root: str) -> list[dict[str, Any]]:
    clauses = [f"hpath like '{sql_quote(root)}%'" for root in roots]
    where = " or ".join(clauses)
    stmt = (
        "select id, content, hpath, path, updated from blocks "
        f"where type='d' and ({where}) "
        f"and hpath not like '{sql_quote(target_root)}%' "
        "order by hpath asc"
    )
    return client.data("/api/query/sql", {"stmt": stmt}) or []


def classify_doc(doc: dict[str, Any]) -> dict[str, Any]:
    hpath = doc.get("hpath") or ""
    title = doc.get("content") or hpath.rstrip("/").split("/")[-1]
    result = {
        "id": doc["id"],
        "title": title,
        "hPath": hpath,
        "kind": "conflict",
        "targetCategory": "",
        "targetHPath": "",
        "sourceRoot": "",
        "reason": "",
    }

    if title in {"未命名", "Untitled"}:
        result["reason"] = "标题缺少稳定语义，需要人工确认是否保留或改名"
        return result

    if hpath.startswith("/算法题/LeetCode Hot100/题集/") or PROBLEM_RE.match(title):
        result["kind"] = "problem"
        result["reason"] = "标题符合题目编号模式或位于旧题集目录"
        return result

    if hpath.startswith("/算法题/LeetCode Hot100/知识点/"):
        rest = hpath.removeprefix("/算法题/LeetCode Hot100/知识点/").strip("/")
        parts = [part for part in rest.split("/") if part]
        if len(parts) == 1 and title in HOT100_KNOWLEDGE_CATEGORY:
            result["kind"] = "concept"
            result["targetCategory"] = HOT100_KNOWLEDGE_CATEGORY[title]
            result["reason"] = "旧 Hot100 知识点页，按显式白名单迁移"
        elif len(parts) == 1:
            result["reason"] = "旧 Hot100 知识点页未命中迁移白名单，需要人工确认分类"
        return result

    if hpath.startswith("/算法题/按数据结构分类/"):
        rest = hpath.removeprefix("/算法题/按数据结构分类/").strip("/")
        parts = [part for part in rest.split("/") if part]
        if len(parts) == 1:
            result["kind"] = "concept"
            result["targetCategory"] = "数据结构"
            result["reason"] = "旧数据结构分类页"
        elif PROBLEM_RE.match(title):
            result["kind"] = "problem"
            result["targetCategory"] = parts[0]
            result["reason"] = "旧数据结构分类下的题目页"
        return result

    if hpath.startswith("/算法题/按方法分类/"):
        rest = hpath.removeprefix("/算法题/按方法分类/").strip("/")
        parts = [part for part in rest.split("/") if part]
        if len(parts) == 1:
            result["kind"] = "concept"
            result["targetCategory"] = "解题方法"
            result["reason"] = "旧方法分类页"
        elif PROBLEM_RE.match(title):
            result["kind"] = "problem"
            result["targetCategory"] = parts[0]
            result["reason"] = "旧方法分类下的题目页"
        return result

    if hpath.startswith("/算法题/常用函数/"):
        result["kind"] = "concept"
        result["targetCategory"] = "常用函数"
        result["reason"] = "旧常用函数页"
        return result

    result["reason"] = "无法稳定识别旧页面类型"
    return result


def target_hpath(item: dict[str, Any], root: str) -> str:
    if item["kind"] == "problem":
        return normalize_hpath(root, "题集", item["title"])
    if item["kind"] == "concept":
        category = item.get("targetCategory") or "未分类"
        return normalize_hpath(root, "知识点", category, item["title"])
    return ""


def cleanup_advice(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "oldPagesWereDeleted": False,
        "safeAfterTargetVerification": [
            {
                "hPath": item["hPath"],
                "title": item["title"],
                "verifyTarget": item["afterVerifyTarget"],
                "advice": "目标页内容完整后，可手动删除旧页。",
            }
            for item in plan.get("deleteCandidates", [])
        ],
        "reviewBeforeDelete": [
            {
                "hPath": item["hPath"],
                "title": item["title"],
                "reason": item["reason"],
                "advice": "先打开旧页确认是否有手写内容；目录页和未命名页不要批量删除。",
            }
            for item in plan.get("conflicts", [])
        ],
    }


def build_plan(config: dict, client: SiyuanClient | None = None) -> dict:
    wiki = config.get("wikiPolicy") or {}
    root = wiki.get("systemRootHPath", "/算法题/面试手撕训练系统")
    base = {
        "mode": "dry-run",
        "sourceRoots": LEGACY_ROOTS,
        "targetRoot": root,
        "targetPages": [
            normalize_hpath(root, "题集"),
            normalize_hpath(root, "知识点", "数据结构"),
            normalize_hpath(root, "知识点", "解题方法"),
            normalize_hpath(root, "知识点", "解题模式"),
            normalize_hpath(root, "知识点", "常用函数"),
            normalize_hpath(root, "错题与复习"),
            normalize_hpath(root, "面试表达"),
            normalize_hpath(root, "Codex 同步日志"),
        ],
        "policy": [
            "preserve legacy pages",
            "merge missing links only",
            "do not write visible codex markers",
            "do not delete pages",
        ],
        "items": [],
        "conflicts": [],
        "deleteCandidates": [],
    }
    if client is None:
        base["summary"] = {
            "scanned": 0,
            "migratable": 0,
            "conflicts": 0,
            "deleteCandidates": 0,
        }
        base["cleanupAdvice"] = cleanup_advice(base)
        return base

    docs = query_documents(client, LEGACY_ROOTS, root)
    seen: set[str] = set()
    for doc in docs:
        if doc["id"] in seen:
            continue
        seen.add(doc["id"])
        item = classify_doc(doc)
        item["targetHPath"] = target_hpath(item, root)
        if item["kind"] == "conflict":
            base["conflicts"].append(item)
        else:
            base["items"].append(item)
            base["deleteCandidates"].append(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "hPath": item["hPath"],
                    "afterVerifyTarget": item["targetHPath"],
                    "deleteAdvice": "迁移后可考虑删除；建议先人工确认目标页内容完整。",
                }
            )
    base["summary"] = {
        "scanned": len(docs),
        "migratable": len(base["items"]),
        "conflicts": len(base["conflicts"]),
        "deleteCandidates": len(base["deleteCandidates"]),
    }
    base["cleanupAdvice"] = cleanup_advice(base)
    return base


def append_section_once(existing: str, heading: str, body: str, source_id: str) -> str:
    if source_id in existing:
        return existing
    body = body.strip()
    if not existing.strip():
        return f"{heading}\n\n{body}\n"
    return existing.rstrip() + f"\n\n{heading}\n\n{body}\n"


def problem_page_markdown(title: str, source: dict[str, Any], source_body: str) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            "## 迁移来源",
            "",
            f"- {source['hPath']}（{source['id']}）",
            "",
            "## 旧笔记内容",
            "",
            source_body,
            "",
            "## 迁移说明",
            "",
            "- 本页由 leetcode-siyuan-migrator 从旧思源笔记迁移生成。",
            "- 旧页面未删除；确认内容完整后可手动清理旧页面。",
        ]
    ).strip() + "\n"


def concept_page_markdown(title: str, category: str, source: dict[str, Any], source_body: str) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            f"分类：{category}",
            "",
            "## 简介",
            "",
            f"{title} 是面试手撕题训练系统中的知识点页面，用于汇总适用场景、常见写法、易错点和关联题目。",
            "",
            "## 什么时候想到它",
            "",
            "- 题目特征稳定指向该知识点",
            "- 代码或思路中明确使用该结构/方法/函数",
            "",
            "## 迁移来源",
            "",
            f"- {source['hPath']}（{source['id']}）",
            "",
            "## 旧笔记内容",
            "",
            source_body,
            "",
            "## 题集",
            "",
            "（后续做题同步时自动补充）",
        ]
    ).strip() + "\n"


def merge_markdown(existing: str, item: dict[str, Any], source_body: str) -> str:
    if item["id"] in existing:
        return existing
    if item["kind"] == "problem":
        body = problem_page_markdown(item["title"], item, source_body)
    else:
        body = concept_page_markdown(item["title"], item.get("targetCategory") or "未分类", item, source_body)
    if not existing.strip():
        return body
    return append_section_once(existing, "## 迁移补充", body, item["id"])


def validate_content(content: str, title: str, source_id: str) -> list[str]:
    errors = []
    if "????" in content:
        errors.append(f"{title}: contains ????")
    if "\ufffd" in content:
        errors.append(f"{title}: contains replacement character")
    if "<!-- codex-" in content:
        errors.append(f"{title}: contains visible codex marker")
    if source_id not in content:
        errors.append(f"{title}: missing source id {source_id}")
    return errors


def apply_plan(config: dict, plan: dict, client: SiyuanClient, notebook: str) -> dict:
    created = []
    updated = []
    validation_errors = []
    validated_target_ids: set[str] = set()
    for hpath in plan["targetPages"]:
        doc_id, was_created = ensure_doc(client, notebook, hpath, "")
        created.append({"hPath": hpath, "id": doc_id, "created": was_created})

    for item in plan["items"]:
        source_md = export_doc(client, item["id"])
        source_body = clean_exported_markdown(source_md, item["title"])
        target_id, was_created = ensure_doc(client, notebook, item["targetHPath"], "")
        existing = export_doc(client, target_id)
        merged = merge_markdown(existing, item, source_body)
        if merged != existing:
            update_doc(client, target_id, merged)
        exported = export_doc(client, target_id)
        validation_errors.extend(validate_content(exported, item["title"], item["id"]))
        validated_target_ids.add(target_id)
        updated.append(
            {
                "source": item["hPath"],
                "target": item["targetHPath"],
                "targetId": target_id,
                "created": was_created,
                "updated": merged != existing,
            }
        )

    log_hpath = normalize_hpath(plan["targetRoot"], "Codex 同步日志")
    log_id, _ = ensure_doc(client, notebook, log_hpath, "# Codex 同步日志\n")
    log = export_doc(client, log_id)
    entry = "\n".join(
        [
            f"## {datetime.now().strftime('%Y-%m-%d %H:%M')} 旧笔记迁移",
            "",
            f"- 扫描旧页面：{plan.get('summary', {}).get('scanned', 0)}",
            f"- 已迁移页面：{len(updated)}",
            f"- 冲突页面：{len(plan['conflicts'])}",
            f"- 删除候选：{len(plan['deleteCandidates'])}",
            "- 旧页面未删除。",
            "",
        ]
    )
    update_doc(client, log_id, log.rstrip() + "\n\n" + entry)
    client.data("/api/sqlite/flushTransaction", {})

    if validation_errors:
        raise SiyuanError("Migration validation failed: " + "; ".join(validation_errors[:10]))
    return {
        "applied": True,
        "createdTargetRoots": created,
        "updated": updated,
        "conflicts": plan["conflicts"],
        "deleteCandidates": plan["deleteCandidates"],
        "cleanupAdvice": cleanup_advice(plan),
        "validation": {
            "checkedTouchedPages": len(validated_target_ids),
            "issueCount": 0,
            "checks": [
                "no ????",
                "no replacement character",
                "no visible codex marker",
                "source id present in migrated target page",
            ],
        },
        "auditLog": f"siyuan://blocks/{log_id}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--apply", action="store_true", help="Apply migration. Default is dry-run.")
    parser.add_argument("--output", help="Write JSON report to an ASCII path.")
    args = parser.parse_args()

    try:
        config_path = Path(args.config)
        config = load_config(config_path)
        client, resolved = open_client_from_config(config, config_path=config_path, update_config=True)
        notebook = resolved.get("notebookId")
        if not notebook:
            raise SiyuanError("配置缺少 notebookId，请运行 configure_workflow.py。")

        plan = build_plan(config, client)
        result = apply_plan(config, plan, client, notebook) if args.apply else plan
        if args.output:
            result["reportPath"] = str(Path(args.output).resolve())
        result["api"] = {"url": resolved.get("url"), "notebookId": notebook}
        if args.output:
            Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (SiyuanError, OSError, json.JSONDecodeError) as exc:
        print(f"Migration failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
