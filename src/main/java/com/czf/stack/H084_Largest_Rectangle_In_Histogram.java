package com.czf.stack;

import java.util.Stack;

/**
 * ClassName: H084_Largest_Rectangle_In_Histogram
 * Package: com.czf.stack
 * Description: 84. 柱状图中最大的矩形
 *
 * @Author 陈智飞
 * @Create 2026/6/29 00:00
 * @Version 1.0
 */
public class H084_Largest_Rectangle_In_Histogram {

    public static void main(String[] args) {
        int[] heights = {2, 1, 5, 6, 2, 3};
        System.out.println(largestRectangleArea(heights));
        System.out.println("expected: 10");

        int[] heights2 = {2, 4};
        System.out.println(largestRectangleArea(heights2));
        System.out.println("expected: 4");
    }

    // region LeetCode solution
    public static int largestRectangleArea(int[] heights) {
        int[] barChart = new int[heights.length + 2];
        System.arraycopy(heights, 0, barChart, 1, heights.length);

        Stack<Integer> stack = new Stack<>();
        stack.push(0);

        int ans = 0;
        for (int i = 1; i < barChart.length; i++) {
            while (barChart[stack.peek()] > barChart[i]) {
                int height = barChart[stack.pop()];
                int width = i - stack.peek() - 1;
                ans = Math.max(ans, height * width);
            }
            stack.push(i);
        }

        return ans;
    }
    // endregion
}
