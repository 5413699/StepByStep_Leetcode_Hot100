# Concept Knowledge Flow

Use this module when a tag would create or refresh a SiYuan concept page.

## Goal

Never create a concept page from generic filler. A concept page must teach the learner when to recognize the concept, what code shape to write, and what mistakes to avoid.

## Sources

Use sources in this order:

1. Existing local concept knowledge in `scripts/sync_leetcode_to_siyuan.py`.
2. Existing repository notes from solved problems.
3. Web search over reputable open learning references when local knowledge is missing. Prefer:
   - OI Wiki
   - cp-algorithms
   - official Java documentation for Java API/function pages
   - well-maintained open algorithm notes or textbook-style references
4. The current problem statement, final code, and coaching digest as task-specific evidence.

Do not use low-signal content farms or generic SEO pages when better references exist.

## Required Payload For New Concepts

If a concept name is not already supported by the local knowledge map, add `conceptKnowledge` to the SiYuan sync payload:

```json
{
  "conceptKnowledge": {
    "拓扑排序": {
      "intro": "用一句具体说明解释它解决什么问题。",
      "signals": [
        "题目中存在依赖关系或先后顺序约束",
        "需要判断是否能完成全部任务或给出合法顺序"
      ],
      "template": [
        "Queue<Integer> queue = new LinkedList<>();",
        "while (!queue.isEmpty()) { ... }"
      ],
      "pitfalls": [
        "入度减到 0 时才入队",
        "有环时无法得到完整拓扑序"
      ],
      "sources": [
        {"label": "OI Wiki 拓扑排序", "url": "https://oi-wiki.org/graph/topo/", "note": "用于确认概念定义和典型代码结构"}
      ]
    }
  }
}
```

## Quality Bar

Each concept must include:

- `intro`: specific explanation, not a category slogan.
- `signals`: at least two recognition signals tied to problem wording or code structure.
- `template`: concrete code skeleton or API usage, not `// 结合具体题型补充模板`.
- `pitfalls`: at least two realistic mistakes.
- `sources`: required for any concept not already in the local knowledge map.

Rejected phrases include:

- `高频知识点`
- `需要结合题目特征`
- `题目特征稳定指向该知识点`
- `代码中明确使用该方法或结构`
- `结合具体题型补充模板`
- `只记结论不理解适用条件`
- `模板细节和边界条件容易写错`

## Failure Policy

If local knowledge is missing and web/search evidence is unavailable, stop the SiYuan sync and report the missing concept. Do not create a placeholder page that looks complete.

If a repair script has to recover an emptied polluted concept page, it may write a visible `TODO` page, but normal finish sync must not create TODO or filler concept pages.
