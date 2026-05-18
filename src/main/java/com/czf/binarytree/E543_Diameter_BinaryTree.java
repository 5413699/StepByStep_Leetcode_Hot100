package com.czf.binarytree;

/**
 * ClassName: E543_Diameter_BinaryTree
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/18 00:00
 * @Version 1.0
 */
public class E543_Diameter_BinaryTree {

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

    // 初始化二叉树直径为0
    // 该变量diameterOfBinaryTree、depth函数都要用，
    // 因此要作为整个类的成员变量
    int ans = 0;
    public int diameterOfBinaryTree(TreeNode root) {
        depth(root);
        return ans;
    }
    /**
     求某节点的二叉树深度，并统计以该节点为根节点二叉树的直径
     */
    public int depth(TreeNode node){
        // 空节点的最长路径为0
        if(node == null){
            return 0;
        }
        // 非空节点的最长路径为该节点左子树深度和右子树深度之和
        int leftDepth = depth(node.left);
        int rightDepth =  depth(node.right);
        // 更新二叉树直径
        ans = Math.max(ans, leftDepth + rightDepth);
        return Math.max(leftDepth, rightDepth) + 1;
    }
}
