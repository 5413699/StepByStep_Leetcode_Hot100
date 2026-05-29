package com.czf.binarytree;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;
import java.util.Queue;

/**
 * ClassName: M236_Lowest_Common_Ancestor
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/23 00:00
 * @Version 1.0
 */
public class M236_Lowest_Common_Ancestor {

    public static class TreeNode {
        int val;
        TreeNode left;
        TreeNode right;

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
        M236_Lowest_Common_Ancestor solution = new M236_Lowest_Common_Ancestor();

        TreeBuildResult example1 = buildTree(new Integer[]{3, 5, 1, 6, 2, 0, 8, null, null, 7, 4});
        TreeNode ans1 = solution.lowestCommonAncestor(example1.root, example1.nodes.get(5), example1.nodes.get(1));
        System.out.println("示例1 actual: " + valueOf(ans1));
        System.out.println("示例1 expected: 3");

        TreeBuildResult example2 = buildTree(new Integer[]{3, 5, 1, 6, 2, 0, 8, null, null, 7, 4});
        TreeNode ans2 = solution.lowestCommonAncestor(example2.root, example2.nodes.get(5), example2.nodes.get(4));
        System.out.println("示例2 actual: " + valueOf(ans2));
        System.out.println("示例2 expected: 5");

        TreeBuildResult example3 = buildTree(new Integer[]{1, 2});
        TreeNode ans3 = solution.lowestCommonAncestor(example3.root, example3.nodes.get(1), example3.nodes.get(2));
        System.out.println("示例3 actual: " + valueOf(ans3));
        System.out.println("示例3 expected: 1");
    }

    // region LeetCode solution
    /**
     * 在以 root 为根的这棵树里，寻找 p 和 q 的最近公共祖先；
     * 如果空树，返回 null；
     * 如果这棵树里只找到了其中一个节点，就返回找到的那个节点；
     * 如果这棵树里已经找到了最近公共祖先，就返回这个祖先节点；
     * 如果一个都没找到，就返回 null。
     */
    public TreeNode lowestCommonAncestor(TreeNode root, TreeNode p, TreeNode q) {
        if (root == null) {
            return null;
        }

        if (root == p || root == q) {
            return root;
        }

        TreeNode left = lowestCommonAncestor(root.left, p, q);
        TreeNode right = lowestCommonAncestor(root.right, p, q);

        if (left != null && right != null) {
            return root;
        }

        if (left != null) {
            return left;
        }

        if (right != null) {
            return right;
        }

        return null;
    }
    // endregion

    private static Integer valueOf(TreeNode node) {
        return node == null ? null : node.val;
    }

    private static TreeBuildResult buildTree(Integer[] values) {
        Map<Integer, TreeNode> nodes = new HashMap<>();
        if (values == null || values.length == 0 || values[0] == null) {
            return new TreeBuildResult(null, nodes);
        }

        TreeNode root = new TreeNode(values[0]);
        nodes.put(root.val, root);
        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);
        int index = 1;

        while (!queue.isEmpty() && index < values.length) {
            TreeNode node = queue.poll();

            if (index < values.length && values[index] != null) {
                node.left = new TreeNode(values[index]);
                nodes.put(node.left.val, node.left);
                queue.offer(node.left);
            }
            index++;

            if (index < values.length && values[index] != null) {
                node.right = new TreeNode(values[index]);
                nodes.put(node.right.val, node.right);
                queue.offer(node.right);
            }
            index++;
        }

        return new TreeBuildResult(root, nodes);
    }

    private static class TreeBuildResult {
        TreeNode root;
        Map<Integer, TreeNode> nodes;

        TreeBuildResult(TreeNode root, Map<Integer, TreeNode> nodes) {
            this.root = root;
            this.nodes = nodes;
        }
    }
}
