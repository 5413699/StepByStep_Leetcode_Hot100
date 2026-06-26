package com.czf.stack;

import java.util.Stack;

/**
 * ClassName: M394_Decode_String
 * Package: com.czf.stack
 * Description: 394. 字符串解码
 *
 * @Author 陈智飞
 * @Create 2026/6/26 00:00
 * @Version 1.0
 */
public class M394_Decode_String {

    public static void main(String[] args) {
        M394_Decode_String solution = new M394_Decode_String();

        System.out.println("示例1 actual: " + solution.decodeString("3[a]2[bc]"));
        System.out.println("示例1 expected: aaabcbc");
        System.out.println("示例2 actual: " + solution.decodeString("3[a2[c]]"));
        System.out.println("示例2 expected: accaccacc");
        System.out.println("示例3 actual: " + solution.decodeString("2[abc]3[cd]ef"));
        System.out.println("示例3 expected: abcabccdcdcdef");
        System.out.println("示例4 actual: " + solution.decodeString("abc3[cd]xyz"));
        System.out.println("示例4 expected: abccdcdcdxyz");
    }

    // region LeetCode solution
    public String decodeString(String s) {
        Stack<Integer> countStack = new Stack<>();
        Stack<StringBuilder> stringStack = new Stack<>();
        StringBuilder cur = new StringBuilder();
        int num = 0;

        for (char c : s.toCharArray()) {
            if (Character.isDigit(c)) {
                num = num * 10 + (c - '0');
            } else if (c == '[') {
                countStack.push(num);
                stringStack.push(cur);
                num = 0;
                cur = new StringBuilder();
            } else if (c == ']') {
                int repeatNum = countStack.pop();
                StringBuilder prev = stringStack.pop();
                for (int i = 0; i < repeatNum; i++) {
                    prev.append(cur);
                }
                cur = prev;
            } else {
                cur.append(c);
            }
        }

        return cur.toString();
    }
    // endregion
}
