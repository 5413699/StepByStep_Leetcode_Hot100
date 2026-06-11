---
name: leetcode-interview-coach
description: LeetCode interview hand-coding training system for this repository. Use when Codex needs to scaffold a Java LeetCode problem, coach the user through algorithm thinking, review or polish the user's solution, insert the final answer, extract a current-problem learning digest from the coaching conversation, update repository notes, commit and push, assess interview readiness, plan reviews, or sync the completed learning record into the user's SiYuan interview-prep wiki with concept backlinks and audit logs.
---

# LeetCode Interview Coach

This is the only LeetCode interview-training entrypoint for this repository. The goal is not only storing solutions; it is helping the user quickly become able to independently hand-code interview problems. Route each request to the smallest independent module below. Load only the referenced file needed for the current task.

## Module Routing

- **Scaffold a problem**: read `references/scaffold-flow.md`.
  - Triggers: "添加这题", "创建结构", "scaffold", "新建题目", pasted problem statement with a request to add it.
  - Output: branch, note file, Java skeleton, sample harness, Maven compile status.

- **Coach/interview practice**: read `references/coach-flow.md`.
  - Triggers: "教我", "讲讲", "没思路", "帮我看代码", "模拟面试".
  - Output: questions, tiered hints, code review, dry run, complexity, interview wording.

- **Assess interview readiness**: read `references/interview-readiness-flow.md`.
  - Triggers: "掌握了吗", "面试怎么说", "复习建议", "我卡在哪里", finish flow after coaching.
  - Output: readiness status, weak points, interview expression quality, next review actions.

- **Finish a completed solution**: read `references/finish-flow.md`.
  - Triggers: "最终答案", "帮我整理", "帮我提交", "收尾", "这版通过了", "一次运行成功".
  - Output: integrated Java answer, updated project note, readiness assessment, Maven compile, Git commit, push, optional SiYuan sync.

- **Extract current-problem learning digest**: read `references/conversation-digest-schema.md`.
  - Use inside finish flow before repository completion or SiYuan sync.
  - Output: a problem-scoped summary of the user's first reaction, stuck points, corrections, breakthroughs, implementation notes, edge cases, interview expression, review advice, and concept updates.

- **Sync to SiYuan wiki**: read `references/siyuan-api-flow.md`.
  - Triggers: "同步思源", "生成 wiki 笔记", or finish flow with SiYuan enabled.
  - Output: problem page link, touched concept/review page links, audit log link, sync status.

- **Apply SiYuan wiki policy**: read `references/siyuan-wiki-policy.md`.
  - Use when deciding where a problem, concept, review status, or audit log should be written in the user's existing SiYuan system.
  - Output: target HPaths, page templates, update rules, dedupe rules.

- **Update SiYuan linked indexes**: read `references/siyuan-linked-index-flow.md`.
  - Use inside SiYuan sync after tags are finalized.
  - Output: problem index, concept pages, category pages, knowledge home, root home, review home, and expression home are mutually linked and validated.

- **Validate SiYuan sync**: read `references/siyuan-sync-validation.md`.
  - Use after any SiYuan write.
  - Output: current-block kramdown checks for Chinese integrity, missing sections, duplicate links, and visible machine markers.

- **Plan review schedule**: read `references/review-schedule-flow.md`.
  - Triggers: "二刷", "复习", "下次什么时候看", finish flow after readiness assessment.
  - Output: review labels and suggested follow-up actions.

- **Generate tags**: read `references/tag-rules.md`.
  - Use before SiYuan sync or whenever the user asks what data structure/method/pattern a problem belongs to.

- **Generate concept knowledge**: read `references/concept-knowledge-flow.md`.
  - Use when a confirmed tag is not already backed by local concept knowledge or when creating a new SiYuan concept page.
  - Output: concrete `conceptKnowledge` with intro, recognition signals, code shape, pitfalls, and source evidence; never generic filler.

- **Migrate legacy SiYuan notes**: use the separate `leetcode-siyuan-migrator` skill.
  - Triggers: "迁移旧笔记", "整理已有思源体系", "把旧分类迁到新系统".
  - This main skill must not perform batch migration during normal finish flow.

