# Tag Rules

Use these rules to generate the tag plan consumed by SiYuan sync. This module is independent and may be reused by other skills.

## Output Shape

```json
{
  "problemTitle": "M200-岛屿数量",
  "tags": {
    "dataStructures": ["矩阵", "图论"],
    "methods": ["DFS", "BFS", "连通块"],
    "patterns": ["网格搜索", "Flood Fill"]
  },
  "tagEvidence": {
    "图论": "每个陆地格子可视为节点，上下左右相邻表示边"
  },
  "suggestedTags": []
}
```

Only write tags with clear evidence. Put low-confidence tags in `suggestedTags`.

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

## Evidence Rules

Each written tag needs one concrete reason:

- From problem statement.
- From method signature.
- From final code.
- From the user's stated thinking.

Do not tag both DFS and BFS unless both are taught, implemented, or explicitly discussed.
