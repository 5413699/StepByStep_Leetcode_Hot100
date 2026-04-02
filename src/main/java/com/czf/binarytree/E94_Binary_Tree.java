package com.czf.binarytree;

import javax.swing.tree.TreeNode;
import java.util.ArrayList;
import java.util.List;
import java.util.Stack;

/**
 * ClassName: E94_Binary_Tree
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/2 20:09
 * @Version 1.0
 */
public class E94_Binary_Tree {


    /**
     * Definition for a binary tree node.
     */
    public static class TreeNode {
         int val;
         TreeNode left;
         TreeNode right;
         TreeNode() {}
         TreeNode(int val) { this.val = val; }
         TreeNode(int val, TreeNode left, TreeNode right) {
             this.val = val;
             this.left = left;
             this.right = right;
         }
     }

    public static void main(String[] args) {
        TreeNode root = new TreeNode(1,
                new TreeNode(2),new TreeNode(3));
        List<Integer> ans = inorderTraversal(root);
        for (int i = 0; i < ans.size(); i++) {
            System.out.println(ans.get(i));
        }

    }

    public static List<Integer> inorderTraversal(TreeNode root) {
        // 1.准备一个栈，存节点顺序
        Stack<TreeNode> stack = new Stack<>();
        // 2.准备一个List存放结果
        List ans = new ArrayList<Integer>();

        // 3.当前遍历的节点
        TreeNode cur = root;
        // 4.迭代思路
        while(cur != null || !stack.isEmpty()){
            // 4.1 不断将左子节点压入栈，直到cur == null
            while(cur != null){
                stack.push(cur);
                cur = cur.left;
            }
            // 4.2 弹出栈顶，加入结果
            cur = stack.pop();
            // 4.4 加入结果
            ans.add(cur.val);
            // 4.5 移动到右子节点
            cur = cur.right;
        }

        return ans;

    }


    public static List<Integer> inorderTraversal2(TreeNode root) {

        // 2.准备一个List存放结果
        List ans = new ArrayList<Integer>();

        return ans;

    }
    /**
     * 先递归访问它的 左子树
     * 再处理 当前节点 → 把 node.val 加入结果
     * 再递归访问它的 右子树
     */
    public void inorder(TreeNode root, List<Integer> res) {
        if (root == null) {
            return;
        }
        inorder(root.left, res);
        res.add(root.val);
        inorder(root.right, res);
    }



}
