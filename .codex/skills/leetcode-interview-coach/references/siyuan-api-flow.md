# SiYuan API Flow

Use this flow only for syncing completed LeetCode notes into SiYuan. This module must remain independent from coaching and scaffolding.

## Official API Contract

- Endpoint default candidate: `http://127.0.0.1:6806`
- Method: POST
- Body: JSON
- Header: `Authorization: Token <token>`
- Success response: `code == 0`
- Token location for users: SiYuan `设置 > 关于 > API Token`

Use only public APIs from `siyuan-note/siyuan`:

- `/api/system/version`
- `/api/notebook/lsNotebooks`
- `/api/filetree/getIDsByHPath`
- `/api/filetree/createDocWithMd`
- `/api/export/exportMdContent` for optional diagnostics only; do not use it as a write-back or user-facing validation source.
- `/api/block/updateBlock`
- `/api/block/appendBlock`
- `/api/sqlite/flushTransaction`
- `/api/notification/pushMsg`
- `/api/notification/pushErrMsg`

Do not edit `.sy` files directly.

## Config

Local config path:

```text
%USERPROFILE%\.codex\leetcode-hot100-workflow.local.json
```

Token should come from `SIYUAN_TOKEN` by default. The actual URL may be auto-detected and written back to config:

For first-run or new-machine setup, use `references/first-run-setup-flow.md` before attempting sync.

Workspace path detection is runtime-first:

1. Respect an existing configured `workspacePath` when it points to a valid SiYuan workspace directory.
2. Try environment variables `SIYUAN_WORKSPACE`, `SIYUAN_WORKSPACE_PATH`, then `SIYUAN_DATA_DIR`.
3. Try known local candidates, including `E:\000_SIYUAN`.
4. Try common user and drive-level folders such as `%USERPROFILE%\Documents\SiYuan`, `%USERPROFILE%\SiYuan`, and `<drive>:\SiYuan`.
5. A valid workspace must contain `conf`, `data`, and `repo` directories.

```json
{
  "siyuan": {
    "enabled": true,
    "url": "http://127.0.0.1:6806",
    "urlAutoDetect": true,
    "lastWorkingUrl": "",
    "workspacePath": "E:\\000_SIYUAN",
    "tokenSource": "env:SIYUAN_TOKEN",
    "notebookId": "",
    "autoCreateConceptPage": true,
    "autoUpdateConceptIndex": true,
    "pushNotification": true
  },
  "wikiPolicy": {
    "systemRootHPath": "/算法题/面试手撕训练系统"
  }
}
```

If config is missing, run `scripts/configure_workflow.py`.

## URL Detection

Before sync:

1. Try `lastWorkingUrl`.
2. Try configured `url`.
3. Try `http://127.0.0.1:6806`.
4. If all fail, inspect local listening ports for `SiYuan-Kernel.exe`.
5. Probe candidates with `/api/system/version`.
6. Write the successful URL back to `lastWorkingUrl`.

Do not print the token.

## Sync Semantics

- Problem HPath: `{systemRootHPath}/题集/{problemTitle}`
- Concept HPaths are defined by `references/siyuan-wiki-policy.md`.
- Validate all generated titles, labels, concept names, tags, and HPaths before any write. If corrupted metadata is detected, stop and report the field; do not create fallback pages.
- Validate the full sync payload before any write. In body text, reject `????`, Unicode replacement characters, and visible mojibake; in titles, labels, tags, concepts, HPaths, and other metadata, also reject ASCII `?`.
- Use `getIDsByHPath` to dedupe.
- Use `createDocWithMd` only for missing documents.
- Do not expose `<!-- codex-* -->` markers in SiYuan pages.
- Do not pass Chinese page bodies through PowerShell pipelines, here-strings, inline `python -` snippets containing Chinese literals, or Git command output decoded by the host console. Build metadata with `scripts/write_utf8_metadata.py` from a UTF-8 source directory, or validate an existing UTF-8 JSON file at an ASCII temp path, then pass only the path to the sync script.
- If a Git branch name is Chinese or is returned as mojibake on Windows, omit it from the sync payload or replace it with an ASCII-safe display value. Keep the commit hash.

After sync, validate current-block Markdown from `/api/block/getBlockKramdown` and return `siyuan://blocks/<id>` links for the problem and touched pages.
