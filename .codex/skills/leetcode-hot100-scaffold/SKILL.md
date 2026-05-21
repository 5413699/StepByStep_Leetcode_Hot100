---
name: leetcode-hot100-scaffold
description: Create problem branches, notes, Java solution skeletons, and runnable sample input/output harnesses for this LeetCode Hot100 Java project. Use when the user pastes a LeetCode problem and asks to add it under notes and com.czf, scaffold a new problem without solving it, or follow this repository's existing LeetCode branch/file naming conventions.
---

# LeetCode Hot100 Scaffold

## Workflow

1. Inspect the project before creating files.
   - Use `Get-ChildItem -Recurse -File` or `rg --files` when available.
   - Read nearby Java files in `src/main/java/com/czf/<category>` and nearby notes in `src/notes`.
   - Preserve the repository's existing naming style, package name, author block, and simple `ListNode`/`TreeNode` helper style.
   - Use `@Author 陈智飞` for newly created Java skeletons.

2. Create or switch to the problem branch before adding files.
   - Follow the existing branch convention: `<category-index>-<order>-<difficulty><problem-number>-<Chinese title>`, for example `4-9-M114-二叉树展开为链表`.
   - Infer `category-index` from destination package and existing branch history. Common mappings in this repo: `arraylist`/数组 -> `2`, `linkedlist`/链表 -> `3`, `binarytree`/二叉树 -> `4`, `stack`/栈 -> `5`, hash map/set problems -> `6`, sliding-window string problems -> `7`, `matrix`/矩阵 -> `8`.
   - Infer `order` as one greater than the highest existing local branch with the same `category-index`. If the problem branch already exists, switch to it instead of creating a duplicate.
   - Prefer the difficulty/problem token as written by the user, such as `H23` or `M114`; if absent, use the difficulty letter plus a three-digit problem number.
   - Use `git status --short --branch` before switching. If unrelated dirty files exist, pause and explain instead of moving branches blindly.
   - Do not create problem files or commit problem work unless the current branch is the intended problem branch. If dirty files prevent switching, stop and ask whether to commit, stash, or postpone those changes first.
   - If normal Git history is blocked, inspect `.git/config`, `.git/refs/heads`, and `.git/logs/HEAD` to infer naming.
   - Prefer `scripts/new_problem_branch.ps1` for this step after deciding category index, difficulty, problem number, and Chinese title.

3. Infer placement from the problem.
   - Primary note path: the matching data-structure category under `src/notes`.
   - Java path: `src/main/java/com/czf/<category-package>/`.
   - Add secondary method-category notes only when the user asks or the repository clearly already cross-lists the same kind of problem.

4. Name files consistently.
   - Prefix by difficulty: `E`, `M`, or `H`.
   - Use a zero-padded problem number when local files do so: `M148_<Chinese title>.md`, `M148_Sort_Linkedlist.java`.
   - Use concise English for Java class names and Chinese problem titles for note names.
   - Keep package names exactly as existing folders use them, including local spelling such as `linkedlist`, `arraylist`, or `quene`.

5. Create only scaffolding unless the user asks for a solution.
   - Notes should contain the problem title, statement, examples, constraints, and advanced prompt if present.
   - Java should compile and expose the expected LeetCode method signature.
   - Leave the method body as a placeholder such as `return null;`, `return 0;`, `return false;`, or an empty body for `void`.
   - Do not add algorithm hints, solution comments, or implementation logic when the user says they want to try it themselves.
   - Add stable markers around the method intended for the final LeetCode answer so `leetcode-interview-coach` can later replace only that region:

```java
    // region LeetCode solution
    public ReturnType methodName(...) {
        return null;
    }
    // endregion
```

6. Add suitable runnable sample input/output.
   - Include a small `main` method using examples from the problem statement when practical.
   - Print the actual result and the expected result text. Keep helpers outside the solution region.
   - Arrays, strings, primitives, and matrices: build samples directly and print with `Arrays.toString`, `Arrays.deepToString`, or the repo's existing style.
   - Linked lists: include minimal `buildList` and `printList` helpers when local helpers are not already present.
   - Binary trees: include minimal level-order builder/serializer helpers using `Integer[]` when practical. For mutation problems, call the method and print the serialized result.
   - API design problems such as `LRUCache`: build the sample operation sequence in `main` and print observed outputs.
   - If a harness would be misleading or too large, add only the LeetCode signature and explain the omission in the final response.

7. Validate.
   - Run `mvn -q -DskipTests compile` when a Java file was added.
   - If Maven needs access outside the sandbox, request escalation and rerun.
   - Report the branch name, created files, sample harness status, and whether compilation passed.

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

Use `scripts/new_problem_branch.ps1` before creating files:

```powershell
powershell -ExecutionPolicy Bypass -File .codex\skills\leetcode-hot100-scaffold\scripts\new_problem_branch.ps1 `
  -CategoryIndex 4 `
  -Difficulty M `
  -ProblemNumber 114 `
  -ChineseTitle "二叉树展开为链表"
```

The branch script prints the chosen branch name, reuses an existing matching branch when found, and refuses to switch if the worktree already has changes.

Use `scripts/replace_solution_region.ps1` from `leetcode-interview-coach` when inserting the user's final answer into a marked Java file.

Use `scripts/finish_problem.ps1` after the final answer is integrated. It compiles, refuses unrelated dirty files, stages only the paths passed in, commits with the user's thinking and a Codex timestamp, then pushes to the current upstream or `origin`.
