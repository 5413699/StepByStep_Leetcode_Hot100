package com.czf.binarytree;

/**
 * ClassName: M230_Kth_Smallest_BinarySearchTree
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/19 00:00
 * @Version 1.0
 */
public class M230_Kth_Smallest_BinarySearchTree {

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


    // 递归里的局部变量不会在不同递归层之间共享。
    int ans = 0;
    int count = 0;

    public int kthSmallest(TreeNode root, int k) {
        inOrder(root, k);

        return ans;
    }
    /**
     中序遍历二叉搜索树，找到第k个元素就返回
     */
    public void inOrder(TreeNode node, int k){

        // 空树的中序遍历结果是空，什么都不用做。
        // 如果答案已找到，后面别再遍历了
        if(node == null || count >= k){
            return;
        }
        inOrder(node.left, k);

        count++;
        if (count == k) {
            ans = node.val;
            return;
        }


        inOrder(node.right, k);
    }
}
