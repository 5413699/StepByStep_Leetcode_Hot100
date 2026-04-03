package com.czf.stack;

import java.util.Stack;

/**
 * ClassName: E20_Vaild_Bracket
 * Package: com.czf.stack
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/3 13:28
 * @Version 1.0
 */
public class E20_Vaild_Bracket{
    public static void main(String[] args) {
        String s = "{}}";
        boolean ans = isValid(s);
        System.out.println(ans);
    }
    public static boolean isValid(String s) {
        // 准备一个栈
        Stack<Character> stack = new Stack<Character>();

        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            // 左括号入栈
            if (c == '(' || c == '[' || c == '{') {
                stack.push(c); //左括号存在stack中
            } else { //假如c是右括号
                if (stack.isEmpty()) {
                    return false;
                }// 栈空→没有左括号匹配
                char cur = stack.pop();//将左括号弹出
                if (c == ')' && cur != '(') {
                    return false;
                }
                if (c == ']' && cur != '[') {
                    return false;
                }
                if (c == '}' && cur != '{') {
                    return false;
                }
            }
        }
        // 遍历结束后，若栈为空说明所有括号匹配
        return stack.isEmpty();
    }

}
