# SiYuan Linked Index Flow

This module defines how a completed problem updates the linked wiki index pages. It is independent from coaching, scaffold, Git, and low-level SiYuan HTTP code.

## Purpose

When a problem is synced, every confirmed tag must update all relevant wiki surfaces:

- the concrete concept page
- the concept category page
- the knowledge home page
- the problem index page
- the root training home page
- review and expression home pages when the problem has review labels

This prevents a problem from appearing only on its problem page while higher-level review entrances stay stale.

## Inputs

The flow consumes:

- problem title and problem block id
- confirmed tags grouped as `dataStructures`, `methods`, `patterns`, `commonFunctions`
- review labels
- concept update notes from the current-problem conversation digest

Only confirmed tags with evidence should be written. Suggested or low-confidence tags must not create concept pages.
Confirmed tags also need concept knowledge. If a concept is missing from the local knowledge map, the sync payload must include `conceptKnowledge` generated from reputable local or open-web references.

## Required Writes

For each confirmed concept tag:

1. Ensure concept page exists at:
   - `{systemRootHPath}/知识点/数据结构/{name}`
   - `{systemRootHPath}/知识点/解题方法/{name}`
   - `{systemRootHPath}/知识点/解题模式/{name}`
   - `{systemRootHPath}/知识点/常用函数/{name}`
2. Ensure the concept page has useful sections:
   - `## 简介`
   - `## 什么时候想到它`
   - `## 常见代码结构`
   - `## 高频易错点`
   - `## 题集`
   - `## 来源依据`
3. Add exactly one problem block reference under the concept page `## 题集`.
4. Add current-problem learning notes under `## 来自题目的理解` when provided.
5. Ensure the parent category page contains `## 知识点` and exactly one block reference to the concept page.
6. Ensure the knowledge home page contains the category entrance and a recent concept link.

For each completed problem:

1. Ensure root home contains the problem under recent sync.
2. Ensure problem index contains the problem under `## 题目列表`.
3. Ensure expression home contains the problem under recent expression practice.
4. If review labels exist, ensure review label pages and review home link to the problem.

## Required Validation

After writes, validate current block Markdown from `/api/block/getBlockKramdown`, not exported full Markdown:

- problem page contains the current problem title
- every touched concept page contains the current problem title
- every touched category page contains each concept name written into that category
- knowledge home contains every touched category name and concept name
- root home, problem index, review home, and expression home contain the problem title when touched
- no user-facing page contains `title:`, `date:`, `lastmod:`, `[^1]`, `<!-- codex-`, or literal HTML anchors
- newly created concept pages do not contain generic filler phrases listed in `concept-knowledge-flow.md`

`/api/export/exportMdContent` must not be used as a write-back or validation source for linked index pages, because it can expand SiYuan block references into Markdown footnotes and child document content.

## Dedupe Rules

- Dedupe by block id first.
- Dedupe by display title second.
- Never append the same problem twice to a concept, review, root, or problem index page.
- Never append the same concept twice to a category or knowledge home page.

## Repair Rules

If a linked page was polluted by exported Markdown:

- use current block Markdown as the repair source
- strip leaked `title/date/lastmod` metadata
- remove exported footnote refs and footnote definitions
- remove accidentally expanded problem-page sections from concept/category/review pages
- preserve user-written content outside the polluted exported sections
- use official SiYuan API only
