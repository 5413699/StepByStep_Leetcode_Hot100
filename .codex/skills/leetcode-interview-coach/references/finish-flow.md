# Finish Flow

Use this flow when the user has a final answer and wants repository completion. This module composes scaffold helpers, interview readiness assessment, Git completion, and optional SiYuan sync; keep the substeps independently callable.

## Required Inputs

- Java scaffold path.
- Project note path.
- Problem title.
- User's final Java solution.
- User's thinking and complexity.
- Optional tag plan JSON.
- Optional readiness JSON.
- Optional current-problem conversation digest JSON.
- Optional SiYuan sync payload JSON.

## Workflow

1. Confirm the latest solution in the conversation is the final answer.
2. Read the target Java file before editing.
3. Replace only the marked `// region LeetCode solution` region using `scripts/replace_solution_region.ps1`.
4. Update only the Codex-marked area in the project Markdown note when a note update is needed.
5. Generate a tag plan using `tag-rules.md`.
6. Generate a current-problem conversation digest using `conversation-digest-schema.md`.
   - Include only the current problem's training process from the latest scaffold/coaching request to closeout.
   - Exclude previous problems, skill iteration, migration, SiYuan API troubleshooting, Git/environment work, and unrelated chat.
   - Write the digest to a UTF-8 JSON file and pass its path with `-ConversationDigestJson`.
7. Generate readiness assessment using `interview-readiness-flow.md`.
8. Run `mvn -q -DskipTests compile`.
9. Stage only current problem files.
10. Commit with:

```text
<problem title>

思路：<user thinking>

Codex 于 <yyyy-MM-dd HH:mm zzz> 提交
```

11. Push current branch.
12. If SiYuan is enabled, call `scripts/sync_leetcode_to_siyuan.py`.
13. Validate exported SiYuan pages using `siyuan-sync-validation.md`.

## Script Interfaces

Replace solution:

```powershell
powershell -ExecutionPolicy Bypass -File .codex\skills\leetcode-interview-coach\scripts\replace_solution_region.ps1 `
  -JavaPath "<java path>" `
  -SolutionContent $solution
```

Commit and push only relevant files:

```powershell
powershell -ExecutionPolicy Bypass -File .codex\skills\leetcode-interview-coach\scripts\finish_problem.ps1 `
  -Paths "<java path>","<note path>" `
  -ProblemTitle "<problem title>" `
  -Thinking "<summary>"
```

Full orchestrated closeout:

```powershell
powershell -ExecutionPolicy Bypass -File .codex\skills\leetcode-interview-coach\scripts\finish_leetcode_workflow.ps1 `
  -JavaPath "<java path>" `
  -NotePath "<note path>" `
  -ProblemTitle "<problem title>" `
  -Thinking "<summary>" `
  -SolutionContent $solution `
  -TagPlanJson "<tag plan json>" `
  -ReadinessJson "<readiness json>" `
  -ConversationDigestJson "<current problem digest json>"
```

The digest file should contain:

```json
{
  "firstReaction": "用户对当前题的第一反应。",
  "stuckPoints": ["当前题中明确卡住的点。"],
  "misconceptions": [{"before": "原理解", "after": "修正后理解"}],
  "breakthroughs": ["当前题的关键突破。"],
  "implementationNotes": ["当前题实现细节。"],
  "edgeCases": ["当前题边界和类型坑。"],
  "interviewExpression": "当前题最终面试表达。",
  "reviewAdvice": ["当前题复习建议。"],
  "conceptUpdates": [{"concept": "DFS", "note": "当前题对该知识点的理解补充。"}]
}
```

## Failure Policy

- If Maven compile fails, stop before Git and SiYuan sync.
- If unrelated dirty files exist, stop before commit.
- If Git succeeds but SiYuan fails, do not roll back Git; report the SiYuan error.
- If SiYuan validation fails, keep outgoing payload files and report the failing block id.
- If a title, HPath, concept name, review label, or tag contains ASCII `?`, Unicode replacement characters, or visible mojibake detected by the sync script, stop before SiYuan write and report the offending field.
