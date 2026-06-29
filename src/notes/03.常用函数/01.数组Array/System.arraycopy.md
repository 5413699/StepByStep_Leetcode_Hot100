# System.arraycopy

<!-- codex-common-function-start -->

## 简介

把源数组中一段连续元素复制到目标数组的指定位置，常用于构造带哨兵的新数组或移动数组片段。

## 什么时候用

- 需要把原数组整体或部分复制到另一个数组中
- 需要在新数组前后预留哨兵、空位或扩容空间
- 需要比手写 for 循环更直接地表达连续区间复制

## 常见代码结构

### 把原数组复制到带左右哨兵的新数组中

```java
int[] barChart = new int[heights.length + 2];
System.arraycopy(heights, 0, barChart, 1, heights.length);
```

## 易错点

- 方法名是全小写的 `arraycopy`，不是 `ArrayCopy` 或 `arrayCopy`
- 参数顺序是源数组、源起点、目标数组、目标起点、复制长度
- `length` 表示复制的元素个数，不是结束下标
- 目标数组空间不足或起点为负数会触发下标越界异常

## 题目使用记录

- H084-柱状图中最大的矩形：把源数组中一段连续元素复制到目标数组的指定位置，常用于构造带哨兵的新数组或移动数组片段。（题目笔记：`src/notes/01.按数据结构分类/06.栈/H084_柱状图中最大的矩形.md`）

## 来源依据

- Oracle Java System API：官方文档定义了 `arraycopy(Object src, int srcPos, Object dest, int destPos, int length)`，用于从源数组指定位置复制指定数量的元素到目标数组指定位置。 (https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/System.html)

<!-- codex-common-function-end -->
