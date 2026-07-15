# Random.nextInt

<!-- codex-common-function-start -->

## 简介

生成从 0（包含）到 bound（不包含）的伪随机整数，常用于随机选择数组下标，降低固定基准触发算法最坏情况的概率。

## 什么时候用

- 需要从 `[0, bound)` 中随机选择一个整数
- 需要从闭区间 `[left, right]` 随机选择数组下标
- 随机化快速选择或快速排序需要避免固定基准在有序输入上稳定退化

## 常见代码结构

### 快速选择中随机选择闭区间内的基准下标

```java
int randomIndex = left + random.nextInt(right - left + 1);
swap(nums, right, randomIndex);
int pivot = nums[right];
```

## 易错点

- `nextInt(bound)` 不会返回 bound，并且 bound 必须大于 0
- 从闭区间 `[left, right]` 取值时，长度必须写成 `right - left + 1`
- 随机基准只能保证期望复杂度，不能把最坏时间复杂度从 `O(n^2)` 改成严格 `O(n)`
- 不要在每轮分区中重复创建 Random 对象，可以复用同一个实例

## 题目使用记录

- M215-数组中的第K个最大元素：生成从 0（包含）到 bound（不包含）的伪随机整数，常用于随机选择数组下标，降低固定基准触发算法最坏情况的概率。（题目笔记：`src/notes/01.按数据结构分类/10.堆/M215_数组中的第K个最大元素.md`）

## 来源依据

- Oracle Java Random API：官方文档说明 `nextInt(int bound)` 返回 `[0, bound)` 范围内近似均匀分布的整数，并要求 bound 为正数。 (https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Random.html)

<!-- codex-common-function-end -->
