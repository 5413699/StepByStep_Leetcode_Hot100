#!/usr/bin/env python3
"""Detect reusable Java function usage for LeetCode closeout workflows."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


FUNCTION_DEFINITIONS: list[dict[str, Any]] = [
    {
        "id": "arrays-fill",
        "functionName": "Arrays.fill",
        "commonFunction": "数组Array的常用函数",
        "notePath": "src/notes/03.常用函数/01.数组Array/Arrays.fill.md",
        "signature": "Arrays.fill(char[] a, char val)",
        "summary": "把数组或数组的一段区间批量填成同一个值，常用于初始化 DP 数组、visited 数组或棋盘行。",
        "whenToUse": [
            "需要把一维数组整体初始化成同一个默认值",
            "二维数组需要逐行初始化，例如 `Arrays.fill(board[i], '.')`",
            "需要重置可复用数组状态",
        ],
        "exampleTitle": "按行初始化二维棋盘",
        "exampleCode": "char[][] board = new char[n][n];\nfor (int i = 0; i < n; i++) {\n    Arrays.fill(board[i], '.');\n}",
        "pitfalls": [
            "二维数组不能一次 `Arrays.fill(board, '.')`，要按行填充",
            "对象数组使用 `Arrays.fill` 会把同一个对象引用放到每个位置",
            "区间重载的右边界 `toIndex` 是开区间",
        ],
        "sources": [
            {
                "label": "Oracle Java Arrays API",
                "url": "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Arrays.html",
                "note": "官方文档定义了 `fill(char[] a, char val)` 及区间重载。",
            }
        ],
        "patterns": [r"\bArrays\s*\.\s*fill\s*\("],
    },
    {
        "id": "string-char-array-constructor",
        "functionName": "new String(char[])",
        "commonFunction": "字符串String的常用函数",
        "notePath": "src/notes/03.常用函数/02.字符串String/String-char数组构造器.md",
        "signature": "new String(char[] value)",
        "summary": "把一段 `char[]` 复制成不可变字符串，常用于把棋盘行、字符路径或临时字符数组转换成答案。",
        "whenToUse": [
            "当前结果保存在 `char[]` 中，但返回值要求 `String`",
            "需要把棋盘的某一行转换成答案字符串",
            "希望保存当前字符数组快照，避免后续修改影响答案",
        ],
        "exampleTitle": "把棋盘一行转换成答案字符串",
        "exampleCode": "List<String> curAns = new ArrayList<>();\nfor (int i = 0; i < n; i++) {\n    curAns.add(new String(board[i]));\n}",
        "pitfalls": [
            "`new String(char[])` 会复制当前字符内容，后续修改原数组不会改变字符串",
            "不要把整张 `char[][]` 直接传给 `new String`，需要逐行转换",
            "如果只需要部分字符，使用带 `offset` 和 `count` 的构造器或先控制数组范围",
        ],
        "sources": [
            {
                "label": "Oracle Java String API",
                "url": "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html",
                "note": "官方文档说明 `String` 表示字符序列，并给出从 `char[]` 创建字符串的用法。",
            }
        ],
        "patterns": [r"\bnew\s+String\s*\(\s*[^)]*\[\s*[^)]*\]\s*\)", r"\bnew\s+String\s*\(\s*[A-Za-z_][A-Za-z0-9_]*\s*\)"],
    },
]


def unique(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            result.append(item)
            seen.add(item)
    return result


def detect_function_usages(solution_java: str, *, problem_title: str = "", problem_note_path: str = "") -> list[dict[str, Any]]:
    usages: list[dict[str, Any]] = []
    for definition in FUNCTION_DEFINITIONS:
        if not any(re.search(pattern, solution_java) for pattern in definition["patterns"]):
            continue
        usage = {key: value for key, value in definition.items() if key != "patterns"}
        usage["problemTitle"] = problem_title
        usage["problemNotePath"] = problem_note_path
        usages.append(usage)
    return usages


def common_function_tags_from_usages(usages: list[dict[str, Any]]) -> list[str]:
    return unique([str(usage.get("commonFunction") or "") for usage in usages])


def common_function_tags(solution_java: str) -> list[str]:
    return common_function_tags_from_usages(detect_function_usages(solution_java))


def append_generated_region(existing: str, generated: str) -> str:
    start = "<!-- codex-common-function-start -->"
    end = "<!-- codex-common-function-end -->"
    region = f"{start}\n\n{generated.strip()}\n\n{end}"
    if start in existing and end in existing:
        before = existing[: existing.index(start)].rstrip()
        after = existing[existing.index(end) + len(end) :].lstrip()
        return (before + "\n\n" + region + ("\n\n" + after if after else "")).strip() + "\n"
    if existing.strip():
        return existing.rstrip() + "\n\n" + region + "\n"
    return region + "\n"


def extract_existing_problem_records(existing: str) -> list[str]:
    records: list[str] = []
    match = re.search(r"(?ms)^##\s+题目使用记录\s*\n(.*?)(?=^##\s+|\Z|<!--)", existing)
    if not match:
        return records
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            records.append(stripped)
    return records


def render_function_note(usage: dict[str, Any], existing: str = "") -> str:
    problem_title = str(usage.get("problemTitle") or "").strip()
    problem_note_path = str(usage.get("problemNotePath") or "").replace("\\", "/")
    if problem_title and problem_note_path:
        problem_line = f"- {problem_title}：{usage['summary']}（题目笔记：`{problem_note_path}`）"
    elif problem_title:
        problem_line = f"- {problem_title}：{usage['summary']}"
    else:
        problem_line = "- 暂无题目使用记录。"
    records = unique(extract_existing_problem_records(existing) + [problem_line])
    generated = "\n".join(
        [
            f"# {usage['functionName']}",
            "",
            "## 简介",
            "",
            str(usage["summary"]),
            "",
            "## 什么时候用",
            "",
            *[f"- {item}" for item in usage.get("whenToUse", [])],
            "",
            "## 常见代码结构",
            "",
            f"### {usage['exampleTitle']}",
            "",
            "```java",
            str(usage["exampleCode"]).rstrip(),
            "```",
            "",
            "## 易错点",
            "",
            *[f"- {item}" for item in usage.get("pitfalls", [])],
            "",
            "## 题目使用记录",
            "",
            *records,
            "",
            "## 来源依据",
            "",
            *[
                f"- {source.get('label')}：{source.get('note')} ({source.get('url')})"
                for source in usage.get("sources", [])
                if isinstance(source, dict)
            ],
        ]
    )
    return append_generated_region(existing, generated)


def note_path_for_usage(repo_root: Path, usage: dict[str, Any]) -> Path:
    return repo_root / str(usage["notePath"])
