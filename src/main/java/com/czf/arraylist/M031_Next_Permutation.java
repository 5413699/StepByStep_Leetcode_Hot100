package com.czf.arraylist;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * ClassName: M031_Next_Permutation
 * Package: com.czf.arraylist
 * Description: 31. 下一个排列
 *
 * @Author 陈智飞
 * @Create 2026/9/4
 * @Version 1.0
 */
public class M031_Next_Permutation {
    public static void main(String[] args) {
        M031_Next_Permutation solution = new M031_Next_Permutation();
        check(solution, new int[]{1, 2, 3}, new int[]{1, 3, 2});
        check(solution, new int[]{3, 2, 1}, new int[]{1, 2, 3});
        check(solution, new int[]{1, 1, 5}, new int[]{1, 5, 1});
        check(solution, new int[]{1, 5, 1}, new int[]{5, 1, 1});
        check(solution, new int[]{2, 3, 1}, new int[]{3, 1, 2});
        check(solution, new int[]{5, 4, 2, 3, 1}, new int[]{5, 4, 3, 1, 2});
        check(solution, new int[]{100}, new int[]{100});
        check(solution, new int[]{100, 100}, new int[]{100, 100});
        check(solution, new int[]{0, 100, 0}, new int[]{100, 0, 0});

        // Independent oracle: enumerate arrays in lexicographic order, then
        // group by element counts. Adjacent arrays in a group are permutations.
        int cases = 0;
        int combinations = 1;
        for (int length = 1; length <= 8; length++) {
            combinations *= 3;
            Map<String, List<int[]>> groups = new HashMap<>();
            for (int encoded = 0; encoded < combinations; encoded++) {
                int[] nums = new int[length];
                int[] counts = new int[3];
                int value = encoded;
                for (int k = length - 1; k >= 0; k--) {
                    nums[k] = value % 3;
                    counts[nums[k]]++;
                    value /= 3;
                }
                String key = Arrays.toString(counts);
                groups.computeIfAbsent(key, ignored -> new ArrayList<>()).add(nums);
            }
            for (List<int[]> permutations : groups.values()) {
                for (int k = 0; k < permutations.size(); k++) {
                    check(solution, permutations.get(k).clone(),
                            permutations.get((k + 1) % permutations.size()));
                    cases++;
                }
            }
        }
        System.out.println("Passed: 9 named cases and " + cases + " exhaustive cases.");
    }

    private static void check(M031_Next_Permutation solution, int[] nums, int[] expected) {
        solution.nextPermutation(nums);
        if (!Arrays.equals(nums, expected)) {
            throw new AssertionError("Expected " + Arrays.toString(expected)
                    + ", got " + Arrays.toString(nums));
        }
    }

    // region LeetCode solution
    public void nextPermutation(int[] nums) {
        // 从右往左寻找第一个可以增大的位置。
        for (int i = nums.length - 2; i >= 0; i--) {
            if (nums[i] < nums[i + 1]) {
                // 后缀非递增：从右找第一个严格更大的数，就是最小可用数。
                int j = nums.length - 1;
                while (nums[j] <= nums[i]) {
                    j--;
                }
                swap(i, j, nums);
                reverse(i + 1, nums.length - 1, nums);
                return;
            }
        }
        // 已经是最大排列，回到最小排列。
        reverse(0, nums.length - 1, nums);
    }

    public void swap(int i, int j, int[] nums) {
        int temp = nums[i];
        nums[i] = nums[j];
        nums[j] = temp;
    }

    public void reverse(int start, int end, int[] nums) {
        for (int i = start, j = end; i < j; i++, j--) {
            swap(i, j, nums);
        }
    }
    // endregion
}
