package com.czf.matrix;

/**
 * ClassName: M200_Number_Of_Islands
 * Package: com.czf.matrix
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/31 00:00
 * @Version 1.0
 */
public class M200_Number_Of_Islands {

    public static void main(String[] args) {
        M200_Number_Of_Islands solution = new M200_Number_Of_Islands();

        char[][] grid1 = {
                {'1', '1', '1', '1', '0'},
                {'1', '1', '0', '1', '0'},
                {'1', '1', '0', '0', '0'},
                {'0', '0', '0', '0', '0'}
        };
        System.out.println("示例1 actual: " + solution.numIslands(grid1));
        System.out.println("示例1 expected: 1");

        char[][] grid2 = {
                {'1', '1', '0', '0', '0'},
                {'1', '1', '0', '0', '0'},
                {'0', '0', '1', '0', '0'},
                {'0', '0', '0', '1', '1'}
        };
        System.out.println("示例2 actual: " + solution.numIslands(grid2));
        System.out.println("示例2 expected: 3");
    }

    // region LeetCode solution
    private int m;
    private int n;

    public int numIslands(char[][] grid) {
        int num = 0;
        m = grid.length;
        n = grid[0].length;

        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == '1') {
                    num++;
                    dfs(grid, i, j);
                }
            }
        }

        return num;
    }

    private void dfs(char[][] grid, int i, int j) {
        if (i < 0 || i >= m || j < 0 || j >= n) {
            return;
        }
        if (grid[i][j] != '1') {
            return;
        }

        grid[i][j] = '0';
        dfs(grid, i + 1, j);
        dfs(grid, i - 1, j);
        dfs(grid, i, j + 1);
        dfs(grid, i, j - 1);
    }
    // endregion
}