## Global Rules

- Prefer Chinese responses in this repository.
- Keep modules decoupled. Do not make scaffold depend on coaching, Git, or SiYuan. Do not make low-level SiYuan API code depend on LeetCode note policy. Use finish flow only as the orchestrator.
- Use this skill's bundled scripts directly; do not route through legacy scaffold tooling.
- Never edit SiYuan `.sy` files directly. Use official HTTP APIs only.
- Never construct Chinese SiYuan payloads through ad hoc PowerShell string concatenation, here-strings, pipelines, inline `python -` snippets containing Chinese literals, or host-decoded Git output. Use UTF-8 Python/JSON files at ASCII temp paths, then pass only file paths to scripts.
- On Windows PowerShell 5.1, do not use plain `Get-Content` output as evidence that a UTF-8 Chinese file is corrupted; read with `-Encoding UTF8` or strict .NET UTF-8 APIs. For runnable Java samples, prefer `$env:JAVA_HOME\bin\java.exe` over bare `java` after checking `where.exe java`.
- On Windows PowerShell 5.1, avoid nested `powershell -File` calls for arguments containing Chinese text, multi-line content, or arrays. Invoke bundled scripts in the current session with explicit parameters, or pass UTF-8 JSON/file paths. Prefer `finish_problem.ps1 -JavaPath ... -NotePath ...` for closeout commits.
- When inspecting local concept support, prefer `rg -F "<tag>"` fixed-string searches over broad regex alternation unless a regex is actually needed.
- SiYuan user-visible pages must not contain `<!-- codex-* -->` markers. Those markers may remain in repository Markdown only.
- The new SiYuan target structure is authoritative: `算法题/面试手撕训练系统`. Legacy pages may be migrated into it, but new writes must not create new knowledge pages under the old `按数据结构分类` / `按方法分类` layout.
- Stop before writing to SiYuan if a title, HPath, concept name, review label, or tag appears corrupted, including any ASCII `?`, Unicode replacement characters, or visible mojibake detected by the sync script. Do not create pages such as `??` or `M200-????`.
- SiYuan review pages must stay signal-only: create review label pages only when a real problem is linked. Audit logs must be newest-first and retain only the last 7 days.
- SiYuan concept pages must never be filled with generic template prose. If a new tag lacks local concept knowledge, search reputable open references when available and pass structured `conceptKnowledge`; otherwise stop before creating the page.
- Treat commit hash as the authoritative Git identifier for SiYuan sync. If the current branch name contains Chinese or is returned as mojibake on Windows, omit it from the payload or use an ASCII-safe display value; do not write corrupted branch names.
- One-time migration from legacy SiYuan pages is handled by `leetcode-siyuan-migrator`, dry-run first and non-destructive by default.
- Before editing repository files, inspect the target files and current `git status --short --branch`.
- Preserve unrelated user changes. Stage only files explicitly relevant to the current problem or skill iteration.

## Repository Completion

When the user reaches a final answer:

1. Locate the current problem's Java scaffold and note.
2. Replace only the marked LeetCode solution region.
3. Update only the intended repository note region.
4. Generate a tag plan with evidence.
5. Generate or verify concept knowledge for every confirmed tag. Use local knowledge first; if missing, search reputable open references when network is available and create structured `conceptKnowledge`.
6. Generate a current-problem conversation digest. Include only the interaction about this problem from scaffold/coaching to closeout; exclude old problems, skill iteration, migration, environment debugging, and unrelated chat.
7. Generate an interview-readiness assessment and review labels.
8. Run `mvn -q -DskipTests compile`.
9. Commit and push with a Chinese message containing the user's thinking and `Codex 于 <timestamp> 提交`.
10. If SiYuan is enabled, run a sync dry-run, discover the actual API URL, write the learning record, validate current-block Markdown, and report failure without rolling back Git.

## User-Facing Closeout

After finishing work, report:

- branch name
- commit hash
- push status
- changed files
- Maven compile status
- SiYuan problem page link and concept page links when synced
- readiness status and next review actions when available
- any skipped or failed step

Keep the final response concise.
