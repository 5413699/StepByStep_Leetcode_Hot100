# Common Function Flow

Use this module inside finish flow when the final Java solution introduces or reinforces reusable Java API usage.

## Goal

Every newly used function must be stored in two places:

1. The SiYuan concept page `## 常见代码结构` for its common-function concept.
2. A repository Markdown note under `src/notes/03.常用函数/...`.

Do not only mention the function in the problem note. A function is reusable knowledge, so it needs a reusable entrance.

## Detection

Detect concrete API usage from the final Java solution and the conversation digest. Current built-in detections include:

- `Arrays.fill(...)` -> `数组Array的常用函数`
- `new String(char[])` / `new String(board[i])` -> `字符串String的常用函数`

When adding a new detection, include:

- function name
- owning common-function concept
- repository note path
- one concrete code structure
- when to use it
- common mistakes
- source evidence from official Java docs or a reputable open learning reference

## Repository Notes

Write generated function notes under:

```text
src/notes/03.常用函数/
  01.数组Array/
  02.字符串String/
  03.集合Collection/
  04.哈希Map/
  05.队列Queue/
  06.栈Stack/
```

Each function note should contain:

- 简介
- 什么时候用
- 常见代码结构
- 易错点
- 题目使用记录
- 来源依据

Use `<!-- codex-common-function-start -->` and `<!-- codex-common-function-end -->` in repository notes so generated content can be updated without destroying user-written additions outside the marked region.
Keep the visible Markdown clean: the first visible line must be `# <function name>`, and the generated markers should wrap the body sections below the title, not the title itself.

## SiYuan Concept Pages

When a detected function belongs to a confirmed or inferred common-function concept, update the concept page:

- Ensure the concept exists with high-quality concept knowledge.
- Add the function-specific example under `## 常见代码结构`.
- Add the current problem under `## 题集`.
- Add a concise note under `## 来自题目的理解`.

If the function maps to a common-function concept that is missing from local knowledge, add concept knowledge first. Do not create a generic placeholder page.

## Sources

Prefer official Java API documentation:

- Oracle Java `java.util.Arrays`
- Oracle Java `java.lang.String`

Use reputable open-source learning notes only as supplementary explanation. Do not cite low-signal SEO pages.

## Validation

For each detected function:

- Repository note exists after finish flow.
- Repository note contains the function name and current problem title.
- SiYuan common-function concept page contains the function name under `## 常见代码结构`.
- Sync validation must fail if a detected function cannot be written to its reusable surfaces.
