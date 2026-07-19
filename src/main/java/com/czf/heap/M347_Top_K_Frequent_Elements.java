package com.czf.heap;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;

/**
 * ClassName: M347_Top_K_Frequent_Elements
 * Package: com.czf.heap
 * Description: 347. 前 K 个高频元素
 *
 * @Author 陈智飞
 * @Create 2026/7/19 00:00
 * @Version 1.0
 */
public class M347_Top_K_Frequent_Elements {

    public static void main(String[] args) {
        M347_Top_K_Frequent_Elements solution = new M347_Top_K_Frequent_Elements();

        int[] example1 = {1, 1, 1, 2, 2, 3};
        System.out.println("example 1 actual: " + Arrays.toString(solution.topKFrequent(example1, 2)));
        System.out.println("example 1 expected: [1, 2] (any order)");

        int[] example2 = {1};
        System.out.println("example 2 actual: " + Arrays.toString(solution.topKFrequent(example2, 1)));
        System.out.println("example 2 expected: [1]");

        int[] example3 = {1, 2, 1, 2, 1, 2, 3, 1, 3, 2};
        System.out.println("example 3 actual: " + Arrays.toString(solution.topKFrequent(example3, 2)));
        System.out.println("example 3 expected: [1, 2] (any order)");
    }

    // region LeetCode solution
    public int[] topKFrequent(int[] nums, int k) {
        Map<Integer, Integer> frequencyMap = new HashMap<>();
        for (int num : nums) {
            frequencyMap.put(
                    num,
                    frequencyMap.getOrDefault(num, 0) + 1
            );
        }

        PriorityQueue<Integer> minHeap = new PriorityQueue<>(
                (a, b) -> frequencyMap.get(a) - frequencyMap.get(b)
        );

        for (int num : frequencyMap.keySet()) {
            minHeap.offer(num);
            if (minHeap.size() > k) {
                minHeap.poll();
            }
        }

        return minHeap.stream()
                .mapToInt(Integer::intValue)
                .toArray();
    }
    // endregion
}
