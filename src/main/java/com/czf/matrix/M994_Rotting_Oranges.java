package com.czf.matrix;

import java.util.Arrays;
import java.util.LinkedList;
import java.util.Queue;

/**
 * ClassName: M994_Rotting_Oranges
 * Package: com.czf.matrix
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/6/3 00:00
 * @Version 1.0
 */
public class M994_Rotting_Oranges {

    public static void main(String[] args) {
        M994_Rotting_Oranges solution = new M994_Rotting_Oranges();

        int[][] grid1 = {
                {2, 1, 1},
                {1, 1, 0},
                {0, 1, 1}
        };
        System.out.println("示例1 actual: " + solution.orangesRotting(copyGrid(grid1)));
        System.out.println("示例1 expected: 4");

        int[][] grid2 = {
                {2, 1, 1},
                {0, 1, 1},
                {1, 0, 1}
        };
        System.out.println("示例2 actual: " + solution.orangesRotting(copyGrid(grid2)));
        System.out.println("示例2 expected: -1");

        int[][] grid3 = {
                {0, 2}
        };
        System.out.println("示例3 actual: " + solution.orangesRotting(copyGrid(grid3)));
        System.out.println("示例3 expected: 0");
    }

    private static int[][] copyGrid(int[][] grid) {
        int[][] copy = new int[grid.length][];
        for (int i = 0; i < grid.length; i++) {
            copy[i] = Arrays.copyOf(grid[i], grid[i].length);
        }
        return copy;
    }

    // region LeetCode solution
    public int orangesRotting(int[][] grid) {
        int m = grid.length;
        int n = grid[0].length;
        int minTime = 0;
        Queue<int[]> rot = new LinkedList<>();
        int freshCount = 0;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == 2) {
                    rot.offer(new int[]{i, j});
                }
                if (grid[i][j] == 1) {
                    freshCount++;
                }
            }
        }

        while (!rot.isEmpty() && freshCount > 0) {
            int size = rot.size();
            for (int i = 0; i < size; i++) {
                int[] cur = rot.poll();
                int x = cur[0];
                int y = cur[1];

                for (int[] dir : dirs) {
                    int rotx = x + dir[0];
                    int roty = y + dir[1];
                    if (rotx < 0 || rotx >= m || roty < 0 || roty >= n) {
                        continue;
                    }
                    if (grid[rotx][roty] != 1) {
                        continue;
                    }

                    grid[rotx][roty] = 2;
                    freshCount--;
                    rot.offer(new int[]{rotx, roty});
                }
            }
            minTime++;
        }

        if (freshCount == 0) {
            return minTime;
        }
        return -1;
    }
    // endregion
}
