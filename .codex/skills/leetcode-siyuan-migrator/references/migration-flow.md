# Migration Flow

This migration moves legacy SiYuan algorithm notes into the new interview-training system. It is independent from daily LeetCode finish flow.

## Target Structure

```text
/算法题/面试手撕训练系统
  /题集
  /知识点
    /数据结构
    /解题方法
    /解题模式
    /常用函数
  /错题与复习
  /面试表达
  /Codex 同步日志
```

## Policy

- Dry-run by default.
- Preserve legacy pages.
- Never delete old pages automatically.
- Do not expose `<!-- codex-* -->` markers in target pages.
- Use UTF-8 Python API only.
- If a target page already exists, merge missing links and leave user-written content intact.
- If source content cannot be classified confidently, list it as a conflict instead of guessing.
- Legacy `/算法题/LeetCode Hot100/知识点/*` pages are migrated only when the title matches an explicit category whitelist. Unknown knowledge titles stay in conflicts for human review.
- Pages titled `未命名` or `Untitled` are always conflicts, even when they live under a known legacy category.
- After migration, report delete candidates only. Never delete automatically.

## API And Encoding

- Use the shared `siyuan_client.py`; it tries `lastWorkingUrl`, configured `url`, default `6806`, then local `SiYuan-Kernel.exe` listening ports.
- Do not print or persist the token.
- Build Chinese page bodies in Python with UTF-8 JSON requests, not ad hoc PowerShell strings.
- Write JSON reports to ASCII temp paths, then summarize the report for the user.

## Classification

- Problem pages: title matches `^[EMH]?\d{2,4}[-.．、]` or page is under old Hot100 `题集`.
- Data structure concepts: old `/按数据结构分类/{name}` pages and whitelisted Hot100 knowledge pages such as `二叉树`, `图论`, `矩阵`.
- Method concepts: old `/按方法分类/{name}` pages and whitelisted Hot100 knowledge pages such as `DFS`, `BFS`, `递归法`.
- Pattern concepts: whitelisted Hot100 knowledge pages such as `Flood Fill`, `网格搜索`, `连通块`.
- Function concepts: old `/常用函数/{name}` pages.
- Root/category index pages are conflicts unless explicitly handled later.

## Cleanup Advice

Return cleanup advice in two groups:

- `safeAfterTargetVerification`: old pages that were migrated to a concrete target. They are delete candidates only after the user verifies the target content.
- `reviewBeforeDelete`: conflicts such as directory pages, index pages, unknown knowledge pages, and `未命名` pages. These require manual inspection.

The final user response must explicitly state that no legacy page was deleted.

## Validation

After apply, export every touched target page and verify:

- No `????`.
- No Unicode replacement character.
- No visible `<!-- codex-` marker.
- The migrated source id appears in the target page.

If validation fails, stop and report the failing target id and check. Do not delete or clean old content after a validation failure.

## Apply Criteria

Only apply when:

- SiYuan API is reachable.
- `SIYUAN_TOKEN` is available.
- The target notebook is configured.
- Dry-run shows no destructive operations.
- User explicitly requested apply.
