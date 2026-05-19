package com.czf.binarytree;

/**
 * ClassName: M098_Validate_BinarySearchTree
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/19 00:00
 * @Version 1.0
 */
public class M098_Validate_BinarySearchTree {

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

    public boolean isValidBST(TreeNode root) {
        return isValid(root, Long.MIN_VALUE, Long.MAX_VALUE);
    }
    /**
     以 node 为根的这棵树，所有节点值都必须严格在 (lower, upper) 范围内。
     */
    public boolean isValid(TreeNode node, long lower, long upper){
        // 空树是二叉搜索树
        if (node == null) {
            return true;
        }
        // 如果根节点的值比左子树大，比右子树小，则该节点不是二叉搜索树
        if (node.val <= lower || node.val >= upper) {
            return false;
        }

        // 若根节点的左右子树也是二叉搜索树，那么该树是二叉搜索树
        return isValid(node.left, lower, node.val)
                && isValid(node.right, node.val, upper);
    }
}
