package com.czf.binarytree;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

/**
 * ClassName: M102_Level_Order_BinaryTree
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/18 00:00
 * @Version 1.0
 */
public class M102_Level_Order_BinaryTree {

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

    public List<List<Integer>> levelOrder(TreeNode root) {
        // 节点值列表集合，每个元素都表示一层的节点值结合
        List<List<Integer>> ans = new ArrayList<>();

        // 如果是空二叉树，返回空集合即可
        if(root == null){
            return ans;
        }

        // 创建队列，逐层存放节点
        Queue<TreeNode> queue = new LinkedList<>();
        // 将根节点入队
        queue.offer(root);

        // 当队列还有元素时，说明还有节点未被遍历
        // 注意这里不能用while(queue != null)
        // queue 这个对象创建后一直不为 null，即使里面的节点都被取完了，它也只是变成“空队列”，不是 null。
        while(!queue.isEmpty()){
            // 统计该层的节点个数
            int size = queue.size();
            // 统计该层的节点值
            List<Integer> level = new ArrayList<>();
            // 遍历该层的每一个节点，将其值保存到level中
            for(int i =0; i < size; i++){
                // 将当前被节点从队列中删去，在队尾追加其下一层的左右孩子
                TreeNode curNode = queue.poll();
                // 记录该节点的值
                level.add(curNode.val);

                // 若左右孩子存在，追加到队尾
                if(curNode.left != null){
                    queue.offer(curNode.left);
                }
                if(curNode.right != null){
                    queue.offer(curNode.right);
                }
            }
            // 遍历完一层后，将遍历结果加到答案中
            ans.add(level);

        }

        // 返回最终答案
        return ans;

    }
}
