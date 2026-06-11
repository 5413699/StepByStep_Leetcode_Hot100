package com.czf.string;

import java.util.ArrayList;
import java.util.List;

/**
 * ClassName: M017_Letter_Combinations_Of_A_Phone_Number
 * Package: com.czf.string
 * Description: 17. 电话号码的字母组合
 *
 * @Author 陈智飞
 * @Create 2026/6/11 00:00
 * @Version 1.0
 */
public class M017_Letter_Combinations_Of_A_Phone_Number {

    public static void main(String[] args) {
        System.out.println(letterCombinations("23"));
        System.out.println("expected size: 9");
        System.out.println(letterCombinations("2"));
        System.out.println("expected size: 3");
    }

    // region LeetCode solution
    public static List<String> letterCombinations(String digits) {
        List<String> ans = new ArrayList<>();
        if (digits == null || digits.length() == 0) {
            return ans;
        }

        String[] map = {
                "", "", "abc", "def", "ghi",
                "jkl", "mno", "pqrs", "tuv", "wxyz"
        };
        StringBuilder path = new StringBuilder();

        backtrack(digits, 0, path, ans, map);
        return ans;
    }

    private static void backtrack(String digits, int index, StringBuilder path, List<String> ans, String[] map) {
        if (index == digits.length()) {
            ans.add(path.toString());
            return;
        }

        String letters = map[digits.charAt(index) - '0'];
        for (char letter : letters.toCharArray()) {
            path.append(letter);

            backtrack(digits, index + 1, path, ans, map);

            path.deleteCharAt(path.length() - 1);
        }
    }
    // endregion
}
