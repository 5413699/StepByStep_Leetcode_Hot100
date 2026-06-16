package com.czf.matrix;

/**
 * ClassName: M079_Word_Search
 * Package: com.czf.matrix
 * Description: 79. 单词搜索
 *
 * @Author 陈智飞
 * @Create 2026/6/16 00:00
 * @Version 1.0
 */
public class M079_Word_Search {

    public static void main(String[] args) {
        M079_Word_Search solution = new M079_Word_Search();

        char[][] board = {
                {'A', 'B', 'C', 'E'},
                {'S', 'F', 'C', 'S'},
                {'A', 'D', 'E', 'E'}
        };

        System.out.println("示例1 actual: " + solution.exist(board, "ABCCED"));
        System.out.println("示例1 expected: true");
        System.out.println("示例2 actual: " + solution.exist(board, "SEE"));
        System.out.println("示例2 expected: true");
        System.out.println("示例3 actual: " + solution.exist(board, "ABCB"));
        System.out.println("示例3 expected: false");
    }

    // region LeetCode solution
    private final int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    public boolean exist(char[][] board, String word) {
        boolean[][] visited = new boolean[board.length][board[0].length];

        for (int i = 0; i < board.length; i++) {
            for (int j = 0; j < board[0].length; j++) {
                if (board[i][j] == word.charAt(0) && dfs(board, word, i, j, 0, visited)) {
                    return true;
                }
            }
        }

        return false;
    }

    private boolean dfs(char[][] board, String word, int i, int j, int k, boolean[][] visited) {
        if (i < 0 || i >= board.length || j < 0 || j >= board[0].length) {
            return false;
        }
        if (visited[i][j]) {
            return false;
        }
        if (board[i][j] != word.charAt(k)) {
            return false;
        }
        if (k == word.length() - 1) {
            return true;
        }

        visited[i][j] = true;
        for (int[] dir : dirs) {
            int nextI = i + dir[0];
            int nextJ = j + dir[1];
            if (dfs(board, word, nextI, nextJ, k + 1, visited)) {
                visited[i][j] = false;
                return true;
            }
        }
        visited[i][j] = false;

        return false;
    }
    // endregion
}
