# Finish Flow

Use this flow when the user has a final answer and wants repository completion. This module composes scaffold helpers and optional SiYuan sync; keep the substeps independently callable.

## Required Inputs

- Java scaffold path.
- Project note path.
- Problem title.
- User's final Java solution.
- User's thinking and complexity.
- Optional tag plan JSON for SiYuan.
- Optional SiYuan sync payload JSON.

## Workflow

1. Confirm the latest solution in the conversation is the final answer.
2. Read the target Java file before editing.
3. Replace only the marked `// region LeetCode solution` region using `scripts/replace_solution_region.ps1`.
4. Update only the Codex-marked area in the project Markdown note when a note update is needed.
5. Generate a tag plan using `tag-rules.md` if SiYuan sync is enabled.
6. Run `mvn -q -DskipTests compile`.
7. Stage only current problem files.
8. Commit with:

```text
<problem title>

思路：<user thinking>

Codex 于 <yyyy-MM-dd HH:mm zzz> 提交
```

9. Push current branch.
10. If SiYuan is enabled, call `scripts/sync_leetcode_to_siyuan.py`.

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
  -TagPlanJson "<tag plan json>"
```

## Failure Policy

- If Maven compile fails, stop before Git and SiYuan sync.
- If unrelated dirty files exist, stop before commit.
- If Git succeeds but SiYuan fails, do not roll back Git; report the SiYuan error.
