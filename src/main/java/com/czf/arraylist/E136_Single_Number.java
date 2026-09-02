package com.czf.arraylist;

/**
 * ClassName: E136_Single_Number
 * Package: com.czf.arraylist
 * Description: 136. 只出现一次的数字
 *
 * @Author 陈智飞
 * @Create 2026/9/2
 * @Version 1.0
 */
public class E136_Single_Number {

    public static void main(String[] args) {
        E136_Single_Number solution = new E136_Single_Number();

        int[] example1 = {2, 2, 1};
        System.out.println("example 1 actual: " + solution.singleNumber(example1));
        System.out.println("example 1 expected: 1");

        int[] example2 = {4, 1, 2, 1, 2};
        System.out.println("example 2 actual: " + solution.singleNumber(example2));
        System.out.println("example 2 expected: 4");

        int[] example3 = {1};
        System.out.println("example 3 actual: " + solution.singleNumber(example3));
        System.out.println("example 3 expected: 1");

        int[] example4 = {-1, 2, 2};
        System.out.println("example 4 actual: " + solution.singleNumber(example4));
        System.out.println("example 4 expected: -1");
    }

    // region LeetCode solution
public int singleNumber(int[] nums) {
    int ans = 0;

    for (int i = 0; i < nums.length; i++) {
        ans = ans ^ nums[i];
    }

    return ans;
}
    // endregion
}
