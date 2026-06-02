#!/usr/bin/env python3
"""Sync a completed LeetCode learning record into the SiYuan interview-training system."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from siyuan_client import (
    DEFAULT_CONFIG,
    SiyuanError,
    block_ref,
    ensure_doc,
    export_doc,
    load_config,
    load_json,
    normalize_hpath,
    open_client_from_config,
    update_doc,
)


STATE_PATH = Path.home() / ".codex" / "leetcode-hot100-siyuan-state.json"


CONCEPT_INTROS = {
    "DFS": {
        "intro": "DFS 是一种沿着一个方向尽可能深入搜索的遍历方法，常用于树、图、矩阵连通块、路径枚举等问题。",
        "signals": ["题目要求从一个起点扩展", "要搜索连通区域", "要遍历树或图", "要枚举路径"],
        "pitfalls": ["递归出口写晚导致越界", "忘记 visited 或原地标记", "需要回溯时没有撤销状态"],
    },
    "BFS": {
        "intro": "BFS 是按层向外扩展的遍历方法，常用于最短步数、层序遍历和状态扩散问题。",
        "signals": ["题目要求最短路径或最少步数", "需要按层处理", "可以用队列扩展状态"],
        "pitfalls": ["入队时不标记导致重复入队", "层数计数位置错误", "队列为空时仍 poll"],
    },
    "动态规划": {
        "intro": "动态规划通过定义状态和状态转移，复用子问题结果解决最优值、计数和可行性问题。",
        "signals": ["存在重叠子问题", "当前结果依赖之前结果", "题目要求最大/最小/方案数"],
        "pitfalls": ["状态定义不清", "初始化错误", "遍历顺序与转移依赖冲突"],
    },
    "矩阵": {
        "intro": "矩阵题通常需要处理二维坐标、边界、方向数组、原地标记或行列关系。",
        "signals": ["输入是二维数组或网格", "需要上下左右移动", "需要处理行列边界"],
        "pitfalls": ["行列下标写反", "边界判断遗漏", "修改原矩阵前没有确认是否允许"],
    },
    "图论": {
        "intro": "图论题关注节点与边的关系，常见任务包括遍历、连通块、最短路、拓扑序和并查集。",
        "signals": ["元素之间存在连接关系", "题目出现路径、连通、依赖或网络", "矩阵格子可抽象成节点"],
        "pitfalls": ["没有 visited 导致重复访问", "有向/无向关系判断错误", "边界状态没有建模清楚"],
    },
}


def unique(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            result.append(item)
            seen.add(item)
    return result


def tags(payload: dict[str, Any]) -> dict[str, list[str]]:
    raw = payload.get("tags") or {}
    return {
        "dataStructures": unique(raw.get("dataStructures") or []),
        "methods": unique(raw.get("methods") or []),
        "patterns": unique(raw.get("patterns") or []),
        "readiness": unique(raw.get("readiness") or []),
    }


def readiness(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("readiness") or {}
    raw.setdefault("status", tags(payload)["readiness"])
    raw.setdefault("skills", [])
    raw.setdefault("weakPoints", [])
    raw.setdefault("interviewExpression", "基本可用")
    raw.setdefault("nextReview", [])
    return raw


def problem_ref(problem_id: str, title: str) -> str:
    return block_ref(problem_id, title)


def append_unique_problem_link(markdown: str, problem_id: str, title: str) -> str:
    if problem_id in markdown or title in markdown:
        return markdown
    link = problem_ref(problem_id, title)
    if "## 题集" in markdown:
        return markdown.rstrip() + f"\n- {link}\n"
    return markdown.rstrip() + f"\n\n## 题集\n\n- {link}\n"


def concept_markdown(name: str, category: str, problem_id: str, title: str) -> str:
    preset = CONCEPT_INTROS.get(name, {})
    intro = preset.get("intro") or f"{name} 是面试手撕题中的一个高频知识点，需要结合题目特征、代码模板和易错点复习。"
    signals = preset.get("signals") or ["题目特征稳定指向该知识点", "代码中明确使用该方法或结构"]
    pitfalls = preset.get("pitfalls") or ["只记结论不理解适用条件", "模板细节和边界条件容易写错"]
    lines = [
        f"# {name}",
        "",
        "## 简介",
        "",
        intro,
        "",
        "## 什么时候想到它",
        "",
        *[f"- {item}" for item in signals],
        "",
        "## 常见代码结构",
        "",
        "```java",
        "// 根据具体题型补充模板",
        "```",
        "",
        "## 高频易错点",
        "",
        *[f"- {item}" for item in pitfalls],
        "",
        "## 题集",
        "",
        f"- {problem_ref(problem_id, title)}",
    ]
    if category:
        lines.insert(2, f"分类：{category}")
        lines.insert(3, "")
    return "\n".join(lines).strip() + "\n"


def review_markdown(label: str, problem_id: str, title: str) -> str:
    descriptions = {
        "一刷卡壳": "这类题首次遇到时缺少稳定思路，需要优先复盘题型识别信号。",
        "提示后完成": "这类题在提示后能完成，说明核心模式正在建立，但还需要二刷固化。",
        "独立完成": "这类题已经能独立完成，后续以间隔复习和面试表达为主。",
        "代码有 bug": "这类题思路可能正确，但实现细节或边界条件不稳定。",
        "面试表达不熟": "这类题需要练习用简洁、可验证的话解释思路和复杂度。",
        "需要二刷": "这类题涉及高频模式或关键卡点，需要安排二刷。",
    }
    return "\n".join(
        [
            f"# {label}",
            "",
            "## 说明",
            "",
            descriptions.get(label, "该复习标签用于跟踪需要再次巩固的题目。"),
            "",
            "## 题集",
            "",
            f"- {problem_ref(problem_id, title)}",
        ]
    ).strip() + "\n"


def render_problem(payload: dict[str, Any], concept_refs: dict[str, str]) -> str:
    title = payload["problemTitle"]
    git = payload.get("git") or {}
    ready = readiness(payload)
    status = ready.get("status") or []
    weak_points = ready.get("weakPoints") or []
    next_review = ready.get("nextReview") or []
    tag_data = tags(payload)
    concept_line = "、".join(concept_refs.values()) or "未标注"
    first_reaction = payload.get("firstReactionMarkdown") or "（未记录）"
    breakthrough = payload.get("breakthroughMarkdown") or "（未记录）"
    interview_expression = payload.get("interviewExpressionMarkdown") or payload.get("thinkingMarkdown", "")

    lines = [
        f"# {title}",
        "",
        f"相关知识点：{concept_line}",
        "",
        "## 题干",
        "",
        payload.get("statementMarkdown", "").strip() or "（未提供）",
        "",
        "## 第一反应",
        "",
        first_reaction.strip(),
        "",
        "## 卡壳点",
        "",
    ]
    lines.extend([f"- {item}" for item in weak_points] or ["- （未记录）"])
    lines.extend(
        [
            "",
            "## 关键突破",
            "",
            breakthrough.strip(),
            "",
            "## 面试版思路",
            "",
            payload.get("thinkingMarkdown", "").strip() or "（未提供）",
            "",
            "## 最终题解",
            "",
            "```java",
            payload.get("solutionJava", "").rstrip(),
            "```",
            "",
            "## 复杂度",
            "",
            payload.get("complexityMarkdown", "").strip() or "（未提供）",
            "",
            "## 易错点",
            "",
        ]
    )
    lines.extend([f"- {pitfall}" for pitfall in payload.get("pitfalls", [])] or ["- （未记录）"])
    lines.extend(
        [
            "",
            "## 面试表达",
            "",
            interview_expression.strip() or "（未记录）",
            "",
            "## 掌握状态",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in status] or ["- （未评估）"])
    lines.extend(["", f"面试表达成熟度：{ready.get('interviewExpression', '基本可用')}", "", "## 复习建议", ""])
    lines.extend([f"- {item}" for item in next_review] or ["- （未生成）"])
    lines.extend(
        [
            "",
            "## 同步记录",
            "",
            f"- Git 分支：{git.get('branch') or '未提供'}",
            f"- Commit：{git.get('commit') or '未提供'}",
            f"- 同步时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- 标签：{json.dumps(tag_data, ensure_ascii=False)}",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def category_paths(root: str, tag_data: dict[str, list[str]]) -> list[tuple[str, str, str]]:
    result: list[tuple[str, str, str]] = []
    for name in tag_data["dataStructures"]:
        result.append(("数据结构", name, normalize_hpath(root, "知识点", "数据结构", name)))
    for name in tag_data["methods"]:
        result.append(("解题方法", name, normalize_hpath(root, "知识点", "解题方法", name)))
    for name in tag_data["patterns"]:
        result.append(("解题模式", name, normalize_hpath(root, "知识点", "解题模式", name)))
    return result


def load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        return load_json(STATE_PATH)
    return {}


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def validate_page(content: str, required: list[str], title: str) -> list[str]:
    errors: list[str] = []
    if "????" in content:
        errors.append(f"{title}: contains ????")
    if "<!-- codex-" in content:
        errors.append(f"{title}: contains visible codex marker")
    for item in required:
        if item and item not in content:
            errors.append(f"{title}: missing {item}")
    return errors


def sync(payload_path: Path, config_path: Path, *, dry_run: bool = False) -> dict[str, Any]:
    config = load_config(config_path)
    if not (config.get("siyuan") or {}).get("enabled", False):
        return {"enabled": False, "message": "SiYuan sync is disabled."}

    payload = load_json(payload_path)
    root = (config.get("wikiPolicy") or {}).get("systemRootHPath", "/算法题/面试手撕训练系统")
    tag_data = tags(payload)
    ready = readiness(payload)
    title = payload["problemTitle"]
    problem_hpath = normalize_hpath(root, "题集", title)
    concept_targets = category_paths(root, tag_data)
    review_targets = [(label, normalize_hpath(root, "错题与复习", label)) for label in ready.get("status", [])]
    audit_hpath = normalize_hpath(root, "Codex 同步日志")

    plan = {
        "dryRun": dry_run,
        "problem": problem_hpath,
        "concepts": [{"category": cat, "name": name, "hPath": hpath} for cat, name, hpath in concept_targets],
        "reviews": [{"label": label, "hPath": hpath} for label, hpath in review_targets],
        "auditLog": audit_hpath,
    }
    if dry_run:
        return plan

    client, resolved = open_client_from_config(config, config_path=config_path, update_config=True)
    notebook = resolved.get("notebookId")
    if not notebook:
        raise SiyuanError("配置缺少 notebookId，请运行 configure_workflow.py。")

    problem_id, problem_created = ensure_doc(client, notebook, problem_hpath, "")
    concept_refs: dict[str, str] = {}
    concept_results = []
    for category, name, hpath in concept_targets:
        cid, created = ensure_doc(client, notebook, hpath, concept_markdown(name, category, problem_id, title))
        concept_refs[name] = block_ref(cid, name)
        if not created:
            existing = export_doc(client, cid)
            updated = append_unique_problem_link(existing, problem_id, title)
            if updated != existing:
                update_doc(client, cid, updated)
        concept_results.append({"name": name, "category": category, "id": cid, "url": f"siyuan://blocks/{cid}", "created": created})

    update_doc(client, problem_id, render_problem(payload, concept_refs))

    review_results = []
    for label, hpath in review_targets:
        rid, created = ensure_doc(client, notebook, hpath, review_markdown(label, problem_id, title))
        if not created:
            existing = export_doc(client, rid)
            updated = append_unique_problem_link(existing, problem_id, title)
            if updated != existing:
                update_doc(client, rid, updated)
        review_results.append({"label": label, "id": rid, "url": f"siyuan://blocks/{rid}", "created": created})

    audit_id, audit_created = ensure_doc(client, notebook, audit_hpath, "# Codex 同步日志\n")
    audit_entry = "\n".join(
        [
            f"## {datetime.now().strftime('%Y-%m-%d %H:%M')} {title}",
            "",
            f"- 题目页：{block_ref(problem_id, title)}",
            f"- Git：{(payload.get('git') or {}).get('branch', '未提供')} / {(payload.get('git') or {}).get('commit', '未提供')}",
            f"- 知识点：{'、'.join(item['name'] for item in concept_results) or '无'}",
            f"- 掌握状态：{'、'.join(label for label, _ in review_targets) or '未评估'}",
            "- 校验：待导出校验",
            "",
        ]
    )
    existing_audit = export_doc(client, audit_id)
    update_doc(client, audit_id, existing_audit.rstrip() + "\n\n" + audit_entry)

    client.data("/api/sqlite/flushTransaction", {})

    validation_errors: list[str] = []
    problem_content = export_doc(client, problem_id)
    validation_errors.extend(
        validate_page(
            problem_content,
            [title, "面试版思路", "最终题解", "掌握状态", (payload.get("git") or {}).get("commit", "")],
            "problem",
        )
    )
    for item in concept_results:
        content = export_doc(client, item["id"])
        validation_errors.extend(validate_page(content, [title], f"concept:{item['name']}"))
    for item in review_results:
        content = export_doc(client, item["id"])
        validation_errors.extend(validate_page(content, [title], f"review:{item['label']}"))
    if validation_errors:
        raise SiyuanError("SiYuan validation failed: " + "; ".join(validation_errors))

    state = load_state()
    state[title] = {
        "problemBlockId": problem_id,
        "conceptBlockIds": {item["name"]: item["id"] for item in concept_results},
        "reviewBlockIds": {item["label"]: item["id"] for item in review_results},
        "lastCommit": (payload.get("git") or {}).get("commit", ""),
        "lastSyncAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_state(state)

    client.push_message(f"LeetCode 面试训练笔记已同步：{title}")
    return {
        "enabled": True,
        "problem": {"title": title, "id": problem_id, "hPath": problem_hpath, "url": f"siyuan://blocks/{problem_id}", "created": problem_created},
        "concepts": concept_results,
        "reviews": review_results,
        "auditLog": {"id": audit_id, "hPath": audit_hpath, "url": f"siyuan://blocks/{audit_id}", "created": audit_created},
        "validation": "passed",
        "resolvedUrl": resolved.get("url"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Completed problem JSON payload.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Workflow config path.")
    parser.add_argument("--dry-run", action="store_true", help="Print target plan without writing SiYuan.")
    args = parser.parse_args()

    try:
        result = sync(Path(args.input), Path(args.config), dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"SiYuan sync failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
