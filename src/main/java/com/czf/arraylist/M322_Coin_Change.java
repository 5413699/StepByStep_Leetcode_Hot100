package com.czf.arraylist;

import java.util.Arrays;

/** 322. 零钱兑换 */
public class M322_Coin_Change {
    // region LeetCode solution
    public int coinChange(int[] coins, int amount) {
        // 记录每个金额需要的硬币数
        int[] dp = new int[amount + 1];
        // 先将所有金额标记为暂时无法凑出
        Arrays.fill(dp, amount + 1);

        // 0元不需要硬币
        dp[0] = 0;
        // 计算最少需要的硬币个数
        for (int i = 1; i <= amount; i++) {
            // 枚举每一枚硬币
            for (int j = 0; j < coins.length; j++) {
                // 假如当前硬币超过了需要金额，说明凑不出了
                // 补充：只是当前这枚硬币不能用，其他面额仍需继续尝试。
                if (coins[j] > i) {
                    continue;
                }
                // 假如加入当前硬币
                dp[i] = Math.min(dp[i - coins[j]] + 1, dp[i]);
            }
        }
        // 假如最后都还没凑出来
        if (dp[amount] == amount + 1) {
            return -1;
        }

        return dp[amount];
    }
    // endregion
}
