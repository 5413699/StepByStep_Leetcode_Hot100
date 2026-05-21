package com.czf.binarytree;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

/**
 * ClassName: M199_BinaryTree_RightSideView
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/21 00:00
 * @Version 1.0
 */
public class M199_BinaryTree_RightSideView {

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

    public List<Integer> rightSideView(TreeNode root) {
        // 创建空list作为答案储存对象
        List<Integer> ans = new ArrayList<>();
        // 如果二叉树为空，返回空列表
        if(root == null){
            return ans;
        }
        // 如果二叉树不为空，创建队列对二叉树进行层序遍历
        // 每层的最后一个元素即为二叉树每层的右视图
        Queue<TreeNode> queue = new LinkedList<>();
        // 将根节点加入队列
        queue.offer(root);
        // 假如队列非空，说明二叉树还有未遍历的元素
        while(!queue.isEmpty()){
            // 记录每一层的元素个数
            int size = queue.size();
            // 遍历该层的每个元素
            for(int i = 0; i < size; i++){
                // 从队列中删除当前元素
                TreeNode curNode = queue.poll();
                // 如果遍历到该层最后一个元素
                if(i == size-1){
                    // 将其加入存储右视图的答案list中
                    ans.add(curNode.val);
                }
                // 向队列中加入该元素的左孩子和右孩子
                if(curNode.left != null){
                    queue.offer(curNode.left);
                }
                if(curNode.right != null){
                    queue.offer(curNode.right);
                }
            }
        }
        return ans;

    }
}
