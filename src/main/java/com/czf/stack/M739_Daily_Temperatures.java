package com.czf.stack;

import java.util.Arrays;
import java.util.Stack;

/**
 * ClassName: M739_Daily_Temperatures
 * Package: com.czf.stack
 * Description: 739. 每日温度
 *
 * @Author 陈智飞
 * @Create 2026/6/26 00:00
 * @Version 1.0
 */
public class M739_Daily_Temperatures {

    public static void main(String[] args) {
        M739_Daily_Temperatures solution = new M739_Daily_Temperatures();

        int[] example1 = {73, 74, 75, 71, 69, 72, 76, 73};
        System.out.println("示例1 actual: " + Arrays.toString(solution.dailyTemperatures(example1)));
        System.out.println("示例1 expected: [1, 1, 4, 2, 1, 1, 0, 0]");

        int[] example2 = {30, 40, 50, 60};
        System.out.println("示例2 actual: " + Arrays.toString(solution.dailyTemperatures(example2)));
        System.out.println("示例2 expected: [1, 1, 1, 0]");

        int[] example3 = {30, 60, 90};
        System.out.println("示例3 actual: " + Arrays.toString(solution.dailyTemperatures(example3)));
        System.out.println("示例3 expected: [1, 1, 0]");
    }

    // region LeetCode solution
    public int[] dailyTemperatures(int[] temperatures) {
        int[] answer = new int[temperatures.length];
        Stack<Integer> indexStack = new Stack<>();

        for (int i = 0; i < temperatures.length; i++) {
            while (!indexStack.isEmpty() && temperatures[i] > temperatures[indexStack.peek()]) {
                int prevIndex = indexStack.pop();
                answer[prevIndex] = i - prevIndex;
            }

            indexStack.push(i);
        }

        return answer;
    }
    // endregion
}
