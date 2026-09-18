package com.czf.arraylist;

/** 279. 完全平方数 */
public class M279_Perfect_Squares {
    // region LeetCode solution
    public int numSquares(int n) {
        // 记录每个数需要几个完全平方数
        int[] dp = new int[n + 1];
        // 和为0只需要1个平方数
        // 勘误：和为0不需要任何完全平方数，下面的 dp[0] = 0 是正确的。
        dp[0] = 0;

        // 逐个后推需要完全平方数的数量
        for (int i = 1; i <= n; i++) {
            // 初始给dp[i]一个较大值，一个数需要完全平方数的数量不可能比这个数还多
            dp[i] = i + 1;
            // 怎么写注释？
            // 补充：枚举最后一个完全平方数 j*j，剩余和为 i-j*j，取总数量的最小值。
            for (int j = 1; j * j <= i; j++) {
                dp[i] = Math.min(dp[i], dp[i - j * j] + 1);
            }
        }

        return dp[n];
    }
    // endregion
}
