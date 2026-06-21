package com.czf.string;

import java.util.ArrayList;
import java.util.List;

/**
 * ClassName: M131_Palindrome_Partitioning
 * Package: com.czf.string
 * Description: 131. 分割回文串
 *
 * @Author 陈智飞
 * @Create 2026/6/21 00:00
 * @Version 1.0
 */
public class M131_Palindrome_Partitioning {

    public static void main(String[] args) {
        System.out.println(partition("aab"));
        System.out.println("expected: [[a, a, b], [aa, b]]");
        System.out.println(partition("a"));
        System.out.println("expected: [[a]]");
    }

    // region LeetCode solution
    public static List<List<String>> partition(String s) {
        List<List<String>> ans = new ArrayList<>();
        List<String> path = new ArrayList<>();

        backtrack(s, 0, path, ans);
        return ans;
    }

    private static void backtrack(String s, int start, List<String> path, List<List<String>> ans) {
        if (start == s.length()) {
            ans.add(new ArrayList<>(path));
            return;
        }

        for (int end = start; end < s.length(); end++) {
            String sub = s.substring(start, end + 1);
            if (isPalindrome(sub)) {
                path.add(sub);
                backtrack(s, end + 1, path, ans);
                path.remove(path.size() - 1);
            }
        }
    }

    private static boolean isPalindrome(String s) {
        for (int i = 0; i < s.length() / 2; i++) {
            if (s.charAt(i) != s.charAt(s.length() - 1 - i)) {
                return false;
            }
        }
        return true;
    }
    // endregion
}
