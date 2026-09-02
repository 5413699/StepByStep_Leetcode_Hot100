package com.czf.arraylist;

/**
 * ClassName: M055_Jump_Game
 * Package: com.czf.arraylist
 * Description: 55. 跳跃游戏
 *
 * @Author 陈智飞
 * @Create 2026/9/1
 * @Version 1.0
 */
public class M055_Jump_Game {

    public static void main(String[] args) {
        M055_Jump_Game solution = new M055_Jump_Game();

        int[] example1 = {2, 3, 1, 1, 4};
        System.out.println("example 1 actual: " + solution.canJump(example1));
        System.out.println("example 1 expected: true");

        int[] example2 = {3, 2, 1, 0, 4};
        System.out.println("example 2 actual: " + solution.canJump(example2));
        System.out.println("example 2 expected: false");
    }

    // region LeetCode solution
    public boolean canJump(int[] nums) {
        int maxReach = 0;

        for (int i = 0; i < nums.length; i++) {
            if (i > maxReach) {
                return false;
            }

            maxReach = Math.max(maxReach, i + nums[i]);
            if (maxReach >= nums.length - 1) {
                return true;
            }
        }

        return true;
    }
    // endregion
}
