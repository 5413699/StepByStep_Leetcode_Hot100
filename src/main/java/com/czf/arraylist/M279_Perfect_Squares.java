package com.czf.arraylist;

/** 279. 完全平方数 */
public class M279_Perfect_Squares {
    public int numSquares(int n) {
        // 记录每个数需要几个完全平方数
        int[] dp = new int[n + 1];
        // 和为0不需要任何完全平方数
        dp[0] = 0;
        for (int i = 1; i <= n; i++) {
            // 初始给dp[i]一个较大值，一个数需要完全平方数的数量不可能比这个数还多
            dp[i] = i + 1;
            // 枚举所有不超过 i 的完全平方数，取最少数量
            for (int j = 1; j * j <= i; j++) {
                dp[i] = Math.min(dp[i], dp[i - j * j] + 1);
            }
        }
        return dp[n];
    }
}
