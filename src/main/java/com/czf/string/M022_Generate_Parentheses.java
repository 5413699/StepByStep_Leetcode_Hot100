package com.czf.string;

import java.util.ArrayList;
import java.util.List;

/**
 * ClassName: M022_Generate_Parentheses
 * Package: com.czf.string
 * Description: 22. 括号生成
 *
 * @Author 陈智飞
 * @Create 2026/6/15 00:00
 * @Version 1.0
 */
public class M022_Generate_Parentheses {

    public static void main(String[] args) {
        System.out.println(generateParenthesis(3));
        System.out.println("expected size: 5");
        System.out.println(generateParenthesis(1));
        System.out.println("expected: [()]");
    }

    // region LeetCode solution
    public static List<String> generateParenthesis(int n) {
        List<String> ans = new ArrayList<>();
        StringBuilder path = new StringBuilder();

        backtrack(n, 0, 0, path, ans);
        return ans;
    }

    private static void backtrack(int n, int left, int right, StringBuilder path, List<String> ans) {
        if (path.length() == 2 * n) {
            ans.add(path.toString());
            return;
        }

        if (left < n) {
            path.append('(');
            backtrack(n, left + 1, right, path, ans);
            path.deleteCharAt(path.length() - 1);
        }

        if (right < left) {
            path.append(')');
            backtrack(n, left, right + 1, path, ans);
            path.deleteCharAt(path.length() - 1);
        }
    }
    // endregion
}
