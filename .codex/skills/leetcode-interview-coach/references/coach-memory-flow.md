# Coach Memory Flow

Use this flow inside coaching only when SiYuan is available and the current problem has clear high-confidence tags. This module keeps long-term memory lightweight; it must not load full historical notes.

## Goal

Use SiYuan as the user's long-term learning memory without making coaching mechanical or context-heavy.

## Workflow

1. Infer 1-3 likely concepts from the current problem statement and local placement, for example `回溯`, `数组`, `字符串`, `图论`.
2. Run `scripts/extract_siyuan_coach_memory.py` with those concepts and `--max-bullets 8`.
3. If the script returns `enabled: false`, empty memory, or an error, continue normal coaching without mentioning the failure unless it affects the user's request.
4. Use returned memory only to tune hints:
   - surface likely old weak points earlier,
   - ask sharper questions,
   - compare with prior patterns only when helpful.
5. Do not paste the memory dump to the user. Paraphrase at most 1-2 relevant reminders.

## Script Interface

```powershell
python .codex\skills\leetcode-interview-coach\scripts\extract_siyuan_coach_memory.py `
  --concept 回溯 `
  --concept 数组 `
  --max-bullets 8
```

Output shape:

```json
{
  "enabled": true,
  "memoryBullets": ["回溯：M039-组合总和：..."],
  "relatedProblems": [{"title": "M039-组合总和", "url": "siyuan://blocks/..."}],
  "reviewWarnings": ["回溯：..."],
  "sourceLinks": ["siyuan://blocks/..."]
}
```

## Coaching Use

- Keep the user's current thinking primary. Memory is a quiet reference, not a script to recite.
- For 回溯题, use memory to choose between these prompts:
  - 全排列：顺序不同算不同，通常考虑 `used`。
  - 子集：顺序不同不算不同，不能重复用，通常递归传 `i + 1`。
  - 组合总和：顺序不同不算不同，可以重复用，通常递归传 `i`。
  - 电话号码组合：每层对应输入位置，通常不需要 `startIndex`。
- If the user repeats an old bug, name it gently and specifically, for example: “这个点你在 39 题也碰到过：`path` 进答案时要拍快照。”

## Limits

- Do not read full problem pages during normal coaching.
- Do not read more than 8 memory bullets.
- Do not block coaching on SiYuan connection failures.
- Do not expose raw kramdown, audit logs, payload JSON, or sync internals to the user.
