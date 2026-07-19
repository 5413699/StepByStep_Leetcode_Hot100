# PriorityQueue.offer/poll/size

<!-- codex-common-function-start -->

## 简介

使用 PriorityQueue 按优先级维护堆顶，配合 offer、poll 和 size 动态保留最优候选。

## 什么时候用

- 只需要前 k 大或前 k 小元素，不需要完整排序
- 每次加入候选后要快速淘汰当前最弱候选
- 需要通过比较器让对象按频率、距离或其他字段确定优先级

## 常见代码结构

### 按频率维护大小为 k 的最小堆

```java
PriorityQueue<Integer> minHeap = new PriorityQueue<>(
        (a, b) -> frequencyMap.get(a) - frequencyMap.get(b)
);

for (int num : frequencyMap.keySet()) {
    minHeap.offer(num);
    if (minHeap.size() > k) {
        minHeap.poll();
    }
}
```

## 易错点

- 默认 PriorityQueue 是最小堆；最大堆需要反向比较器
- 构造器里的 lambda 是 Comparator 比较规则，不能放在匿名类的大括号里
- 堆中保存的对象类型和比较依据可以不同，例如保存元素值但按频率比较
- 一般场景优先用 `Integer.compare(priorityA, priorityB)`，避免两个大整数直接相减溢出
- PriorityQueue 只保证堆顶最优，遍历或 stream 的结果不保证整体有序

## 题目使用记录

- M347-前K个高频元素：使用 PriorityQueue 按优先级维护堆顶，配合 offer、poll 和 size 动态保留最优候选。（题目笔记：`src/notes/01.按数据结构分类/10.堆/M347_前K个高频元素.md`）

## 来源依据

- Oracle Java PriorityQueue API：官方文档说明 PriorityQueue 按自然顺序或构造器提供的 Comparator 排序，并定义 offer、poll、peek 等操作。 (https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/PriorityQueue.html)

<!-- codex-common-function-end -->
