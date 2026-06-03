# Conversation Digest Schema

Use this module during finish flow when the user asks to save, submit, sync, or close out a completed problem.

## Boundary

Workflow scripts cannot read the Codex chat transcript by themselves. The active Codex agent must summarize the visible conversation before calling the finish or SiYuan sync scripts. The scripts then persist and validate that structured digest.

## Required Behavior

Before repository closeout or SiYuan sync, create a UTF-8 JSON object named `conversationDigest` from the current problem's training conversation only. Keep it factual and concise. Record learning signals that help the user review how they reached the answer, not every message.

Current problem scope starts at the latest problem scaffold/coaching request for the problem being finished and ends at the closeout request. Exclude:

- previous LeetCode problems
- skill iteration and migration work
- SiYuan API debugging that is not part of understanding the algorithm
- environment, Git, or encoding troubleshooting unless it directly changes this problem's learning record
- casual or repeated messages that add no new learning signal

```json
{
  "firstReaction": "用户最开始的直觉或初始方案。",
  "stuckPoints": ["用户明确卡住或困惑的点。"],
  "misconceptions": [
    {
      "before": "用户原先的误解或不完整理解。",
      "after": "经过讨论后形成的正确理解。"
    }
  ],
  "breakthroughs": ["关键转折或真正理解的点。"],
  "implementationNotes": ["代码实现中需要保留的细节。"],
  "edgeCases": ["边界条件、类型坑、初始化坑。"],
  "interviewExpression": "最终适合面试时说出口的表达。",
  "reviewAdvice": ["二刷或复习时要重点检查的动作。"],
  "conceptUpdates": [
    {
      "concept": "DFS",
      "note": "本题中 DFS 的递归入口来自发现未访问陆地，递归语义是标记完整连通块。"
    }
  ]
}
```

## Field Rules

- `firstReaction`: preserve the user's original direction, even if incomplete.
- `stuckPoints`: include concrete blockers such as helper-function parameters, recursion return value, boundary checks, char/int confusion, or interview wording.
- `misconceptions`: use only when there is a real before/after correction.
- `breakthroughs`: include the reusable idea that unlocked the problem.
- `implementationNotes`: record code-level facts the user may forget.
- `edgeCases`: record cases that affect correctness.
- `interviewExpression`: use the polished final explanation when available.
- `reviewAdvice`: convert weak points into future review actions.
- `conceptUpdates`: only mention concepts already supported by the tag plan or clearly evidenced by the problem/code.

## Persistence Mapping

The SiYuan sync script maps the digest into:

- problem page: `第一反应`、`卡壳点`、`关键突破`、`思考过程`、`易错点`、`面试表达`、`复习建议`
- concept pages: `来自题目的理解`
- review pages: through readiness labels and weak points
- home pages: recent problem/concept/review entries
- audit log: whether a conversation digest was included

## Encoding Guard

If any title, HPath, tag, label, or concept name contains ASCII `?`, Unicode replacement characters, or visible mojibake detected by the sync script, stop before writing to SiYuan and report the offending field. Do not create pages such as `??` or `M200-????`.
