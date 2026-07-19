# Stream.mapToInt/toArray

<!-- codex-common-function-start -->

## 简介

把对象流映射为 IntStream，并收集成基本类型 `int[]`，常用于将 `Collection<Integer>` 转换为 LeetCode 要求的数组。

## 什么时候用

- 已有 Collection<Integer>，返回值要求 int[]
- 需要在收集数组前把对象字段映射为 int
- 需要通过方法引用 `Integer::intValue` 完成拆箱

## 常见代码结构

### 把 PriorityQueue<Integer> 转成 int[]

```java
return minHeap.stream()
        .mapToInt(Integer::intValue)
        .toArray();
```

## 易错点

- 集合自身的 `toArray()` 返回 Object[]，不能直接赋给 int[]
- `mapToInt` 需要返回 int 的映射函数，`Integer::intValue` 用于拆箱
- PriorityQueue 的 stream 不保证频率排序；只有题目允许任意顺序时才能直接返回

## 题目使用记录

- M347-前K个高频元素：把对象流映射为 IntStream，并收集成基本类型 `int[]`，常用于将 `Collection<Integer>` 转换为 LeetCode 要求的数组。（题目笔记：`src/notes/01.按数据结构分类/10.堆/M347_前K个高频元素.md`）

## 来源依据

- Oracle Java Stream API：官方文档定义了 mapToInt 将对象流转换为 IntStream。 (https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/Stream.html)
- Oracle Java IntStream API：官方文档定义了 IntStream.toArray 返回包含流元素的 int[]。 (https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/stream/IntStream.html)

<!-- codex-common-function-end -->
