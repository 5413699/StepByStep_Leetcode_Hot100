package com.czf.arraylist;

import java.util.ArrayList;
import java.util.List;

/**
 * ClassName: M078_Subsets
 * Package: com.czf.arraylist
 * Description: 78. 子集
 *
 * @Author 陈智飞
 * @Create 2026/6/11 00:00
 * @Version 1.0
 */
public class M078_Subsets {

    public static void main(String[] args) {
        int[] nums = {1, 2, 3};
        List<List<Integer>> ans = subsets(nums);
        for (List<Integer> item : ans) {
            System.out.println(item);
        }
        System.out.println("expected size: 8");

        int[] nums2 = {0};
        System.out.println("case2 actual: " + subsets(nums2));
        System.out.println("case2 expected size: 2");
    }

    // region LeetCode solution
    public static List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> ans = new ArrayList<>();
        List<Integer> path = new ArrayList<>();

        backtrack(nums, 0, path, ans);
        return ans;
    }

    private static void backtrack(int[] nums, int startIndex, List<Integer> path, List<List<Integer>> ans) {
        ans.add(new ArrayList<>(path));

        for (int i = startIndex; i < nums.length; i++) {
            path.add(nums[i]);

            backtrack(nums, i + 1, path, ans);

            path.remove(path.size() - 1);
        }
    }
    // endregion
}
