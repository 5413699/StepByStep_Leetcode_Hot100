# Math.max

<!-- codex-common-function-start -->

## 简介

`Math.max(a, b)` 返回两个数中较大的一个。它是静态方法，可以直接调用，不需要创建 `Math` 对象。两个 `int` 参数对应的返回值也是 `int`。

## 什么时候用

需要比较两个候选答案、维护最大值，或在动态规划中选择收益更大的方案时使用。

## 常见代码结构

```java
int lastOne = Math.max(lastTwo, nums[1]);
ans = Math.max(lastOne, lastTwo + nums[i]);
```

第一行比较前两间房的金额；第二行比较“不偷当前房屋”和“偷当前房屋”的收益。`Math.max` 本身不修改参数变量或数组。

## 易错点

- Java 中写 `Math.max(a, b)`，不能直接写未定义的 `max(a, b)`。
- 调用只能比较传入的数，不能修正状态定义、初始化或返回值错误。
- `lastTwo + nums[i]` 会先计算再传入函数；`Math.max` 不会防止整数加法溢出。本题最大答案不超过 20000，`int` 足够。

## 题目使用记录

- [M198-打家劫舍](../../01.按数据结构分类/01.数组/M198_打家劫舍.md)：比较偷与不偷的收益；本次 `[1,2]` 的错误来自返回未更新的 `ans`，不是 `Math.max`。

## 来源依据

- [Oracle Java Math.max(int, int)](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Math.html#max(int,int))：返回两个 `int` 值中较大的一个。

<!-- codex-common-function-end -->
