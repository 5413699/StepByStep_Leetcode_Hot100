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
  /错题与复习
  /面试表达
  /Codex 同步日志
```

## Policy

- Dry-run by default.
- Preserve legacy pages.
- Do not expose `<!-- codex-* -->` markers in target pages.
- Use UTF-8 Python API only.
- If a target page already exists, merge missing links and leave user-written content intact.
- If source content cannot be classified confidently, list it as a conflict instead of guessing.

## Apply Criteria

Only apply when:

- SiYuan API is reachable.
- `SIYUAN_TOKEN` is available.
- The target notebook is configured.
- Dry-run shows no destructive operations.
- User explicitly requested apply.

