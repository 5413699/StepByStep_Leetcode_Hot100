# First-Run Setup Flow

Use this flow when this repository is cloned to a new machine, SiYuan paths differ from the original machine, or the user asks to set up the skill for full SiYuan create/update capability.

## Goal

Configure only local machine state so the skill can:

- discover the local SiYuan workspace
- connect to the local SiYuan HTTP API
- choose the target notebook
- write repository workflow config outside the repo
- leave the repository and SiYuan `.sy` files untouched during setup unless the user explicitly runs a sync/migration command later

## Information To Request

Ask for only the missing items after running the check script.

1. **SiYuan workspace path**
   - Where to find it: open SiYuan, go to `设置 > 关于`, and look for the workspace/data location.
   - Accept either the workspace root containing `conf`, `data`, and `repo`, or a child path such as `...\data`; scripts normalize child paths back to the workspace root.
   - Optional environment variables: `SIYUAN_WORKSPACE`, `SIYUAN_WORKSPACE_PATH`, or `SIYUAN_DATA_DIR`.

2. **SiYuan API Token**
   - Where to find it: open SiYuan, go to `设置 > 关于 > API Token`.
   - Preferred setup on Windows:
     ```powershell
     setx SIYUAN_TOKEN "the token copied from SiYuan"
     ```
   - Tell the user to open a new terminal or restart Codex after `setx`.
   - Do not print, commit, or store the token in repository files.
   - Temporary token entry through `configure_workflow.py` is allowed for verification, but the script does not persist it.

3. **Target notebook**
   - Where to find it: start SiYuan and open the notebook that should contain `算法题/面试手撕训练系统`.
   - The configure script lists open notebooks and asks the user to choose by number.

4. **Target wiki root HPath**
   - Default: `/算法题/面试手撕训练系统`.
   - Ask only if the user wants a different root.

## Procedure

1. Inspect current local status:
   ```powershell
   python .codex\skills\leetcode-interview-coach\scripts\configure_workflow.py --check
   ```

2. Explain the missing items from the check output in plain Chinese. Include where the user can find each missing item.

3. After the user supplies missing information, prefer environment variables for machine-local secrets and paths:
   ```powershell
   setx SIYUAN_TOKEN "..."
   setx SIYUAN_WORKSPACE "E:\000_SIYUAN"
   ```

4. Ask the user to start SiYuan, unlock the workspace if needed, and open the target notebook.

5. If the user supplied exact values, apply them non-interactively:
   ```powershell
   python .codex\skills\leetcode-interview-coach\scripts\configure_workflow.py --workspace "E:\000_SIYUAN" --system-root "/算法题/面试手撕训练系统" --notebook-name "notebook name" --verify --write
   ```
   Use `--notebook-id` instead of `--notebook-name` when the user provides the id.

6. Otherwise run the interactive configuration:
   ```powershell
   python .codex\skills\leetcode-interview-coach\scripts\configure_workflow.py
   ```

7. Verify again:
   ```powershell
   python .codex\skills\leetcode-interview-coach\scripts\configure_workflow.py --check
   ```

8. Report:
   - local config path
   - detected workspace path
   - API reachability and resolved URL
   - selected notebook name/id when available
   - system root HPath
   - remaining missing items, if any

## Safety Rules

- Never edit SiYuan `.sy` files directly.
- Never store `SIYUAN_TOKEN` in the repository or final response.
- Do not create or update SiYuan pages during setup. Setup only validates connectivity and writes local workflow config.
- If API connection fails, ask the user to confirm SiYuan is running, the token is current, and the target notebook is open.
- If workspace detection finds multiple plausible roots, prefer a valid existing configured path, then environment variables, then the first valid discovered workspace. Ask the user only if this would choose an obviously wrong workspace.
