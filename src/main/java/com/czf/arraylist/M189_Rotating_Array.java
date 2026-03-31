package com.czf.arraylist;

/**
 * ClassName: M189_Rotating_Array
 * Package: com.czf.arraylist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/3/31 11:13
 * @Version 1.0
 */
public class M189_Rotating_Array {

    public static void main(String[] args) {
        int[] nums = new int[]{1, 2, 3, 4, 5, 6, 7};
        rotate(nums,3);
        for (int i = 0; i < nums.length; i++) {
            System.out.print(nums[i]);
        }

    }



    /**
     * 原地操作方法
     * 假设数组是 [1,2,3,4,5,6,7] ，k = 3 ， 你希望结果是 [5,6,7,1,2,3,4] 。
     * 完全原地 O(1) 空间轮转数组。最常用的方法是三次翻转法。
     * ①先将数组翻转一次7 6 5 4 3 2 1
     * ②将前k个数翻转 5 6 7 4 3 2 1
     * ③翻转剩下的部分5 6 7 1 2 3 4
     * ✅ 时间复杂度：O(n)
     * ✅ 空间复杂度：O(1)
     */
    public static void rotate(int[] nums, int k) {
        int length = nums.length;
        k = k % length;
        // 先将数组翻转一次
        for(int i = 0 , j = length-1; i < j ; i++ , j--){
            int left = nums[i];
            nums[i] = nums[j];
            nums[j] = left;
        }
        // 将前k个数翻转
        for(int i = 0 , j = k-1 ; i < j ; i++ , j--){
            int left = nums[i];
            nums[i] = nums[j];
            nums[j] = left;
        }
        // 翻转剩下的部分
        for(int i = k , j = length-1 ; i < j ; i++ , j--){
            int left = nums[i];
            nums[i] = nums[j];
            nums[j] = left;
        }


    }





    /**
     * 常规方法
     * 时间复杂度：O(n)
     * 空间复杂度：O(n)（因为用了额外数组 ans）
     */

    public static void rotate1(int[] nums, int k) {
        int length = nums.length;
        int[] ans = new int[length];
        int index;
        for(int i =0 ; i<length ; i++){
            // 计算新元素的索引位置
            index = (i+k)%length;
            ans[index]=nums[i];
        }
        // 把 ans 的内容拷贝回 nums，实现原方法的修改
        for (int i = 0; i < length; i++) {
            nums[i] = ans[i];
        }
    }


}

