package com.czf.binarytree;

/**
 * ClassName: M114_Flatten_BinaryTree
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/21 00:00
 * @Version 1.0
 */
public class M114_Flatten_BinaryTree {

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

    public void flatten(TreeNode root) {
        // 将根节点的左子树搬到右子树
        TreeNode cur = root;
        while(cur != null){
            // 如果当前节点有左子树
            if(cur.left != null){
                // 目前表示当前节点的左子树
                TreeNode pre = cur.left;
                // 找到左子树最右侧的节点，将其连接到右子树
                while(pre.right != null){
                    pre = pre.right;
                }
                // 将最右侧节点连接到右子树，先把原右子树挂到左子树尾巴上，
                pre.right = cur.right;
                // 再把左子树搬到右边。
                cur.right = cur.left;
                // 将左子树置空
                cur.left = null;
            }
            // 将下个节点的左子树搬到右子树
            cur = cur.right;
        }
    }

}

