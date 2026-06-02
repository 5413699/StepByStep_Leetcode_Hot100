# Interview Readiness Flow

Use this module when a problem is completed or when the user asks whether they have mastered a problem.

## Goal

Assess whether the user is becoming able to independently hand-code interview problems.

## Output Shape

```json
{
  "status": ["提示后完成", "需要二刷"],
  "skills": ["网格 DFS", "连通块计数", "原地 visited 标记"],
  "weakPoints": ["DFS 越界判断", "char 与 int 区分"],
  "interviewExpression": "基本可用",
  "nextReview": ["2 天后重写", "7 天后口述"]
}
```

## Status Rules

- No initial idea: `一刷卡壳`
- Solved after hints: `提示后完成`
- Solved without hints: `独立完成`
- Boundary or implementation bug: `代码有 bug`
- Correct idea but verbose or unclear explanation: `面试表达不熟`
- Repeated concept confusion or important pattern: `需要二刷`

## Interview Expression Levels

- `不熟`: cannot describe the core invariant or why the algorithm works.
- `基本可用`: can state the main idea and complexity, but still needs polishing.
- `面试可用`: concise, correct, and can handle follow-up questions.

