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
- `/api/export/exportMdContent`
- `/api/block/updateBlock`
- `/api/block/appendBlock`
- `/api/sqlite/flushTransaction`
- `/api/notification/pushMsg`
- `/api/notification/pushErrMsg`

Do not edit `.sy` files directly.

## Config

Local config path:

```text
C:\Users\ADMIN\.codex\leetcode-hot100-workflow.local.json
```

Token should come from `SIYUAN_TOKEN` by default. The actual URL may be auto-detected and written back to config:

```json
{
  "siyuan": {
    "enabled": true,
    "url": "http://127.0.0.1:6806",
    "urlAutoDetect": true,
    "lastWorkingUrl": "",
    "workspacePath": "F:\\就业资料-陈智飞\\SiYuan_czf",
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
- Use `getIDsByHPath` to dedupe.
- Use `createDocWithMd` only for missing documents.
- Do not expose `<!-- codex-* -->` markers in SiYuan pages.

After sync, validate exported content and return `siyuan://blocks/<id>` links for the problem and touched pages.
