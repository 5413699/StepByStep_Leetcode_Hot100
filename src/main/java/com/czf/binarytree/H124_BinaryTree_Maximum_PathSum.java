package com.czf.binarytree;

import java.util.LinkedList;
import java.util.Queue;

/**
 * ClassName: H124_BinaryTree_Maximum_PathSum
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/29 00:00
 * @Version 1.0
 */
public class H124_BinaryTree_Maximum_PathSum {

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
        H124_BinaryTree_Maximum_PathSum solution = new H124_BinaryTree_Maximum_PathSum();

        TreeNode root1 = buildTree(new Integer[]{1, 2, 3});
        System.out.println("示例1 actual: " + solution.maxPathSum(root1));
        System.out.println("示例1 expected: 6");

        TreeNode root2 = buildTree(new Integer[]{-10, 9, 20, null, null, 15, 7});
        System.out.println("示例2 actual: " + solution.maxPathSum(root2));
        System.out.println("示例2 expected: 42");
    }

    // region LeetCode solution
    private int ans = Integer.MIN_VALUE;

    public int maxPathSum(TreeNode root) {
        gain(root);
        return ans;
    }

    /**
     * 计算当前节点能向父节点提供的最大单边路径和。
     */
    public int gain(TreeNode node) {
        if (node == null) {
            return 0;
        }

        int left = Math.max(0, gain(node.left));
        int right = Math.max(0, gain(node.right));

        ans = Math.max(ans, left + right + node.val);

        return node.val + Math.max(left, right);
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
