#!/usr/bin/env python3
"""Dry-run/apply migration into the LeetCode interview-training SiYuan system."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
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
    get_block_kramdown,
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
PROBLEM_TITLE_RE = re.compile(r"([EMH]?\d{2,4}[-.．、][^\n\]\)）]*)")
CATEGORY_ORDER = ["数据结构", "解题方法", "解题模式", "常用函数"]
AUDIT_RETENTION_DAYS = 7

DIFFICULTY_LABELS = {"E": "简单", "M": "中等", "H": "困难"}

CATEGORY_DESCRIPTIONS = {
    "数据结构": "先判断题目操作的对象是什么，例如树、数组、矩阵、队列、哈希映射或图。",
    "解题方法": "再判断用什么遍历、递归、搜索、前缀和等方法把问题拆开。",
    "解题模式": "沉淀可迁移的题型模式，例如网格搜索、连通块、Flood Fill。",
    "常用函数": "把 Java API 的高频使用方式单独复习，降低手写时的语法损耗。",
}

CONCEPT_ALIASES = {
    "队列（迭代法）": "队列",
    "递归": "递归法",
    "哈希表": "哈希映射",
    "深度优先搜索": "DFS",
    "广度优先搜索": "BFS",
}

REVIEW_LABEL_DESCRIPTIONS = {
    "一刷卡壳": "首次做题时无法稳定找到切入点，优先复盘题型识别信号。",
    "提示后完成": "提示后能做出，说明模式正在形成，需要二刷固化。",
    "独立完成": "可以独立完成，后续重点保持速度、边界和表达稳定。",
    "代码有 bug": "思路基本正确，但实现细节或边界条件还不稳定。",
    "面试表达不熟": "能写代码但讲述不够清晰，需要专项练习表达。",
    "需要二刷": "涉及高频模式或关键卡点，应进入下一轮复习。",
}

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
    "可变数组": "数据结构",
    "哈希映射": "数据结构",
    "数组Array的常用函数": "常用函数",
    "可变数组的常用函数": "常用函数",
    "队列Queue的常用函数": "常用函数",
    "哈希映射hashmap的常用函数": "常用函数",
}

CONCEPT_PROFILES = {
    "DFS": {
        "intro": "DFS 用递归或栈沿一个方向持续深入，适合把树、图、网格中的可达状态一次性访问完。",
        "signals": ["从某个起点向外扩展并访问所有可达节点", "需要标记 visited 或把已访问状态改掉", "树/图/网格问题可以拆成当前节点加相邻节点"],
        "pitfalls": ["递归出口必须先处理越界和非法状态", "访问标记要在继续递归前完成", "如果是回溯问题，离开节点前要撤销选择"],
        "template": ["private void dfs(...) {", "    if (越界或状态非法) return;", "    标记当前状态;", "    dfs(下一个状态);", "}"],
    },
    "BFS": {
        "intro": "BFS 用队列按层扩展状态，适合最短步数、层序遍历和逐圈扩散问题。",
        "signals": ["题目要求最短路径、最少步数或按层输出", "每次从当前层扩展到下一层", "状态天然适合先进先出处理"],
        "pitfalls": ["通常应在入队时标记 visited", "层数统计要固定当前队列大小", "不要在队列为空后继续 poll"],
        "template": ["Queue<Node> queue = new LinkedList<>();", "while (!queue.isEmpty()) {", "    int size = queue.size();", "    for (int i = 0; i < size; i++) { ... }", "}"],
    },
    "Flood Fill": {
        "intro": "Flood Fill 是从一个种子位置出发，把同一连通区域全部访问或改色的网格搜索模式。",
        "signals": ["从一个格子出发扩散到同类格子", "需要把一整片区域标记掉", "题目强调上下左右相邻"],
        "pitfalls": ["先判断边界再访问 grid", "改色或标记要避免重复递归", "注意字符 `'1'` 和数字 `1` 的区别"],
        "template": ["if (越界 || grid[i][j] != 目标状态) return;", "grid[i][j] = 已访问状态;", "for (int[] d : dirs) dfs(i + d[0], j + d[1]);"],
    },
    "网格搜索": {
        "intro": "网格搜索把二维数组中的每个格子看成状态，核心是坐标、边界和方向数组。",
        "signals": ["输入是二维数组或矩阵", "需要上下左右或八方向移动", "循环遍历每个格子并从特定格子出发搜索"],
        "pitfalls": ["行列下标不要写反", "边界条件使用 `i >= m` 和 `j >= n`", "修改原网格前确认题目允许"],
        "template": ["int[][] dirs = {{1,0},{-1,0},{0,1},{0,-1}};", "for (int[] d : dirs) {", "    int ni = i + d[0], nj = j + d[1];", "}"],
    },
    "连通块": {
        "intro": "连通块表示通过相邻关系连接成的一组节点，常见任务是统计块数或处理每一块的大小/性质。",
        "signals": ["题目要求统计岛屿、区域或组件数量", "同一块中的节点通过相邻关系互相到达", "发现一个未访问节点后要把整块标记掉"],
        "pitfalls": ["计数应发生在发现新块时，而不是访问块内每个节点时", "标记不完整会导致重复计数", "方向关系要符合题目定义"],
        "template": ["if (发现未访问节点) {", "    count++;", "    dfs/bfs 标记整个连通块;", "}"],
    },
    "图论": {
        "intro": "图论关注节点与边的关系。网格、依赖、社交关系和路径问题都可以抽象成图。",
        "signals": ["元素之间存在连接、可达、依赖或路径关系", "可以把对象抽象为节点，把关系抽象为边", "题目关注连通性、最短路、拓扑序或组件"],
        "pitfalls": ["先判断是有向图还是无向图", "visited 的粒度要与状态定义一致", "网格题也可能是隐式图，不一定给出邻接表"],
        "template": ["for (Node next : neighbors(cur)) {", "    if (!visited.contains(next)) {", "        visited.add(next);", "    }", "}"],
    },
    "矩阵": {
        "intro": "矩阵题的核心是二维坐标、行列边界、方向遍历和必要时的原地标记。",
        "signals": ["输入类型是二维数组、网格或棋盘", "题目描述上下左右移动或行列变化", "需要遍历所有格子找起点"],
        "pitfalls": ["`m = grid.length`，`n = grid[0].length`", "坐标判断要覆盖小于 0 和大于等于边界", "字符矩阵要使用字符字面量"],
        "template": ["int m = grid.length, n = grid[0].length;", "for (int i = 0; i < m; i++) {", "    for (int j = 0; j < n; j++) { ... }", "}"],
    },
    "二叉树": {
        "intro": "二叉树题通常把问题拆成当前节点、左子树、右子树三个部分，用递归或层序遍历处理。",
        "signals": ["题目给出 `TreeNode`", "答案依赖左右子树的信息", "可以把整棵树问题缩小到某个子树"],
        "pitfalls": ["空节点返回值要和题意对应", "递归返回值和全局答案不要混淆", "注意路径类问题能否同时取左右两边"],
        "template": ["if (root == null) return ...;", "left = dfs(root.left);", "right = dfs(root.right);", "return 根据当前节点和左右结果计算;"],
    },
    "递归法": {
        "intro": "递归法把大问题拆成同结构的小问题，关键是明确函数语义、终止条件和返回值。",
        "signals": ["当前问题可以交给子问题先解决", "树、链表、分治区间天然递归", "需要从子结构返回信息给父结构"],
        "pitfalls": ["辅助函数参数要包含递归过程中必须继承的状态", "终止条件要覆盖空结构或空区间", "不要只照抄主函数参数"],
        "template": ["return helper(初始对象, 初始状态);", "private Type helper(Node node, State state) {", "    if (node == null) return base;", "}"],
    },
    "数组": {
        "intro": "数组题关注连续存储、下标访问、区间和排序关系，常和双指针、滑动窗口、二分配合。",
        "signals": ["输入是 `int[]` 或顺序列表", "需要按下标遍历、交换、统计或维护区间", "题目强调有序数组时优先考虑二分或双指针"],
        "pitfalls": ["区间边界是否左闭右闭要统一", "空数组和单元素数组要单独确认", "修改数组前确认题目是否允许"],
        "template": ["for (int i = 0; i < nums.length; i++) {", "    // 使用 nums[i] 更新状态", "}"],
    },
    "可变数组": {
        "intro": "可变数组通常对应 Java 的 `ArrayList`，适合动态收集遍历结果或维护顺序集合。",
        "signals": ["结果数量不固定", "需要按顺序追加答案", "题目返回 `List` 或 `List<List<...>>`"],
        "pitfalls": ["泛型类型要写完整", "不要在遍历时错误修改同一个列表", "每一层/每一组结果通常要新建 list"],
        "template": ["List<Integer> list = new ArrayList<>();", "list.add(value);", "ans.add(new ArrayList<>(list));"],
    },
    "哈希映射": {
        "intro": "哈希映射用 key 快速定位 value，适合计数、索引映射、前缀和统计和缓存状态。",
        "signals": ["需要 O(1) 查询某个值是否出现过", "需要记录出现次数或下标", "暴力查找中存在重复扫描"],
        "pitfalls": ["`getOrDefault` 的默认值要符合计数语义", "key 的类型可能需要 `Long` 防溢出", "回溯场景离开节点要撤销计数"],
        "template": ["Map<Key, Integer> map = new HashMap<>();", "map.put(key, map.getOrDefault(key, 0) + 1);"],
    },
    "队列": {
        "intro": "队列先进先出，常用于 BFS、层序遍历和按到达顺序处理状态。",
        "signals": ["需要按层访问节点", "状态从起点一圈圈扩散", "每次处理最早加入的元素"],
        "pitfalls": ["循环条件应是 `!queue.isEmpty()`", "层序遍历要先记录 `size`", "入队前判断空节点"],
        "template": ["Queue<TreeNode> queue = new LinkedList<>();", "queue.offer(root);", "TreeNode cur = queue.poll();"],
    },
    "数组Array的常用函数": {
        "intro": "数组常用函数用于处理固定长度顺序数据，复习时重点关注长度、下标访问、拷贝、排序和填充。",
        "signals": ["代码直接操作 `int[]`、`char[]` 或二维数组", "需要用 `length` 判断边界", "需要排序、填充或拷贝数组"],
        "pitfalls": ["数组长度是属性 `length`，不是方法 `size()`", "二维数组的行列边界要分别取 `grid.length` 和 `grid[0].length`", "排序会修改原数组"],
        "template": ["nums.length", "Arrays.sort(nums);", "Arrays.fill(nums, value);", "int[] copy = Arrays.copyOf(nums, nums.length);"],
    },
    "可变数组的常用函数": {
        "intro": "可变数组常用函数对应 Java `List`/`ArrayList`，适合收集不定长结果和按顺序追加元素。",
        "signals": ["返回值是 `List` 或 `List<List<...>>`", "需要逐步追加答案", "需要按下标读取或修改动态列表"],
        "pitfalls": ["`size()` 是方法，数组的 `length` 是属性", "每层结果要新建 `List`，避免复用同一个对象", "泛型类型要写完整"],
        "template": ["List<Integer> list = new ArrayList<>();", "list.add(value);", "list.get(i);", "list.set(i, value);", "list.size();"],
    },
    "哈希映射hashmap的常用函数": {
        "intro": "哈希映射常用函数用于通过 key 快速查询、计数、记录下标或维护前缀和出现次数。",
        "signals": ["需要快速判断某个 key 是否出现过", "需要记录次数、下标或映射关系", "代码中出现 `HashMap`、`Map`、`getOrDefault`"],
        "pitfalls": ["`getOrDefault` 的默认值要和计数语义一致", "回溯场景离开节点要撤销计数", "前缀和可能需要 `Long` 作为 key"],
        "template": ["Map<Integer, Integer> map = new HashMap<>();", "map.put(key, map.getOrDefault(key, 0) + 1);", "map.containsKey(key);", "map.get(key);"],
    },
    "队列Queue的常用函数": {
        "intro": "队列常用函数用于先进先出处理状态，常见于 BFS 和二叉树层序遍历。",
        "signals": ["代码使用 `Queue` 或 `LinkedList`", "需要入队、出队处理状态", "按层遍历时要读取当前 `queue.size()`"],
        "pitfalls": ["循环条件应写 `!queue.isEmpty()`", "通常用 `offer`/`poll`，不要混淆栈的 `push`/`pop`", "层序遍历要先固定当前层大小"],
        "template": ["Queue<TreeNode> queue = new LinkedList<>();", "queue.offer(root);", "TreeNode cur = queue.poll();", "queue.isEmpty();", "queue.size();"],
    },
}

COMMON_FUNCTION_KEYWORDS = {
    "数组Array的常用函数": [r"\bint\[\]", r"\bchar\[\]", r"\[\]\[\]", r"\.length\b", r"\bArrays\."],
    "可变数组的常用函数": [r"\bList<", r"\bArrayList<", r"\.add\(", r"\.get\(", r"\.set\(", r"\.size\(\)"],
    "哈希映射hashmap的常用函数": [r"\bHashMap<", r"\bMap<", r"\.getOrDefault\(", r"\.containsKey\(", r"\.put\("],
    "队列Queue的常用函数": [r"\bQueue<", r"\bLinkedList<", r"\.offer\(", r"\.poll\(", r"\.isEmpty\(\)"],
}


def sql_quote(value: str) -> str:
    return value.replace("'", "''")


def page_link(block_id: str, text: str) -> str:
    escaped = text.replace('"', '\\"')
    return f'(({block_id} "{escaped}"))'


def clean_exported_markdown(markdown: str, title: str) -> str:
    text = markdown.replace("\r\n", "\n").replace("\r", "\n").strip()
    text = text.replace("\u200d", "")
    text = re.sub(r"(?s)^---\n.*?\n---\n*", "", text).strip()
    text = re.sub(r"(?ms)^\[\^\d+\]:\s+#\s+.*?(?=^\[\^\d+\]:\s+#\s+|\Z)", "", text).strip()
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and lines[0].strip() == f"# {title}":
        lines.pop(0)
    text = "\n".join(lines).strip()
    text = re.sub(r"<!--\s*codex-[^>]*-->", "", text).strip()
    return text or "（源页面无正文内容）"


def strip_block_markdown(markdown: str) -> str:
    text = re.sub(r"(?ms)(?:\A|\n)---\s*\n.*?\n---\s*(?=\n|\Z)", "\n", markdown.strip())
    text = re.sub(r"\{:\s+[^}]*\}", "", text)
    text = re.sub(r"(?m)^#\s+.+$", "", text)
    text = re.sub(r"(?m)^(title|date|lastmod):.*$", "", text)
    text = text.replace("仓库 `src/notes`\u200b 与 `src/main/java`", "仓库学习笔记与 Java 题解文件")
    text = text.replace("仓库 `src/notes` 与 `src/main/java`", "仓库学习笔记与 Java 题解文件")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def own_doc_markdown(client: SiyuanClient, doc_id: str) -> str:
    return strip_block_markdown(get_block_kramdown(client, doc_id))


def strip_markdown_noise(markdown: str, title: str) -> str:
    text = clean_exported_markdown(markdown, title)
    text = re.sub(rf"(?m)^#\s*{re.escape(title)}\s*$", "", text).strip()
    text = remove_legacy_label_lines(text)
    text = re.sub(r"(?ms)^##\s*迁移来源\s*\n.*?(?=^##\s+|\Z)", "", text).strip()
    text = re.sub(r"(?ms)^##\s*迁移说明\s*\n.*?(?=^##\s+|\Z)", "", text).strip()
    text = re.sub(r"(?ms)^##\s*来源索引\s*\n.*?(?=^##\s+|\Z)", "", text).strip()
    text = re.sub(r"(?ms)^##\s*迁移记录\s*\n.*?(?=^##\s+|\Z)", "", text).strip()
    text = re.sub(r"(?ms)^##\s*旧笔记内容\s*\n", "", text).strip()
    text = re.sub(r"(?ms)^##\s*迁移补充\s*\n", "", text).strip()
    text = re.sub(r"(?ms)^##\s*旧笔记重组补充\s*\n", "", text).strip()
    text = re.sub(r"(?m)^---\s*$", "", text).strip()
    text = re.sub(r"(?m)^title:.*$", "", text)
    text = re.sub(r"(?m)^date:.*$", "", text)
    text = re.sub(r"(?m)^lastmod:.*$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    text = remove_empty_sections(text)
    return text or "（源页面无正文内容）"


def remove_legacy_label_lines(markdown: str) -> str:
    lines = []
    for line in markdown.splitlines():
        stripped = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", line).strip()
        if re.match(r"^(相关数据结构|相关方法|方法|记录)\s*[：:].*$", stripped):
            continue
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def remove_section(markdown: str, heading: str) -> str:
    return re.sub(rf"(?ms)^##\s*{re.escape(heading)}\s*\n.*?(?=^##\s+|\Z)", "", markdown).strip()


def unwrap_section_heading(markdown: str, heading: str) -> str:
    text = re.sub(rf"(?m)^##\s*{re.escape(heading)}\s*$\n?", "", markdown)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def remove_empty_sections(markdown: str) -> str:
    text = markdown
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"(?ms)^##\s+(.+?)\s*\n\s*(?=^##\s+|\Z)", "", text).strip()
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def replace_footnote_links(markdown: str, link_map: dict[str, str]) -> str:
    text = markdown
    for name in sorted(link_map, key=len, reverse=True):
        text = re.sub(rf"(?<!\[){re.escape(name)}\[\^\d+\]", link_map[name], text)
        text = re.sub(rf"(?<!\[){re.escape(name)}\[(?:<sup>|</sup>)?\d+\]", link_map[name], text)
    text = re.sub(r"\[\^\d+\]", "", text)
    text = re.sub(r"\[<sup>\d+\]|\[</sup>\d+\]|</?sup>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def problem_learning_body(markdown: str) -> str:
    text = remove_section(markdown, "知识链接")
    text = unwrap_section_heading(text, "学习记录")
    return remove_empty_sections(text)


def concept_supplement_body(concept: dict[str, Any], markdown: str) -> str:
    text = markdown
    text = re.sub(r"(?m)^分类\s*[：:].*$", "", text).strip()
    for heading in ["简介", "什么时候想到它", "常见代码结构", "高频易错点", "题集"]:
        text = remove_section(text, heading)
    text = unwrap_section_heading(text, "补充说明")
    if concept.get("category") == "常用函数":
        return ""
    return remove_empty_sections(text)


def extract_section(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"(?ms)^##\s*{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)")
    match = pattern.search(markdown)
    return match.group(1).strip() if match else ""


def split_link_names(text: str) -> list[str]:
    plain = re.sub(r"<a\s+[^>]*>(.*?)</a>", r"\1", text)
    plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", plain)
    plain = re.sub(r"\[\^\d+\]", "", plain)
    plain = re.sub(r"\[(?:<sup>|</sup>)?\d+\]", "", plain)
    plain = re.sub(r"</?sup>", "", plain)
    plain = re.sub(r"<[^>]+>", "", plain)
    values = []
    for value in re.split(r"[、,，]\s*", plain):
        cleaned = value.strip(" ：:;-—\t")
        if cleaned and "待补充" not in cleaned and "未标注" not in cleaned:
            values.append(cleaned)
    return unique(values)


def extract_existing_knowledge_links(markdown: str) -> dict[str, list[str]]:
    result = {"dataStructures": [], "methods": [], "patterns": [], "commonFunctions": []}
    section = extract_section(markdown, "知识链接")
    label_map = {
        "数据结构": "dataStructures",
        "解题方法": "methods",
        "方法": "methods",
        "解题模式": "patterns",
        "常用函数": "commonFunctions",
    }
    for line in section.splitlines():
        stripped = line.strip().lstrip("-").strip()
        if "：" in stripped:
            label, tail = stripped.split("：", 1)
        elif ":" in stripped:
            label, tail = stripped.split(":", 1)
        else:
            continue
        key = label_map.get(label.strip())
        if key:
            result[key].extend(split_link_names(tail))
    return {key: unique(values) for key, values in result.items()}


def extract_title_tags(markdown: str) -> dict[str, list[str]]:
    result = {"dataStructures": [], "methods": [], "patterns": [], "commonFunctions": []}
    for line in markdown.splitlines()[:12]:
        plain = re.sub(r"\[[^\]]+\]\([^)]+\)", lambda m: m.group(0).split("]")[0].lstrip("["), line)
        plain = re.sub(r"\[\^\d+\]|\[[<\s/]*sup>?\d*\]?|<[^>]+>", "", plain)
        if line.startswith("相关数据结构"):
            tail = plain.split("：", 1)[-1]
            result["dataStructures"].extend([x.strip(" 、,，") for x in re.split(r"[、,，]\s*", tail) if x.strip(" 、,，")])
        if line.startswith("方法"):
            tail = plain.split("：", 1)[-1]
            values = [x.strip(" 、,，") for x in re.split(r"[、,，]\s*", tail) if x.strip(" 、,，")]
            for value in values:
                category = HOT100_KNOWLEDGE_CATEGORY.get(value)
                if category == "解题模式":
                    result["patterns"].append(value)
                else:
                    result["methods"].append(value)
    return {key: unique(values) for key, values in result.items()}


def unique(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        cleaned = normalize_concept_name(item)
        if cleaned and cleaned not in seen:
            result.append(cleaned)
            seen.add(cleaned)
    return result


def normalize_concept_name(name: str) -> str:
    cleaned = name.strip()
    return CONCEPT_ALIASES.get(cleaned, cleaned)


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


def query_target_documents(client: SiyuanClient, target_root: str) -> list[dict[str, Any]]:
    stmt = (
        "select id, content, hpath, path, updated from blocks "
        "where type='d' "
        f"and hpath like '{sql_quote(target_root)}%' "
        "order by hpath asc"
    )
    return client.data("/api/query/sql", {"stmt": stmt}) or []


def classify_doc(doc: dict[str, Any]) -> dict[str, Any]:
    hpath = doc.get("hpath") or ""
    raw_title = doc.get("content") or hpath.rstrip("/").split("/")[-1]
    title = normalize_concept_name(raw_title)
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


def classify_target_doc(doc: dict[str, Any], root: str) -> dict[str, Any]:
    hpath = doc.get("hpath") or ""
    raw_title = doc.get("content") or hpath.rstrip("/").split("/")[-1]
    title = normalize_concept_name(raw_title)
    result = {
        "id": doc["id"],
        "title": title,
        "hPath": hpath,
        "kind": "conflict",
        "targetCategory": "",
        "targetHPath": hpath,
        "sourceRoot": "target",
        "reason": "",
    }
    if hpath.startswith(normalize_hpath(root, "题集") + "/") and PROBLEM_RE.match(title):
        result["kind"] = "problem"
        result["reason"] = "新系统题目页，参与清理重组"
        return result
    for category in CATEGORY_ORDER:
        prefix = normalize_hpath(root, "知识点", category) + "/"
        if hpath.startswith(prefix):
            result["kind"] = "concept"
            result["targetCategory"] = category
            result["reason"] = "新系统知识点页，参与清理重组"
            return result
    result["reason"] = "新系统根目录或分类目录，不作为模型节点"
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


def hpath_depth(hpath: str) -> int:
    return len([part for part in hpath.split("/") if part])


def verify_delete_candidate_targets(client: SiyuanClient, notebook: str, plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for item in plan.get("deleteCandidates", []):
        target = item.get("afterVerifyTarget", "")
        ids = client.data("/api/filetree/getIDsByHPath", {"notebook": notebook, "path": target}) or []
        if not ids:
            errors.append(f"{item.get('hPath')}: target page does not exist: {target}")
    return errors


def delete_safe_legacy_pages(client: SiyuanClient, plan: dict[str, Any]) -> list[dict[str, Any]]:
    deleted: list[dict[str, Any]] = []
    candidates = sorted(plan.get("deleteCandidates", []), key=lambda item: hpath_depth(item.get("hPath", "")), reverse=True)
    seen: set[str] = set()
    for item in candidates:
        doc_id = item.get("id", "")
        if not doc_id or doc_id in seen:
            continue
        seen.add(doc_id)
        client.data("/api/filetree/removeDocByID", {"id": doc_id})
        deleted.append({"id": doc_id, "title": item.get("title", ""), "hPath": item.get("hPath", "")})
    return deleted


def is_trivial_legacy_conflict(item: dict[str, Any], body: str) -> bool:
    title = item.get("title", "")
    hpath = item.get("hPath", "")
    text = clean_exported_markdown(body, title)
    text = re.sub(r"\[\^\d+\]", "", text)
    text = re.sub(r"\s+", "", text)
    if title in {"未命名", "Untitled"} and not text:
        return True
    if hpath in {"/算法题/常用函数", "/算法题/按数据结构分类", "/算法题/按方法分类"}:
        return True
    return False


def delete_trivial_legacy_conflicts(client: SiyuanClient, plan: dict[str, Any]) -> list[dict[str, Any]]:
    deleted: list[dict[str, Any]] = []
    for item in sorted(plan.get("conflicts", []), key=lambda row: hpath_depth(row.get("hPath", "")), reverse=True):
        doc_id = item.get("id", "")
        if not doc_id:
            continue
        body = export_doc(client, doc_id)
        if not is_trivial_legacy_conflict(item, body):
            continue
        client.data("/api/filetree/removeDocByID", {"id": doc_id})
        deleted.append({"id": doc_id, "title": item.get("title", ""), "hPath": item.get("hPath", "")})
    return deleted


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
    source_bodies: dict[str, str] = {}
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
            try:
                source_bodies[item["id"]] = strip_markdown_noise(export_doc(client, item["id"]), item["title"])
            except SiyuanError:
                source_bodies[item["id"]] = ""
            base["deleteCandidates"].append(
                {
                    "id": item["id"],
                    "title": item["title"],
                    "hPath": item["hPath"],
                    "afterVerifyTarget": item["targetHPath"],
                    "deleteAdvice": "迁移后可考虑删除；建议先人工确认目标页内容完整。",
                }
            )
    target_items: list[dict[str, Any]] = []
    target_bodies: dict[str, str] = {}
    for doc in query_target_documents(client, root):
        item = classify_target_doc(doc, root)
        if item["kind"] in {"problem", "concept"}:
            target_items.append(item)
            try:
                target_bodies[item["id"]] = strip_markdown_noise(export_doc(client, item["id"]), item["title"])
            except SiyuanError:
                target_bodies[item["id"]] = ""
    if not base["items"] and target_items:
        base["mode"] = "repair-existing-target"
        base["items"] = target_items
        source_bodies = target_bodies
    base["summary"] = {
        "scanned": len(docs),
        "migratable": len(base["items"]),
        "conflicts": len(base["conflicts"]),
        "deleteCandidates": len(base["deleteCandidates"]),
        "targetPagesScanned": len(target_items),
    }
    model = build_knowledge_model(base["items"], source_bodies)
    base["modelSummary"] = {
        "problems": len(model["problems"]),
        "concepts": len(model["concepts"]),
        "categories": {key: len(value) for key, value in model["categoryIndex"].items()},
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


def source_line(source: dict[str, Any]) -> str:
    return f"- `{source['id']}`：{source['hPath']}"


def problem_sort_key(title: str) -> tuple[int, str]:
    match = re.search(r"\d{2,4}", title)
    return (int(match.group(0)) if match else 99999, title)


def infer_problem_tags(problem: dict[str, Any]) -> dict[str, list[str]]:
    tags = {"dataStructures": [], "methods": [], "patterns": [], "commonFunctions": []}
    for source in problem["sources"]:
        hpath = source["hPath"]
        if "/按数据结构分类/" in hpath:
            rest = hpath.split("/按数据结构分类/", 1)[1].strip("/")
            parts = [part for part in rest.split("/") if part]
            if len(parts) >= 2:
                tags["dataStructures"].append(parts[0])
        if "/按方法分类/" in hpath:
            rest = hpath.split("/按方法分类/", 1)[1].strip("/")
            parts = [part for part in rest.split("/") if part]
            if len(parts) >= 2:
                tags["methods"].append(parts[0])
        if "/常用函数/" in hpath:
            rest = hpath.split("/常用函数/", 1)[1].strip("/")
            parts = [part for part in rest.split("/") if part]
            if len(parts) >= 2:
                tags["commonFunctions"].append(parts[0])
    extracted = extract_title_tags(problem["body"])
    tags["dataStructures"].extend(extracted["dataStructures"])
    tags["methods"].extend(extracted["methods"])
    tags["patterns"].extend(extracted["patterns"])
    tags["commonFunctions"].extend(extracted["commonFunctions"])
    for concept_name, patterns in COMMON_FUNCTION_KEYWORDS.items():
        if any(re.search(pattern, problem["body"], re.IGNORECASE) for pattern in patterns):
            tags["commonFunctions"].append(concept_name)
    return {key: unique(values) for key, values in tags.items()}


def merge_problem_body(existing: str, incoming: str) -> str:
    if not existing or existing == "（源页面无正文内容）":
        return incoming
    if not incoming or incoming == "（源页面无正文内容）" or incoming in existing:
        return existing
    existing_sections = {name for name in re.findall(r"(?m)^##\s+(.+?)\s*$", existing)}
    additions: list[str] = []
    for heading in ["题干", "思路", "思考过程", "题解", "复杂度", "易错点"]:
        section = extract_section(incoming, heading)
        if section and heading not in existing_sections:
            additions.append(f"## {heading}\n\n{section}")
    if additions:
        return existing.rstrip() + "\n\n" + "\n\n".join(additions)
    return existing


def build_knowledge_model(items: list[dict[str, Any]], source_bodies: dict[str, str]) -> dict[str, Any]:
    problems: dict[str, dict[str, Any]] = {}
    concepts: dict[str, dict[str, Any]] = {}

    for item in items:
        body = source_bodies.get(item["id"], "")
        if item["kind"] == "problem":
            problem = problems.setdefault(
                item["title"],
                {
                    "title": item["title"],
                    "body": "",
                    "sources": [],
                    "tags": {"dataStructures": [], "methods": [], "patterns": [], "commonFunctions": []},
                },
            )
            problem["body"] = merge_problem_body(problem["body"], body)
            problem["sources"].append(item)
        elif item["kind"] == "concept":
            category = item.get("targetCategory") or HOT100_KNOWLEDGE_CATEGORY.get(item["title"], "未分类")
            concept = concepts.setdefault(
                item["title"],
                {"name": item["title"], "category": category, "body": "", "sources": [], "problems": []},
            )
            concept["category"] = category
            concept["body"] = merge_problem_body(concept["body"], body)
            concept["sources"].append(item)

    for problem in problems.values():
        problem["tags"] = infer_problem_tags(problem)
        existing_links = extract_existing_knowledge_links(problem["body"])
        for key, values in existing_links.items():
            problem["tags"][key].extend(values)
        problem["tags"] = {key: unique(values) for key, values in problem["tags"].items()}
        for category_key, category_name in [
            ("dataStructures", "数据结构"),
            ("methods", "解题方法"),
            ("patterns", "解题模式"),
            ("commonFunctions", "常用函数"),
        ]:
            for name in problem["tags"].get(category_key, []):
                if not name:
                    continue
                concept = concepts.setdefault(
                    name,
                    {"name": name, "category": HOT100_KNOWLEDGE_CATEGORY.get(name, category_name), "body": "", "sources": [], "problems": []},
                )
                if concept["category"] == "未分类":
                    concept["category"] = HOT100_KNOWLEDGE_CATEGORY.get(name, category_name)
                concept["problems"].append(problem["title"])

    for concept in concepts.values():
        concept["problems"] = sorted(unique(concept["problems"]), key=problem_sort_key)

    category_index: dict[str, list[str]] = {category: [] for category in CATEGORY_ORDER}
    for concept in concepts.values():
        category = concept.get("category") or "未分类"
        category_index.setdefault(category, []).append(concept["name"])
    for category, names in category_index.items():
        category_index[category] = sorted(unique(names))

    return {"problems": problems, "concepts": concepts, "categoryIndex": category_index}


def concept_profile(name: str, body: str) -> dict[str, list[str] | str]:
    preset = CONCEPT_PROFILES.get(name, {})
    intro = preset.get("intro")
    if not intro:
        first_paragraph = next((part.strip() for part in body.split("\n\n") if part.strip() and not part.startswith("##")), "")
        intro = first_paragraph[:220] if first_paragraph else f"{name} 是当前面试训练体系中的知识点，需要通过题目链接、代码结构和易错点一起复习。"
    return {
        "intro": intro,
        "signals": preset.get("signals") or ["旧笔记或题目标签明确指向该知识点", "相关题目的解法会反复使用该结构或方法"],
        "pitfalls": preset.get("pitfalls") or ["仅记名称但不能说清适用条件", "代码模板和边界条件没有和题目场景绑定"],
        "template": preset.get("template") or ["// 结合关联题目补充代码结构"],
    }


def render_problem_page(problem: dict[str, Any], concept_refs: dict[str, str]) -> str:
    body = replace_footnote_links(problem_learning_body(strip_markdown_noise(problem["body"], problem["title"])), concept_refs)
    tags = problem["tags"]
    lines = [
        "## 知识链接",
        "",
        f"- 数据结构：{'、'.join(concept_refs[name] for name in tags['dataStructures'] if name in concept_refs) or '（待补充）'}",
        f"- 解题方法：{'、'.join(concept_refs[name] for name in tags['methods'] if name in concept_refs) or '（待补充）'}",
        f"- 解题模式：{'、'.join(concept_refs[name] for name in tags['patterns'] if name in concept_refs) or '（待补充）'}",
        f"- 常用函数：{'、'.join(concept_refs[name] for name in tags.get('commonFunctions', []) if name in concept_refs) or '（待补充）'}",
        "",
        "## 学习记录",
        "",
        body,
    ]
    return "\n".join(lines).strip() + "\n"


def render_concept_page(concept: dict[str, Any], problem_refs: dict[str, str]) -> str:
    profile = concept_profile(concept["name"], concept["body"])
    body = replace_footnote_links(concept_supplement_body(concept, strip_markdown_noise(concept["body"], concept["name"])), problem_refs)
    problem_links = [problem_refs[title] for title in concept["problems"] if title in problem_refs]
    lines = [
        f"分类：{concept['category']}",
        "",
        "## 简介",
        "",
        str(profile["intro"]),
        "",
        "## 什么时候想到它",
        "",
        *[f"- {item}" for item in profile["signals"]],
        "",
        "## 常见代码结构",
        "",
        "```java",
        *[str(item) for item in profile["template"]],
        "```",
        "",
        "## 高频易错点",
        "",
        *[f"- {item}" for item in profile["pitfalls"]],
    ]
    normalized_body = re.sub(r"\s+", "", body)
    normalized_intro = re.sub(r"\s+", "", str(profile["intro"]))
    body_is_duplicate = not normalized_body or normalized_body == normalized_intro or normalized_body in re.sub(r"\s+", "", "\n".join(lines))
    if body and body != "（源页面无正文内容）" and not body_is_duplicate:
        lines.extend(["", "## 补充说明", "", body])
    lines.extend(["", "## 题集", ""])
    lines.extend([f"- {link}" for link in problem_links] or ["- （暂未关联题目）"])
    return "\n".join(lines).strip() + "\n"


def render_category_page(category: str, concept_names: list[str], concept_refs: dict[str, str], model: dict[str, Any]) -> str:
    lines = [
        "## 知识点",
        "",
    ]
    if concept_names:
        for name in concept_names:
            concept = model["concepts"].get(name, {})
            count = len(concept.get("problems") or [])
            ref = concept_refs.get(name, name)
            lines.append(f"- {ref}：关联题目 {count} 道")
    else:
        lines.append("- （暂无知识点）")
    return "\n".join(lines).strip() + "\n"


def render_root_home(
    section_ids: dict[str, str],
    category_ids: dict[str, str],
    concept_ids: dict[str, str],
    problem_ids: dict[str, str],
    model: dict[str, Any],
) -> str:
    category_lines = []
    for category in CATEGORY_ORDER:
        concept_count = len(model["categoryIndex"].get(category, []))
        problem_titles = {
            title
            for name in model["categoryIndex"].get(category, [])
            for title in model["concepts"].get(name, {}).get("problems", [])
        }
        category_lines.append(f"- {page_link(category_ids[category], category)}：{concept_count} 个知识点，关联题目 {len(problem_titles)} 道")

    concept_items = sorted(
        model["concepts"].items(),
        key=lambda pair: (-len(pair[1].get("problems", [])), pair[0]),
    )[:10]
    recent_titles = sorted(model["problems"], key=problem_sort_key)[-6:]

    lines = [
        "## 今日入口",
        "",
        f"- {page_link(section_ids['题集'], '题集')}：按题号复习已经整理过的题目。",
        f"- {page_link(section_ids['知识点'], '知识点')}：按数据结构、方法、模式、常用函数复习。",
        f"- {page_link(section_ids['错题与复习'], '错题与复习')}：按掌握状态安排二刷和表达训练。",
        f"- {page_link(section_ids['面试表达'], '面试表达')}：沉淀面试中可直接说出口的解题表达。",
        f"- {page_link(section_ids['Codex 同步日志'], 'Codex 同步日志')}：审阅自动同步、修复和迁移记录。",
        "",
        "## 训练概览",
        "",
        f"- 已整理题目：{len(model['problems'])} 道",
        f"- 已整理知识点：{len(model['concepts'])} 个",
        *category_lines,
        "",
        "## 高频知识地图",
        "",
    ]
    for name, concept in concept_items:
        category = concept.get("category", "")
        category_ref = page_link(category_ids[category], category) if category in category_ids else category
        concept_ref = page_link(concept_ids[name], name) if name in concept_ids else name
        lines.append(f"- {category_ref} / {concept_ref}：关联题目 {len(concept.get('problems', []))} 道")
    lines.extend(["", "## 最近整理题目", ""])
    for title in recent_titles:
        lines.append(f"- {page_link(problem_ids[title], title)}")
    lines.extend(
        [
            "",
            "## 使用原则",
            "",
            "- 先从题集页定位题目，再跳到知识点页复盘共性。",
            "- 复习时重点看卡壳点、易错点和面试版思路，不只背代码。",
            "- 知识点页用于建立迁移能力：看到什么信号、用什么方法、容易错在哪里。",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def render_problem_index(problem_ids: dict[str, str], model: dict[str, Any]) -> str:
    groups: dict[str, list[str]] = {"E": [], "M": [], "H": []}
    for title in sorted(model["problems"], key=problem_sort_key):
        difficulty = title[0] if title and title[0] in groups else "M"
        groups.setdefault(difficulty, []).append(title)

    lines = [
        "## 题目列表",
        "",
        f"当前题集已整理 {len(problem_ids)} 道题。每个题目页包含知识链接、学习记录和迁移后的题解内容。",
        "",
    ]
    for difficulty in ["E", "M", "H"]:
        titles = groups.get(difficulty) or []
        if not titles:
            continue
        lines.extend([f"## {DIFFICULTY_LABELS.get(difficulty, difficulty)}", ""])
        for title in titles:
            problem = model["problems"].get(title, {})
            tags = problem.get("tags", {})
            pieces = []
            if tags.get("dataStructures"):
                pieces.append("数据结构：" + "、".join(tags["dataStructures"]))
            if tags.get("methods"):
                pieces.append("方法：" + "、".join(tags["methods"]))
            if tags.get("patterns"):
                pieces.append("模式：" + "、".join(tags["patterns"]))
            lines.append(f"- {page_link(problem_ids[title], title)}：{'；'.join(pieces) if pieces else '标签待补充'}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_knowledge_home(category_ids: dict[str, str], concept_ids: dict[str, str], model: dict[str, Any]) -> str:
    lines = ["## 分类入口", ""]
    for category in CATEGORY_ORDER:
        names = model["categoryIndex"].get(category, [])
        problem_titles = {
            title
            for name in names
            for title in model["concepts"].get(name, {}).get("problems", [])
        }
        lines.append(f"- {page_link(category_ids[category], category)}：{len(names)} 个知识点，关联题目 {len(problem_titles)} 道。{CATEGORY_DESCRIPTIONS[category]}")

    lines.extend(["", "## 高频知识点", ""])
    for name, concept in sorted(model["concepts"].items(), key=lambda pair: (-len(pair[1].get("problems", [])), pair[0]))[:12]:
        if name in concept_ids:
            lines.append(f"- {page_link(concept_ids[name], name)}：关联题目 {len(concept.get('problems', []))} 道")

    lines.extend(
        [
            "",
            "## 复习方法",
            "",
            "- 先读知识点简介，确认这个概念解决哪类问题。",
            "- 再看“什么时候想到它”，训练题型识别。",
            "- 最后回到关联题目，复盘代码结构和易错点。",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def render_review_home() -> str:
    lines = [
        "## 复习原则",
        "",
        "这里仅保留需要复盘的真实题目入口。没有题目归档时，不自动堆叠空标签页。",
        "",
        "## 当前复习入口",
        "",
        "- 暂无自动归档题目。完成题目收尾后，只有带复习标签的题目会出现在这里。",
        "",
        "## 记录标准",
        "",
        "- 卡壳点写成具体问题，例如“想不到辅助函数参数”或“边界条件顺序写错”。",
        "- 二刷时记录是否能独立说清题型、状态定义、复杂度和易错点。",
    ]
    return "\n".join(lines).strip() + "\n"


def render_interview_expression_home(problem_ids: dict[str, str]) -> str:
    def ref(title: str) -> str:
        return page_link(problem_ids[title], title) if title in problem_ids else title

    lines = [
        "## 思路表达模板",
        "",
        "### 树形递归题",
        "",
        f"- 代表题：{ref('H124-二叉树中的最大路径和')}、{ref('M236-二叉树的最近公共祖先')}",
        "- 表达顺序：先说明递归函数语义，再说明空节点返回值，最后说明如何合并左右子树结果。",
        "- 常用句式：这个辅助函数返回的是当前子树能向父节点提供的信息；全局答案在每个节点处单独更新。",
        "",
        "### BFS 层序题",
        "",
        f"- 代表题：{ref('M102. 二叉树的层序遍历')}、{ref('M199-二叉树的右视图')}",
        "- 表达顺序：先说明队列含义，再说明每轮先固定当前层 size，最后说明如何加入下一层节点。",
        "",
        "### DFS 网格题",
        "",
        f"- 代表题：{ref('M200-岛屿数量')}",
        "- 表达顺序：遍历网格发现新起点，答案加一；随后 DFS 标记整块连通区域，避免重复计数。",
        "",
        "### 前缀和题",
        "",
        f"- 代表题：{ref('M437-路径总和 III')}",
        "- 表达顺序：固定当前节点作为终点，用历史前缀和出现次数判断有多少合法起点；进入节点加入，离开节点撤销。",
        "",
        "## 复杂度表达",
        "",
        "- 先说每个节点或格子访问次数。",
        "- 再说辅助结构和递归栈分别占多少空间。",
        "- 如果最坏和平衡情况不同，要明确区分。",
    ]
    return "\n".join(lines).strip() + "\n"


def audit_with_intro(existing: str, entry: str) -> str:
    intro = "## 说明\n\n这里记录 Codex 对面试训练系统进行的同步、迁移、修复和验证操作，供用户审阅。"
    body = strip_block_markdown(existing)
    retained = retain_recent_audit_entries(body, datetime.now())
    return intro + "\n\n" + entry.strip() + ("\n\n" + retained if retained else "") + "\n"


def retain_recent_audit_entries(markdown: str, now: datetime) -> str:
    body = re.sub(r"(?ms)^##\s*说明\s*\n.*?(?=^##\s+|\Z)", "", markdown).strip()
    entries: list[tuple[datetime, str]] = []
    for match in re.finditer(r"(?ms)^##\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}).*?\n.*?(?=^##\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}|\Z)", body):
        stamp = datetime.strptime(match.group(1) + " " + match.group(2), "%Y-%m-%d %H:%M")
        if stamp >= now - timedelta(days=AUDIT_RETENTION_DAYS):
            entries.append((stamp, match.group(0).strip()))
    entries.sort(key=lambda item: item[0], reverse=True)
    return "\n\n".join(entry for _, entry in entries)


def validate_content(content: str, title: str, source_id: str = "") -> list[str]:
    errors = []
    body = clean_exported_markdown(content, title)
    if "????" in body:
        errors.append(f"{title}: contains ????")
    if "\ufffd" in body:
        errors.append(f"{title}: contains replacement character")
    if "<!-- codex-" in body:
        errors.append(f"{title}: contains visible codex marker")
    forbidden = [
        "## 旧笔记内容",
        "## 迁移补充",
        "## 旧笔记重组补充",
        "## 来源索引",
        "## 迁移记录",
        "<a href=",
    ]
    for marker in forbidden:
        if marker in body:
            errors.append(f"{title}: contains forbidden user-facing marker {marker}")
    for line in body.splitlines():
        stripped = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", line).strip()
        if re.match(r"^(相关数据结构|相关方法|方法|记录)\s*[：:].*$", stripped):
            errors.append(f"{title}: contains legacy label line {stripped}")
    if re.search(r"(?m)^---\s*$", body) or re.search(r"(?m)^(title|date|lastmod):\s+", body):
        errors.append(f"{title}: contains exported frontmatter in body")
    return errors


def apply_plan(
    config: dict,
    plan: dict,
    client: SiyuanClient,
    notebook: str,
    *,
    delete_safe_legacy: bool = False,
    delete_trivial_legacy: bool = False,
) -> dict:
    created = []
    updated = []
    validation_errors = []
    validated_target_ids: set[str] = set()
    source_bodies: dict[str, str] = {}
    for item in plan["items"]:
        source_md = export_doc(client, item["id"])
        source_bodies[item["id"]] = strip_markdown_noise(source_md, item["title"])
    model = build_knowledge_model(plan["items"], source_bodies)

    for hpath in plan["targetPages"]:
        doc_id, was_created = ensure_doc(client, notebook, hpath, "")
        created.append({"hPath": hpath, "id": doc_id, "created": was_created})

    problem_ids: dict[str, str] = {}
    concept_ids: dict[str, str] = {}
    section_ids: dict[str, str] = {}
    category_ids: dict[str, str] = {}
    for title in sorted(model["problems"], key=problem_sort_key):
        hpath = normalize_hpath(plan["targetRoot"], "题集", title)
        problem_id, was_created = ensure_doc(client, notebook, hpath, "")
        problem_ids[title] = problem_id
        updated.append({"kind": "problem", "source": "", "target": hpath, "targetId": problem_id, "created": was_created, "updated": False})

    for name, concept in sorted(model["concepts"].items(), key=lambda pair: (CATEGORY_ORDER.index(pair[1].get("category", "常用函数")) if pair[1].get("category") in CATEGORY_ORDER else 99, pair[0])):
        hpath = normalize_hpath(plan["targetRoot"], "知识点", concept["category"], name)
        concept_id, was_created = ensure_doc(client, notebook, hpath, "")
        concept_ids[name] = concept_id
        updated.append({"kind": "concept", "source": "", "target": hpath, "targetId": concept_id, "created": was_created, "updated": False})

    for section in ["题集", "知识点", "错题与复习", "面试表达", "Codex 同步日志"]:
        section_id, _ = ensure_doc(client, notebook, normalize_hpath(plan["targetRoot"], section), "")
        section_ids[section] = section_id
    root_id, _ = ensure_doc(client, notebook, normalize_hpath(plan["targetRoot"]), "")

    problem_refs = {title: page_link(block_id, title) for title, block_id in problem_ids.items()}
    concept_refs = {name: page_link(block_id, name) for name, block_id in concept_ids.items()}

    for title, problem in sorted(model["problems"].items(), key=lambda pair: problem_sort_key(pair[0])):
        target_id = problem_ids[title]
        rendered = render_problem_page(problem, concept_refs)
        update_doc(client, target_id, rendered)
        exported = export_doc(client, target_id)
        for source in problem["sources"]:
            validation_errors.extend(validate_content(exported, title, source["id"]))
        validated_target_ids.add(target_id)
        for row in updated:
            if row["targetId"] == target_id:
                row["updated"] = True
                row["source"] = "；".join(source["hPath"] for source in problem["sources"])
                break

    for name, concept in sorted(model["concepts"].items()):
        target_id = concept_ids[name]
        rendered = render_concept_page(concept, problem_refs)
        update_doc(client, target_id, rendered)
        exported = export_doc(client, target_id)
        for source in concept["sources"]:
            validation_errors.extend(validate_content(exported, name, source["id"]))
        validation_errors.extend(validate_content(exported, name, ""))
        validated_target_ids.add(target_id)
        for row in updated:
            if row["targetId"] == target_id:
                row["updated"] = True
                row["source"] = "；".join(source["hPath"] for source in concept["sources"])
                break

    for category in CATEGORY_ORDER:
        hpath = normalize_hpath(plan["targetRoot"], "知识点", category)
        category_id, was_created = ensure_doc(client, notebook, hpath, "")
        category_ids[category] = category_id
        rendered = render_category_page(category, model["categoryIndex"].get(category, []), concept_refs, model)
        update_doc(client, category_id, rendered)
        current = get_block_kramdown(client, category_id)
        validation_errors.extend(validate_content(current, category, ""))
        if model["categoryIndex"].get(category) and "（暂无知识点）" in current:
            validation_errors.append(f"{category}: category index unexpectedly empty")
        validated_target_ids.add(category_id)
        updated.append({"kind": "category", "source": "", "target": hpath, "targetId": category_id, "created": was_created, "updated": True})

    homepage_payloads = {
        "root": (root_id, render_root_home(section_ids, category_ids, concept_ids, problem_ids, model)),
        "题集": (section_ids["题集"], render_problem_index(problem_ids, model)),
        "知识点": (section_ids["知识点"], render_knowledge_home(category_ids, concept_ids, model)),
        "错题与复习": (section_ids["错题与复习"], render_review_home()),
        "面试表达": (section_ids["面试表达"], render_interview_expression_home(problem_ids)),
    }
    for title, (doc_id, rendered) in homepage_payloads.items():
        update_doc(client, doc_id, rendered)
        current = get_block_kramdown(client, doc_id)
        validation_errors.extend(validate_content(current, title, ""))
        if len(current.strip()) < 80:
            validation_errors.append(f"{title}: homepage unexpectedly empty")
        validated_target_ids.add(doc_id)
        updated.append({"kind": "homepage", "source": "", "target": normalize_hpath(plan["targetRoot"], "" if title == "root" else title), "targetId": doc_id, "created": False, "updated": True})

    log_hpath = normalize_hpath(plan["targetRoot"], "Codex 同步日志")
    log_id = section_ids["Codex 同步日志"]
    entry = "\n".join(
        [
            f"## {datetime.now().strftime('%Y-%m-%d %H:%M')} 旧笔记迁移",
            "",
            f"- 扫描旧页面：{plan.get('summary', {}).get('scanned', 0)}",
            f"- 已迁移页面：{len(updated)}",
            f"- 冲突页面：{len(plan['conflicts'])}",
            f"- 删除候选：{len(plan['deleteCandidates'])}",
            "- 迁移方式：按新面试训练体系重组旧内容，并生成题目/知识点/分类索引链接。",
            "- 旧页面未删除。",
            "",
        ]
    )
    update_doc(client, log_id, audit_with_intro(get_block_kramdown(client, log_id), entry))
    log_current = get_block_kramdown(client, log_id)
    validation_errors.extend(validate_content(log_current, "Codex 同步日志", ""))
    validated_target_ids.add(log_id)
    client.data("/api/sqlite/flushTransaction", {})

    if validation_errors:
        raise SiyuanError("Migration validation failed: " + "; ".join(validation_errors[:10]))
    delete_target_errors = verify_delete_candidate_targets(client, notebook, plan) if delete_safe_legacy else []
    if delete_target_errors:
        raise SiyuanError("Legacy cleanup blocked: " + "; ".join(delete_target_errors[:10]))
    deleted_legacy_pages = delete_safe_legacy_pages(client, plan) if delete_safe_legacy else []
    deleted_trivial_conflicts = delete_trivial_legacy_conflicts(client, plan) if delete_trivial_legacy else []
    if deleted_legacy_pages or deleted_trivial_conflicts:
        client.data("/api/sqlite/flushTransaction", {})
    return {
        "applied": True,
        "mode": plan.get("mode", "dry-run"),
        "createdTargetRoots": created,
        "updated": updated,
        "conflicts": plan["conflicts"],
        "deleteCandidates": plan["deleteCandidates"],
        "cleanupAdvice": cleanup_advice(plan),
        "legacyCleanup": {
            "requested": delete_safe_legacy,
            "deletedCount": len(deleted_legacy_pages),
            "deleted": deleted_legacy_pages,
            "trivialConflictCleanupRequested": delete_trivial_legacy,
            "trivialConflictDeletedCount": len(deleted_trivial_conflicts),
            "trivialConflictDeleted": deleted_trivial_conflicts,
            "notDeletedConflicts": plan["conflicts"],
        },
        "validation": {
            "checkedTouchedPages": len(validated_target_ids),
            "issueCount": 0,
            "checks": [
                "no ????",
                "no replacement character",
                "no visible codex marker",
                "native block references allowed; no HTML anchor source",
                "no source index or migration record in user-facing pages",
                "no legacy copy markers or old label lines",
                "category indexes are non-empty when concepts exist",
                "root and section home pages are non-empty",
            ],
        },
        "modelSummary": {
            "problems": len(model["problems"]),
            "concepts": len(model["concepts"]),
            "categories": {key: len(value) for key, value in model["categoryIndex"].items()},
        },
        "homepages": {title: f"siyuan://blocks/{doc_id}" for title, (doc_id, _) in homepage_payloads.items()},
        "auditLog": f"siyuan://blocks/{log_id}",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--apply", action="store_true", help="Apply migration. Default is dry-run.")
    parser.add_argument("--delete-safe-legacy", action="store_true", help="After successful apply validation, delete only safe migrated legacy pages. Conflicts are preserved.")
    parser.add_argument("--delete-trivial-legacy", action="store_true", help="After successful apply validation, delete empty legacy pages and obsolete legacy category index pages.")
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
        if args.delete_safe_legacy and not args.apply:
            raise SiyuanError("--delete-safe-legacy requires --apply.")
        if args.delete_trivial_legacy and not args.apply:
            raise SiyuanError("--delete-trivial-legacy requires --apply.")
        result = (
            apply_plan(
                config,
                plan,
                client,
                notebook,
                delete_safe_legacy=args.delete_safe_legacy,
                delete_trivial_legacy=args.delete_trivial_legacy,
            )
            if args.apply
            else plan
        )
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
