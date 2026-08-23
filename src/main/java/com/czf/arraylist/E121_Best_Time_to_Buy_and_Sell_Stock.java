package com.czf.arraylist;

/**
 * ClassName: E121_Best_Time_to_Buy_and_Sell_Stock
 * Package: com.czf.arraylist
 * Description: 121. 买卖股票的最佳时机
 *
 * @Author 陈智飞
 * @Create 2026/8/23 00:00
 * @Version 1.0
 */
public class E121_Best_Time_to_Buy_and_Sell_Stock {

    public static void main(String[] args) {
        E121_Best_Time_to_Buy_and_Sell_Stock solution =
                new E121_Best_Time_to_Buy_and_Sell_Stock();

        int[] example1 = {7, 1, 5, 3, 6, 4};
        System.out.println("example 1 actual: " + solution.maxProfit(example1));
        System.out.println("example 1 expected: 5");

        int[] example2 = {7, 6, 4, 3, 1};
        System.out.println("example 2 actual: " + solution.maxProfit(example2));
        System.out.println("example 2 expected: 0");

        int[] singleDay = {5};
        System.out.println("single day actual: " + solution.maxProfit(singleDay));
        System.out.println("single day expected: 0");

        int[] delayedProfit = {5, 4, 3, 10};
        System.out.println("delayed profit actual: " + solution.maxProfit(delayedProfit));
        System.out.println("delayed profit expected: 7");
    }

    // region LeetCode solution
    public int maxProfit(int[] prices) {
        int minPrice = Integer.MAX_VALUE;
        int ans = 0;

        // 遍历每天的价格
        for (int price : prices) {
            // 更新买入价：只记录当前为止的最低价格
            if (price < minPrice) {
                minPrice = price;
            }

            // 今天作为卖出日，计算今天能够获得的最大利润
            ans = Math.max(ans, price - minPrice);
        }

        return ans;
    }
    // endregion
}
