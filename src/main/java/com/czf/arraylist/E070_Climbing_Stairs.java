package com.czf.arraylist;

/**
 * 70. 爬楼梯
 * @Author 陈智飞
 * @Create 2026/9/9
 */
public class E070_Climbing_Stairs {
    public static void main(String[] args) {
        E070_Climbing_Stairs solution = new E070_Climbing_Stairs();
        // Independent counting oracle: choose positions for each two-step move.
        for (int n = 1; n <= 45; n++) {
            long expected = 0;
            for (int twos = 0; twos <= n / 2; twos++) {
                long combinations = 1;
                for (int k = 1; k <= twos; k++) {
                    combinations = combinations * (n - twos - k + 1) / k;
                }
                expected += combinations;
            }
            if (solution.climbStairs(n) != expected) {
                throw new AssertionError("Failed for n=" + n);
            }
        }
        System.out.println("Passed all 45 valid inputs.");
    }

    // region LeetCode solution
    public int climbStairs(int n) {
        // 只保存前两个台阶的方法数。
        int lastTwo = 1;
        if (n == 1) {
            return lastTwo;
        }

        int lastOne = 2;
        // n == 2 时循环不执行，直接返回 2。
        int answer = 2;

        for (int i = 3; i <= n; i++) {
            answer = lastOne + lastTwo;
            // 先算新状态，再将两个旧状态向前移动。
            lastTwo = lastOne;
            lastOne = answer;
        }
        return answer;
    }
    // endregion
}
