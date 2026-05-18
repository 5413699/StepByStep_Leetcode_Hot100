package com.czf.binarytree;

import java.util.LinkedList;
import java.util.Queue;

/**
 * ClassName: E101_Symmetric_BinaryTree
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智锋
 * @Create 2026/5/13 00:00
 * @Version 1.0
 */
public class E101_Symmetric_BinaryTree {

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

    public boolean isSymmetric(TreeNode root) {
        // 如果树为空，视为对称
        if(root == null){
            return true;
        }
        // 新建一个队列，存放根节点的左子树和右子树，
        // 如果左子树和右子树对称，那么这个数轴对称
        Queue<TreeNode> queue =  new LinkedList<>();
        queue.offer(root.left);
        queue.offer(root.right);

        // 当队列非空时，说明该节点存在左子树或者右子树
        // 此时进入循环
        while(!queue.isEmpty()){
            // 由于先进先出，先出来的是左子树节点
            TreeNode left = queue.poll();
            TreeNode right = queue.poll();
            // 如果两者都为空，说明当前节点无左子树右子树，
            // 检查下一个节点
            if(left == null && right ==null){
                continue;
            }
            // 如果只有一个为空，说明不对称
            if(left == null || right == null){
                return false;
            }
            // 如果左子树和右子树值不同，也说明不对称
            if(left.val != right.val){
                return false;
            }
            // 假如左子树右子树均非空，且值相同
            // 需要比较该节点的下一层是否仍然对称
            queue.offer(left.left);
            queue.offer(right.right);
            queue.offer(left.right);
            queue.offer(right.left);
        }

        // 如果队列为空，节点仍对称，说明该二叉树是对称二叉树
        return true;

    }
}
