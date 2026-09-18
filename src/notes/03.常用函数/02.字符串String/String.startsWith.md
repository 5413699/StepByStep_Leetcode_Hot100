# String.startsWith

<!-- codex-common-function-start -->

## 简介

`s.startsWith(word, start)` 判断字符串 `s` 从下标 `start` 开始的部分是否以 `word` 开头，适合用下标表示剩余字符串的递归或记忆化搜索，无需显式调用 `substring`。

## 什么时候用

- 需要判断某个候选单词能否接在当前字符串位置上
- 递归状态用起点下标表示后缀，希望直接判断前缀匹配
- 匹配成功后需要按候选单词长度推进下标

## 常见代码结构

### 单词拆分：从 start 匹配候选单词并传回成功结果

```java
for (String word : wordDict) {
    if (s.startsWith(word, start)) {
        if (dfs(s, wordDict, start + word.length(), memo)) {
            memo[start] = true;
            return true;
        }
    }
}
memo[start] = false;
return false;
```

## 易错点

- 方法名是 `startsWith`，不是 `startWith`，中间的 s 不能遗漏
- 第二个参数是当前字符串中的起点下标，不是待匹配单词的长度
- 匹配成功后的下一起点是 `start + word.length()`，不能只写 `word.length()`
- `startsWith` 只说明这一个候选前缀匹配，不保证后面的字符串也能拆分；还要判断递归结果
- `toffset` 为负数或大于字符串长度时返回 false；剩余字符不足以容纳 prefix 时也无法匹配
- 前缀比较可能检查多个字符，单次调用应按 O(word.length()) 计入复杂度分析

## 题目使用记录

- M139-单词拆分：`s.startsWith(word, start)` 判断字符串 `s` 从下标 `start` 开始的部分是否以 `word` 开头，适合用下标表示剩余字符串的递归或记忆化搜索，无需显式调用 `substring`。（题目笔记：`src/notes/01.按数据结构分类/08.字符串/M139_单词拆分.md`）

## 来源依据

- Oracle Java 17 String.startsWith(String, int)：官方文档定义 `startsWith(String prefix, int toffset)`：检查从指定下标开始的子串是否以 prefix 开头；toffset 为负数或大于字符串长度时返回 false，其余情况的结果等同于 `this.substring(toffset).startsWith(prefix)`。本次已读取并核对该 API 小节。 (https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/String.html#startsWith(java.lang.String,int))

<!-- codex-common-function-end -->
