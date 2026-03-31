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
     * 常规方法
     * 时间复杂度：O(n)
     * 空间复杂度：O(n)（因为用了额外数组 ans）
     */

    public static void rotate(int[] nums, int k) {
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

