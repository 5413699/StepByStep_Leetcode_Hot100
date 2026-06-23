<!-- codex-common-function-start -->

# Arrays.fill

## 简介

把数组或数组的一段区间批量填成同一个值，常用于初始化 DP 数组、visited 数组或棋盘行。

## 什么时候用

- 需要把一维数组整体初始化成同一个默认值
- 二维数组需要逐行初始化，例如 `Arrays.fill(board[i], '.')`
- 需要重置可复用数组状态

## 常见代码结构

### 按行初始化二维棋盘

```java
char[][] board = new char[n][n];
for (int i = 0; i < n; i++) {
    Arrays.fill(board[i], '.');
}
```

## 易错点

- 二维数组不能一次 `Arrays.fill(board, '.')`，要按行填充
- 对象数组使用 `Arrays.fill` 会把同一个对象引用放到每个位置
- 区间重载的右边界 `toIndex` 是开区间

## 题目使用记录

- H051-N皇后：把数组或数组的一段区间批量填成同一个值，常用于初始化 DP 数组、visited 数组或棋盘行。（题目笔记：`src/notes/01.按数据结构分类/01.数组/H051_N皇后.md`）

## 来源依据

- Oracle Java Arrays API：官方文档定义了 `fill(char[] a, char val)` 及区间重载。 (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Arrays.html)

<!-- codex-common-function-end -->
