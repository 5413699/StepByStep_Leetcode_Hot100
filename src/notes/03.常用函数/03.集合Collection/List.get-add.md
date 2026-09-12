# List.get / List.add

<!-- codex-common-function-start -->

## 简介

`List.get(index)` 读取指定下标的元素，`List.add(value)` 把元素追加到列表末尾。下标从 `0` 开始；访问 `List` 使用 `.get(...)`，访问数组才使用 `[...]`。

本题使用的实现类是 `ArrayList`：`get(index)` 的时间复杂度为 `O(1)`，末尾 `add(value)` 的摊还时间复杂度为 `O(1)`；扩容时某一次追加可能需要 `O(n)`。这些复杂度不能直接推广到所有 `List` 实现。

## 什么时候用

- 用列表保存长度逐步增长的一行数据。
- 用 `List<List<Integer>>` 保存长度不相同的多行数据。
- 已经生成上一行，需要按下标读取它的元素来计算当前行。

## 常见代码结构

### 追加元素并按下标读取

```java
List<Integer> row = new ArrayList<>();
row.add(1);
row.add(2);
int first = row.get(0); // 读取第一个元素，得到 1
```

### 杨辉三角：读取上一行，生成独立的新行

以下循环位于 `generate(int numRows)` 方法内，保留本题最终代码中的变量名与注释：

```java
List<List<Integer>> ans = new ArrayList<>();

// 开始加入答案
for (int i = 0; i < numRows; i++) {
    List<Integer> row = new ArrayList<>();
    // 注意第i行有i+1个元素
    for (int j = 0; j <= i; j++) {
        // 头尾的数字是1
        if (j == 0 || j == i) {
            row.add(1);
        } else {
            row.add(ans.get(i - 1).get(j - 1) + ans.get(i - 1).get(j));
        }
    }
    ans.add(row);
}
```

`ans.get(i - 1)` 先取得上一行这个列表，再调用 `.get(j)` 取得其中一个数字。每轮都创建新的 `row`，各行才会分别保存自己的元素。

## 易错点

- `ans[i]` 不能用于 `List<List<Integer>>`，应写 `ans.get(i)`。
- `get(index)` 要求 `0 <= index < size()`；列表当前没有的元素不能直接读取。
- 当前第 `i` 行有 `i + 1` 个元素，列下标必须遍历 `0..i`。本题使用 `j < i` 曾导致缺少最后一个元素，之后读取上一行时越界。
- `.add(value)` 是追加，不是覆盖。修改已有位置使用 `.set(index, value)`，且该位置必须已经存在。
- `ans.add(row)` 保存的是列表引用，不会复制 `row`；若多次加入同一个列表并继续修改，已加入的行也会受到影响。因此本题每一行都要 `new ArrayList<>()`。这一点是复习提醒，并非本次对话中实际发生的错误。

## 题目使用记录

- [E118-杨辉三角](../../01.按数据结构分类/01.数组/E118_杨辉三角.md)：我先把二维 `List` 写成 `ans[...]`，编译提示需要数组；改用 `ans.get(i - 1).get(j)` 后解决。随后将列循环的 `j < i` 修正为 `j <= i`，完整生成第 `i` 行的 `i + 1` 个数字。

## 来源依据

- [Oracle Java 21 List API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html)：`get(int index)`、`add(E e)` 与 `set(int index, E element)` 的语义及下标约束。
- [Oracle Java 21 ArrayList API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html)：`get` 等操作为常数时间，追加 `add` 为摊还常数时间。

<!-- codex-common-function-end -->
