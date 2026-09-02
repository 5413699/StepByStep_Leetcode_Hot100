package com.czf.arraylist;

/**
 * ClassName: E169_Majority_Element
 * Package: com.czf.arraylist
 * Description: 169. 多数元素
 *
 * @Author 陈智飞
 * @Create 2026/9/2
 * @Version 1.0
 */
public class E169_Majority_Element {

    public static void main(String[] args) {
        E169_Majority_Element solution = new E169_Majority_Element();

        int[] example1 = {3, 2, 3};
        System.out.println("example 1 actual: " + solution.majorityElement(example1));
        System.out.println("example 1 expected: 3");

        int[] example2 = {2, 2, 1, 1, 1, 2, 2};
        System.out.println("example 2 actual: " + solution.majorityElement(example2));
        System.out.println("example 2 expected: 2");

        int[] example3 = {1};
        System.out.println("example 3 actual: " + solution.majorityElement(example3));
        System.out.println("example 3 expected: 1");
    }

    // region LeetCode solution
public int majorityElement(int[] nums) {
    int candidate = 0;
    int count = 0;

    for (int i = 0; i < nums.length; i++) {
        if (count == 0) {
            candidate = nums[i];
        }

        if (nums[i] != candidate) {
            count--;
        } else {
            count++;
        }
    }

    return candidate;
}
    // endregion
}
