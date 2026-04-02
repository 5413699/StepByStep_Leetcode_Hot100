package com.czf.binarytree;

/**
 * ClassName: E104_Maxdepth_BinaryTree
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/2 21:47
 * @Version 1.0
 */
public class E104_Maxdepth_BinaryTree {

    public static class TreeNode{
        int val;
        TreeNode left;
        TreeNode right;
        TreeNode(int val){
            this.val=val;
        }
        TreeNode(int val,TreeNode left,TreeNode right){
            this.val=val;
            this.left=left;
            this.right=right;
        }
    }

    public static void main(String[] args) {
        TreeNode root = new TreeNode(1);
        TreeNode root2 = new TreeNode(2);
        TreeNode root3= new TreeNode(3);
        TreeNode root4 = new TreeNode(4);
        root.left=root2;
        root.right=root3;
        root2.left=root4;

        int ans = maxDepth(root);
        System.out.println(ans);

    }

    public static int maxDepth(TreeNode root) {
            TreeNode cur = root;
            if(cur == null){
                return 0;
            }
            return Math.max(maxDepth(root.left),maxDepth(root.right))+1;
    }



}
