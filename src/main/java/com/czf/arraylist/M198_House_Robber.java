package com.czf.arraylist;

/**
 * 198. 打家劫舍
 *
 * @Author 陈智飞
 * @Create 2026/9/12
 */
public class M198_House_Robber {
    public static void main(String[] args) {
        M198_House_Robber solution = new M198_House_Robber();
        int[][] cases = {{1, 2, 3, 1}, {2, 7, 9, 3, 1}, {1}, {1, 2}, {2, 1}, {0, 0}, {2, 1, 1, 2}};
        int[] expected = {4, 12, 1, 2, 2, 0, 4};
        for (int i = 0; i < cases.length; i++) {
            if (solution.rob(cases[i]) != expected[i]) {
                throw new AssertionError("Unexpected result for case " + i);
            }
        }
        System.out.println("Passed samples and boundary cases.");
    }

    // region LeetCode solution
    public int rob(int[] nums) {
        int length = nums.length;
        int ans = nums[0];
        // 初始化
        int lastTwo = nums[0];
        if (nums.length == 1) {
            return lastTwo;
        }
        int lastOne = Math.max(lastTwo, nums[1]);

        for (int i = 2; i < nums.length; i++) {
            ans = Math.max(lastOne, lastTwo + nums[i]);
            lastTwo = lastOne;
            lastOne = ans;
        }
        return lastOne;
    }
    // endregion
}
