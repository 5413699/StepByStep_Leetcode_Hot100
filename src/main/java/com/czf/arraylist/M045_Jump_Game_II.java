package com.czf.arraylist;

/**
 * ClassName: M045_Jump_Game_II
 * Package: com.czf.arraylist
 * Description: 45. 跳跃游戏 II
 *
 * @Author 陈智飞
 * @Create 2026/9/2
 * @Version 1.0
 */
public class M045_Jump_Game_II {

    public static void main(String[] args) {
        M045_Jump_Game_II solution = new M045_Jump_Game_II();

        int[] example1 = {2, 3, 1, 1, 4};
        System.out.println("example 1 actual: " + solution.jump(example1));
        System.out.println("example 1 expected: 2");

        int[] example2 = {2, 3, 0, 1, 4};
        System.out.println("example 2 actual: " + solution.jump(example2));
        System.out.println("example 2 expected: 2");

        int[] example3 = {0};
        System.out.println("example 3 actual: " + solution.jump(example3));
        System.out.println("example 3 expected: 0");
    }

    // region LeetCode solution
public int jump(int[] nums) {
    int step = 0;
    int curEnd = 0;
    int farthest = 0;

    for (int i = 0; i < nums.length - 1; i++) {
        farthest = Math.max(farthest, i + nums[i]);

        if (farthest >= nums.length - 1) {
            return step + 1;
        }

        if (i == curEnd) {
            curEnd = farthest;
            step++;
        }
    }

    return step;
}
    // endregion
}
