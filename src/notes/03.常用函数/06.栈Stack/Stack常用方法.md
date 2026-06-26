# Stack.push/pop/peek/isEmpty

<!-- codex-common-function-start -->

## 简介

使用 Java `Stack` 保存还没有找到更高温度的日期下标，当前温度更高时连续弹出并填写等待天数。

## 什么时候用

- 需要维护后进先出的状态
- 需要查看或删除最近加入的元素
- 需要用辅助栈同步保存额外状态，例如当前最小值

## 常见代码结构

### 每日温度中保存未解决日期下标

```java
Stack<Integer> indexStack = new Stack<>();

while (!indexStack.isEmpty() && temperatures[i] > temperatures[indexStack.peek()]) {
    int prevIndex = indexStack.pop();
    answer[prevIndex] = i - prevIndex;
}
indexStack.push(i);
```

## 易错点

- 空栈时调用 `peek()` 或 `pop()` 会抛异常，第一次使用前要先判空
- `peek()` 只查看栈顶，不会删除元素；`pop()` 会删除并返回栈顶元素
- 辅助栈需要和主栈同步 push/pop，否则状态会错位

## 题目使用记录

- M155-最小栈：使用 Java `Stack` 完成后进先出的压栈、弹栈、查看栈顶和判空操作，常用于括号匹配、辅助栈、单调栈等题型。（题目笔记：`src/notes/01.按数据结构分类/06.栈/M155_最小栈.md`）
- M394-字符串解码：使用 Java `Stack` 保存进入括号前的重复次数和上一层字符串，遇到右括号时再弹出状态并合并当前层结果。（题目笔记：`src/notes/01.按数据结构分类/06.栈/M394_字符串解码.md`）
- M739-每日温度：使用 Java `Stack` 保存还没有找到更高温度的日期下标，当前温度更高时连续弹出并填写等待天数。（题目笔记：`src/notes/01.按数据结构分类/06.栈/M739_每日温度.md`）

## 来源依据

- Oracle Java Stack API：官方文档说明 `Stack` 表示 LIFO 栈，并提供 `push`、`pop`、`peek`、`empty` 等栈操作；`isEmpty` 来自其集合父类体系。 (https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Stack.html)

<!-- codex-common-function-end -->
