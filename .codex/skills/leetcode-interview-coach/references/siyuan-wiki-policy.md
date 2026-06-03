# SiYuan Wiki Policy

Use this module when deciding how a completed LeetCode learning record should be represented in SiYuan. This is separate from low-level API operations.

## Target System

All new LeetCode interview-training writes go under:

```text
/算法题/面试手撕训练系统
  /题集
  /知识点
    /数据结构
    /解题方法
    /解题模式
    /常用函数
  /错题与复习
  /面试表达
  /Codex 同步日志
```

Do not create new pages under legacy roots such as `/算法题/按数据结构分类` or `/算法题/按方法分类`. Existing legacy pages are handled by the separate `leetcode-siyuan-migrator` skill.

## Problem Page

Problem HPath:

```text
{systemRootHPath}/题集/{problemTitle}
```

Problem pages are learning records, not only solutions. Include:

- 题干
- 第一反应
- 卡壳点
- 关键突破
- 思考过程
- 面试版思路
- 最终题解
- 复杂度
- 易错点
- 面试表达
- 掌握状态
- 复习建议
- 同步记录

Never expose `<!-- codex-* -->` markers in SiYuan pages.
Use SiYuan native block references `((blockId "display"))` for links to problem, concept, review, and category pages. Do not use HTML anchors, because SiYuan may show `<a href=...>` as literal source in the editor.
Do not write `来源索引`, `迁移记录`, raw source ids, raw source HPaths, or HTML link source code in user-facing pages. Put audit details in `Codex 同步日志`.

## Concept Pages

Concept HPaths:

- Data structures: `{systemRootHPath}/知识点/数据结构/{name}`
- Methods: `{systemRootHPath}/知识点/解题方法/{name}`
- Patterns: `{systemRootHPath}/知识点/解题模式/{name}`
- Common functions: `{systemRootHPath}/知识点/常用函数/{name}`

When creating a concept page, include:

- 简介
- 什么时候想到它
- 常见代码结构
- 高频易错点
- 题集

When updating an existing concept page:

- Preserve user-written content.
- Add missing sections only when absent.
- Add the problem link under `## 题集` only if not already present.
- Do not write HTML comment markers.
- Do not write HTML `<a href=...>` links.
- `什么时候想到它` must be concept-specific. Avoid using the same generic two bullets for every concept.
- When a current-problem conversation digest has concept updates, add them under `## 来自题目的理解` and dedupe by problem id and note text.

## Category Index Pages

Category pages are:

- `{systemRootHPath}/知识点/数据结构`
- `{systemRootHPath}/知识点/解题方法`
- `{systemRootHPath}/知识点/解题模式`
- `{systemRootHPath}/知识点/常用函数`

Each category page should contain `## 知识点` and visible block references to child concept pages. If a category has child concepts, the page must not be empty.
Show associated problem counts when available.
When a completed problem links to a concept, the parent category page must be updated in the same sync. For example, a problem tagged `图论` must update both `{systemRootHPath}/知识点/数据结构/图论` and `{systemRootHPath}/知识点/数据结构`.

## Home Pages

Maintain these section home pages automatically:

- `{systemRootHPath}`
- `{systemRootHPath}/题集`
- `{systemRootHPath}/知识点`
- `{systemRootHPath}/错题与复习`
- `{systemRootHPath}/面试表达`

The root home page should contain entry links, training overview, high-frequency knowledge map, recent problems, and concise usage principles.

The section home pages should not be blank:

- `题集`: problem links grouped or appended by solved problem.
- `知识点`: category entrances plus recently linked concepts. It must include every category and concept touched by the current sync.
- `错题与复习`: only real review entries. Do not show all possible labels when they have no linked problems.
- `面试表达`: reusable interview explanation templates and recent expression-practice problems.

Use current-block Markdown from `/api/block/getBlockKramdown` when updating home pages. Do not use `/api/export/exportMdContent` as the write-back source for home pages or directory pages, because export may include child documents and YAML metadata.

## Review Pages

Review labels are written under:

```text
{systemRootHPath}/错题与复习/{label}
```

Examples:

- 一刷卡壳
- 提示后完成
- 独立完成
- 代码有 bug
- 面试表达不熟
- 需要二刷

Create a review page only when at least one problem has that label. Empty review pages and generic label lists are noise and should be removed during repair.

The review home page should stay compact:

- explain the review principle
- show current review entries only when they exist
- avoid boilerplate priority lists unless they are tied to real problem links

## Audit Log

Audit log HPath:

```text
{systemRootHPath}/Codex 同步日志
```

Write one entry per sync with:

- problem title
- branch and commit
- touched problem/concept/review pages
- whether a current-problem conversation digest was included
- validation status
- skipped or failed steps

The audit page should begin with a concise `## 说明`. New entries must be inserted before older entries, and only entries from the last 7 days should be retained. Use current-block Markdown from `/api/block/getBlockKramdown`, not exported full document Markdown. Clean SiYuan block attributes and YAML/frontmatter before writing back.

`/api/block/getBlockKramdown` may include SiYuan block attributes such as `{: id="..." updated="..."}`. Treat these as Kramdown metadata in diagnostics; do not render them intentionally in user-facing Markdown and strip them before reusing content.

## Encoding Guard

Before creating or updating any page, reject corrupted title/path metadata. Stop if `problemTitle`, HPath, concept name, review label, or tag contains ASCII `?`, Unicode replacement characters, or visible mojibake detected by the sync script. This prevents accidental pages such as `??` or `M200-????`.
