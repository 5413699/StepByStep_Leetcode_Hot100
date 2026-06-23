# new String(char[])

<!-- codex-common-function-start -->

## 简介

把一段 `char[]` 复制成不可变字符串，常用于把棋盘行、字符路径或临时字符数组转换成答案。

## 什么时候用

- 当前结果保存在 `char[]` 中，但返回值要求 `String`
- 需要把棋盘的某一行转换成答案字符串
- 希望保存当前字符数组快照，避免后续修改影响答案

## 常见代码结构

### 把棋盘一行转换成答案字符串

```java
List<String> curAns = new ArrayList<>();
for (int i = 0; i < n; i++) {
    curAns.add(new String(board[i]));
}
```

## 易错点

- `new String(char[])` 会复制当前字符内容，后续修改原数组不会改变字符串
- 不要把整张 `char[][]` 直接传给 `new String`，需要逐行转换
- 如果只需要部分字符，使用带 `offset` 和 `count` 的构造器或先控制数组范围

## 题目使用记录

- H051-N皇后：把一段 `char[]` 复制成不可变字符串，常用于把棋盘行、字符路径或临时字符数组转换成答案。（题目笔记：`src/notes/01.按数据结构分类/01.数组/H051_N皇后.md`）

## 来源依据

- Oracle Java String API：官方文档说明 `String` 表示字符序列，并给出从 `char[]` 创建字符串的用法。 (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html)

<!-- codex-common-function-end -->
