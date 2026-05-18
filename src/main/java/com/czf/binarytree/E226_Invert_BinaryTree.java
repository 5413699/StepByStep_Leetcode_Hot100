package com.czf.binarytree;

/**
 * ClassName: E226_Invert_BinaryTree
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智锋
 * @Create 2026/5/13 00:00
 * @Version 1.0
 */
public class E226_Invert_BinaryTree {

    public static void main(String[] args) {
        TreeNode root= new TreeNode(4,
                new TreeNode(2,
                        new TreeNode(1),new TreeNode(3)),
                new TreeNode(7,
                        new TreeNode(6),new TreeNode(9)));
        TreeNode ans = invertTree(root);
        System.out.println(ans);
    }


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
        @Override
        public String toString() {
            java.util.List<Integer> result = new java.util.ArrayList<>();
            java.util.Queue<TreeNode> queue = new java.util.LinkedList<>();
            queue.offer(this);

            while (!queue.isEmpty()) {
                TreeNode node = queue.poll();
                if (node != null) {
                    result.add(node.val);
                    queue.offer(node.left);
                    queue.offer(node.right);
                } else {
                    result.add(null);
                }
            }

            // 移除末尾的 null 值
            while (!result.isEmpty() && result.get(result.size() - 1) == null) {
                result.remove(result.size() - 1);
            }

            return result.toString().replace("null", "null");
        }
    }

    public static TreeNode invertTree(TreeNode root) {
        // 空树翻转后还是空树
        if (root == null) {
            return null;
        }

        TreeNode temp = root.left;
        root.left = root.right;
        root.right = temp;
        invertTree(root.left);
        invertTree(root.right);
        return root;
    }
}
