package com.czf.arraylist;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * ClassName: M046_Permutations
 * Package: com.czf.arraylist
 * Description: 46. 全排列
 *
 * @Author 陈智飞
 * @Create 2026/6/10 00:00
 * @Version 1.0
 */
public class M046_Permutations {

    public static void main(String[] args) {
        int[] nums = {1, 2, 3};
        List<List<Integer>> ans = permute(nums);
        for (List<Integer> item : ans) {
            System.out.println(item);
        }
        System.out.println("expected size: 6");

        int[] nums2 = {0, 1};
        System.out.println("case2 actual: " + permute(nums2));
        System.out.println("case2 expected: " + Arrays.asList(Arrays.asList(0, 1), Arrays.asList(1, 0)));
    }

    // region LeetCode solution
    public static List<List<Integer>> permute(int[] nums) {
        List<List<Integer>> ans = new ArrayList<>();
        List<Integer> path = new ArrayList<>();
        boolean[] used = new boolean[nums.length];

        backtrack(nums, path, used, ans);
        return ans;
    }

    private static void backtrack(int[] nums, List<Integer> path, boolean[] used, List<List<Integer>> ans) {
        if (path.size() == nums.length) {
            ans.add(new ArrayList<>(path));
            return;
        }

        for (int i = 0; i < nums.length; i++) {
            if (used[i]) {
                continue;
            }

            path.add(nums[i]);
            used[i] = true;

            backtrack(nums, path, used, ans);

            path.remove(path.size() - 1);
            used[i] = false;
        }
    }
    // endregion
}
