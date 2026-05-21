package com.czf.binarytree;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

/**
 * ClassName: M105_Construct_BinaryTree
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/21 00:00
 * @Version 1.0
 */
public class M105_Construct_BinaryTree {

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
        M105_Construct_BinaryTree solution = new M105_Construct_BinaryTree();

        int[] preorder1 = {3, 9, 20, 15, 7};
        int[] inorder1 = {9, 3, 15, 20, 7};
        TreeNode ans1 = solution.buildTree(preorder1, inorder1);
        System.out.println("示例1 preorder: " + Arrays.toString(preorder1));
        System.out.println("示例1 inorder: " + Arrays.toString(inorder1));
        System.out.println("示例1 actual: " + serialize(ans1));
        System.out.println("示例1 expected: [3, 9, 20, null, null, 15, 7]");

        int[] preorder2 = {-1};
        int[] inorder2 = {-1};
        TreeNode ans2 = solution.buildTree(preorder2, inorder2);
        System.out.println("示例2 preorder: " + Arrays.toString(preorder2));
        System.out.println("示例2 inorder: " + Arrays.toString(inorder2));
        System.out.println("示例2 actual: " + serialize(ans2));
        System.out.println("示例2 expected: [-1]");
    }

    // region LeetCode solution
    public TreeNode buildTree(int[] preorder, int[] inorder) {
        return null;
    }
    // endregion

    private static List<Integer> serialize(TreeNode root) {
        List<Integer> ans = new ArrayList<>();
        if (root == null) {
            return ans;
        }

        Queue<TreeNode> queue = new LinkedList<>();
        queue.offer(root);

        while (!queue.isEmpty()) {
            TreeNode node = queue.poll();
            if (node == null) {
                ans.add(null);
                continue;
            }

            ans.add(node.val);
            queue.offer(node.left);
            queue.offer(node.right);
        }

        int last = ans.size() - 1;
        while (last >= 0 && ans.get(last) == null) {
            ans.remove(last);
            last--;
        }

        return ans;
    }
}
