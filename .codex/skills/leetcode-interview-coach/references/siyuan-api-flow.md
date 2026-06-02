# SiYuan API Flow

Use this flow only for syncing completed LeetCode notes into SiYuan. This module must remain independent from coaching and scaffolding.

## Official API Contract

- Endpoint default: `http://127.0.0.1:6806`
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

Token should come from `SIYUAN_TOKEN` by default:

```json
{
  "siyuan": {
    "enabled": true,
    "url": "http://127.0.0.1:6806",
    "workspacePath": "F:\\就业资料-陈智飞\\SiYuan_czf",
    "tokenSource": "env:SIYUAN_TOKEN",
    "notebookId": "",
    "problemRootHPath": "/算法/LeetCode Hot100/题集",
    "conceptRootHPath": "/算法/LeetCode Hot100/知识点",
    "indexHPath": "/算法/LeetCode Hot100 Wiki",
    "autoCreateConceptPage": true,
    "autoUpdateConceptIndex": true,
    "pushNotification": true
  }
}
```

If config is missing, run `scripts/configure_workflow.py`.

## Sync Semantics

- Problem HPath: `{problemRootHPath}/{problemTitle}`
- Concept HPath: `{conceptRootHPath}/{conceptName}`
- Use `getIDsByHPath` to dedupe.
- Use `createDocWithMd` only for missing documents.
- Use fixed regions to avoid overwriting user content:

```markdown
<!-- codex-leetcode-start -->
...
<!-- codex-leetcode-end -->
```

Concept index region:

```markdown
## 题集

<!-- codex-leetcode-index-start -->
((problemId "Problem Title"))
<!-- codex-leetcode-index-end -->
```

After sync, return `siyuan://blocks/<id>` links for the problem and touched concepts.
