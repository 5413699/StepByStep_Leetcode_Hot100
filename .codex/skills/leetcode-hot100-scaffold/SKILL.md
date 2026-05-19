---
name: leetcode-hot100-scaffold
description: Create notes and Java solution skeletons for this LeetCode Hot100 Java project. Use when the user pastes a LeetCode problem and asks to add it under notes and com.czf, scaffold a new problem, create the note/code files without solving it, or follow this repository's existing LeetCode naming and placement conventions.
---

# LeetCode Hot100 Scaffold

## Workflow

1. Inspect the project before creating files.
   - Use `Get-ChildItem -Recurse -File` or `rg --files` when available.
   - Read nearby Java files in `src/main/java/com/czf/<category>` and nearby notes in `src/notes`.
   - Preserve the repository's existing naming style, package name, author block, and simple `ListNode`/`TreeNode` helper style.
   - Use `@Author 陈智飞` for newly created Java skeletons.

2. Infer placement from the problem.
   - Primary note path: the matching data-structure category under `src/notes`.
   - Java path: `src/main/java/com/czf/<category-package>/`.
   - Add secondary method-category notes only when the user asks or the repository clearly already cross-lists the same kind of problem.

3. Name files consistently.
   - Prefix by difficulty: `E`, `M`, or `H`.
   - Use a zero-padded problem number when local files do so: `M148_<Chinese title>.md`, `M148_Sort_Linkedlist.java`.
   - Use concise English for Java class names and Chinese problem titles for note names.
   - Keep package names exactly as existing folders use them, including local spelling such as `linkedlist`, `arraylist`, or `quene`.

4. Create only scaffolding unless the user asks for a solution.
   - Notes should contain the problem title, statement, examples, constraints, and advanced prompt if present.
   - Java should compile and expose the expected LeetCode method signature.
   - Leave the method body as a placeholder such as `return null;`, `return 0;`, `return false;`, or an empty body for `void`.
   - Do not add algorithm hints, solution comments, or implementation logic when the user says they want to try it themselves.

5. Validate.
   - Run `mvn -q -DskipTests compile` when a Java file was added.
   - If Maven needs access outside the sandbox, request escalation and rerun.
   - Report created files and whether compilation passed.

## Script

Use `scripts/new_problem_scaffold.ps1` after deciding the exact paths, class name, package, method stub, and note content. It creates the two files and refuses to overwrite existing files.

Example:

```powershell
powershell -ExecutionPolicy Bypass -File .codex\skills\leetcode-hot100-scaffold\scripts\new_problem_scaffold.ps1 `
  -NotePath "<resolved note path>" `
  -JavaPath "src\main\java\com\czf\linkedlist\M148_Sort_Linkedlist.java" `
  -NoteContent $noteContent `
  -JavaContent $javaContent
```

Prefer `apply_patch` for small one-off edits. Prefer the script when creating both files from prepared content.
