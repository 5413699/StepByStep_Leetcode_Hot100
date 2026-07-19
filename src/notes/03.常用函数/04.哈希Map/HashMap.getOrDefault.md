# HashMap.getOrDefault

<!-- codex-common-function-start -->

## 简介

读取 key 对应的 value；当 key 不存在时返回指定默认值，常用于频率统计和状态计数。

## 什么时候用

- 需要统计元素出现次数，并让第一次出现从 0 开始累加
- 读取映射值时希望显式提供缺省值
- 希望避免先写 containsKey 再分支处理

## 常见代码结构

### 统计数组中每个元素的出现频率

```java
Map<Integer, Integer> frequencyMap = new HashMap<>();
for (int num : nums) {
    frequencyMap.put(num, frequencyMap.getOrDefault(num, 0) + 1);
}
```

## 易错点

- 方法名是 `getOrDefault`，不要拼成 `getOrDfault`
- 该方法只返回默认值，不会自动把默认值写入 Map
- 如果 key 明确映射到 null，返回结果仍可能是 null，使用包装类型拆箱时要注意

## 题目使用记录

- M347-前K个高频元素：读取 key 对应的 value；当 key 不存在时返回指定默认值，常用于频率统计和状态计数。（题目笔记：`src/notes/01.按数据结构分类/10.堆/M347_前K个高频元素.md`）

## 来源依据

- Oracle Java Map API：官方文档定义了 `getOrDefault(Object key, V defaultValue)` 的返回语义。 (https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Map.html)

<!-- codex-common-function-end -->
