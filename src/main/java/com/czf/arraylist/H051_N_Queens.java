package com.czf.arraylist;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * ClassName: H051_N_Queens
 * Package: com.czf.arraylist
 * Description: 51. N 皇后
 *
 * @Author 陈智飞
 * @Create 2026/6/23 00:00
 * @Version 1.0
 */
public class H051_N_Queens {

    public static void main(String[] args) {
        H051_N_Queens solution = new H051_N_Queens();

        List<List<String>> ans1 = solution.solveNQueens(4);
        System.out.println("示例1 actual: " + ans1);
        System.out.println("示例1 expected size: 2");

        List<List<String>> ans2 = solution.solveNQueens(1);
        System.out.println("示例2 actual: " + ans2);
        System.out.println("示例2 expected: [[Q]]");
    }

    // region LeetCode solution
public List<List<String>> solveNQueens(int n) {
    List<List<String>> ans = new ArrayList<>();
    char[][] board = new char[n][n];
    boolean[] cols = new boolean[n];
    boolean[] leftUpRightDown = new boolean[2 * n];
    boolean[] rightUpLeftDown = new boolean[2 * n];

    for (int i = 0; i < n; i++) {
        Arrays.fill(board[i], '.');
    }

    backtrack(ans, board, cols, leftUpRightDown, rightUpLeftDown, 0, n);
    return ans;
}

private void backtrack(List<List<String>> ans, char[][] board, boolean[] cols,
                       boolean[] leftUpRightDown, boolean[] rightUpLeftDown,
                       int row, int n) {
    if (row == n) {
        List<String> curAns = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            curAns.add(new String(board[i]));
        }
        ans.add(curAns);
        return;
    }

    for (int col = 0; col < n; col++) {
        int d1 = row - col + n;
        int d2 = row + col;
        if (cols[col] || leftUpRightDown[d1] || rightUpLeftDown[d2]) {
            continue;
        }

        board[row][col] = 'Q';
        cols[col] = true;
        leftUpRightDown[d1] = true;
        rightUpLeftDown[d2] = true;

        backtrack(ans, board, cols, leftUpRightDown, rightUpLeftDown, row + 1, n);

        board[row][col] = '.';
        cols[col] = false;
        leftUpRightDown[d1] = false;
        rightUpLeftDown[d2] = false;
    }
}
    // endregion
}
