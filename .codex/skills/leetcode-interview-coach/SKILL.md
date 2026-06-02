---
name: leetcode-interview-coach
description: One-stop LeetCode Hot100 Java workflow for this repository. Use when Codex needs to scaffold a new LeetCode problem branch and Java/note structure, coach the user through an algorithm interview problem with Socratic hints, review or polish the user's solution, insert the final Java answer into the scaffold, update project notes, commit and push the finished branch, or sync the completed problem into the user's SiYuan wiki with concept backlinks.
---

# LeetCode Interview Coach

This is the only LeetCode Hot100 skill entrypoint for this repository. Route each request to the smallest independent module below. Load only the referenced file needed for the current task.

## Module Routing

- **Scaffold a problem**: read `references/scaffold-flow.md`.
  - Triggers: "添加这题", "创建结构", "scaffold", "新建题目", pasted problem statement with a request to add it.
  - Output: branch, note file, Java skeleton, sample harness, Maven compile status.

- **Coach/interview practice**: read `references/coach-flow.md`.
  - Triggers: "教我", "讲讲", "没思路", "帮我看代码", "模拟面试".
  - Output: questions, tiered hints, code review, dry run, complexity, interview wording.

- **Finish a completed solution**: read `references/finish-flow.md`.
  - Triggers: "最终答案", "帮我整理", "帮我提交", "收尾", "这版通过了", "一次运行成功".
  - Output: integrated Java answer, updated project note, Maven compile, Git commit, push, optional SiYuan sync.

- **Sync to SiYuan wiki**: read `references/siyuan-api-flow.md`.
  - Triggers: "同步思源", "生成 wiki 笔记", or finish flow with SiYuan enabled.
  - Output: problem page link, touched concept page links, sync status.

- **Generate tags**: read `references/tag-rules.md`.
  - Use before SiYuan sync or whenever the user asks what data structure/method/pattern a problem belongs to.

## Global Rules

- Prefer Chinese responses in this repository.
- Keep modules decoupled. Do not make scaffold depend on coaching, Git, or SiYuan. Do not make SiYuan sync depend on Git. Use finish flow only as the orchestrator.
- Do not call or depend on the removed scaffold skill. Its scripts have been migrated into this skill.
- Never edit SiYuan `.sy` files directly. Use official HTTP APIs only.
- Before editing repository files, inspect the target files and current `git status --short --branch`.
- Preserve unrelated user changes. Stage only files explicitly relevant to the current problem or skill iteration.

## Repository Completion

When the user reaches a final answer:

1. Locate the current problem's Java scaffold and note.
2. Replace only the marked LeetCode solution region.
3. Update only the intended note region.
4. Generate a tag plan with evidence when SiYuan sync is enabled.
5. Run `mvn -q -DskipTests compile`.
6. Commit and push with a Chinese message containing the user's thinking and `Codex 于 <timestamp> 提交`.
7. Sync to SiYuan if configured; report failure without rolling back Git.

## User-Facing Closeout

After finishing work, report:

- branch name
- commit hash
- push status
- changed files
- Maven compile status
- SiYuan problem page link and concept page links when synced
- any skipped or failed step

Keep the final response concise.
