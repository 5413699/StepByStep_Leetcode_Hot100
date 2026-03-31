package com.czf.arraylist;

/**
 * ClassName: H041_Lost_Positive_Num
 * Package: com.czf.arraylist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/3/31 15:04
 * @Version 1.0
 */
public class H041_Lost_Positive_Num {

    public static void main(String[] args) {
        int[] nums = new int[]{1,2,0};
        int ans = firstMissingPositive(nums);
        System.out.println(ans);
    }
    public static int firstMissingPositive(int[] nums) {
        // 缺失的最小正整数一定在[1，n+1] 范围内，n= nums.length
        // 其他数字可以忽略(负数、0、超过 n 的数字)
        int length = nums.length;
        // 遍历数组
        for(int i = 0; i < length; i++){
            // 1.将每个在[1，n+1]范围内的正整数交换到下标x-1的位置
            // 若正整数已经在合适的位置，不用交换，避免重复交换导致循环
            while(nums[i] > 0 && nums[i] <= length && nums[i] != nums[nums[i]-1]){
                int index = nums[i]-1;
                int swap = nums[index];
                nums[index] = nums[i];
                nums[i] = swap;
            }
        }

        // 2.找到第一个 nums[i]!=i+1 的位置→i+1 就是缺失的最小正整数
        for(int i = 0; i < length; i++){
            if(nums[i]!= i+1){
                return i+1;
            }
        }

        // 如果所有位置都正确，返回length+1
        return length + 1;
    }
}
