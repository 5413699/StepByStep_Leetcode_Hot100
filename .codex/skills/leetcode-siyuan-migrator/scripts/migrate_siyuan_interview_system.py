#!/usr/bin/env python3
"""Dry-run/apply migration into the LeetCode interview-training SiYuan system."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COACH_SCRIPTS = ROOT / "leetcode-interview-coach" / "scripts"
sys.path.insert(0, str(COACH_SCRIPTS))

from siyuan_client import (  # noqa: E402
    DEFAULT_CONFIG,
    SiyuanError,
    ensure_doc,
    load_config,
    load_json,
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


def build_plan(config: dict) -> dict:
    wiki = config.get("wikiPolicy") or {}
    root = wiki.get("systemRootHPath", "/算法题/面试手撕训练系统")
    return {
        "mode": "dry-run",
        "sourceRoots": LEGACY_ROOTS,
        "targetRoot": root,
        "targetPages": [
            normalize_hpath(root, "题集"),
            normalize_hpath(root, "知识点", "数据结构"),
            normalize_hpath(root, "知识点", "解题方法"),
            normalize_hpath(root, "知识点", "解题模式"),
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
        "conflicts": [],
    }


def apply_plan(config: dict, plan: dict) -> dict:
    client, resolved = open_client_from_config(config, update_config=True)
    notebook = resolved["notebookId"]
    created = []
    for hpath in plan["targetPages"]:
        doc_id, was_created = ensure_doc(client, notebook, hpath, "")
        created.append({"hPath": hpath, "id": doc_id, "created": was_created})

    log_hpath = normalize_hpath(plan["targetRoot"], "Codex 同步日志")
    log_id, _ = ensure_doc(client, notebook, log_hpath, "")
    update_doc(
        client,
        log_id,
        "# Codex 同步日志\n\n## 迁移初始化\n\n- 已创建面试手撕训练系统目标结构。\n- 旧页面未删除；后续迁移应逐页 dry-run 后再 apply。\n",
    )
    client.data("/api/sqlite/flushTransaction", {})
    return {"applied": True, "created": created, "auditLog": f"siyuan://blocks/{log_id}"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--apply", action="store_true", help="Apply target-structure bootstrap. Default is dry-run.")
    args = parser.parse_args()

    try:
        config = load_config(Path(args.config))
        plan = build_plan(config)
        if not args.apply:
            print(json.dumps(plan, ensure_ascii=False, indent=2))
            return 0
        result = apply_plan(config, plan)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (SiyuanError, OSError, json.JSONDecodeError) as exc:
        print(f"Migration failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
