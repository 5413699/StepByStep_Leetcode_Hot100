package com.czf.heap;

import java.util.Random;

/**
 * ClassName: M215_Kth_Largest_Element_In_An_Array
 * Package: com.czf.heap
 * Description: 215. 数组中的第 K 个最大元素
 *
 * @Author 陈智飞
 * @Create 2026/7/15 00:00
 * @Version 1.0
 */
public class M215_Kth_Largest_Element_In_An_Array {

    public static void main(String[] args) {
        M215_Kth_Largest_Element_In_An_Array solution =
                new M215_Kth_Largest_Element_In_An_Array();

        int[] example1 = {3, 2, 1, 5, 6, 4};
        System.out.println("example 1 actual: " + solution.findKthLargest(example1, 2));
        System.out.println("example 1 expected: 5");

        int[] example2 = {3, 2, 3, 1, 2, 4, 5, 5, 6};
        System.out.println("example 2 actual: " + solution.findKthLargest(example2, 4));
        System.out.println("example 2 expected: 4");

        int[] allEqual = {2, 2, 2, 2, 2};
        System.out.println("all equal actual: " + solution.findKthLargest(allEqual, 3));
        System.out.println("all equal expected: 2");

        int[] ascending = {1, 2, 3, 4, 5};
        System.out.println("k equals length actual: " + solution.findKthLargest(ascending, 5));
        System.out.println("k equals length expected: 1");
    }

    // region LeetCode solution
    private static final Random random = new Random();

    public int findKthLargest(int[] nums, int k) {
        int target = nums.length - k;
        int length = nums.length;
        int left = 0;
        int right = length - 1;

        while (left <= right) {
            int[] index = partition(nums, left, right);
            if (target < index[0]) {
                right = index[0] - 1;
            } else if (target > index[1]) {
                left = index[1] + 1;
            } else {
                return nums[target];
            }
        }

        throw new IllegalStateException("Target index not found");
    }

    private int[] partition(int[] nums, int left, int right) {
        int randomIndex = left + random.nextInt(right - left + 1);
        swap(nums, right, randomIndex);
        int pivot = nums[right];

        int cur = left;
        int leftIndex = left;
        int rightIndex = right;

        while (cur <= rightIndex) {
            if (nums[cur] < pivot) {
                swap(nums, cur, leftIndex);
                leftIndex++;
                cur++;
            } else if (nums[cur] > pivot) {
                swap(nums, cur, rightIndex);
                rightIndex--;
            } else {
                cur++;
            }
        }

        return new int[]{leftIndex, rightIndex};
    }

    public void swap(int[] nums, int i, int j) {
        int temp = nums[i];
        nums[i] = nums[j];
        nums[j] = temp;
    }
    // endregion
}
