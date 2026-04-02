package com.czf.binarytree;

import java.util.LinkedList;
import java.util.Queue;

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

        int ans = maxDepth2(root);
        System.out.println(ans);

    }

    public static int maxDepth(TreeNode root) {
            TreeNode cur = root;
            if(cur == null){
                return 0;
            }
            return Math.max(maxDepth(root.left),maxDepth(root.right))+1;
    }
    public static int maxDepth2(TreeNode root) {
        Queue<TreeNode> queue = new LinkedList<>();
        int depth = 0;
        if(root == null) {
            return 0;
        }

        queue.add(root);
        // 若当前层不为空
        while(!queue.isEmpty()){
            int size = queue.size();//存放当前层的节点个数
            //将该层的元素替换为下一层的元素
            for(int i = 0; i < size; i++){
                // 取出当前元素
                TreeNode node = queue.poll();
                // 将下一层的元素加入队列中
                if(node.left != null){
                    queue.add(node.left);
                }
                if(node.right != null){
                    queue.add(node.right);
                }
            }
            // 当前层处理完，深度加 1
            depth++;
        }
        return depth;
    }



}
