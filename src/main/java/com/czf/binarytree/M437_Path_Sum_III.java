package com.czf.binarytree;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Queue;

/**
 * ClassName: M437_Path_Sum_III
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/22 00:00
 * @Version 1.0
 */
public class M437_Path_Sum_III {

    public static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;

        TreeNode() {
        }

        TreeNode(int val) {
            this.val = val;
        }

        TreeNode(int val, TreeNode left, TreeNode right) {
            this.val = val;
            this.left = left;
            this.right = right;
        }
    }

    public static void main(String[] args) {
        M437_Path_Sum_III solution = new M437_Path_Sum_III();

        TreeNode root1 = buildTree(new Integer[]{10, 5, -3, 3, 2, null, 11, 3, -2, null, 1});
        int targetSum1 = 8;
        System.out.println("示例1 actual: " + solution.pathSum(root1, targetSum1));
        System.out.println("示例1 expected: 3");

        TreeNode root2 = buildTree(new Integer[]{5, 4, 8, 11, null, 13, 4, 7, 2, null, null, 5, 1});
        int targetSum2 = 22;
        System.out.println("示例2 actual: " + solution.pathSum(root2, targetSum2));
        System.out.println("示例2 expected: 3");
    }

    // region LeetCode solution
    /**
     * 前缀和：固定当前节点作为路径终点，
     * 判断当前路径上有多少个历史前缀和可以与当前前缀和组成 targetSum。
     */
    public int pathSum(TreeNode root, int targetSum) {
        Map<Long, Integer> map = new HashMap<>();
        map.put(0L, 1);
        return dfs(root, 0L, targetSum, map);
    }

    /**
     * 在当前路径前缀和记录 map 的帮助下，
     * 统计以当前节点及其子树中的节点作为终点的合法路径数量。
     */
    public int dfs(TreeNode node, long currentSum, int targetSum, Map<Long, Integer> map) {
        if (node == null) {
            return 0;
        }

        currentSum += node.val;
        int count = map.getOrDefault(currentSum - targetSum, 0);

        map.put(currentSum, map.getOrDefault(currentSum, 0) + 1);

        count += dfs(node.left, currentSum, targetSum, map);
        count += dfs(node.right, currentSum, targetSum, map);

        map.put(currentSum, map.getOrDefault(currentSum, 0) - 1);
        if (map.get(currentSum) == 0) {
            map.remove(currentSum);
        }

        return count;
    }
    // endregion

    private static TreeNode buildTree(Integer[] values) {
        if (values == null || values.length == 0 || values[0] == null) {
            return null;
        }

        TreeNode root = new TreeNode(values[0]);
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        int index = 1;

        while (!queue.isEmpty() && index < values.length) {
            TreeNode node = queue.poll();

            if (index < values.length && values[index] != null) {
                node.left = new TreeNode(values[index]);
                queue.offer(node.left);
            }
            index++;

            if (index < values.length && values[index] != null) {
                node.right = new TreeNode(values[index]);
                queue.offer(node.right);
            }
            index++;
        }

        return root;
    }
}
