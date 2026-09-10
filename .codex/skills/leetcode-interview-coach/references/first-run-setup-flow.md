# First-Run Setup Flow

Use this flow when this repository is cloned to a new machine, publishing paths differ, or the user asks to set up direct YuQue publishing or full SiYuan create/update capability.

## Goal

Configure only local machine state so the skill can:

- choose whether completed learning records go to YuQue, SiYuan, both, or neither
- connect to YuQue directly without using SiYuan as an intermediate store
- discover the local SiYuan workspace
- connect to the local SiYuan HTTP API
- choose the target notebook
- write repository workflow config outside the repo
- leave the repository and SiYuan `.sy` files untouched during setup unless the user explicitly runs a sync/migration command later

## Information To Request

Ask for only the missing items after running the check script.

### Publishing target

Choose one of:

- YuQue only: direct publishing, with native Lake formatting for structured learning records; SiYuan is not required.
- SiYuan only: preserve the existing workflow.
- Both: run the two independent publishing exits.
- None: keep repository completion and Git only.

### YuQue Personal Access Token

- Read the `YuQue` environment variable. On Windows, also check the user environment registry value when the current Codex process has not inherited a value after `setx`.
- The token is used as `X-Auth-Token` and is never printed, previewed, committed, or stored in the local workflow JSON.
- If missing, ask the user to set it with `setx YuQue "the token copied from YuQue"` and restart Codex, or enter it temporarily for verification without persisting it.

### YuQue repository and parent path

- The script lists repositories available through the token. Save only the selected owner `namespace` and `repoSlug` (for example `dcczf` + `fbtgtc`; together they identify `dcczf/fbtgtc`).
- List the repository table of contents and let the user choose a parent path for new LeetCode documents, such as `算法题/题集`.
- Store the resolved parent UUID locally so a new document is never silently created in the wrong location.
- Setup performs read-only account, repository, and directory checks. It does not create a repository or document.

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

2. Explain the missing items from the check output in plain Chinese. Include where the user can find each missing item. The check must only report requirements for enabled targets.

3. After the user supplies missing information, prefer environment variables for machine-local secrets and paths:
   ```powershell
   setx SIYUAN_TOKEN "..."
   setx SIYUAN_WORKSPACE "E:\000_SIYUAN"
   setx YuQue "the YuQue Personal Access Token"
   ```

4. If SiYuan is enabled, ask the user to start SiYuan, unlock the workspace if needed, and open the target notebook. If only YuQue is enabled, no SiYuan process or workspace is required.

5. If the user supplied exact values, apply them non-interactively:
   ```powershell
   python .codex\skills\leetcode-interview-coach\scripts\configure_workflow.py --workspace "E:\000_SIYUAN" --system-root "/算法题/面试手撕训练系统" --notebook-name "notebook name" --verify --write
   ```
   Use `--notebook-id` instead of `--notebook-name` when the user provides the id.

   For direct YuQue setup, use the interactive flow so the script can list repositories and parent paths. Non-interactive values may provide the YuQue namespace and parent path when those options are available.

6. Otherwise run the interactive configuration:
   ```powershell
   python .codex\skills\leetcode-interview-coach\scripts\configure_workflow.py
   ```

7. Verify again:
   ```powershell
   python .codex\skills\leetcode-interview-coach\scripts\configure_workflow.py --check
   ```

8. Report:
   - enabled publishing targets
   - YuQue account, repository namespace, and selected parent path when enabled
   - local config path
   - detected workspace path
   - API reachability and resolved URL
   - selected notebook name/id when available
   - system root HPath
   - remaining missing items, if any

## Safety Rules

- Never edit SiYuan `.sy` files directly.
- Never store `SIYUAN_TOKEN` in the repository or final response.
- Never store `YuQue` in the repository, local workflow JSON, logs, or final response.
- Do not create or update SiYuan pages during setup. Setup only validates connectivity and writes local workflow config.
- Do not create or update YuQue documents during setup. Setup only validates access and resolves the selected repository/parent path.
- If API connection fails, ask the user to confirm SiYuan is running, the token is current, and the target notebook is open.
- If YuQue access fails, report the HTTP status without printing the token and ask the user to confirm the `YuQue` variable and repository permissions.
- If workspace detection finds multiple plausible roots, prefer a valid existing configured path, then environment variables, then the first valid discovered workspace. Ask the user only if this would choose an obviously wrong workspace.
