package com.czf.string;

import java.util.List;

/**
 * ClassName: M139_Word_Break
 * Package: com.czf.string
 * Description: 139. 单词拆分
 *
 * @Author 陈智飞
 * @Create 2026/9/18
 * @Version 1.0
 */
public class M139_Word_Break {

    public static void main(String[] args) {
        M139_Word_Break solution = new M139_Word_Break();

        String example1 = "leetcode";
        List<String> wordDict1 = List.of("leet", "code");
        System.out.println("example 1 actual: " + solution.wordBreak(example1, wordDict1));
        System.out.println("example 1 expected: true");

        String example2 = "applepenapple";
        List<String> wordDict2 = List.of("apple", "pen");
        System.out.println("example 2 actual: " + solution.wordBreak(example2, wordDict2));
        System.out.println("example 2 expected: true");

        String example3 = "catsandog";
        List<String> wordDict3 = List.of("cats", "dog", "sand", "and", "cat");
        System.out.println("example 3 actual: " + solution.wordBreak(example3, wordDict3));
        System.out.println("example 3 expected: false");
    }

    // region LeetCode solution
    public boolean wordBreak(String s, List<String> wordDict) {
        int start = 0;
        Boolean[] memo = new Boolean[s.length()];
        return dfs(s, wordDict, start, memo);
    }

    private boolean dfs(String s, List<String> wordDict, int start, Boolean[] memo) {
        // 如果已经完成了拆分
        if (start == s.length()) {
            return true;
        }

        // 这个后缀已经计算过，直接使用结果
        if (memo[start] != null) {
            return memo[start];
        }

        for (String word : wordDict) {
            // 如果s 从下标 start 开始，以 word 开头。
            if (s.startsWith(word, start)) {
                if (dfs(s, wordDict, start + word.length(), memo)) {
                    memo[start] = true;
                    return true;
                }
            }
        }

        memo[start] = false;
        return false;
    }
    // endregion
}
