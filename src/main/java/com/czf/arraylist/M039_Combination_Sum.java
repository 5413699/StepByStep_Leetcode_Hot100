package com.czf.arraylist;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * ClassName: M039_Combination_Sum
 * Package: com.czf.arraylist
 * Description: 39. 组合总和
 *
 * @Author 陈智飞
 * @Create 2026/6/15 00:00
 * @Version 1.0
 */
public class M039_Combination_Sum {

    public static void main(String[] args) {
        int[] candidates = {2, 3, 6, 7};
        System.out.println(combinationSum(candidates, 7));
        System.out.println("expected: [[2, 2, 3], [7]]");

        int[] candidates2 = {2, 3, 5};
        System.out.println(combinationSum(candidates2, 8));
        System.out.println("expected size: 3");

        int[] candidates3 = {2};
        System.out.println(combinationSum(candidates3, 1));
        System.out.println("expected: []");
    }

    // region LeetCode solution
    public static List<List<Integer>> combinationSum(int[] candidates, int target) {
        List<List<Integer>> ans = new ArrayList<>();
        List<Integer> path = new ArrayList<>();

        Arrays.sort(candidates);
        backtrack(candidates, 0, target, path, ans);
        return ans;
    }

    private static void backtrack(int[] candidates, int startIndex, int remain, List<Integer> path, List<List<Integer>> ans) {
        if (remain == 0) {
            ans.add(new ArrayList<>(path));
            return;
        }

        for (int i = startIndex; i < candidates.length; i++) {
            if (candidates[i] > remain) {
                break;
            }

            path.add(candidates[i]);

            backtrack(candidates, i, remain - candidates[i], path, ans);

            path.remove(path.size() - 1);
        }
    }
    // endregion
}
