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
5. Run `scripts/migrate_siyuan_interview_system.py` without `--apply` first and save `--output` to an ASCII temp path.
6. Inspect dry-run `summary`, `items`, `conflicts`, and `cleanupAdvice`.
7. Apply only with an explicit `--apply`.
8. Validate exported pages for Chinese integrity, replacement characters, visible machine markers, and source ids.

## Output

Report:

- source roots scanned
- pages created or updated
- conflicts requiring user review
- `cleanupAdvice.safeAfterTargetVerification`
- `cleanupAdvice.reviewBeforeDelete`
- validation summary
- report JSON path
- API URL used, never token
- audit log link when applied

Never say an old page is safe to delete without the condition: first verify that the target page contains the expected migrated content. Directory/index pages and `未命名` pages require manual review.
