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
   - `/算法题/面试手撕训练系统/知识点`
   - `/算法题/面试手撕训练系统/错题与复习`
   - `/算法题/面试手撕训练系统/Codex 同步日志`
5. Show dry-run output first.
6. Apply only with an explicit `--apply`.
7. Validate exported pages for Chinese integrity and duplicate links.

## Output

Report:

- source roots scanned
- pages to create
- pages to update
- pages skipped
- conflicts requiring user review
- audit log link when applied

