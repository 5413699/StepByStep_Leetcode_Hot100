package com.czf.arraylist;

/**
 * ClassName: M075_Sort_Colors
 * Package: com.czf.arraylist
 * Description: 75. 颜色分类
 *
 * @Author 陈智飞
 * @Create 2026/9/4
 * @Version 1.0
 */
public class M075_Sort_Colors {

    public static void main(String[] args) {
        M075_Sort_Colors solution = new M075_Sort_Colors();
        check(solution, new int[]{2, 0, 2, 1, 1, 0});
        check(solution, new int[]{2, 0, 1});
        check(solution, new int[]{1, 2, 0});

        int cases = 0;
        int combinations = 1;
        for (int length = 1; length <= 8; length++) {
            combinations *= 3;
            for (int encoded = 0; encoded < combinations; encoded++) {
                int[] nums = new int[length];
                int value = encoded;
                for (int i = 0; i < length; i++) {
                    nums[i] = value % 3;
                    value /= 3;
                }
                check(solution, nums);
                cases++;
            }
        }
        System.out.println("Passed: 3 named cases and " + cases + " exhaustive cases.");
    }

    private static void check(M075_Sort_Colors solution, int[] nums) {
        // Counting is only the test oracle, not the submitted algorithm.
        int[] counts = new int[3];
        for (int num : nums) {
            counts[num]++;
        }
        solution.sortColors(nums);
        int index = 0;
        for (int color = 0; color <= 2; color++) {
            for (int j = 0; j < counts[color]; j++) {
                if (nums[index++] != color) {
                    throw new AssertionError("Incorrect color order or element count");
                }
            }
        }
    }

    // region LeetCode solution
    public void sortColors(int[] nums) {
        int nextZero = 0;
        int nextTwo = nums.length - 1;
        int i = 0;

        // 待检查区域为闭区间 [i, nextTwo]。
        while (i <= nextTwo) {
            if (nums[i] == 0) {
                // 换回的是已检查的 1，或当前位置与自身交换。
                swap(i, nextZero, nums);
                nextZero++;
                i++;
            } else if (nums[i] == 1) {
                i++;
            } else if (nums[i] == 2) {
                // 从右侧换回的元素未知，必须留在 i 继续检查。
                swap(i, nextTwo, nums);
                nextTwo--;
            }
        }
    }

    public void swap(int i, int j, int[] nums) {
        int temp = nums[i];
        nums[i] = nums[j];
        nums[j] = temp;
    }
    // endregion
}
