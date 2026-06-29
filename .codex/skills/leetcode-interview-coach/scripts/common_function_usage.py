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
        "id": "system-arraycopy",
        "functionName": "System.arraycopy",
        "commonFunction": "数组Array的常用函数",
        "notePath": "src/notes/03.常用函数/01.数组Array/System.arraycopy.md",
        "signature": "System.arraycopy(Object src, int srcPos, Object dest, int destPos, int length)",
        "summary": "把源数组中一段连续元素复制到目标数组的指定位置，常用于构造带哨兵的新数组或移动数组片段。",
        "whenToUse": [
            "需要把原数组整体或部分复制到另一个数组中",
            "需要在新数组前后预留哨兵、空位或扩容空间",
            "需要比手写 for 循环更直接地表达连续区间复制",
        ],
        "exampleTitle": "把原数组复制到带左右哨兵的新数组中",
        "exampleCode": "int[] barChart = new int[heights.length + 2];\nSystem.arraycopy(heights, 0, barChart, 1, heights.length);",
        "pitfalls": [
            "方法名是全小写的 `arraycopy`，不是 `ArrayCopy` 或 `arrayCopy`",
            "参数顺序是源数组、源起点、目标数组、目标起点、复制长度",
            "`length` 表示复制的元素个数，不是结束下标",
            "目标数组空间不足或起点为负数会触发下标越界异常",
        ],
        "sources": [
            {
                "label": "Oracle Java System API",
                "url": "https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/System.html",
                "note": "官方文档定义了 `arraycopy(Object src, int srcPos, Object dest, int destPos, int length)`，用于从源数组指定位置复制指定数量的元素到目标数组指定位置。",
            }
        ],
        "patterns": [r"\bSystem\s*\.\s*arraycopy\s*\("],
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
    {
        "id": "stack-basic-methods",
        "functionName": "Stack.push/pop/peek/isEmpty",
        "commonFunction": "栈Stack的常用函数",
        "notePath": "src/notes/03.常用函数/06.栈Stack/Stack常用方法.md",
        "signature": "Stack<E>.push(E item) / pop() / peek() / isEmpty()",
        "summary": "使用 Java `Stack` 完成后进先出的压栈、弹栈、查看栈顶和判空操作，常用于括号匹配、辅助栈、单调栈等题型。",
        "whenToUse": [
            "需要维护后进先出的状态",
            "需要查看或删除最近加入的元素",
            "需要用辅助栈同步保存额外状态，例如当前最小值",
        ],
        "exampleTitle": "最小栈中的普通栈和辅助栈同步维护",
        "exampleCode": "Stack<Integer> stack = new Stack<>();\nStack<Integer> minStack = new Stack<>();\n\nstack.push(val);\nif (minStack.isEmpty()) {\n    minStack.push(val);\n} else {\n    minStack.push(Math.min(val, minStack.peek()));\n}",
        "pitfalls": [
            "空栈时调用 `peek()` 或 `pop()` 会抛异常，第一次使用前要先判空",
            "`peek()` 只查看栈顶，不会删除元素；`pop()` 会删除并返回栈顶元素",
            "辅助栈需要和主栈同步 push/pop，否则状态会错位",
        ],
        "sources": [
            {
                "label": "Oracle Java Stack API",
                "url": "https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Stack.html",
                "note": "官方文档说明 `Stack` 表示 LIFO 栈，并提供 `push`、`pop`、`peek`、`empty` 等栈操作；`isEmpty` 来自其集合父类体系。",
            }
        ],
        "patterns": [r"\bimport\s+java\.util\.Stack\s*;", r"\bStack\s*<[^>]+>\s+[A-Za-z_][A-Za-z0-9_]*", r"\bnew\s+Stack\s*<"],
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
        if usage.get("id") == "stack-basic-methods" and "decodeString" in solution_java:
            usage["exampleTitle"] = "字符串解码中保存括号层状态"
            usage["exampleCode"] = (
                "Stack<Integer> countStack = new Stack<>();\n"
                "Stack<StringBuilder> stringStack = new Stack<>();\n\n"
                "countStack.push(num);\n"
                "stringStack.push(cur);\n\n"
                "int repeatNum = countStack.pop();\n"
                "StringBuilder prev = stringStack.pop();"
            )
            usage["summary"] = "使用 Java `Stack` 保存进入括号前的重复次数和上一层字符串，遇到右括号时再弹出状态并合并当前层结果。"
        elif usage.get("id") == "stack-basic-methods" and "dailyTemperatures" in solution_java:
            usage["exampleTitle"] = "每日温度中保存未解决日期下标"
            usage["exampleCode"] = (
                "Stack<Integer> indexStack = new Stack<>();\n\n"
                "while (!indexStack.isEmpty() && temperatures[i] > temperatures[indexStack.peek()]) {\n"
                "    int prevIndex = indexStack.pop();\n"
                "    answer[prevIndex] = i - prevIndex;\n"
                "}\n"
                "indexStack.push(i);"
            )
            usage["summary"] = "使用 Java `Stack` 保存还没有找到更高温度的日期下标，当前温度更高时连续弹出并填写等待天数。"
        elif usage.get("id") == "stack-basic-methods" and "largestRectangleArea" in solution_java:
            usage["exampleTitle"] = "柱状图最大矩形中保存未确定右边界的柱子下标"
            usage["exampleCode"] = (
                "Stack<Integer> stack = new Stack<>();\n"
                "stack.push(0);\n\n"
                "while (barChart[stack.peek()] > barChart[i]) {\n"
                "    int height = barChart[stack.pop()];\n"
                "    int width = i - stack.peek() - 1;\n"
                "    ans = Math.max(ans, height * width);\n"
                "}\n"
                "stack.push(i);"
            )
            usage["summary"] = "使用 Java `Stack` 保存还没有找到右侧更矮柱子的柱子下标，当前柱子更矮时连续弹出并结算矩形面积。"
        usage["problemTitle"] = problem_title
        usage["problemNotePath"] = problem_note_path
        usages.append(usage)
    return usages


def common_function_tags_from_usages(usages: list[dict[str, Any]]) -> list[str]:
    return unique([str(usage.get("commonFunction") or "") for usage in usages])


def common_function_tags(solution_java: str) -> list[str]:
    return common_function_tags_from_usages(detect_function_usages(solution_java))


def append_generated_region(existing: str, title: str, generated: str) -> str:
    start = "<!-- codex-common-function-start -->"
    end = "<!-- codex-common-function-end -->"
    region = f"{start}\n\n{generated.strip()}\n\n{end}"
    if start in existing and end in existing:
        before = existing[: existing.index(start)].rstrip()
        after = existing[existing.index(end) + len(end) :].lstrip()
        if not before.strip():
            before = title
        return (before + "\n\n" + region + ("\n\n" + after if after else "")).strip() + "\n"
    if existing.strip():
        return existing.rstrip() + "\n\n" + region + "\n"
    return title.rstrip() + "\n\n" + region + "\n"


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
        problem_line = ""
    existing_records = extract_existing_problem_records(existing)
    if problem_title:
        existing_records = [
            record for record in existing_records
            if not record.startswith(f"- {problem_title}：")
        ]
    records = unique(existing_records + ([problem_line] if problem_line else []))
    if not records:
        records = ["- 暂无题目使用记录。"]
    generated = "\n".join(
        [
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
    return append_generated_region(existing, f"# {usage['functionName']}", generated)


def note_path_for_usage(repo_root: Path, usage: dict[str, Any]) -> Path:
    return repo_root / str(usage["notePath"])
