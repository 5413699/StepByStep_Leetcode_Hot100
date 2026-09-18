# Arrays.fill

<!-- codex-common-function-start -->

## 简介

把数组或数组的一段区间批量填成同一个值，常用于初始化 DP 数组、visited 数组或棋盘行。

## 什么时候用

- 需要把一维数组整体初始化成同一个默认值
- 二维数组需要逐行初始化，例如 `Arrays.fill(board[i], '.')`
- 需要重置可复用数组状态

## 常见代码结构

### 零钱兑换：初始化不可达金额，再单独设置零金额

```java
int[] dp = new int[amount + 1];
// 先把所有金额标记为不可达。
Arrays.fill(dp, amount + 1);
// 凑出 0 元不需要硬币，作为转移起点。
dp[0] = 0;
```

## 易错点

- 先填充哨兵，再设置 `dp[0] = 0`；顺序相反会覆盖零金额的初始值
- 新建 int 数组默认全为 0，但 0 不能表示无法凑出的正金额
- `Arrays.fill(int[] a, int val)` 原地修改数组，返回值为 void，不需要重新赋给 dp
- 区间重载的右边界 `toIndex` 是开区间

## 题目使用记录

- H051-N皇后：把数组或数组的一段区间批量填成同一个值，常用于初始化 DP 数组、visited 数组或棋盘行。（题目笔记：`src/notes/01.按数据结构分类/01.数组/H051_N皇后.md`）
- M322-零钱兑换：把数组或数组的一段区间批量填成同一个值，常用于初始化 DP 数组、visited 数组或棋盘行。（题目笔记：`src/notes/01.按数据结构分类/01.数组/M322_零钱兑换.md`）

## 来源依据

- Oracle Java Arrays.fill(int[], int)：官方文档定义了 `fill(int[] a, int val)`：将指定 int 值赋给数组中的每个元素。 (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Arrays.html#fill(int%5B%5D,int))

<!-- codex-common-function-end -->
