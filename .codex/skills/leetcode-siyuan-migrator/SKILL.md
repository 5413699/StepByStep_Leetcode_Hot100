---
name: leetcode-siyuan-migrator
description: One-time SiYuan migration assistant for the LeetCode interview-training wiki. Use when Codex needs to audit, dry-run, or apply a migration from the user's legacy SiYuan algorithm-note structure into the new 面试手撕训练系统 structure, preserving old pages by default and writing an audit log.
---

# LeetCode SiYuan Migrator

Use this skill only for one-time or batch migration of existing SiYuan algorithm notes. Do not use it for normal problem finish flow.

## Core Rule

Migration is high-risk and low-frequency. Always dry-run first. Never delete or overwrite legacy pages unless the user explicitly asks for a destructive cleanup step.

## Workflow

1. Read `references/migration-flow.md`.
2. Verify SiYuan API connectivity through the shared UTF-8 client in `../leetcode-interview-coach/scripts/siyuan_client.py`.
3. Discover existing pages from legacy roots:
   - `/算法题/LeetCode Hot100`
   - `/算法题/按数据结构分类`
   - `/算法题/按方法分类`
   - `/算法题/常用函数`
4. Build a migration plan into:
   - `/算法题/面试手撕训练系统/题集`
   - `/算法题/面试手撕训练系统/知识点/数据结构`
   - `/算法题/面试手撕训练系统/知识点/解题方法`
   - `/算法题/面试手撕训练系统/知识点/解题模式`
   - `/算法题/面试手撕训练系统/知识点/常用函数`
   - `/算法题/面试手撕训练系统/错题与复习`
   - `/算法题/面试手撕训练系统/面试表达`
   - `/算法题/面试手撕训练系统/Codex 同步日志`
5. Build a reorganization model: problems, concepts, problem-concept links, and category indexes. Do not dump old pages into `旧笔记内容`.
6. Run `scripts/migrate_siyuan_interview_system.py` without `--apply` first and save `--output` to an ASCII temp path.
7. Inspect dry-run `summary`, `modelSummary`, `items`, `conflicts`, and `cleanupAdvice`.
8. Apply only with an explicit `--apply`.
9. Validate exported pages for Chinese integrity, replacement characters, visible machine markers, source ids, non-empty category indexes, and absence of legacy copy markers.
10. Ensure the root home page and section home pages are populated and useful. For home, category, and audit pages, use `/api/block/getBlockKramdown` for current-block content; do not write back full export output.
11. Keep `错题与复习` compact: remove empty review label pages and do not list labels without linked problems.
12. Keep `Codex 同步日志` newest-first and retain only the last 7 days.
13. If existing target pages are damaged or incomplete, run `scripts/repair_siyuan_from_repo.py` to rebuild the target wiki from repository notes and Java solutions instead of reusing damaged target pages as the source.

## Output

Report:

- source roots scanned
- pages created or updated
- model summary: problem count, concept count, category concept counts
- conflicts requiring user review
- `cleanupAdvice.safeAfterTargetVerification`
- `cleanupAdvice.reviewBeforeDelete`
- validation summary
- home page links and non-empty section-homepage verification
- report JSON path
- API URL used, never token
- audit log link when applied

Use native SiYuan block references for links. Never write HTML anchors into SiYuan pages.

If raw Kramdown shows `{: id="..." updated="..."}`, that is SiYuan block metadata, not learning content. Strip it before writing back or presenting diagnostics.

Never say an old page is safe to delete without the condition: first verify that the target page contains the expected migrated content. Directory/index pages and `未命名` pages require manual review.
