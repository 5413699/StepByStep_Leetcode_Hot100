# Math.min

<!-- codex-common-function-start -->

## 简介

`Math.min(a, b)` 返回两个数中较小的一个，常用于维护最少次数、最低代价等候选答案。它是静态方法，两个 int 参数对应的返回值也是 int。

## 什么时候用

- 需要在两个候选答案中保留较小值
- 动态规划枚举多个来源，要不断更新组成当前状态的最少次数或代价
- 需要把当前最优答案与新候选比较，并把返回值保存回状态变量

## 常见代码结构

### 完全平方数：枚举最后一个平方数，维护一维 DP 最小值

```java
int[] dp = new int[n + 1];
dp[0] = 0;
for (int i = 1; i <= n; i++) {
    // i 个 1 一定能组成 i，先设置一个更大的初始值。
    dp[i] = i + 1;
    for (int j = 1; j * j <= i; j++) {
        dp[i] = Math.min(dp[i], dp[i - j * j] + 1);
    }
}
```

## 易错点

- Java 中写 `Math.min(a, b)`，不能直接写未定义的 `min(a, b)`，也不能把最少数量误写成 `Math.max`
- `Math.min` 只返回比较结果，不会直接修改参数；需要用 `dp[i] = ...` 保存结果
- 求最小值的 DP 不能把所有非零状态保留为默认 0，否则合法正数候选无法更新它；完全平方数可用 `i + 1` 初始化
- 参数里的加法先计算，`Math.min` 不负责避免溢出；若依赖状态仍是 `Integer.MAX_VALUE`，必须先处理不可达状态。完全平方数按 i 递增且 j 从 1 开始，依赖状态均已求解，因此该顺序下使用 `Integer.MAX_VALUE` 初始化当前状态也安全

## 题目使用记录

- M279-完全平方数：`Math.min(a, b)` 返回两个数中较小的一个，常用于维护最少次数、最低代价等候选答案。它是静态方法，两个 int 参数对应的返回值也是 int。（题目笔记：`src/notes/01.按数据结构分类/01.数组/M279_完全平方数.md`）

## 来源依据

- Oracle Java Math.min(int, int)：官方文档定义了静态方法 `min(int a, int b)`：返回两个 int 中较小的值；相等时返回该值。 (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Math.html#min(int,int))

<!-- codex-common-function-end -->
