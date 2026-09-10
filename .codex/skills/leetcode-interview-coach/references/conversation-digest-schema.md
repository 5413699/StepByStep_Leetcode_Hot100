# Conversation Digest Schema

Use this module during finish flow when the user asks to save, submit, sync, or close out a completed problem.

## Boundary

Workflow scripts cannot read the Codex chat transcript by themselves. The active Codex agent extracts the actual conversation before calling finish or publishing scripts. Scripts only render and persist the provided material. The concise digest supports readiness and indexes; it must not replace the full teaching record described below.

## Full Teaching Record and Answer Variants

Read `note-template.md` for presentation. These fields are optional for backward compatibility, but new closeouts should supply all recoverable current-problem teaching history. Preserve actual order, questions, replies, code attempts, and feedback; missing passages must be marked as missing, never invented from the digest.

```json
{
  "problemTitle": "E70-爬楼梯",
  "problemUrl": "https://leetcode.cn/problems/climbing-stairs/",
  "statementMarkdown": "完整题干、示例和限制",
  "teachingTranscript": [
    {"role": "assistant", "contentMarkdown": "实际讲解与提问。"},
    {"role": "user", "contentMarkdown": "实际回答；代码使用带语言的围栏。"},
    {"role": "assistant", "contentMarkdown": "原始反馈，包含原有口误。", "correctionMarkdown": "勘误：具体说明该教练口误，不归因给用户。"}
  ],
  "solutionVariants": [
    {"title": "数组 DP", "language": "java", "code": "可复制的有效代码，保留原注释与变量名", "timeComplexity": "O(n)", "spaceComplexity": "O(n)", "isFinal": false, "explanation": "需要查看各阶状态时适用。", "correctionMarkdown": "仅当存在必要修正或过时注释时说明。"},
    {"title": "滚动变量", "language": "java", "code": "最终有效代码", "timeComplexity": "O(n)", "spaceComplexity": "O(1)", "isFinal": true, "explanation": "只需要最终答案时适用。"}
  ],
  "trainingMarkdown": "根据真实对话整理的简短训练记录；可省略并使用 digest。",
  "complexityMarkdown": "复杂度与边界说明。",
  "reviewMarkdown": "面试表达、掌握状态与复习动作；可省略并使用 digest/readiness。",
  "conversationDigest": {}
}
```

`teachingTranscript` 项目角色仅为 `assistant` / `user`；非对话的来源或缺失说明可明确写入相应 Markdown，不能冒称原话。`solutionVariants` 非空时必须有且只有一个 `isFinal: true`。只记录真实有效版本，不要求每题多版本。`solutionJava` 继续作为旧发布目标和 Java 集成的最终答案字段，与最终 Java variant 一致。

保留用户原注释与变量名；仅规范缩进、空白、代码语言。历史错误代码保留在教学记录并加旁注；单列答案有必要修正时必须可编译且明确说明。主代理校核，不由渲染器修复或编造。

旧 payload 没有新增字段时继续支持 `noteContent` 或已有 `processMarkdown`；没有原文时展示「完整教学记录未提供」，摘要不得伪装成逐轮对话。

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
