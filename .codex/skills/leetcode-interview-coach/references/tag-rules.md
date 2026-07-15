# Tag Rules

Use these rules to generate the tag plan consumed by SiYuan sync. This module is independent and may be reused by other skills.

## Output Shape

```json
{
  "problemTitle": "M200-岛屿数量",
  "tags": {
    "dataStructures": ["矩阵", "图论"],
    "methods": ["DFS"],
    "patterns": ["网格搜索", "连通块", "Flood Fill"],
    "commonFunctions": [],
    "readiness": ["提示后完成", "需要二刷"]
  },
  "tagEvidence": {
    "图论": "每个陆地格子可视为节点，上下左右相邻表示边"
  },
  "conceptKnowledge": {},
  "suggestedTags": []
}
```

Only write tags with clear evidence. Put low-confidence tags in `suggestedTags`. Do not tag both DFS and BFS unless both are taught, implemented, or explicitly discussed.

Before a confirmed tag can create a new SiYuan concept page, it must have concrete concept knowledge. If the local knowledge map does not support the tag, generate `conceptKnowledge` using `concept-knowledge-flow.md`; do not rely on generic category prose.

## Primary Data Structure

- `src/notes/.../矩阵` or `com.czf.matrix`: `矩阵`
- binary tree statement or `TreeNode`: `二叉树`
- linked list statement or `ListNode`: `链表`
- array/list statement or `int[]`: `数组`
- string sliding window: `字符串`
- map/set counting or lookup: `哈希映射`
- stack monotonic or parentheses: `栈`
- queue level-order or BFS: `队列`
- graph nodes/edges or connected components: `图论`

## Method Tags

- recursive tree traversal: `递归法`
- postorder return value from child to parent: `后序递归`
- breadth-first traversal or `Queue`: `BFS`
- depth-first traversal or recursive flood fill: `DFS`
- prefix sum plus map: `前缀和`
- two pointers or fast/slow: `双指针`
- sliding window: `滑动窗口`
- binary search on answer or sorted range: `二分查找`
- dynamic programming state transition: `动态规划`
- greedy local choice: `贪心`
- backtracking choose/unchoose: `回溯`

## Pattern Tags

- grid four-direction traversal: `网格搜索`
- island/region/connected land: `连通块`, `Flood Fill`
- BST inorder property: `中序遍历`
- tree lowest common ancestor: `最近公共祖先`
- LRU with hash map and doubly linked list: `双向链表`, `LRU`

## Common Function Tags

Use `commonFunctions` only when the user's notes or solution explicitly emphasize reusable Java API usage, for example:

- `数组Array的常用函数`
- `字符串String的常用函数`
- `可变数组的常用函数`
- `哈希映射hashmap的常用函数`
- `栈Stack的常用函数`
- `队列Queue的常用函数`
- `Collections的常用函数`
- `随机数Random的常用函数`

Normalize aliases before writing to SiYuan:

- `Array`, `Arrays` -> `数组Array的常用函数`
- `String`, `new String(char[])`, `char[] -> String` -> `字符串String的常用函数`
- `ArrayList`, `List` -> `可变数组的常用函数`
- `HashMap`, `Map` -> `哈希映射hashmap的常用函数`
- `Stack` -> `栈Stack的常用函数`
- `Queue`, `LinkedList` when used as a queue -> `队列Queue的常用函数`
- `Random`, `Random.nextInt` -> `随机数Random的常用函数`

## Evidence Rules

Each written tag needs one concrete reason:

- From problem statement.
- From method signature.
- From final code.
- From the user's stated thinking.
- From the observed coaching process for readiness tags.

Conversation digest `conceptUpdates` may update concept pages only when the concept is already present in a written tag group or has clear evidence in `tagEvidence`. Low-confidence concepts should be placed in `suggestedTags` and should not be written into SiYuan concept pages.

## Readiness Tags

- No initial idea: `一刷卡壳`
- Solved after hints: `提示后完成`
- Solved without hints: `独立完成`
- Boundary or implementation bug: `代码有 bug`
- Correct but verbose explanation: `面试表达不熟`
- Important pattern or repeated confusion: `需要二刷`
