package com.czf.arraylist;

import java.util.ArrayList;
import java.util.List;

/**
 * 118. 杨辉三角
 *
 * @Author 陈智飞
 * @Create 2026/9/11
 */
public class E118_Pascals_Triangle {
    public static void main(String[] args) {
        E118_Pascals_Triangle solution = new E118_Pascals_Triangle();
        List<List<Integer>> result = solution.generate(5);
        List<List<Integer>> expected = List.of(
                List.of(1), List.of(1, 1), List.of(1, 2, 1),
                List.of(1, 3, 3, 1), List.of(1, 4, 6, 4, 1));
        if (!result.equals(expected) || !solution.generate(1).equals(List.of(List.of(1)))) {
            throw new AssertionError("杨辉三角结果错误");
        }
        System.out.println("Passed sample and boundary cases.");
    }

    // region LeetCode solution
    public List<List<Integer>> generate(int numRows) {
        List<List<Integer>> ans = new ArrayList<>();

        // 开始加入答案
        for (int i = 0; i < numRows; i++) {
            List<Integer> row = new ArrayList<>();
            // 注意第i行有i+1个元素
            for (int j = 0; j <= i; j++) {
                // 头尾的数字是1
                if (j == 0 || j == i) {
                    row.add(1);
                } else {
                    row.add(ans.get(i - 1).get(j - 1) + ans.get(i - 1).get(j));
                }
            }
            ans.add(row);
        }

        return ans;
    }
    // endregion
}
