package com.czf.binarytree;

/**
 * ClassName: E108_Convert_SortedArray_BinarySearchTree
 * Package: com.czf.binarytree
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/5/19 00:00
 * @Version 1.0
 */
public class E108_Convert_SortedArray_BinarySearchTree {

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

    public TreeNode sortedArrayToBST(int[] nums) {
        return build(nums, 0, nums.length-1);
    }
    // 把 nums[left...right] 这一段有序数组转换成一棵平衡二叉搜索树，并返回这棵树的根节点。
    public TreeNode build(int[] nums, int left, int right){
        // 区间内没有元素，返回空树即可
        if(left > right){
            return null;
        }
        int mid = left + (right - left)/2;
        // 区间中点作为树的根节点
        TreeNode root = new TreeNode(nums[mid]);
        // 左半区间作为树的左子树
        root.left = build(nums, left, mid - 1);
        root.right = build(nums, mid + 1, right);
        return root;
    }
}
