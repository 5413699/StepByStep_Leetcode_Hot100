# PriorityQueue.offer/poll/peek/size

<!-- codex-common-function-start -->

## 简介

使用一个最大堆保存较小的一半、一个最小堆保存较大的一半，通过 offer、poll、peek 和 size 动态维护中位数。

## 什么时候用

- 需要持续快速取得当前最小值或最大值
- 只需要前 k 大或前 k 小元素，不需要完整排序
- 需要用两个堆分别维护较小一半和较大一半的边界

## 常见代码结构

### 数据流中用最大堆和最小堆维护中位数

```java
PriorityQueue<Integer> small = new PriorityQueue<>(
        (a, b) -> Integer.compare(b, a)
);
PriorityQueue<Integer> large = new PriorityQueue<>();

if (small.isEmpty() || num <= small.peek()) {
    small.offer(num);
} else {
    large.offer(num);
}

if (small.size() > large.size() + 1) {
    large.offer(small.poll());
}
if (large.size() > small.size()) {
    small.offer(large.poll());
}
```

## 易错点

- 默认 PriorityQueue 是最小堆；最大堆需要反向比较器
- 构造器里的 lambda 是 Comparator 比较规则，不能放在匿名类的大括号里
- 堆中保存的对象类型和比较依据可以不同，例如保存元素值但按频率比较
- 一般场景优先用 `Integer.compare(priorityA, priorityB)`，避免两个大整数直接相减溢出
- 空堆调用 `peek()` 或 `poll()` 会返回 null，自动拆箱时可能触发空指针异常
- PriorityQueue 只保证堆顶最优，遍历或 stream 的结果不保证整体有序

## 题目使用记录

- M347-前K个高频元素：使用 PriorityQueue 按优先级维护堆顶，配合 offer、poll 和 size 动态保留最优候选。（题目笔记：`src/notes/01.按数据结构分类/10.堆/M347_前K个高频元素.md`）
- H295-数据流的中位数：使用一个最大堆保存较小的一半、一个最小堆保存较大的一半，通过 offer、poll、peek 和 size 动态维护中位数。（题目笔记：`src/notes/01.按数据结构分类/10.堆/H295_数据流的中位数.md`）

## 来源依据

- Oracle Java PriorityQueue API：官方文档说明 PriorityQueue 按自然顺序或构造器提供的 Comparator 排序，并定义 offer、poll、peek 等操作。 (https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/PriorityQueue.html)

<!-- codex-common-function-end -->
