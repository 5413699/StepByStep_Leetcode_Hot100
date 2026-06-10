# Scaffold Flow

Use this flow when the user asks to add a LeetCode Hot100 problem, create a branch, create the Java skeleton, or scaffold runnable examples. This module is independent from coaching, Git finishing, and SiYuan sync.

## Workflow

1. Inspect the project before creating files.
   - Read nearby Java files in `src/main/java/com/czf/<category>`.
   - Read nearby notes in `src/notes`.
   - On Windows PowerShell 5.1, do not rely on plain `Get-Content` for UTF-8 files without BOM. Use `Get-Content -Encoding UTF8` for display, or `[System.IO.File]::ReadAllText($path, [System.Text.UTF8Encoding]::new($false,$true))` when checking Chinese integrity.
   - Preserve package names, class naming, author style, helper methods, and sample harness style.

2. Create or switch to the problem branch before adding files.
   - Branch format: `<category-index>-<order>-<difficulty><problem-number>-<Chinese title>`.
   - Category index mapping:
     - array/list: `2`
     - linked list: `3`
     - binary tree: `4`
     - stack: `5`
     - hash map/set: `6`
     - sliding-window string: `7`
     - matrix/grid/graph grid: `8`
   - Use `scripts/new_problem_branch.ps1` after deciding category, difficulty, number, and title.
   - If the worktree has unrelated changes, stop before switching branches.

3. Infer placement.
   - Java path: `src/main/java/com/czf/<category-package>/`.
   - Note path: matching primary data-structure category under `src/notes/01.按数据结构分类`.
   - Add method-category notes only when explicitly requested.

4. Create skeleton only.
   - Include problem statement, examples, constraints, and advanced prompt in the note.
   - Include a runnable `main` harness when practical.
   - Put LeetCode answer code only between:

```java
// region LeetCode solution
// endregion
```

5. Use `scripts/new_problem_scaffold.ps1` to create the note and Java file. The script refuses to overwrite existing files.

6. Validate with `mvn -q -DskipTests compile`.
   - If running a sample `main`, prefer `& "$env:JAVA_HOME\bin\java.exe" -cp target\classes <main-class>` instead of bare `java`, because Windows PATH may resolve to stale `Oracle\javapath\java.exe`.

## Script Interfaces

Create or switch branch:

```powershell
powershell -ExecutionPolicy Bypass -File .codex\skills\leetcode-interview-coach\scripts\new_problem_branch.ps1 `
  -CategoryIndex 8 `
  -Difficulty M `
  -ProblemNumber 200 `
  -ChineseTitle "岛屿数量"
```

Create files:

```powershell
powershell -ExecutionPolicy Bypass -File .codex\skills\leetcode-interview-coach\scripts\new_problem_scaffold.ps1 `
  -NotePath "<note path>" `
  -JavaPath "<java path>" `
  -NoteContent $noteContent `
  -JavaContent $javaContent
```
