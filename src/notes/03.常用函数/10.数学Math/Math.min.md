# Math.min

<!-- codex-common-function-start -->

## 简介

`Math.min(a, b)` 返回两个数中较小的一个，常用于维护最少次数、最低代价等候选答案。它是静态方法，两个 int 参数对应的返回值也是 int。

## 什么时候用

- 需要在两个候选答案中保留较小值
- 动态规划枚举多个来源，要不断更新组成当前状态的最少次数或代价
- 需要把当前最优答案与新候选比较，并把返回值保存回状态变量

## 常见代码结构

### 零钱兑换：枚举最后一枚硬币，维护最少硬币数

```java
int[] dp = new int[amount + 1];
Arrays.fill(dp, amount + 1);
dp[0] = 0;
for (int i = 1; i <= amount; i++) {
    for (int coin : coins) {
        if (coin > i) {
            continue;
        }
        dp[i] = Math.min(dp[i], dp[i - coin] + 1);
    }
}
int answer = dp[amount] == amount + 1 ? -1 : dp[amount];
```

## 易错点

- `Math.min` 只返回较小值，需要用 `dp[i] = ...` 保存结果
- 不可达金额不能保留默认 0；面额均为正时，`amount + 1` 大于所有合法硬币数量，可作为安全哨兵
- 参数里的加法先计算；若用 `Integer.MAX_VALUE` 表示不可达，必须先判断依赖状态，避免加 1 溢出
- 先检查面额不超过当前金额，再读取 `dp[i - coin]`；面额未排序时，过大只跳过当前硬币，不能结束枚举

## 题目使用记录

- M279-完全平方数：`Math.min(a, b)` 返回两个数中较小的一个，常用于维护最少次数、最低代价等候选答案。它是静态方法，两个 int 参数对应的返回值也是 int。（题目笔记：`src/notes/01.按数据结构分类/01.数组/M279_完全平方数.md`）
- M322-零钱兑换：`Math.min(a, b)` 返回两个数中较小的一个，常用于维护最少次数、最低代价等候选答案。它是静态方法，两个 int 参数对应的返回值也是 int。（题目笔记：`src/notes/01.按数据结构分类/01.数组/M322_零钱兑换.md`）

## 来源依据

- Oracle Java Math.min(int, int)：官方文档定义了静态方法 `min(int a, int b)`：返回两个 int 中较小的值；相等时返回该值。 (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Math.html#min(int,int))

<!-- codex-common-function-end -->
