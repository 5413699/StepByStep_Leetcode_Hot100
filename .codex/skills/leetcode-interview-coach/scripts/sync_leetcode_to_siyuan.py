#!/usr/bin/env python3
"""Sync a completed LeetCode learning record into the SiYuan interview-training system."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from siyuan_client import (
    DEFAULT_CONFIG,
    SiyuanError,
    ensure_doc,
    get_block_kramdown,
    load_config,
    load_json,
    normalize_hpath,
    open_client_from_config,
    page_link,
    update_doc,
)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


STATE_PATH = Path.home() / ".codex" / "leetcode-hot100-siyuan-state.json"
AUDIT_RETENTION_DAYS = 7

CATEGORY_ORDER = ["数据结构", "解题方法", "解题模式", "常用函数"]

CATEGORY_DESCRIPTIONS = {
    "数据结构": "先判断题目操作的对象是什么，例如树、数组、矩阵、队列、哈希映射或图。",
    "解题方法": "再判断用什么遍历、递归、搜索、前缀和等方法把问题拆开。",
    "解题模式": "沉淀可迁移的题型模式，例如网格搜索、连通块、Flood Fill。",
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

MOJIBAKE_PROBE_TERMS = ["算法", "面试", "手撕", "训练", "添加", "教我", "提交"]


def utf8_as_gbk_mojibake(text: str) -> str:
    return text.encode("utf-8").decode("gbk", errors="ignore")


CORRUPTION_MARKERS = list(
    dict.fromkeys(
        [
            "?",
            "\ufffd",
            "\u951f\u65a4\u62f7",
            "\u00ef\u00bf\u00bd",
            *[utf8_as_gbk_mojibake(term) for term in MOJIBAKE_PROBE_TERMS],
        ]
    )
)
CONTENT_CORRUPTION_MARKERS = [marker for marker in CORRUPTION_MARKERS if marker != "?"]
SIYUAN_INLINE_MARKERS = "\u200b\u200c\u200d\ufeff"
GENERIC_CONCEPT_PHRASES = [
    "高频知识点",
    "需要结合题目特征",
    "题目特征稳定指向该知识点",
    "代码中明确使用该方法或结构",
    "结合具体题型补充模板",
    "只记结论不理解适用条件",
    "模板细节和边界条件容易写错",
]

TAG_ALIASES = {
    "commonFunctions": {
        "Array": "数组Array的常用函数",
        "Arrays": "数组Array的常用函数",
        "array": "数组Array的常用函数",
        "ArrayList": "可变数组的常用函数",
        "List": "可变数组的常用函数",
        "HashMap": "哈希映射hashmap的常用函数",
        "Map": "哈希映射hashmap的常用函数",
        "Queue": "队列Queue的常用函数",
        "LinkedList": "队列Queue的常用函数",
    }
}


CONCEPT_INTROS = {
    "DFS": {
        "intro": "DFS 是一种沿着一个方向尽可能深入搜索的遍历方法，常用于树、图、矩阵连通块、路径枚举等问题。",
        "signals": ["题目要求从一个起点扩展", "要搜索连通区域", "要遍历树或图", "要枚举路径"],
        "pitfalls": ["递归出口写晚导致越界", "忘记 visited 或原地标记", "需要回溯时没有撤销状态"],
        "template": ["private void dfs(...) {", "    if (越界或状态非法) return;", "    标记当前状态;", "    dfs(下一个状态);", "}"],
    },
    "BFS": {
        "intro": "BFS 是按层向外扩展的遍历方法，常用于最短步数、层序遍历和状态扩散问题。",
        "signals": ["题目要求最短路径或最少步数", "需要按层处理", "可以用队列扩展状态"],
        "pitfalls": ["入队时不标记导致重复入队", "层数计数位置错误", "队列为空时仍 poll"],
        "template": ["Queue<Node> queue = new LinkedList<>();", "while (!queue.isEmpty()) {", "    int size = queue.size();", "    // 处理当前层", "}"],
    },
    "多源 BFS": {
        "intro": "多源 BFS 是把多个初始状态同时加入队列，从这些起点同步按层向外扩散，常用于最短时间、状态传播和多起点最短距离问题。",
        "signals": ["题目存在多个初始起点", "每一轮所有起点同时扩散", "要求最少分钟数、最短距离或最早到达时间"],
        "pitfalls": ["只从一个起点开始导致答案偏大", "没有固定当前层 size，导致同一轮和下一轮混在一起", "新增状态入队前没有立即标记，导致重复入队"],
        "template": ["Queue<int[]> queue = new LinkedList<>();", "// 所有初始源点同时入队", "while (!queue.isEmpty()) {", "    int size = queue.size();", "    // 当前层代表同一轮扩散", "}"],
    },
    "动态规划": {
        "intro": "动态规划通过定义状态和状态转移，复用子问题结果解决最优值、计数和可行性问题。",
        "signals": ["存在重叠子问题", "当前结果依赖之前结果", "题目要求最大/最小/方案数"],
        "pitfalls": ["状态定义不清", "初始化错误", "遍历顺序与转移依赖冲突"],
        "template": ["// 1. 定义 dp[i] 的含义", "// 2. 写出状态转移", "// 3. 初始化边界", "for (...) {", "    dp[i] = ...;", "}"],
    },
    "矩阵": {
        "intro": "矩阵题通常需要处理二维坐标、边界、方向数组、原地标记或行列关系。",
        "signals": ["输入是二维数组或网格", "需要上下左右移动", "需要处理行列边界"],
        "pitfalls": ["行列下标写反", "边界判断遗漏", "修改原矩阵前没有确认是否允许"],
        "template": ["int m = grid.length;", "int n = grid[0].length;", "for (int i = 0; i < m; i++) {", "    for (int j = 0; j < n; j++) { ... }", "}"],
    },
    "图论": {
        "intro": "图论题关注节点与边的关系，常见任务包括遍历、连通块、最短路、拓扑序和并查集。",
        "signals": ["元素之间存在连接关系", "题目出现路径、连通、依赖或网络", "矩阵格子可抽象成节点"],
        "pitfalls": ["没有 visited 导致重复访问", "有向/无向关系判断错误", "边界状态没有建模清楚"],
        "template": ["// 明确节点、边、起点和访问状态", "for (Node next : graph[cur]) {", "    if (!visited[next]) { ... }", "}"],
    },
    "Flood Fill": {
        "intro": "Flood Fill 从一个种子位置出发，把同一连通区域全部访问或改色，常见于岛屿、染色和区域填充问题。",
        "signals": ["从一个格子扩散到同类格子", "需要把一整片区域标记掉", "题目强调上下左右相邻"],
        "pitfalls": ["先判断边界再访问 grid", "标记要发生在继续递归前", "字符矩阵要使用 `'1'`、`'0'`"],
        "template": ["if (越界 || grid[i][j] != 目标状态) return;", "grid[i][j] = 已访问状态;", "dfs(i + 1, j);", "dfs(i - 1, j);"],
    },
    "网格搜索": {
        "intro": "网格搜索把二维数组中的格子看成状态，核心是坐标、边界判断和方向数组。",
        "signals": ["输入是二维数组或矩阵", "需要上下左右移动", "要遍历每个格子寻找搜索起点"],
        "pitfalls": ["行列下标写反", "边界条件遗漏 `i < 0` 或 `i >= m`", "原地修改前没有确认题目允许"],
        "template": ["int[][] dirs = {{1,0},{-1,0},{0,1},{0,-1}};", "for (int[] d : dirs) {", "    int ni = i + d[0];", "    int nj = j + d[1];", "}"],
    },
    "连通块": {
        "intro": "连通块表示通过相邻关系连成的一组节点，常见任务是统计块数、面积或判断连通性。",
        "signals": ["发现一个未访问节点就代表一个新区域", "同一块中的节点能通过相邻关系互相到达", "需要整块标记避免重复计数"],
        "pitfalls": ["在块内每个节点都计数导致重复", "visited 标记不完整", "方向关系和题目定义不一致"],
        "template": ["if (发现未访问节点) {", "    count++;", "    dfs/bfs 标记整个连通块;", "}"],
    },
    "二叉树": {
        "intro": "二叉树题通常把问题拆成当前节点、左子树、右子树，用递归或层序遍历组合答案。",
        "signals": ["题目给出 TreeNode", "答案依赖左右子树结果", "可以把整棵树问题缩小到某个子树"],
        "pitfalls": ["空节点返回值和题意不匹配", "递归返回值与全局答案混淆", "路径类题目误把左右两边都返回给父节点"],
        "template": ["if (root == null) return ...;", "left = dfs(root.left);", "right = dfs(root.right);", "// 用当前节点合并左右子树结果"],
    },
    "递归法": {
        "intro": "递归法把大问题拆成同结构的小问题，重点是函数语义、终止条件、参数和返回值。",
        "signals": ["当前问题可以交给子问题先解决", "树、链表、区间天然可递归", "需要从子结构返回信息给父结构"],
        "pitfalls": ["辅助函数参数缺少递归状态", "终止条件不覆盖空结构", "只照抄主函数入参导致表达力不足"],
        "template": ["private Type helper(Node node, State state) {", "    if (node == null) return base;", "    // 处理当前节点并递归子问题", "}"],
    },
    "数组": {
        "intro": "数组题围绕下标、区间、顺序和原地修改展开，常与双指针、二分、滑动窗口配合。",
        "signals": ["输入是 int[] 或顺序列表", "需要按下标遍历、交换或统计", "题目强调有序数组"],
        "pitfalls": ["区间开闭不统一", "空数组和单元素边界遗漏", "修改数组前未确认是否允许"],
        "template": ["for (int i = 0; i < nums.length; i++) {", "    // 明确 i 表示当前位置还是区间边界", "}"],
    },
    "可变数组": {
        "intro": "可变数组通常对应 ArrayList，适合动态收集遍历结果、层结果或不定长答案。",
        "signals": ["返回 List 或 List<List<...>>", "结果数量不固定", "需要按顺序追加答案"],
        "pitfalls": ["复用同一个临时列表导致结果被后续修改", "泛型类型不完整", "每层结果没有单独创建"],
        "template": ["List<Integer> ans = new ArrayList<>();", "ans.add(value);", "return ans;"],
    },
    "哈希映射": {
        "intro": "哈希映射用 key 快速定位 value，适合计数、索引映射、前缀和统计和缓存状态。",
        "signals": ["需要 O(1) 查询是否出现过", "需要记录出现次数或下标", "暴力查找中存在重复扫描"],
        "pitfalls": ["默认值语义错误", "key 类型没有防溢出", "回溯场景离开节点没有撤销计数"],
        "template": ["Map<Key, Integer> map = new HashMap<>();", "map.put(key, map.getOrDefault(key, 0) + 1);", "int count = map.getOrDefault(key, 0);"],
    },
    "队列": {
        "intro": "队列先进先出，常用于 BFS、层序遍历和按到达顺序处理状态。",
        "signals": ["需要按层访问节点", "状态从起点一圈圈扩散", "每次处理最早加入的元素"],
        "pitfalls": ["循环条件写成 queue != null", "层序遍历没有固定当前层 size", "空节点直接入队"],
        "template": ["Queue<Node> queue = new LinkedList<>();", "queue.offer(start);", "Node cur = queue.poll();"],
    },
    "前缀和": {
        "intro": "前缀和把区间和转换成两个前缀状态的差，适合快速统计连续区间、路径前缀或子数组和。",
        "signals": ["题目反复询问一段连续区间的和", "需要统计和为 target 的子数组或路径", "当前状态可由之前累计值推出"],
        "pitfalls": ["忘记初始化前缀和 0", "哈希表记录的是出现次数而不是单个下标", "整数范围可能需要 long"],
        "template": ["long prefix = 0;", "map.put(0L, 1);", "prefix += value;", "ans += map.getOrDefault(prefix - target, 0);"],
    },
    "中序遍历": {
        "intro": "中序遍历按左子树、当前节点、右子树访问二叉树，在二叉搜索树中天然得到升序序列。",
        "signals": ["题目涉及 BST 的有序性", "需要第 k 小、合法性判断或升序输出", "当前节点必须在左子树之后、右子树之前处理"],
        "pitfalls": ["把普通二叉树误当 BST", "递归提前停止时没有共享计数状态", "边界值比较用 int 导致溢出"],
        "template": ["inorder(root.left);", "// 处理 root", "inorder(root.right);"],
    },
    "后序递归": {
        "intro": "后序递归先拿到左右子问题结果，再在当前节点合并，适合树的高度、直径、最大路径和等自底向上的题。",
        "signals": ["当前节点答案依赖左右子树返回值", "需要向父节点返回贡献或状态", "全局答案可能在任意子树内更新"],
        "pitfalls": ["混淆返回给父节点的值和全局答案", "空节点返回值没有和题意对齐", "把左右两边同时返回给父节点形成分叉"],
        "template": ["int left = dfs(root.left);", "int right = dfs(root.right);", "更新当前节点答案;", "return 给父节点的单侧状态;"],
    },
    "最近公共祖先": {
        "intro": "最近公共祖先题的核心是让递归返回“当前子树里找到的目标节点或已确定的祖先”，再根据左右子树返回值合并。",
        "signals": ["题目要求两个节点的最低共同祖先", "节点本身也可以是自己的祖先", "p、q 保证存在于树中"],
        "pitfalls": ["忘记 root == p 或 root == q 时直接返回", "误以为 p 和 q 必须分居左右两侧", "没有理解返回值可能是目标节点也可能是答案"],
        "template": ["if (root == null || root == p || root == q) return root;", "TreeNode left = dfs(root.left);", "TreeNode right = dfs(root.right);", "if (left != null && right != null) return root;"],
    },
    "双指针": {
        "intro": "双指针用两个位置共同维护搜索范围或关系，常用于有序数组、链表快慢指针、原地去重和左右夹逼。",
        "signals": ["需要同时关注区间两端", "数组有序且要找两数关系", "链表需要快慢速度差"],
        "pitfalls": ["指针移动条件不单调", "循环边界 `left < right` 和 `left <= right` 混用", "更新答案后忘记移动指针"],
        "template": ["int left = 0, right = nums.length - 1;", "while (left < right) {", "    if (需要变大) left++; else right--;", "}"],
    },
    "滑动窗口": {
        "intro": "滑动窗口用左右边界维护一个连续区间，右边界扩张收集信息，左边界收缩恢复约束。",
        "signals": ["题目要求连续子数组或子串", "窗口内状态可增量维护", "约束满足后可以移动左边界"],
        "pitfalls": ["窗口条件收缩时机错误", "计数 map 增减不对称", "把非连续问题误套滑动窗口"],
        "template": ["for (int right = 0; right < n; right++) {", "    加入 nums[right];", "    while (窗口不合法) 移出 nums[left++];", "}"],
    },
    "二分查找": {
        "intro": "二分查找利用单调性不断排除一半候选区间，既可查找有序数组，也可在答案空间上搜索最小可行值。",
        "signals": ["搜索范围有序或答案具有单调可行性", "要求 O(log n)", "问最小满足条件或最大满足条件"],
        "pitfalls": ["区间开闭不统一", "mid 计算溢出", "可行性判断方向写反"],
        "template": ["int left = 0, right = n - 1;", "while (left <= right) {", "    int mid = left + (right - left) / 2;", "    // 根据单调性收缩区间", "}"],
    },
    "贪心": {
        "intro": "贪心每一步选择局部最优，并依赖问题结构保证这些局部选择能组成全局最优。",
        "signals": ["题目可按排序后逐步决策", "局部选择不会破坏未来最优性", "可以用交换论证或反证说明正确性"],
        "pitfalls": ["只有直觉没有证明", "排序关键字选错", "局部最优不等于全局最优"],
        "template": ["Arrays.sort(items, comparator);", "for (Item item : items) {", "    if (可以选择) 更新答案;", "}"],
    },
    "回溯": {
        "intro": "回溯是在决策树上尝试选择、递归深入、撤销选择，适合排列组合、子集、棋盘放置和约束搜索。",
        "signals": ["需要枚举所有可行方案", "每一步有多个选择", "选择后需要恢复现场尝试下一种可能"],
        "pitfalls": ["忘记撤销选择", "剪枝条件写错导致漏解", "把路径对象直接加入答案后又被修改"],
        "template": ["path.add(choice);", "backtrack(next);", "path.remove(path.size() - 1);"],
    },
    "字符串": {
        "intro": "字符串题关注字符顺序、子串、匹配和频次状态，常与双指针、滑动窗口、哈希计数配合。",
        "signals": ["输入是 String 或 char[]", "需要处理子串、回文、匹配或字符频次", "答案依赖连续字符区间"],
        "pitfalls": ["charAt 下标越界", "子串边界左闭右开混淆", "Unicode 与普通 ASCII 字符假设不一致"],
        "template": ["for (int i = 0; i < s.length(); i++) {", "    char c = s.charAt(i);", "}"],
    },
    "栈": {
        "intro": "栈后进先出，适合处理最近未匹配元素、括号匹配、单调栈和递归过程的显式模拟。",
        "signals": ["需要和最近的前一个元素配对", "括号或路径需要撤销最近状态", "要维护单调递增或递减结构"],
        "pitfalls": ["空栈时 peek/pop", "入栈的是值还是下标不清楚", "单调栈弹出条件方向写反"],
        "template": ["Deque<Integer> stack = new ArrayDeque<>();", "while (!stack.isEmpty() && 条件) stack.pop();", "stack.push(i);"],
    },
    "链表": {
        "intro": "链表题围绕指针重连和节点身份展开，重点是 dummy 节点、前驱节点和断链顺序。",
        "signals": ["题目给出 ListNode", "需要删除、反转、合并或找环", "不能随机访问，只能沿 next 前进"],
        "pitfalls": ["丢失 next 指针", "返回头节点错误", "没有 dummy 导致头节点特殊处理复杂"],
        "template": ["ListNode dummy = new ListNode(0);", "dummy.next = head;", "ListNode prev = dummy;"],
    },
    "双向链表": {
        "intro": "双向链表让节点能 O(1) 从当前位置摘除或插入到头尾，常与哈希表组合实现 LRU 等缓存结构。",
        "signals": ["需要 O(1) 删除任意已知节点", "需要维护最近/最久顺序", "节点要同时知道前驱和后继"],
        "pitfalls": ["忘记同时更新 prev 和 next", "头尾哨兵节点连接错误", "哈希表与链表节点状态不同步"],
        "template": ["node.prev.next = node.next;", "node.next.prev = node.prev;", "// insert after head"],
    },
    "LRU": {
        "intro": "LRU 缓存用哈希表定位节点，用双向链表维护最近使用顺序，使 get 和 put 都能达到 O(1)。",
        "signals": ["题目要求最近最少使用淘汰", "get/put 都要求 O(1)", "需要同时支持快速查找和顺序更新"],
        "pitfalls": ["访问后忘记移动到最近端", "容量满时没有同时删除链表尾和 map 项", "更新已有 key 时重复创建节点"],
        "template": ["Map<Integer, Node> map = new HashMap<>();", "// get/put 后 moveToHead(node)", "// 超容量 removeTail()"],
    },
    "数组Array的常用函数": {
        "intro": "Java 数组是定长连续容器，面试中常配合 Arrays 工具类完成排序、填充、拷贝和字符串化调试。",
        "signals": ["代码中使用 int[]、char[] 或二维数组", "需要排序、初始化默认值或复制区间", "需要输出数组内容辅助验证"],
        "pitfalls": ["Arrays.copyOfRange 右边界是开区间", "二维数组 fill 不能一次填满所有行", "Arrays.asList 处理基本类型数组会得到单个元素"],
        "template": ["Arrays.sort(nums);", "Arrays.fill(dp, INF);", "int[] part = Arrays.copyOfRange(nums, l, r);"],
    },
    "可变数组的常用函数": {
        "intro": "ArrayList 适合保存数量不固定的结果，常用 add、get、set、remove 和 size 组合构造答案。",
        "signals": ["返回 List", "结果需要动态追加", "需要按下标读取已收集结果"],
        "pitfalls": ["remove(index) 和 remove(Object) 重载混淆", "遍历时删除导致下标跳过", "把临时 list 引用直接放入答案后继续修改"],
        "template": ["List<Integer> list = new ArrayList<>();", "list.add(x);", "int last = list.get(list.size() - 1);"],
    },
    "哈希映射hashmap的常用函数": {
        "intro": "HashMap 通过 key 做平均 O(1) 查找，面试中常用 getOrDefault、put、containsKey 和 remove 维护计数或索引。",
        "signals": ["需要记录频次、下标或映射关系", "暴力查找会重复扫描", "需要快速判断某个状态是否出现过"],
        "pitfalls": ["get 返回 null 时直接拆箱", "计数减到 0 后没有按语义删除", "可变对象作为 key 导致哈希不稳定"],
        "template": ["map.put(key, map.getOrDefault(key, 0) + 1);", "if (map.containsKey(key)) { ... }", "map.remove(key);"],
    },
    "队列Queue的常用函数": {
        "intro": "Queue 接口常用于 BFS，推荐用 offer 入队、poll 出队、peek 查看队头，避免 add/remove 在失败时抛异常。",
        "signals": ["代码需要先进先出处理", "BFS 层序扩展", "状态要按到达顺序处理"],
        "pitfalls": ["poll 可能返回 null", "使用 queue.size() 时没有先固定层大小", "LinkedList 可存 null 但 BFS 队列不应放 null 状态"],
        "template": ["Queue<int[]> queue = new LinkedList<>();", "queue.offer(new int[]{i, j});", "int[] cur = queue.poll();"],
    },
    "Collections的常用函数": {
        "intro": "Collections 提供对 List 等集合的排序、反转、最大最小值和二分查找，适合处理对象集合而不是基本类型数组。",
        "signals": ["数据已经放在 List 中", "需要按自定义规则排序", "需要反转或查找集合中的极值"],
        "pitfalls": ["Collections.binarySearch 要求列表已按同一规则排序", "sort 会原地修改列表", "基本类型数组不能直接使用 Collections.sort"],
        "template": ["Collections.sort(list);", "Collections.reverse(list);", "int idx = Collections.binarySearch(list, target);"],
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


def as_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [as_text(item) for item in value if as_text(item)]
    if isinstance(value, tuple):
        return [as_text(item) for item in value if as_text(item)]
    text = as_text(value)
    return [text] if text else []


def normalize_tag_group(group: str, items: Any) -> list[str]:
    aliases = TAG_ALIASES.get(group, {})
    return unique([aliases.get(item, item) for item in as_list(items)])


def tags(payload: dict[str, Any]) -> dict[str, list[str]]:
    raw = payload.get("tags") or {}
    return {
        "dataStructures": normalize_tag_group("dataStructures", raw.get("dataStructures") or []),
        "methods": normalize_tag_group("methods", raw.get("methods") or []),
        "patterns": normalize_tag_group("patterns", raw.get("patterns") or []),
        "commonFunctions": normalize_tag_group("commonFunctions", raw.get("commonFunctions") or []),
        "readiness": normalize_tag_group("readiness", raw.get("readiness") or []),
    }


def readiness(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("readiness") or {}
    raw.setdefault("status", tags(payload)["readiness"])
    raw.setdefault("skills", [])
    raw.setdefault("weakPoints", [])
    raw.setdefault("interviewExpression", "基本可用")
    raw.setdefault("nextReview", [])
    return raw


def conversation_digest(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("conversationDigest") or {}
    if not isinstance(raw, dict):
        return {}

    misconceptions: list[dict[str, str]] = []
    for item in raw.get("misconceptions") or []:
        if not isinstance(item, dict):
            continue
        before = as_text(item.get("before"))
        after = as_text(item.get("after"))
        if before or after:
            misconceptions.append({"before": before, "after": after})

    concept_updates: list[dict[str, str]] = []
    for item in raw.get("conceptUpdates") or []:
        if not isinstance(item, dict):
            continue
        concept = as_text(item.get("concept"))
        note = as_text(item.get("note"))
        if concept and note:
            concept_updates.append({"concept": concept, "note": note})

    return {
        "firstReaction": as_text(raw.get("firstReaction")),
        "stuckPoints": as_list(raw.get("stuckPoints")),
        "misconceptions": misconceptions,
        "breakthroughs": as_list(raw.get("breakthroughs")),
        "implementationNotes": as_list(raw.get("implementationNotes")),
        "edgeCases": as_list(raw.get("edgeCases")),
        "interviewExpression": as_text(raw.get("interviewExpression")),
        "reviewAdvice": as_list(raw.get("reviewAdvice")),
        "conceptUpdates": concept_updates,
    }


def digest_has_content(digest: dict[str, Any]) -> bool:
    return any(
        [
            as_text(digest.get("firstReaction")),
            digest.get("stuckPoints"),
            digest.get("misconceptions"),
            digest.get("breakthroughs"),
            digest.get("implementationNotes"),
            digest.get("edgeCases"),
            as_text(digest.get("interviewExpression")),
            digest.get("reviewAdvice"),
            digest.get("conceptUpdates"),
        ]
    )


def process_markdown(payload: dict[str, Any], digest: dict[str, Any]) -> str:
    explicit = as_text(payload.get("processMarkdown"))
    lines: list[str] = []
    if explicit:
        lines.append(explicit)
    if digest.get("misconceptions"):
        lines.extend(["", "### 误区纠正", ""])
        for item in digest["misconceptions"]:
            before = item.get("before") or "未记录"
            after = item.get("after") or "未记录"
            lines.append(f"- 原先：{before}")
            lines.append(f"  修正：{after}")
    if digest.get("implementationNotes"):
        lines.extend(["", "### 实现细节", ""])
        lines.extend([f"- {item}" for item in digest["implementationNotes"]])
    if digest.get("edgeCases"):
        lines.extend(["", "### 边界与类型", ""])
        lines.extend([f"- {item}" for item in digest["edgeCases"]])
    return "\n".join(lines).strip()


def concept_update_notes(payload: dict[str, Any], tag_data: dict[str, list[str]] | None = None) -> dict[str, list[str]]:
    allowed: set[str] = set()
    if tag_data:
        for group in ["dataStructures", "methods", "patterns", "commonFunctions"]:
            allowed.update(tag_data.get(group) or [])
    result: dict[str, list[str]] = {}
    for item in conversation_digest(payload).get("conceptUpdates", []):
        concept = item["concept"]
        if allowed and concept not in allowed:
            continue
        result.setdefault(concept, [])
        result[concept].append(item["note"])
    return {key: unique(value) for key, value in result.items()}


def concept_knowledge(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = payload.get("conceptKnowledge") or {}
    result: dict[str, dict[str, Any]] = {}
    if not isinstance(raw, dict):
        return result
    for name, data in raw.items():
        if isinstance(data, dict):
            result[as_text(name)] = data
    return result


def concept_preset(name: str, payload_knowledge: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    if name in CONCEPT_INTROS:
        return CONCEPT_INTROS[name]
    if payload_knowledge and name in payload_knowledge:
        return payload_knowledge[name]
    raise SiyuanError(
        f"缺少知识点 `{name}` 的高质量介绍，已停止创建概念页。"
        "请先基于本地知识库或网络开源资料生成 conceptKnowledge，包含 intro/signals/template/pitfalls/sources。"
    )


def validate_concept_preset(name: str, preset: dict[str, Any], *, require_sources: bool) -> None:
    intro = as_text(preset.get("intro"))
    signals = as_list(preset.get("signals"))
    template = as_list(preset.get("template"))
    pitfalls = as_list(preset.get("pitfalls"))
    sources = preset.get("sources") or []
    joined = "\n".join([intro, *signals, *template, *pitfalls])
    missing = []
    if len(intro) < 24:
        missing.append("intro")
    if len(signals) < 2:
        missing.append("signals")
    if not template:
        missing.append("template")
    if len(pitfalls) < 2:
        missing.append("pitfalls")
    if require_sources and not sources:
        missing.append("sources")
    if missing:
        raise SiyuanError(f"知识点 `{name}` 的 conceptKnowledge 不完整，缺少或过短：{', '.join(missing)}")
    corrupted = [text for text in [intro, *signals, *template, *pitfalls] if is_probably_corrupted_text(text)]
    for item in sources:
        if isinstance(item, dict):
            corrupted.extend(as_text(item.get(key)) for key in ["label", "name", "title", "url", "note"] if is_probably_corrupted_text(as_text(item.get(key))))
        else:
            text = as_text(item)
            if is_probably_corrupted_text(text):
                corrupted.append(text)
    if corrupted:
        raise SiyuanError(f"知识点 `{name}` 的 conceptKnowledge 疑似编码损坏，已拒绝创建：{corrupted[0]!r}")
    generic = [phrase for phrase in GENERIC_CONCEPT_PHRASES if phrase in joined]
    if generic:
        raise SiyuanError(f"知识点 `{name}` 的介绍含套话，已拒绝创建：{', '.join(generic)}")


def is_probably_corrupted_text(text: str) -> bool:
    if not text:
        return False
    if "?" in text:
        return True
    if "????" in text:
        return True
    if "\ufffd" in text:
        return True
    for marker in CORRUPTION_MARKERS:
        if marker and marker != "?" and marker in text:
            return True
    if re.search(r"(?<!\w)\?{2,}(?!\w)", text):
        return True
    return False


def is_probably_corrupted_body(text: str) -> bool:
    if not text:
        return False
    if "????" in text or "\ufffd" in text:
        return True
    for marker in CONTENT_CORRUPTION_MARKERS:
        if marker and marker in text:
            return True
    if re.search(r"(?<!\w)\?{2,}(?!\w)", text):
        return True
    return False


def is_git_ref_text(text: str) -> bool:
    return bool(text) and bool(re.fullmatch(r"[0-9A-Za-z._/\-]+", text))


def sanitized_git(payload: dict[str, Any]) -> dict[str, str]:
    raw = payload.get("git") or {}
    branch = as_text(raw.get("branch"))
    commit = as_text(raw.get("commit"))
    result: dict[str, str] = {}
    if branch and not is_probably_corrupted_text(branch) and is_git_ref_text(branch):
        result["branch"] = branch
    if commit and not is_probably_corrupted_text(commit):
        result["commit"] = commit
    return result


def collect_named_strings(value: Any, path: str = "$") -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in {"problemTitle", "title", "name", "label", "concept", "hPath", "path", "systemRootHPath"}:
                if isinstance(child, str):
                    result.append((child_path, child))
            result.extend(collect_named_strings(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.extend(collect_named_strings(child, f"{path}[{index}]"))
    return result


def collect_payload_strings(value: Any, path: str = "$") -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    if isinstance(value, str):
        result.append((path, value))
    elif isinstance(value, dict):
        for key, child in value.items():
            result.extend(collect_payload_strings(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            result.extend(collect_payload_strings(child, f"{path}[{index}]"))
    return result


def validate_sync_text_inputs(payload: dict[str, Any], root: str, plan: dict[str, Any]) -> None:
    solution_java = as_text(payload.get("solutionJava"))
    if not solution_java:
        raise SiyuanError("同步负载缺少 solutionJava，已停止写入思源，避免生成空的最终题解。")

    candidates: list[tuple[str, str]] = [("wikiPolicy.systemRootHPath", root)]
    candidates.extend(collect_named_strings(payload))
    candidates.extend(collect_named_strings(plan, "plan"))
    bad = [(path, text) for path, text in candidates if is_probably_corrupted_text(text)]
    if bad:
        details = "; ".join(f"{path}={text!r}" for path, text in bad[:12])
        raise SiyuanError(
            "检测到疑似编码损坏的标题、标签或路径，已停止写入思源，避免创建 ??/???? 页面："
            + details
        )
    body_candidates: list[tuple[str, str]] = []
    body_candidates.extend(collect_payload_strings(payload.get("statementMarkdown"), "$.statementMarkdown"))
    body_candidates.extend(collect_payload_strings(payload.get("thinkingMarkdown"), "$.thinkingMarkdown"))
    body_candidates.extend(collect_payload_strings(payload.get("firstReactionMarkdown"), "$.firstReactionMarkdown"))
    body_candidates.extend(collect_payload_strings(payload.get("breakthroughMarkdown"), "$.breakthroughMarkdown"))
    body_candidates.extend(collect_payload_strings(payload.get("interviewExpressionMarkdown"), "$.interviewExpressionMarkdown"))
    body_candidates.extend(collect_payload_strings(payload.get("processMarkdown"), "$.processMarkdown"))
    body_candidates.extend(collect_payload_strings(solution_java, "$.solutionJava"))
    body_candidates.extend(collect_payload_strings(payload.get("complexityMarkdown"), "$.complexityMarkdown"))
    body_candidates.extend(collect_payload_strings(payload.get("pitfalls"), "$.pitfalls"))
    body_candidates.extend(collect_payload_strings(payload.get("readiness"), "$.readiness"))
    body_candidates.extend(collect_payload_strings(payload.get("conversationDigest"), "$.conversationDigest"))
    body_candidates.extend(collect_payload_strings(payload.get("conceptKnowledge"), "$.conceptKnowledge"))
    body_bad = [(path, text) for path, text in body_candidates if is_probably_corrupted_body(text)]
    if body_bad:
        details = "; ".join(f"{path}={text!r}" for path, text in body_bad[:12])
        raise SiyuanError("检测到疑似编码损坏的正文内容，已停止写入思源：" + details)

    rendered_problem = render_problem(payload, {})
    if is_probably_corrupted_body(rendered_problem):
        raise SiyuanError("检测到疑似编码损坏的题目页渲染结果，已停止写入思源。")


def problem_ref(problem_id: str, title: str) -> str:
    return page_link(problem_id, title)


def append_unique_under_heading(markdown: str, heading: str, line: str, *dedupe_keys: str) -> str:
    primary_key = dedupe_keys[0] if dedupe_keys else ""
    secondary_keys = [key for key in dedupe_keys[1:] if key]
    entry = line if line.startswith("- ") else f"- {line}"
    pattern = re.compile(rf"(?ms)(^##\s*{re.escape(heading)}\s*\n)(.*?)(?=^##\s+|\Z)")
    match = pattern.search(markdown)
    if not match:
        if line in markdown or (primary_key and primary_key in markdown):
            return f"## {heading}\n\n{markdown.strip()}\n"
        return markdown.rstrip() + f"\n\n## {heading}\n\n{entry}\n"
    body = match.group(2).rstrip()
    if line in body or (primary_key and primary_key in body):
        return markdown
    for key in secondary_keys:
        if key not in body:
            continue
        lines = body.splitlines()
        for index, existing_line in enumerate(lines):
            if key in existing_line and (not primary_key or primary_key not in existing_line):
                lines[index] = entry
                replacement = match.group(1) + "\n".join(lines).rstrip() + "\n"
                return markdown[: match.start()] + replacement + markdown[match.end() :]
    replacement = match.group(1) + (body + "\n" if body else "\n") + entry + "\n"
    return markdown[: match.start()] + replacement + markdown[match.end() :]


def strip_block_markdown(markdown: str) -> str:
    text = re.sub(r"(?ms)(?:\A|\n)---\s*\n.*?\n---\s*(?=\n|\Z)", "\n", markdown.strip())
    text = re.sub(r"(?m)^(title|date|lastmod):\s*.*$", "", text)
    text = re.sub(r"\{:\s+[^}]*\}", "", text)
    text = re.sub(r"(?m)^#\s+.+$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def own_doc_markdown(client: Any, doc_id: str) -> str:
    return strip_block_markdown(get_block_kramdown(client, doc_id))


def doc_blocks_markdown(client: Any, doc_id: str) -> str:
    escaped_id = doc_id.replace("'", "''")
    rows = client.data(
        "/api/query/sql",
        {
            "stmt": (
                "select markdown, content from blocks "
                f"where root_id='{escaped_id}' "
                "order by created, sort, id"
            )
        },
    ) or []
    parts: list[str] = []
    for row in rows:
        text = as_text(row.get("markdown")) or as_text(row.get("content"))
        if text:
            parts.append(text)
    return strip_block_markdown("\n".join(parts))


def solution_required_lines(solution_java: str) -> list[str]:
    lines = [line.strip() for line in solution_java.splitlines()]
    candidates = [
        line
        for line in lines
        if line
        and not line.startswith("//")
        and (
            re.search(r"\b(public|private|protected)\b", line)
            or "return " in line
            or "new " in line
            or "visited" in line
            or "dirs" in line
        )
    ]
    return unique(candidates[:4])


def clean_linked_page_markdown(markdown: str) -> str:
    has_export_pollution = bool(
        re.search(r"(?m)^(title|date|lastmod):\s*", markdown)
        or re.search(r"\[\^\d+\]", markdown)
        or re.search(r"(?ms)(?:^|\n)\[\^\d+\]:\s*#\s+", markdown)
    )
    text = re.sub(r"(?m)^(title|date|lastmod):\s*.*$", "", markdown)
    text = re.sub(r"(?ms)(?:^|\n)\[\^\d+\]:\s*#\s+.*?(?=\n##\s+|\Z)", "\n", text)
    text = re.sub(r"\[\^\d+\]", "", text)
    if has_export_pollution:
        first_problem_heading = re.search(
            r"(?m)^##\s+(知识链接|题干|第一反应|卡壳点|关键突破|思考过程|面试版思路|最终题解|复杂度|易错点|面试表达|掌握状态|复习建议|同步记录)\s*$",
            text,
        )
        if first_problem_heading:
            text = text[: first_problem_heading.start()].rstrip() + "\n"
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def retain_recent_audit_entries(markdown: str, now: datetime) -> str:
    body = re.sub(r"(?ms)^##\s*说明\s*\n.*?(?=^##\s+|\Z)", "", markdown).strip()
    entries: list[tuple[datetime, str]] = []
    for match in re.finditer(r"(?ms)^##\s*(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}).*?\n.*?(?=^##\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}|\Z)", body):
        stamp = datetime.strptime(match.group(1) + " " + match.group(2), "%Y-%m-%d %H:%M")
        if stamp >= now - timedelta(days=AUDIT_RETENTION_DAYS):
            entries.append((stamp, match.group(0).strip()))
    entries.sort(key=lambda item: item[0], reverse=True)
    return "\n\n".join(entry for _, entry in entries)


def audit_with_intro(existing: str, entry: str) -> str:
    intro = "## 说明\n\n这里记录 Codex 对面试训练系统进行的同步、收尾、修复和验证操作，供用户审阅。"
    retained = retain_recent_audit_entries(existing, datetime.now())
    return intro + "\n\n" + entry.strip() + ("\n\n" + retained if retained else "") + "\n"


def ensure_heading(markdown: str, heading: str, intro: str = "") -> str:
    if re.search(rf"(?m)^##\s*{re.escape(heading)}\s*$", markdown):
        return markdown
    body = markdown.rstrip()
    addition = f"## {heading}\n\n{intro.strip()}\n" if intro.strip() else f"## {heading}\n"
    return (body + "\n\n" + addition if body else addition).strip() + "\n"


def append_unique_problem_link(markdown: str, problem_id: str, title: str) -> str:
    return append_unique_under_heading(markdown, "题集", f"- {problem_ref(problem_id, title)}", problem_id, title)


def append_unique_concept_link(markdown: str, concept_id: str, name: str) -> str:
    return append_unique_under_heading(markdown, "知识点", f"- {page_link(concept_id, name)}", concept_id, name)


def append_unique_learning_note(markdown: str, problem_id: str, title: str, note: str) -> str:
    markdown = markdown.replace("- 暂无自动补充。\n", "").replace("- 暂无自动补充。", "")
    line = f"- {problem_ref(problem_id, title)}：{note}"
    return append_unique_under_heading(markdown, "来自题目的理解", line, note)


def coach_memory_notes(payload: dict[str, Any], tag_data: dict[str, list[str]] | None = None) -> dict[str, list[str]]:
    allowed: set[str] = set()
    if tag_data:
        for group in ["dataStructures", "methods", "patterns", "commonFunctions"]:
            allowed.update(tag_data.get(group) or [])
    digest = conversation_digest(payload)
    result: dict[str, list[str]] = {}
    for item in digest.get("conceptUpdates", []):
        concept = item["concept"]
        if allowed and concept not in allowed:
            continue
        note = as_text(item.get("note"))
        if note:
            result.setdefault(concept, []).append(note)
    for concept in allowed:
        for item in as_list(digest.get("reviewAdvice"))[:2]:
            if concept in item:
                result.setdefault(concept, []).append(item)
    return {key: unique(value)[:3] for key, value in result.items()}


def append_unique_coach_memory(markdown: str, problem_id: str, title: str, note: str, *, limit: int = 20) -> str:
    markdown = markdown.replace("- 暂无自动补充。\n", "").replace("- 暂无自动补充。", "")
    line = f"- {problem_ref(problem_id, title)}：{note}"
    updated = append_unique_under_heading(markdown, "教练摘要", line, note)
    pattern = re.compile(r"(?ms)^(##\s+教练摘要\s*\n)(.*?)(?=^##\s+|\Z)")
    match = pattern.search(updated)
    if not match:
        return updated
    header = match.group(1)
    body = match.group(2)
    bullets = []
    seen = set()
    for raw in body.splitlines():
        text = raw.strip()
        if not text.startswith("- "):
            continue
        key = text
        if key in seen:
            continue
        seen.add(key)
        bullets.append(text)
    trimmed = "\n".join(bullets[:limit]).strip()
    replacement = header + ("\n" + trimmed + "\n\n" if trimmed else "\n")
    return updated[: match.start()] + replacement + updated[match.end() :]


def concept_markdown(name: str, category: str, problem_id: str, title: str, preset: dict[str, Any]) -> str:
    intro = as_text(preset.get("intro"))
    signals = as_list(preset.get("signals"))
    pitfalls = as_list(preset.get("pitfalls"))
    template_lines = as_list(preset.get("template"))
    sources = []
    for item in preset.get("sources") or []:
        if isinstance(item, dict):
            label = as_text(item.get("label") or item.get("name") or item.get("title"))
            url = as_text(item.get("url"))
            note = as_text(item.get("note"))
            display = label or url or note
            if display:
                sources.append(f"- {display}" + (f"：{note}" if note and note != display else "") + (f" ({url})" if url and url != display else ""))
        else:
            text = as_text(item)
            if text:
                sources.append(f"- {text}")
    lines = [
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
        *template_lines,
        "```",
        "",
        "## 高频易错点",
        "",
        *[f"- {item}" for item in pitfalls],
        "",
        "## 来源依据",
        "",
        *(sources or ["- 本地 LeetCode Hot100 知识库"]),
        "",
        "## 题集",
        "",
        f"- {problem_ref(problem_id, title)}",
        "",
        "## 来自题目的理解",
        "",
        "## 教练摘要",
        "",
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
            "## 说明",
            "",
            descriptions.get(label, "该复习标签用于跟踪需要再次巩固的题目。"),
            "",
            "## 题集",
            "",
            f"- {problem_ref(problem_id, title)}",
        ]
    ).strip() + "\n"


def update_homepages(
    client: Any,
    notebook: str,
    root: str,
    *,
    problem_id: str,
    title: str,
    concept_results: list[dict[str, Any]],
    category_results: dict[str, dict[str, Any]],
    review_results: list[dict[str, Any]],
    audit_id: str,
) -> dict[str, Any]:
    section_ids: dict[str, str] = {}
    for name in ["题集", "知识点", "错题与复习", "面试表达", "Codex 同步日志"]:
        sid, _ = ensure_doc(client, notebook, normalize_hpath(root, name), "")
        section_ids[name] = sid
    root_id, _ = ensure_doc(client, notebook, normalize_hpath(root), "")

    root_md = clean_linked_page_markdown(own_doc_markdown(client, root_id))
    if not root_md:
        root_md = "\n".join(
            [
                "## 今日入口",
                "",
                f"- {page_link(section_ids['题集'], '题集')}：按题号复习已经整理过的 Hot100 题目。",
                f"- {page_link(section_ids['知识点'], '知识点')}：按数据结构、方法、模式、常用函数复习。",
                f"- {page_link(section_ids['错题与复习'], '错题与复习')}：按掌握状态安排二刷和表达训练。",
                f"- {page_link(section_ids['面试表达'], '面试表达')}：沉淀面试中可直接说出口的解题表达。",
                f"- {page_link(audit_id, 'Codex 同步日志')}：审阅自动同步、修复和迁移记录。",
            ]
        )
    root_md = ensure_heading(root_md, "最近同步")
    root_md = append_unique_under_heading(root_md, "最近同步", f"- {problem_ref(problem_id, title)}：{datetime.now().strftime('%Y-%m-%d %H:%M')} 同步", problem_id, title)
    update_doc(client, root_id, root_md)

    problem_index = clean_linked_page_markdown(own_doc_markdown(client, section_ids["题集"]))
    if not problem_index:
        problem_index = "## 题目列表\n\n这里按题号汇总已完成整理的题目页。"
    problem_index = append_unique_under_heading(problem_index, "题目列表", f"- {problem_ref(problem_id, title)}", problem_id, title)
    update_doc(client, section_ids["题集"], problem_index)

    knowledge_home = clean_linked_page_markdown(own_doc_markdown(client, section_ids["知识点"]))
    if not knowledge_home:
        lines = ["## 分类入口", ""]
        for category in CATEGORY_ORDER:
            category_item = category_results.get(category)
            if category_item:
                lines.append(f"- {page_link(category_item['id'], category)}：{CATEGORY_DESCRIPTIONS[category]}")
            else:
                lines.append(f"- {category}：{CATEGORY_DESCRIPTIONS[category]}")
        knowledge_home = "\n".join(lines)
    knowledge_home = ensure_heading(knowledge_home, "分类入口")
    for category in CATEGORY_ORDER:
        category_item = category_results.get(category)
        if category_item:
            line = f"- {page_link(category_item['id'], category)}：{CATEGORY_DESCRIPTIONS[category]}"
            knowledge_home = append_unique_under_heading(knowledge_home, "分类入口", line, category_item["id"], category)
        else:
            knowledge_home = append_unique_under_heading(knowledge_home, "分类入口", f"- {category}：{CATEGORY_DESCRIPTIONS[category]}", "", category)
    knowledge_home = ensure_heading(knowledge_home, "最近关联知识点")
    for item in concept_results:
        knowledge_home = append_unique_under_heading(knowledge_home, "最近关联知识点", f"- {page_link(item['id'], item['name'])}：来自 {problem_ref(problem_id, title)}", item["id"], item["name"])
    update_doc(client, section_ids["知识点"], knowledge_home)

    review_home = clean_linked_page_markdown(own_doc_markdown(client, section_ids["错题与复习"]))
    if not review_home:
        review_home = "\n".join(
            [
                "## 复习原则",
                "",
                "这里仅保留需要复盘的真实题目入口。没有题目归档时，不自动堆叠空标签页。",
                "",
                "## 当前复习入口",
                "",
                "- 暂无自动归档题目。完成题目收尾后，只有带复习标签的题目会出现在这里。",
            ]
        )
    if review_results:
        review_home = review_home.replace("- 暂无自动归档题目。完成题目收尾后，只有带复习标签的题目会出现在这里。", "").strip()
        review_home = ensure_heading(review_home, "最近归档")
        for item in review_results:
            line = f"- {page_link(item['id'], item['label'])}：{problem_ref(problem_id, title)}"
            review_home = append_unique_under_heading(review_home, "最近归档", line, line)
    update_doc(client, section_ids["错题与复习"], review_home)

    expression_home = clean_linked_page_markdown(own_doc_markdown(client, section_ids["面试表达"]))
    if not expression_home:
        expression_home = "\n".join(
            [
                "## 思路表达模板",
                "",
                "- 先说明题型识别信号。",
                "- 再说明核心状态、辅助函数或遍历结构。",
                "- 然后说明为什么这样更新答案，以及复杂度。",
                "",
                "## 复杂度表达",
                "",
                "- 时间复杂度先看每个节点、格子或元素被访问几次。",
                "- 空间复杂度区分辅助结构和递归栈。",
            ]
        )
    expression_home = ensure_heading(expression_home, "最近可练表达题")
    expression_home = append_unique_under_heading(expression_home, "最近可练表达题", f"- {problem_ref(problem_id, title)}", problem_id, title)
    update_doc(client, section_ids["面试表达"], expression_home)

    client.data("/api/sqlite/flushTransaction", {})
    return {
        "root": {"id": root_id, "url": f"siyuan://blocks/{root_id}"},
        "sections": {name: {"id": sid, "url": f"siyuan://blocks/{sid}"} for name, sid in section_ids.items()},
    }


def render_problem(payload: dict[str, Any], concept_refs: dict[str, str]) -> str:
    title = payload["problemTitle"]
    git = sanitized_git(payload)
    ready = readiness(payload)
    status = as_list(ready.get("status"))
    digest = conversation_digest(payload)
    weak_points = unique(as_list(ready.get("weakPoints")) + as_list(digest.get("stuckPoints")))
    next_review = unique(as_list(ready.get("nextReview")) + as_list(digest.get("reviewAdvice")))
    tag_data = tags(payload)
    concept_line = "、".join(concept_refs.values()) or "未标注"
    first_reaction = as_text(payload.get("firstReactionMarkdown")) or as_text(digest.get("firstReaction")) or "（未记录）"
    breakthrough_items = as_list(payload.get("breakthroughMarkdown")) + as_list(digest.get("breakthroughs"))
    breakthrough = "\n".join([f"- {item}" for item in unique(breakthrough_items)]) if breakthrough_items else "（未记录）"
    interview_expression = (
        as_text(payload.get("interviewExpressionMarkdown"))
        or as_text(digest.get("interviewExpression"))
        or as_text(payload.get("thinkingMarkdown"))
    )
    process = process_markdown(payload, digest)
    pitfall_items = unique(
        as_list(payload.get("pitfalls"))
        + as_list(digest.get("implementationNotes"))
        + as_list(digest.get("edgeCases"))
    )

    lines = [
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
            "## 思考过程",
            "",
            process or "（未记录）",
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
    lines.extend([f"- {pitfall}" for pitfall in pitfall_items] or ["- （未记录）"])
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
    for name in tag_data["commonFunctions"]:
        result.append(("常用函数", name, normalize_hpath(root, "知识点", "常用函数", name)))
    return result


def load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        return load_json(STATE_PATH)
    return {}


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def comparable_markdown(text: str) -> str:
    text = text or ""
    text = re.sub(f"[{SIYUAN_INLINE_MARKERS}]", "", text)
    text = re.sub(r"\(\([0-9a-z-]+\s+\"([^\"]+)\"\)\)", r"\1", text)
    text = re.sub(r"\{:\s+[^}]*\}", "", text)
    text = re.sub(r"[`*_~]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def validate_page(content: str, required: list[str], title: str) -> list[str]:
    errors: list[str] = []
    comparable_content = comparable_markdown(content)
    if re.search(r"(?m)^(title|date|lastmod):\s*", content):
        errors.append(f"{title}: contains leaked frontmatter metadata")
    if re.search(r"\[\^\d+\]", content):
        errors.append(f"{title}: contains exported footnote reference")
    if "????" in content:
        errors.append(f"{title}: contains ????")
    if "\ufffd" in content:
        errors.append(f"{title}: contains replacement character")
    for marker in CONTENT_CORRUPTION_MARKERS:
        if marker in content:
            errors.append(f"{title}: contains mojibake marker {marker}")
    if "<!-- codex-" in content:
        errors.append(f"{title}: contains visible codex marker")
    if title.startswith("concept:"):
        generic = [phrase for phrase in GENERIC_CONCEPT_PHRASES if phrase in content]
        if generic:
            errors.append(f"{title}: contains generic concept filler {', '.join(generic)}")
    for marker in ["<a href=", "## 来源索引", "## 迁移记录", "## 旧笔记内容", "## 迁移补充", "## 旧笔记重组补充"]:
        if marker in content:
            errors.append(f"{title}: contains forbidden marker {marker}")
    for item in required:
        if item and comparable_markdown(item) not in comparable_content:
            errors.append(f"{title}: missing {item}")
    return errors


def sync(payload_path: Path, config_path: Path, *, dry_run: bool = False) -> dict[str, Any]:
    config = load_config(config_path)
    if not (config.get("siyuan") or {}).get("enabled", False):
        return {"enabled": False, "message": "SiYuan sync is disabled."}

    payload = load_json(payload_path)
    root = (config.get("wikiPolicy") or {}).get("systemRootHPath", "/算法题/面试手撕训练系统")
    tag_data = tags(payload)
    payload_knowledge = concept_knowledge(payload)
    ready = readiness(payload)
    title = payload["problemTitle"]
    problem_hpath = normalize_hpath(root, "题集", title)
    concept_targets = category_paths(root, tag_data)
    if not concept_targets:
        raise SiyuanError("缺少可写入的知识点标签，已停止同步。请先根据 tag-rules.md 生成带 evidence 的 tags。")
    for _, name, _ in concept_targets:
        preset = concept_preset(name, payload_knowledge)
        validate_concept_preset(name, preset, require_sources=name not in CONCEPT_INTROS)
    review_targets = [(label, normalize_hpath(root, "错题与复习", label)) for label in as_list(ready.get("status"))]
    audit_hpath = normalize_hpath(root, "Codex 同步日志")
    digest = conversation_digest(payload)

    plan = {
        "dryRun": dry_run,
        "problem": problem_hpath,
        "concepts": [{"category": cat, "name": name, "hPath": hpath} for cat, name, hpath in concept_targets],
        "reviews": [{"label": label, "hPath": hpath} for label, hpath in review_targets],
        "auditLog": audit_hpath,
        "conversationDigest": "included" if digest_has_content(digest) else "missing",
    }
    validate_sync_text_inputs(payload, root, plan)
    if dry_run:
        return plan

    client, resolved = open_client_from_config(config, config_path=config_path, update_config=True)
    notebook = resolved.get("notebookId")
    if not notebook:
        raise SiyuanError("配置缺少 notebookId，请运行 configure_workflow.py。")

    problem_id, problem_created = ensure_doc(client, notebook, problem_hpath, "")
    concept_refs: dict[str, str] = {}
    learning_notes = concept_update_notes(payload, tag_data)
    coach_notes = coach_memory_notes(payload, tag_data)
    concept_results = []
    category_results: dict[str, dict[str, Any]] = {}
    for category, name, hpath in concept_targets:
        preset = concept_preset(name, payload_knowledge)
        initial_concept = concept_markdown(name, category, problem_id, title, preset)
        cid, created = ensure_doc(client, notebook, hpath, initial_concept)
        concept_refs[name] = page_link(cid, name)
        existing = initial_concept if created else clean_linked_page_markdown(own_doc_markdown(client, cid))
        updated = append_unique_problem_link(existing, problem_id, title)
        for note in learning_notes.get(name, []):
            updated = append_unique_learning_note(updated, problem_id, title, note)
        for note in coach_notes.get(name, []):
            updated = append_unique_coach_memory(updated, problem_id, title, note)
        if updated != existing:
            update_doc(client, cid, updated)
        concept_results.append({"name": name, "category": category, "id": cid, "url": f"siyuan://blocks/{cid}", "created": created})
        category_hpath = normalize_hpath(root, "知识点", category)
        category_id, category_created = ensure_doc(client, notebook, category_hpath, f"# {category}\n\n## 知识点\n")
        existing_category = clean_linked_page_markdown(own_doc_markdown(client, category_id))
        updated_category = append_unique_concept_link(existing_category, cid, name)
        if updated_category != existing_category:
            update_doc(client, category_id, updated_category)
        category_results[category] = {
            "category": category,
            "id": category_id,
            "hPath": category_hpath,
            "url": f"siyuan://blocks/{category_id}",
            "created": category_created,
        }

    problem_markdown = render_problem(payload, concept_refs)
    update_doc(client, problem_id, problem_markdown)

    review_results = []
    for label, hpath in review_targets:
        rid, created = ensure_doc(client, notebook, hpath, review_markdown(label, problem_id, title))
        if not created:
            existing = clean_linked_page_markdown(own_doc_markdown(client, rid))
            updated = append_unique_problem_link(existing, problem_id, title)
            if updated != existing:
                update_doc(client, rid, updated)
        review_results.append({"label": label, "id": rid, "url": f"siyuan://blocks/{rid}", "created": created})

    audit_id, audit_created = ensure_doc(client, notebook, audit_hpath, "# Codex 同步日志\n")
    git = sanitized_git(payload)
    audit_entry = "\n".join(
        [
            f"## {datetime.now().strftime('%Y-%m-%d %H:%M')} {title}",
            "",
            f"- 题目页：{page_link(problem_id, title)}",
            f"- Git：{git.get('branch', '未提供')} / {git.get('commit', '未提供')}",
            f"- 知识点：{'、'.join(item['name'] for item in concept_results) or '无'}",
            f"- 掌握状态：{'、'.join(label for label, _ in review_targets) or '未评估'}",
            f"- 当前题目对话摘要：{'已写入' if digest_has_content(digest) else '未提供'}",
            "- 校验：待导出校验",
            "",
        ]
    )
    existing_audit = clean_linked_page_markdown(own_doc_markdown(client, audit_id))
    update_doc(client, audit_id, audit_with_intro(existing_audit, audit_entry))

    homepage_results = update_homepages(
        client,
        notebook,
        root,
        problem_id=problem_id,
        title=title,
        concept_results=concept_results,
        category_results=category_results,
        review_results=review_results,
        audit_id=audit_id,
    )

    client.data("/api/sqlite/flushTransaction", {})

    validation_errors: list[str] = []
    problem_content = own_doc_markdown(client, problem_id)
    problem_blocks_content = doc_blocks_markdown(client, problem_id)
    digest_required: list[str] = []
    if digest_has_content(digest):
        digest_required.extend(["第一反应", "卡壳点", "关键突破", "面试表达", "复习建议"])
    validation_errors.extend(
        validate_page(
            problem_blocks_content or problem_content,
            ["面试版思路", "最终题解", "掌握状态", sanitized_git(payload).get("commit", "")] + digest_required,
            "problem",
        )
    )
    solution_lines = solution_required_lines(as_text(payload.get("solutionJava")))
    if not solution_lines:
        validation_errors.append("problem: solutionJava has no verifiable code lines")
    else:
        validation_errors.extend(validate_page(problem_blocks_content, solution_lines, "problem:solution"))
    for item in concept_results:
        content = own_doc_markdown(client, item["id"])
        required = [title] + learning_notes.get(item["name"], []) + coach_notes.get(item["name"], [])
        validation_errors.extend(validate_page(content, required, f"concept:{item['name']}"))
    for item in category_results.values():
        content = own_doc_markdown(client, item["id"])
        concept_names = [concept["name"] for concept in concept_results if concept["category"] == item["category"]]
        validation_errors.extend(validate_page(content, ["## 知识点"] + concept_names, f"category:{item['category']}"))
    for item in review_results:
        content = own_doc_markdown(client, item["id"])
        validation_errors.extend(validate_page(content, [title], f"review:{item['label']}"))
    for name, item in homepage_results["sections"].items():
        if name == "Codex 同步日志":
            continue
        content = own_doc_markdown(client, item["id"])
        required: list[str] = []
        if name == "题集":
            required = [title]
        elif name == "知识点":
            required = unique(CATEGORY_ORDER + [item["name"] for item in concept_results])
        elif name in {"错题与复习", "面试表达"}:
            required = [title]
        validation_errors.extend(validate_page(content, required, f"homepage:{name}"))
        if len(content.strip()) < 40:
            validation_errors.append(f"homepage:{name}: unexpectedly empty")
    root_home = own_doc_markdown(client, homepage_results["root"]["id"])
    validation_errors.extend(validate_page(root_home, [title], "homepage:root"))
    if len(root_home.strip()) < 40:
        validation_errors.append("homepage:root: unexpectedly empty")
    if validation_errors:
        raise SiyuanError("SiYuan validation failed: " + "; ".join(validation_errors))

    state = load_state()
    state[title] = {
        "problemBlockId": problem_id,
        "conceptBlockIds": {item["name"]: item["id"] for item in concept_results},
        "reviewBlockIds": {item["label"]: item["id"] for item in review_results},
        "lastCommit": sanitized_git(payload).get("commit", ""),
        "lastSyncAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    save_state(state)

    client.push_message(f"LeetCode 面试训练笔记已同步：{title}")
    return {
        "enabled": True,
        "problem": {"title": title, "id": problem_id, "hPath": problem_hpath, "url": f"siyuan://blocks/{problem_id}", "created": problem_created},
        "concepts": concept_results,
        "categories": list(category_results.values()),
        "reviews": review_results,
        "homepages": homepage_results,
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
