package com.czf.stack;

import java.util.Stack;

/**
 * ClassName: M155_Min_Stack
 * Package: com.czf.stack
 * Description: 155. 最小栈
 *
 * @Author 陈智飞
 * @Create 2026/6/23 00:00
 * @Version 1.0
 */
public class M155_Min_Stack {

    public static void main(String[] args) {
        MinStack minStack = new MinStack();
        minStack.push(-2);
        minStack.push(0);
        minStack.push(-3);

        System.out.println("getMin actual: " + minStack.getMin());
        System.out.println("getMin expected: -3");

        minStack.pop();
        System.out.println("top actual: " + minStack.top());
        System.out.println("top expected: 0");
        System.out.println("getMin actual: " + minStack.getMin());
        System.out.println("getMin expected: -2");
    }
}

// region LeetCode solution
class MinStack {
    private final Stack<Integer> stack;
    private final Stack<Integer> minStack;

    public MinStack() {
        stack = new Stack<>();
        minStack = new Stack<>();
    }

    public void push(int val) {
        stack.push(val);

        if (minStack.isEmpty()) {
            minStack.push(val);
        } else {
            minStack.push(Math.min(val, minStack.peek()));
        }
    }

    public void pop() {
        stack.pop();
        minStack.pop();
    }

    public int top() {
        return stack.peek();
    }

    public int getMin() {
        return minStack.peek();
    }
}
// endregion
