# Migration Flow

This migration moves legacy SiYuan algorithm notes into the new interview-training system. It is independent from daily LeetCode finish flow.

## Target Structure

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

## Policy

- Dry-run by default.
- Preserve legacy pages.
- Never delete old pages automatically.
- The target system must be independent from the legacy system: migrate and reorganize content into the new interview-training structure instead of displaying a raw `旧笔记内容` dump.
- Do not expose `<!-- codex-* -->` markers in target pages.
- Do not expose `来源索引`, `迁移记录`, raw source ids, raw source HPaths, or HTML link source code in user-facing problem/concept/category pages. Write source ids and paths only to JSON reports or `Codex 同步日志`.
- Use SiYuan native block references `((blockId "display"))` for page links. Do not use HTML `<a href=...>` because SiYuan may show it as literal text in the editor.
- Use UTF-8 Python API only.
- If a target page already exists, merge missing links and leave user-written content intact.
- If source content cannot be classified confidently, list it as a conflict instead of guessing.
- Legacy `/算法题/LeetCode Hot100/知识点/*` pages are migrated only when the title matches an explicit category whitelist. Unknown knowledge titles stay in conflicts for human review.
- Pages titled `未命名` or `Untitled` are always conflicts, even when they live under a known legacy category.
- After migration, report delete candidates only. Never delete automatically.

## API And Encoding

- Use the shared `siyuan_client.py`; it tries `lastWorkingUrl`, configured `url`, default `6806`, then local `SiYuan-Kernel.exe` listening ports.
- Do not print or persist the token.
- Build Chinese page bodies in Python with UTF-8 JSON requests, not ad hoc PowerShell strings.
- Write JSON reports to ASCII temp paths, then summarize the report for the user.

## Classification

- Problem pages: title matches `^[EMH]?\d{2,4}[-.．、]` or page is under old Hot100 `题集`.
- Data structure concepts: old `/按数据结构分类/{name}` pages and whitelisted Hot100 knowledge pages such as `二叉树`, `图论`, `矩阵`.
- Method concepts: old `/按方法分类/{name}` pages and whitelisted Hot100 knowledge pages such as `DFS`, `BFS`, `递归法`.
- Pattern concepts: whitelisted Hot100 knowledge pages such as `Flood Fill`, `网格搜索`, `连通块`.
- Function concepts: old `/常用函数/{name}` pages.
- Root/category index pages are conflicts unless explicitly handled later.

## Reorganization Model

Build a knowledge model before writing:

1. Parse legacy problem pages into problem records.
2. Parse legacy concept pages into concept records.
3. Infer problem-to-concept edges from old paths, title tag lines, and whitelisted Hot100 knowledge pages.
4. Render target pages from the model:
   - Problem pages contain `知识链接`, `题干`, `面试版思路`, `最终题解`, `复杂度`, `易错点`, and `同步记录`.
   - Concept pages contain `简介`, specific `什么时候想到它`, `常见代码结构`, `高频易错点`, and `题集`.
   - Category index pages list child concept block references and associated problem counts.
   - Root and section home pages are rendered as useful entrances, not left blank:
     - root: 今日入口, 训练概览, 高频知识地图, 最近整理题目.
     - 题集: problem links grouped by difficulty or order.
     - 知识点: category entrances and high-frequency concepts.
     - 错题与复习: compact review principle and only real review entries. Do not create or show empty label pages.
     - 面试表达: reusable explanation templates and representative problems.
     - Codex 同步日志: newest entries first, retaining only the last 7 days.

Do not create empty category pages when child concepts exist. Do not write `## 旧笔记内容`, `## 迁移补充`, duplicated YAML frontmatter, `来源索引`, `迁移记录`, or HTML link source code into target pages.

If target pages are already damaged or incomplete, do not use them as the only source for another overwrite. Prefer repository notes and Java files through `scripts/repair_siyuan_from_repo.py`, or ask the user for an external source.

When repairing home, category, or audit pages, read current-block content with `/api/block/getBlockKramdown`. Do not write back `/api/export/exportMdContent` output, because export can include child documents and frontmatter.

`/api/block/getBlockKramdown` may include SiYuan Kramdown block attributes such as `{: id="..." updated="..."}`. They explain what the user may see in diagnostics or raw exports. Strip them before reusing content, measuring page length, or showing previews.

## Concept Quality

Concept pages must not use one generic sentence for every `什么时候想到它` section. Prefer a concept-specific profile:

- DFS: start from a node/cell and recursively visit all reachable states.
- BFS: level-order expansion, shortest steps, queue processing.
- Flood Fill: seed cell expands to a same-type connected region.
- 网格搜索: matrix coordinates, boundary checks, direction arrays.
- 连通块: discover one unvisited component and mark the whole component.
- 图论: model objects as nodes and relationships as edges.
- 矩阵: two-dimensional coordinates and row/column boundaries.
- 二叉树: current node plus left/right subtree recursion.

When no profile exists, derive the intro from the legacy concept text and keep generic fallback wording short.

## Cleanup Advice

Return cleanup advice in two groups:

- `safeAfterTargetVerification`: old pages that were migrated to a concrete target. They are delete candidates only after the user verifies the target content.
- `reviewBeforeDelete`: conflicts such as directory pages, index pages, unknown knowledge pages, and `未命名` pages. These require manual inspection.

The final user response must explicitly state that no legacy page was deleted.

When the user explicitly asks to delete old useless pages, only delete pages that are verified trivial old directory/index pages or empty `未命名` pages after target pages pass validation.

## Validation

After apply, export every touched target page and verify:

- No `????`.
- No Unicode replacement character.
- No visible `<!-- codex-` marker.
- No `## 旧笔记内容`.
- No `## 迁移补充`.
- No `来源索引` or `迁移记录` in user-facing pages.
- No literal `<a href=...>` link source code.
- No duplicated YAML frontmatter in body.
- Category index pages that have child concepts are not empty.
- Root and section home pages are not empty and contain entry links or section-specific guidance.
- Review home page does not contain empty/generic label lists, and empty review label pages do not remain.
- Audit log entries are newest-first and older than 7 days are pruned.
- Concept pages include at least one linked problem when the model has related problems.

`/api/export/exportMdContent` may serialize SiYuan block references as Markdown footnote-style `[^1]` definitions. Treat that as an export representation, not a user-facing failure. Validate the editor-facing source by ensuring scripts wrote native block references, not HTML anchors.

If validation fails, stop and report the failing target id and check. Do not delete or clean old content after a validation failure.

## Apply Criteria

Only apply when:

- SiYuan API is reachable.
- `SIYUAN_TOKEN` is available.
- The target notebook is configured.
- Dry-run shows no destructive operations.
- User explicitly requested apply.
