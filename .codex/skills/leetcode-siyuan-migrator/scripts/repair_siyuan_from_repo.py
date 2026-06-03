#!/usr/bin/env python3
"""Repair the SiYuan interview wiki from repository notes and Java solutions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
COACH_SCRIPTS = ROOT / ".codex" / "skills" / "leetcode-interview-coach" / "scripts"
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


CATEGORY_ORDER = ["数据结构", "解题方法", "解题模式", "常用函数"]

DIFFICULTY_LABELS = {"E": "简单", "M": "中等", "H": "困难"}

OBSOLETE_CONCEPT_HPATHS = [
    ("知识点", "数据结构", "队列（迭代法）"),
]

CATEGORY_DESCRIPTIONS = {
    "数据结构": "先判断题目操作的对象是什么，例如树、数组、矩阵、队列、哈希映射或图。",
    "解题方法": "再判断用什么遍历、递归、搜索、前缀和等方法把问题拆开。",
    "解题模式": "最后沉淀可迁移的题型模式，例如网格搜索、连通块、Flood Fill。",
    "常用函数": "把 Java API 的高频使用方式单独复习，降低手写时的语法损耗。",
}

REVIEW_LABEL_DESCRIPTIONS = {
    "一刷卡壳": "首次做题时无法稳定找到切入点，优先复盘题型识别信号。",
    "提示后完成": "提示后能做出，说明模式正在形成，需要二刷固化。",
    "独立完成": "可以独立完成，后续重点保持速度、边界和表达稳定。",
    "代码有 bug": "思路基本正确，但实现细节或边界条件还不稳定。",
    "面试表达不熟": "能写代码但讲述不够清晰，需要专项练习表达。",
    "需要二刷": "涉及高频模式或关键卡点，应进入下一轮复习。",
}

AUDIT_RETENTION_DAYS = 7

PROBLEMS: list[dict[str, Any]] = [
    {
        "key": "E101",
        "title": "E101-对称二叉树",
        "java": "src/main/java/com/czf/binarytree/E101_Symmetric_BinaryTree.java",
        "tags": {"dataStructures": ["二叉树", "队列"], "methods": ["BFS"], "patterns": [], "commonFunctions": ["队列Queue的常用函数"]},
        "fallbackThinking": "可以把需要镜像比较的节点成对放入队列。每次取出一对节点，先判断空值是否对称，再判断节点值是否相等；如果当前这一对合法，就继续把 `left.left/right.right` 和 `left.right/right.left` 成对入队。队列处理结束仍未发现冲突，说明整棵树对称。",
        "complexity": "每个节点最多入队、出队一次，时间复杂度是 O(n)。队列最多保存一层节点，最坏空间复杂度 O(n)。",
    },
    {
        "key": "E108",
        "title": "E108. 将有序数组转换为二叉搜索树",
        "java": "src/main/java/com/czf/binarytree/E108_Convert_SortedArray_BinarySearchTree.java",
        "tags": {"dataStructures": ["二叉树", "数组"], "methods": ["递归法"], "patterns": [], "commonFunctions": ["数组Array的常用函数"]},
        "fallbackThinking": "有序数组要构造成平衡二叉搜索树，核心是每次选择当前区间的中点作为根节点。中点左侧递归构造左子树，右侧递归构造右子树。区间为空时返回 null。",
        "complexity": "每个元素只会创建一次节点，时间复杂度 O(n)。递归栈取决于树高，平衡情况下空间复杂度 O(log n)。",
    },
    {
        "key": "E543",
        "title": "E543-二叉树的直径",
        "java": "src/main/java/com/czf/binarytree/E543_Diameter_BinaryTree.java",
        "tags": {"dataStructures": ["二叉树"], "methods": ["递归法"], "patterns": [], "commonFunctions": []},
        "fallbackThinking": "经过某个节点的最长路径长度等于左子树最大深度加右子树最大深度。递归函数返回当前节点的最大深度，同时用 `leftDepth + rightDepth` 更新全局直径。",
        "complexity": "每个节点访问一次，时间复杂度 O(n)。递归栈取决于树高，最坏 O(n)，平衡树 O(log n)。",
    },
    {
        "key": "H124",
        "title": "H124-二叉树中的最大路径和",
        "java": "src/main/java/com/czf/binarytree/H124_BinaryTree_Maximum_PathSum.java",
        "tags": {"dataStructures": ["二叉树"], "methods": ["递归法"], "patterns": [], "commonFunctions": []},
        "fallbackThinking": "使用后序递归。每个节点先计算左右子树能提供的最大单边贡献，负贡献直接舍弃。用 `leftGain + node.val + rightGain` 更新全局最大路径和；返回给父节点时只能选择左右一边继续向上，所以返回 `node.val + max(leftGain, rightGain)`。",
        "complexity": "每个节点访问一次，时间复杂度 O(n)。递归栈取决于树高，最坏 O(n)，平衡树 O(log n)。",
    },
    {
        "key": "M098",
        "title": "M098-验证二叉搜索树",
        "java": "src/main/java/com/czf/binarytree/M098_Validate_BinarySearchTree.java",
        "tags": {"dataStructures": ["二叉树"], "methods": ["递归法"], "patterns": [], "commonFunctions": []},
        "fallbackThinking": "只比较当前节点和直接左右孩子不够，因为右子树里的所有节点都必须大于根节点，左子树里的所有节点都必须小于根节点。因此递归时维护当前节点允许的取值范围 `(lower, upper)`。节点值不在范围内则返回 false；递归左子树时上界变为当前节点值，递归右子树时下界变为当前节点值。",
        "complexity": "每个节点访问一次，时间复杂度 O(n)。递归栈取决于树高，最坏 O(n)，平衡树 O(log n)。",
    },
    {
        "key": "M102",
        "title": "M102. 二叉树的层序遍历",
        "java": "src/main/java/com/czf/binarytree/M102_Level_Order_BinaryTree.java",
        "tags": {"dataStructures": ["二叉树", "队列", "可变数组"], "methods": ["BFS"], "patterns": [], "commonFunctions": ["队列Queue的常用函数", "可变数组的常用函数"]},
        "fallbackThinking": "层序遍历使用队列。先把根节点入队，每轮循环先记录当前队列大小 `size`，这个 size 就是当前层节点数。循环处理这一层的节点，把节点值加入当前层列表，并把非空左右孩子加入队列。当前层处理完后把层列表加入答案。",
        "complexity": "每个节点入队、出队一次，时间复杂度 O(n)。队列和答案使用 O(n) 空间。",
    },
    {
        "key": "M105",
        "title": "M105-从前序与中序遍历序列构造二叉树",
        "java": "src/main/java/com/czf/binarytree/M105_Construct_BinaryTree.java",
        "tags": {"dataStructures": ["二叉树", "数组", "哈希映射"], "methods": ["递归法"], "patterns": [], "commonFunctions": ["数组Array的常用函数", "哈希映射hashmap的常用函数"]},
        "fallbackThinking": "前序遍历的第一个元素是当前子树根节点。再用中序遍历中根节点的位置划分左子树和右子树，并根据左子树大小切分前序区间。为了避免每次在线性扫描中序数组，先用 HashMap 记录每个值在中序数组中的下标。",
        "complexity": "每个节点创建一次，HashMap 查询根节点位置为 O(1)，时间复杂度 O(n)。HashMap 和递归栈最坏空间复杂度 O(n)。",
    },
    {
        "key": "M114",
        "title": "M114-二叉树展开为链表",
        "java": "src/main/java/com/czf/binarytree/M114_Flatten_BinaryTree.java",
        "tags": {"dataStructures": ["二叉树"], "methods": [], "patterns": [], "commonFunctions": []},
        "fallbackThinking": "原地展开时遍历当前节点。如果当前节点有左子树，就找到左子树最右侧节点，把原右子树挂到这个最右侧节点的 right 上；再把左子树整体搬到当前节点 right，并把 left 置空。随后继续沿 right 指针向后处理。",
        "complexity": "每个节点会沿右链被访问，常见实现时间复杂度 O(n)，额外空间 O(1)。",
    },
    {
        "key": "M199",
        "title": "M199-二叉树的右视图",
        "java": "src/main/java/com/czf/binarytree/M199_BinaryTree_RightSideView.java",
        "tags": {"dataStructures": ["二叉树", "队列", "可变数组"], "methods": ["BFS"], "patterns": [], "commonFunctions": ["队列Queue的常用函数", "可变数组的常用函数"]},
        "fallbackThinking": "右视图就是每一层最右侧的节点。使用队列做层序遍历，每层先固定 `size`，遍历这一层时如果 `i == size - 1`，就把当前节点值加入答案。左右孩子按正常顺序入队即可。",
        "complexity": "每个节点访问一次，时间复杂度 O(n)。队列最坏 O(n)，答案 O(h)。",
    },
    {
        "key": "M200",
        "title": "M200-岛屿数量",
        "java": "src/main/java/com/czf/matrix/M200_Number_Of_Islands.java",
        "tags": {"dataStructures": ["矩阵", "图论"], "methods": ["DFS"], "patterns": ["网格搜索", "连通块", "Flood Fill"], "commonFunctions": ["数组Array的常用函数"]},
        "fallbackThinking": "遍历整个网格，如果遇到字符 `'1'`，说明发现一座还没有统计过的新岛屿，答案加一。随后从该格子出发做 DFS，把上下左右连通的所有陆地都标记成 `'0'`，避免后续重复计数。",
        "complexity": "每个格子最多被访问一次，时间复杂度 O(mn)。递归栈最坏情况下可能达到 O(mn)。",
    },
    {
        "key": "M230",
        "title": "M230.二叉搜索树中第K小的元素",
        "java": "src/main/java/com/czf/binarytree/M230_Kth_Smallest_BinarySearchTree.java",
        "tags": {"dataStructures": ["二叉树"], "methods": ["递归法", "中序遍历"], "patterns": [], "commonFunctions": []},
        "fallbackThinking": "二叉搜索树的中序遍历结果是升序的，因此第 k 小元素就是中序遍历访问到的第 k 个节点。可以维护全局 `count` 和 `ans`，递归中序遍历，访问到第 k 个节点后记录答案，并在递归入口判断是否已经找到，减少无用遍历。",
        "complexity": "若提前停止，时间复杂度 O(k) 到 O(n)；递归栈空间 O(h)。",
    },
    {
        "key": "M236",
        "title": "M236-二叉树的最近公共祖先",
        "java": "src/main/java/com/czf/binarytree/M236_Lowest_Common_Ancestor.java",
        "tags": {"dataStructures": ["二叉树"], "methods": ["递归法"], "patterns": [], "commonFunctions": []},
        "fallbackThinking": "递归函数在当前子树中寻找 p、q 或它们的最近公共祖先。空节点返回 null；当前节点等于 p 或 q 时返回当前节点。递归左右子树后，如果左右都非空，说明 p 和 q 分别在两侧，当前节点就是最近公共祖先；如果只有一侧非空，就把那一侧结果向上返回。",
        "complexity": "每个节点最多访问一次，时间复杂度 O(n)。递归栈空间 O(h)，最坏 O(n)。",
    },
    {
        "key": "M437",
        "title": "M437-路径总和 III",
        "java": "src/main/java/com/czf/binarytree/M437_Path_Sum_III.java",
        "tags": {"dataStructures": ["二叉树", "哈希映射"], "methods": ["递归法", "前缀和"], "patterns": [], "commonFunctions": ["哈希映射hashmap的常用函数"]},
        "fallbackThinking": "优化版固定当前节点作为路径终点，维护从根到当前节点的前缀和。若当前前缀和为 `currentSum`，路径和为 target 的起点数量等于历史前缀和 `currentSum - targetSum` 出现次数。进入节点时加入当前前缀和，递归左右子树，离开节点时撤销，避免影响其他分支。",
        "complexity": "每个节点访问一次，HashMap 操作平均 O(1)，时间复杂度 O(n)。HashMap 和递归栈最坏 O(n)。",
    },
]

CONCEPT_PROFILES = {
    "二叉树": ("数据结构", "二叉树题通常把问题拆成当前节点、左子树、右子树三个部分，用递归或层序遍历处理。", ["题目给出 `TreeNode`", "答案依赖左右子树的信息", "可以把整棵树问题缩小到某个子树"], ["空节点返回值要和题意对应", "递归返回值和全局答案不要混淆", "路径类问题要区分完整路径和向父节点返回的单边路径"]),
    "队列": ("数据结构", "队列先进先出，常用于 BFS、层序遍历和按到达顺序处理状态。", ["需要按层访问节点", "状态从起点一圈圈扩散", "每次处理最早加入的元素"], ["循环条件应是 `!queue.isEmpty()`", "层序遍历要先记录 `size`", "入队前判断空节点"]),
    "可变数组": ("数据结构", "可变数组通常对应 Java 的 `ArrayList`，适合动态收集遍历结果或维护顺序集合。", ["结果数量不固定", "需要按顺序追加答案", "题目返回 `List` 或 `List<List<...>>`"], ["泛型类型要写完整", "不要复用同一个临时列表", "每一层/每一组结果通常要新建 list"]),
    "数组": ("数据结构", "数组题关注连续存储、下标访问、区间和排序关系。", ["输入是数组", "需要按下标遍历或切分区间", "题目强调有序数组"], ["区间边界要统一", "空数组和单元素边界要确认", "修改数组前确认题目是否允许"]),
    "哈希映射": ("数据结构", "哈希映射用 key 快速定位 value，适合计数、索引映射、前缀和统计和缓存状态。", ["需要 O(1) 查询是否出现过", "需要记录出现次数或下标", "暴力查找中存在重复扫描"], ["默认值语义要正确", "key 类型可能需要 Long 防溢出", "回溯场景离开节点要撤销计数"]),
    "矩阵": ("数据结构", "矩阵题的核心是二维坐标、行列边界、方向遍历和必要时的原地标记。", ["输入是二维数组或网格", "题目描述上下左右移动", "需要遍历所有格子找起点"], ["`m = grid.length`，`n = grid[0].length`", "先判断边界再访问 grid", "字符矩阵要使用字符字面量"]),
    "图论": ("数据结构", "图论关注节点与边的关系。网格、路径和连通性问题都可以抽象成图。", ["元素之间存在连接、可达或路径关系", "可以把对象抽象为节点，把关系抽象为边", "题目关注连通性或组件"], ["先判断有向还是无向", "visited 粒度要与状态定义一致", "网格题也可能是隐式图"]),
    "DFS": ("解题方法", "DFS 用递归或栈沿一个方向持续深入，适合把树、图、网格中的可达状态一次性访问完。", ["从某个起点向外扩展并访问所有可达节点", "需要标记 visited 或把已访问状态改掉", "树/图/网格问题可以拆成当前节点加相邻节点"], ["递归出口必须先处理越界和非法状态", "访问标记要在继续递归前完成", "如果是回溯问题，离开节点前要撤销选择"]),
    "BFS": ("解题方法", "BFS 用队列按层扩展状态，适合最短步数、层序遍历和逐圈扩散问题。", ["题目要求按层输出", "每次从当前层扩展到下一层", "状态适合先进先出处理"], ["通常应在入队时标记 visited", "层数统计要固定当前队列大小", "不要把循环条件写成 `queue != null`"]),
    "递归法": ("解题方法", "递归法把大问题拆成同结构的小问题，关键是明确函数语义、终止条件和返回值。", ["当前问题可以交给子问题先解决", "树、链表、分治区间天然递归", "需要从子结构返回信息给父结构"], ["辅助函数参数要包含递归状态", "终止条件要覆盖空结构或空区间", "不要只照抄主函数参数"]),
    "中序遍历": ("解题方法", "中序遍历按左、根、右访问二叉树；在二叉搜索树中会得到升序序列。", ["题目是 BST 并要求第 k 小、排序或有序性", "需要从小到大访问节点", "可以利用左根右顺序"], ["空节点直接返回", "计数变量要跨递归层共享", "找到答案后要避免继续无用遍历"]),
    "前缀和": ("解题方法", "前缀和把区间或路径和转换成两个累计和之差，常与 HashMap 计数配合。", ["需要快速判断某段和是否等于目标值", "路径/数组中存在正负数，不能简单剪枝", "暴力枚举起点终点有重复计算"], ["前缀和可能溢出，要考虑 long", "初始前缀和 0 要加入一次", "回溯离开路径时要撤销计数"]),
    "网格搜索": ("解题模式", "网格搜索把二维数组中的每个格子看成状态，核心是坐标、边界和方向数组。", ["输入是二维数组或矩阵", "需要上下左右移动", "要遍历每个格子寻找搜索起点"], ["行列下标不要写反", "边界条件要覆盖小于 0 和大于等于边界", "修改原网格前确认题目允许"]),
    "连通块": ("解题模式", "连通块表示通过相邻关系连接成的一组节点，常见任务是统计块数或处理每一块的大小/性质。", ["题目要求统计岛屿、区域或组件数量", "同一块中的节点通过相邻关系互相到达", "发现一个未访问节点后要把整块标记掉"], ["计数应发生在发现新块时", "标记不完整会导致重复计数", "方向关系要符合题目定义"]),
    "Flood Fill": ("解题模式", "Flood Fill 是从一个种子位置出发，把同一连通区域全部访问或改色的网格搜索模式。", ["从一个格子出发扩散到同类格子", "需要把一整片区域标记掉", "题目强调上下左右相邻"], ["先判断边界再访问 grid", "改色或标记要避免重复递归", "注意字符 `'1'` 和数字 `1` 的区别"]),
    "数组Array的常用函数": ("常用函数", "数组常用函数用于处理固定长度顺序数据，复习时重点关注长度、下标访问、拷贝、排序和填充。", ["代码直接操作数组或二维数组", "需要用 `length` 判断边界", "需要排序、填充或拷贝数组"], ["数组长度是属性 `length`", "二维数组行列边界分别取 `grid.length` 和 `grid[0].length`", "排序会修改原数组"]),
    "可变数组的常用函数": ("常用函数", "可变数组常用函数对应 Java `List`/`ArrayList`，适合收集不定长结果和按顺序追加元素。", ["返回值是 `List` 或 `List<List<...>>`", "需要逐步追加答案", "需要按下标读取或修改动态列表"], ["`size()` 是方法", "每层结果要新建 `List`", "泛型类型要写完整"]),
    "哈希映射hashmap的常用函数": ("常用函数", "哈希映射常用函数用于通过 key 快速查询、计数、记录下标或维护前缀和出现次数。", ["需要快速判断 key 是否出现过", "需要记录次数、下标或映射关系", "代码中出现 `HashMap`、`Map`、`getOrDefault`"], ["默认值要和计数语义一致", "回溯场景离开节点要撤销计数", "前缀和可能需要 Long 作为 key"]),
    "队列Queue的常用函数": ("常用函数", "队列常用函数用于先进先出处理状态，常见于 BFS 和二叉树层序遍历。", ["代码使用 `Queue` 或 `LinkedList`", "需要入队、出队处理状态", "按层遍历时要读取当前 `queue.size()`"], ["循环条件应写 `!queue.isEmpty()`", "通常用 `offer`/`poll`", "层序遍历要先固定当前层大小"]),
}


def page_link(block_id: str, text: str) -> str:
    escaped = text.replace('"', '\\"')
    return f'(({block_id} "{escaped}"))'


def problem_number(problem: dict[str, Any]) -> int:
    match = re.search(r"\d+", problem["key"])
    return int(match.group(0)) if match else 99999


def sorted_problems() -> list[dict[str, Any]]:
    return sorted(PROBLEMS, key=problem_number)


def distinct_problem_count_for_category(category: str, concept_names: dict[str, str]) -> int:
    names = {name for name, cat in concept_names.items() if cat == category}
    titles: set[str] = set()
    for problem in PROBLEMS:
        tags = problem["tags"]
        for key in ["dataStructures", "methods", "patterns", "commonFunctions"]:
            if any(name in names for name in tags[key]):
                titles.add(problem["title"])
    return len(titles)


def render_root_home(
    section_ids: dict[str, str],
    category_ids: dict[str, str],
    concept_ids: dict[str, str],
    concept_names: dict[str, str],
    problems_by_concept: dict[str, list[str]],
    problem_ids: dict[str, str],
) -> str:
    category_lines = []
    for category in CATEGORY_ORDER:
        concept_count = sum(1 for cat in concept_names.values() if cat == category)
        problem_count = distinct_problem_count_for_category(category, concept_names)
        category_lines.append(f"- {page_link(category_ids[category], category)}：{concept_count} 个知识点，关联题目 {problem_count} 道")

    top_concepts = sorted(
        problems_by_concept.items(),
        key=lambda pair: (-len(pair[1]), pair[0]),
    )[:10]
    problem_preview = sorted_problems()[-6:]

    lines = [
        "## 今日入口",
        "",
        f"- {page_link(section_ids['题集'], '题集')}：按题号复习已经整理过的 Hot100 题目。",
        f"- {page_link(section_ids['知识点'], '知识点')}：按数据结构、方法、模式、常用函数复习。",
        f"- {page_link(section_ids['错题与复习'], '错题与复习')}：按掌握状态安排二刷和表达训练。",
        f"- {page_link(section_ids['面试表达'], '面试表达')}：沉淀面试中可直接说出口的解题表达。",
        f"- {page_link(section_ids['Codex 同步日志'], 'Codex 同步日志')}：审阅自动同步、修复和迁移记录。",
        "",
        "## 训练概览",
        "",
        f"- 已整理题目：{len(problem_ids)} 道",
        f"- 已整理知识点：{len(concept_names)} 个",
        *category_lines,
        "",
        "## 高频知识地图",
        "",
    ]
    for name, titles in top_concepts:
        category = concept_names[name]
        lines.append(f"- {page_link(category_ids[category], category)} / {page_link(concept_ids[name], name)}：关联题目 {len(titles)} 道")
    lines.extend(["", "## 最近整理题目", ""])
    for problem in problem_preview:
        lines.append(f"- {page_link(problem_ids[problem['title']], problem['title'])}")
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


def render_knowledge_home(
    category_ids: dict[str, str],
    concept_ids: dict[str, str],
    concept_names: dict[str, str],
    problems_by_concept: dict[str, list[str]],
) -> str:
    lines = ["## 分类入口", ""]
    for category in CATEGORY_ORDER:
        names = sorted(name for name, cat in concept_names.items() if cat == category)
        problem_count = distinct_problem_count_for_category(category, concept_names)
        lines.append(f"- {page_link(category_ids[category], category)}：{len(names)} 个知识点，关联题目 {problem_count} 道。{CATEGORY_DESCRIPTIONS[category]}")

    lines.extend(["", "## 高频知识点", ""])
    for name, titles in sorted(problems_by_concept.items(), key=lambda pair: (-len(pair[1]), pair[0]))[:12]:
        lines.append(f"- {page_link(concept_ids[name], name)}：关联题目 {len(titles)} 道")

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


def render_problem_index(problem_ids: dict[str, str]) -> str:
    groups: dict[str, list[dict[str, Any]]] = {"E": [], "M": [], "H": []}
    for problem in sorted_problems():
        groups.setdefault(problem["key"][0], []).append(problem)

    lines = [
        "## 题目列表",
        "",
        f"当前题集已整理 {len(problem_ids)} 道题。每个题目页包含题干、思路、最终题解、复杂度和易错点。",
        "",
    ]
    for difficulty in ["E", "M", "H"]:
        items = groups.get(difficulty) or []
        if not items:
            continue
        lines.extend([f"## {DIFFICULTY_LABELS.get(difficulty, difficulty)}", ""])
        for problem in items:
            tags = problem["tags"]
            pieces = []
            if tags["dataStructures"]:
                pieces.append("数据结构：" + "、".join(tags["dataStructures"]))
            if tags["methods"]:
                pieces.append("方法：" + "、".join(tags["methods"]))
            if tags["patterns"]:
                pieces.append("模式：" + "、".join(tags["patterns"]))
            lines.append(f"- {page_link(problem_ids[problem['title']], problem['title'])}：{'；'.join(pieces) if pieces else '标签待补充'}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_review_home(review_ids: dict[str, str] | None = None) -> str:
    lines = [
        "## 复习原则",
        "",
        "这里仅保留需要复盘的真实题目入口。没有题目归档时，不自动堆叠空标签页。",
        "",
        "## 当前复习入口",
        "",
    ]
    if review_ids:
        for label, rid in review_ids.items():
            lines.append(f"- {page_link(rid, label)}：{REVIEW_LABEL_DESCRIPTIONS.get(label, '需要复盘的题目集合')}")
    else:
        lines.append("- 暂无自动归档题目。完成题目收尾后，只有带复习标签的题目会出现在这里。")
    lines.extend(
        [
            "",
            "## 记录标准",
            "",
            "- 卡壳点写成具体问题，例如“想不到辅助函数参数”或“边界条件顺序写错”。",
            "- 二刷时记录是否能独立说清题型、状态定义、复杂度和易错点。",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def render_review_label(label: str, existing: str) -> str:
    if existing.strip() and "## 题集" in existing:
        return existing
    return "\n".join(
        [
            "## 说明",
            "",
            REVIEW_LABEL_DESCRIPTIONS[label],
            "",
            "## 题集",
            "",
            "- 暂无自动归档题目。",
        ]
    ).strip() + "\n"


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
        "",
        "## 卡壳复盘表达",
        "",
        "- 我卡在是否需要辅助函数，因为主函数参数不足以携带递归状态。",
        "- 我卡在返回值语义，后来区分了“返回给父节点的信息”和“用于更新最终答案的信息”。",
        "- 我卡在边界条件，后来固定成先判越界、再判状态、再递归扩展。",
    ]
    return "\n".join(lines).strip() + "\n"


def audit_with_intro(existing: str, entry: str) -> str:
    intro = "## 说明\n\n这里记录 Codex 对面试训练系统进行的同步、迁移、修复和验证操作，供用户审阅。"
    cleaned = strip_siyuan_metadata(existing)
    retained = retain_recent_audit_entries(cleaned, datetime.now())
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


def strip_siyuan_metadata(markdown: str) -> str:
    text = re.sub(r"(?m)^\{:\s+[^}]*\}\s*$", "", markdown.strip())
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"(?ms)(?:\A|\n)---\s*\n.*?\n---\s*(?=\n|\Z)", "\n", text)
    text = re.sub(r"(?m)^\{:\s+[^}]*\}\s*$", "", text)
    text = re.sub(r"(?m)^#\s+Codex 同步日志\s*$", "", text)
    text = re.sub(r"(?m)^(title|date|lastmod):.*$", "", text)
    text = text.replace("仓库 `src/notes`\u200b 与 `src/main/java`", "仓库学习笔记与 Java 题解文件")
    text = text.replace("仓库 `src/notes` 与 `src/main/java`", "仓库学习笔记与 Java 题解文件")
    text = text.replace("无脚注式引用、", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def find_note(repo: Path, key: str) -> Path | None:
    for path in (repo / "src" / "notes").rglob("*.md"):
        if path.name.startswith(key):
            return path
    return None


def section(markdown: str, heading: str) -> str:
    match = re.search(rf"(?ms)^##\s*{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)", markdown)
    return match.group(1).strip() if match else ""


def codex_region(markdown: str) -> str:
    match = re.search(r"(?s)<!-- codex-leetcode-start -->(.*?)<!-- codex-leetcode-end -->", markdown)
    return match.group(1).strip() if match else ""


def statement_from_note(markdown: str) -> str:
    region = codex_region(markdown)
    if region and section(region, "题干"):
        return section(region, "题干")
    return re.split(r"(?m)^##\s*思路\s*$|<!-- codex-leetcode-start -->", markdown, maxsplit=1)[0].strip()


def thinking_from_note(markdown: str, fallback: str) -> str:
    region = codex_region(markdown)
    if region:
        parts = []
        for name in ["思路", "思考过程"]:
            value = section(region, name)
            if value:
                label = "思路" if name == "思路" else "关键思考"
                parts.append(f"**{label}**\n\n{value}")
        if parts:
            return "\n\n".join(parts)
    value = section(markdown, "思路")
    return value or fallback


def extract_solution(java_text: str) -> str:
    match = re.search(r"(?s)//\s*region LeetCode solution\s*(.*?)\s*//\s*endregion", java_text)
    if match:
        return match.group(1).strip()
    cleaned = re.sub(r"(?m)^package\s+.*?;\s*$", "", java_text)
    cleaned = re.sub(r"(?m)^import\s+.*?;\s*$", "", cleaned)
    return cleaned.strip()


def render_problem(problem: dict[str, Any], note_text: str, java_text: str, concept_refs: dict[str, str]) -> str:
    tags = problem["tags"]
    region = codex_region(note_text)
    thinking = thinking_from_note(note_text, problem["fallbackThinking"])
    complexity = section(region, "复杂度") or problem["complexity"]
    pitfalls = section(region, "易错点")
    lines = [
        "## 知识链接",
        "",
        f"- 数据结构：{'、'.join(concept_refs[name] for name in tags['dataStructures'] if name in concept_refs) or '（待补充）'}",
        f"- 解题方法：{'、'.join(concept_refs[name] for name in tags['methods'] if name in concept_refs) or '（待补充）'}",
        f"- 解题模式：{'、'.join(concept_refs[name] for name in tags['patterns'] if name in concept_refs) or '（待补充）'}",
        f"- 常用函数：{'、'.join(concept_refs[name] for name in tags['commonFunctions'] if name in concept_refs) or '（待补充）'}",
        "",
        "## 题干",
        "",
        statement_from_note(note_text),
        "",
        "## 面试版思路",
        "",
        thinking,
        "",
        "## 最终题解",
        "",
        "```java",
        extract_solution(java_text),
        "```",
        "",
        "## 复杂度",
        "",
        complexity,
        "",
        "## 易错点",
        "",
        pitfalls or "- 递归/遍历题要先明确空节点、边界和返回值语义。\n- 写代码时注意题目输入类型，字符、数组、集合 API 不要混用。",
        "",
        "## 同步记录",
        "",
        "- 恢复来源：仓库题解与学习笔记。",
        f"- 恢复时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    return "\n".join(lines).strip() + "\n"


def concept_template(name: str, category: str, problem_links: list[str]) -> str:
    profile = CONCEPT_PROFILES.get(name, (category, f"{name} 是面试训练体系中的知识点，需要结合题目特征、代码结构和易错点复习。", ["题目特征稳定指向该知识点"], ["只记名称但不能说清适用条件"]))
    _, intro, signals, pitfalls = profile
    lines = [
        f"分类：{category}",
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
        "// 结合关联题目复习代码结构",
        "```",
        "",
        "## 高频易错点",
        "",
        *[f"- {item}" for item in pitfalls],
        "",
        "## 题集",
        "",
        *[f"- {link}" for link in problem_links],
    ]
    return "\n".join(lines).strip() + "\n"


def validate_export(markdown: str, title: str) -> list[str]:
    errors = []
    for marker in [
        "????",
        "\ufffd",
        "<!-- codex-",
        "<a href=",
        "## 来源索引",
        "## 迁移记录",
        "## 旧笔记内容",
        "## 迁移补充",
        "src/main/java",
        "src/notes",
        "F:\\",
    ]:
        if marker in markdown:
            errors.append(f"{title}: contains {marker}")
    for required in ["## 知识链接", "## 题干", "## 面试版思路", "## 最终题解"]:
        if title.startswith(("E", "M", "H")) and required not in markdown:
            errors.append(f"{title}: missing {required}")
    return errors


def sync(config_path: Path, *, dry_run: bool) -> dict[str, Any]:
    config = load_config(config_path)
    root = (config.get("wikiPolicy") or {}).get("systemRootHPath", "/算法题/面试手撕训练系统")
    plan = {"dryRun": dry_run, "problems": [p["title"] for p in PROBLEMS]}
    if dry_run:
        return plan

    client, resolved = open_client_from_config(config, config_path=config_path, update_config=True)
    notebook = resolved.get("notebookId")
    if not notebook:
        raise SiyuanError("配置缺少 notebookId。")

    concept_names: dict[str, str] = {}
    for problem in PROBLEMS:
        for key, category in [("dataStructures", "数据结构"), ("methods", "解题方法"), ("patterns", "解题模式"), ("commonFunctions", "常用函数")]:
            for name in problem["tags"][key]:
                concept_names[name] = CONCEPT_PROFILES.get(name, (category, "", [], []))[0]

    concept_ids: dict[str, str] = {}
    for name, category in sorted(concept_names.items(), key=lambda pair: (CATEGORY_ORDER.index(pair[1]), pair[0])):
        hpath = normalize_hpath(root, "知识点", category, name)
        cid, _ = ensure_doc(client, notebook, hpath, "")
        concept_ids[name] = cid
    concept_refs = {name: page_link(cid, name) for name, cid in concept_ids.items()}

    problem_ids: dict[str, str] = {}
    for problem in PROBLEMS:
        hpath = normalize_hpath(root, "题集", problem["title"])
        pid, _ = ensure_doc(client, notebook, hpath, "")
        problem_ids[problem["title"]] = pid

    section_ids: dict[str, str] = {}
    for section_name in ["题集", "知识点", "错题与复习", "面试表达", "Codex 同步日志"]:
        sid, _ = ensure_doc(client, notebook, normalize_hpath(root, section_name), "")
        section_ids[section_name] = sid
    root_id, _ = ensure_doc(client, notebook, normalize_hpath(root), "")

    updated = []
    validation_errors: list[str] = []
    for problem in PROBLEMS:
        note_path = find_note(ROOT, problem["key"])
        if not note_path:
            raise SiyuanError(f"找不到仓库笔记：{problem['key']}")
        java_path = ROOT / problem["java"]
        if not java_path.exists():
            raise SiyuanError(f"找不到 Java 文件：{java_path}")
        rendered = render_problem(problem, read_text(note_path), read_text(java_path), concept_refs)
        update_doc(client, problem_ids[problem["title"]], rendered)
        exported = export_doc(client, problem_ids[problem["title"]])
        validation_errors.extend(validate_export(exported, problem["title"]))
        updated.append({"kind": "problem", "title": problem["title"], "id": problem_ids[problem["title"]]})

    problems_by_concept: dict[str, list[str]] = {name: [] for name in concept_names}
    for problem in PROBLEMS:
        for key in ["dataStructures", "methods", "patterns", "commonFunctions"]:
            for name in problem["tags"][key]:
                problems_by_concept.setdefault(name, []).append(problem["title"])
    problem_refs = {title: page_link(pid, title) for title, pid in problem_ids.items()}

    for name, titles in problems_by_concept.items():
        category = concept_names[name]
        links = [problem_refs[title] for title in sorted(titles, key=lambda title: int(re.search(r"\d+", title).group(0)) if re.search(r"\d+", title) else 99999)]
        update_doc(client, concept_ids[name], concept_template(name, category, links))
        exported = export_doc(client, concept_ids[name])
        if "来源索引" in exported or "迁移记录" in exported:
            validation_errors.append(f"{name}: invalid exported markers")
        updated.append({"kind": "concept", "title": name, "id": concept_ids[name]})

    category_ids: dict[str, str] = {}
    for category in CATEGORY_ORDER:
        hpath = normalize_hpath(root, "知识点", category)
        cid, _ = ensure_doc(client, notebook, hpath, "")
        category_ids[category] = cid
        names = sorted([name for name, cat in concept_names.items() if cat == category])
        lines = ["## 知识点", ""]
        for name in names:
            count = len(problems_by_concept.get(name, []))
            lines.append(f"- {page_link(concept_ids[name], name)}：关联题目 {count} 道")
        update_doc(client, cid, "\n".join(lines).strip() + "\n")
        exported = export_doc(client, cid)
        if "<a href=" in exported or "来源索引" in exported or "迁移记录" in exported:
            validation_errors.append(f"{category}: invalid exported markers")
        updated.append({"kind": "category", "title": category, "id": cid})

    removed_empty_reviews = []
    for label in REVIEW_LABEL_DESCRIPTIONS:
        hpath = normalize_hpath(root, "错题与复习", label)
        ids = client.data("/api/filetree/getIDsByHPath", {"notebook": notebook, "path": hpath}) or []
        for doc_id in ids:
            current = get_block_kramdown(client, str(doc_id))
            if "暂无自动归档题目" in current or "((" not in current:
                client.data("/api/filetree/removeDocByID", {"id": str(doc_id)})
                removed_empty_reviews.append({"hPath": hpath, "id": str(doc_id)})

    homepage_payloads = {
        "root": (root_id, render_root_home(section_ids, category_ids, concept_ids, concept_names, problems_by_concept, problem_ids)),
        "题集": (section_ids["题集"], render_problem_index(problem_ids)),
        "知识点": (section_ids["知识点"], render_knowledge_home(category_ids, concept_ids, concept_names, problems_by_concept)),
        "错题与复习": (section_ids["错题与复习"], render_review_home()),
        "面试表达": (section_ids["面试表达"], render_interview_expression_home(problem_ids)),
    }
    for title, (doc_id, markdown) in homepage_payloads.items():
        update_doc(client, doc_id, markdown)
        current = get_block_kramdown(client, doc_id)
        validation_errors.extend(validate_export(current, title))
        if len(current.strip()) < 80:
            validation_errors.append(f"{title}: homepage unexpectedly empty")
        updated.append({"kind": "homepage", "title": title, "id": doc_id})

    audit_hpath = normalize_hpath(root, "Codex 同步日志")
    audit_id = section_ids["Codex 同步日志"]
    existing = export_doc(client, audit_id)
    entry = "\n".join(
        [
            f"## {datetime.now().strftime('%Y-%m-%d %H:%M')} 仓库恢复思源题库",
            "",
            f"- 题目页：{len(PROBLEMS)}",
            f"- 知识点：{len(concept_names)}",
            "- 首页维护：已刷新根首页、题集首页、知识点首页、错题与复习首页、面试表达首页。",
            "- 恢复来源：仓库学习笔记与 Java 题解文件。",
            "- 校验：无 HTML 链接源码、无来源索引、无迁移记录。",
            "",
        ]
    )
    update_doc(client, audit_id, audit_with_intro(get_block_kramdown(client, audit_id), entry))
    exported_audit = get_block_kramdown(client, audit_id)
    if "## 说明" not in exported_audit or "<a href=" in exported_audit:
        validation_errors.append("Codex 同步日志: invalid intro or link source")
    validation_errors.extend(validate_export(exported_audit, "Codex 同步日志"))
    updated.append({"kind": "audit", "title": "Codex 同步日志", "id": audit_id})

    client.data("/api/sqlite/flushTransaction", {})
    if validation_errors:
        raise SiyuanError("Repo repair validation failed: " + "; ".join(validation_errors[:20]))
    removed_obsolete = []
    for parts in OBSOLETE_CONCEPT_HPATHS:
        hpath = normalize_hpath(root, *parts)
        ids = client.data("/api/filetree/getIDsByHPath", {"notebook": notebook, "path": hpath}) or []
        for doc_id in ids:
            client.data("/api/filetree/removeDocByID", {"id": str(doc_id)})
            removed_obsolete.append({"hPath": hpath, "id": str(doc_id)})
    if removed_obsolete:
        client.data("/api/sqlite/flushTransaction", {})
    return {
        "dryRun": False,
        "updated": updated,
        "removedObsoleteConceptPages": removed_obsolete,
        "removedEmptyReviewPages": removed_empty_reviews,
        "homepages": {title: f"siyuan://blocks/{doc_id}" for title, (doc_id, _) in homepage_payloads.items()},
        "auditLog": f"siyuan://blocks/{audit_id}",
        "resolvedUrl": resolved.get("url"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = sync(Path(args.config), dry_run=args.dry_run)
        if args.output:
            result["reportPath"] = str(Path(args.output).resolve())
            Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"Repo repair failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
