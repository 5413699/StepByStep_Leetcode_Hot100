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
- 面试版思路
- 最终题解
- 复杂度
- 易错点
- 面试表达
- 掌握状态
- 复习建议
- 同步记录

Never expose `<!-- codex-* -->` markers in SiYuan pages.

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

Each review page should contain a concise explanation and a `## 题集` list.

## Audit Log

Audit log HPath:

```text
{systemRootHPath}/Codex 同步日志
```

Append one entry per sync with:

- problem title
- branch and commit
- touched problem/concept/review pages
- validation status
- skipped or failed steps
