package com.czf.arraylist;

import java.util.Arrays;

/**
 * ClassName: M016_Closest_Three_Number_Combo
 * Package: com.czf.arraylist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/7 16:08
 * @Version 1.0
 */
public class M016_Closest_Three_Number_Combo {


    public static void main(String[] args) {
        int[] nums = new int[]{-1 , 2 , 1 , -4};
        int target = 1;
        int ans = threeSumClosest(nums,target);
        System.out.println(ans);
    }
    public static int threeSumClosest(int[] nums, int target) {
        // 1.排序
        Arrays.sort(nums);
        // 2.初始化最接近的和,默认为数组前三个数
        int ans = nums[0] + nums[1] + nums[2];
        int n = nums.length;
        // 3.固定一个数，然后使用双指针寻找
        // 由于是三数之和，因此固定到只剩三个元素时，就已经遍历完所有情况了
        // 当然这里用n也可以
        for(int i = 0; i < n-2; i++){
            // 4.由于数组排好序了,
            // 因此假如本元素和上一个元素相同，结果也会相同，可跳过本次循环
            if (i > 0 && nums[i] == nums[i - 1]) {
                continue; // 跳过本次循环，去尝试下一个不同的 nums[i]
            }
            // 4.左指针指向该数的下一个元素
            int left = i+1;
            // 5.右指针指向数组最后一个元素
            int right = n-1;
            while(left < right){
                // 6.计算三数之和及其与目标值的差
                int sum = nums[i] + nums[left] + nums[right];
                // 如果和正好等于目标值，直接返回，这是最完美的解
                if (sum == target) {
                    return sum;
                }
                int dif = target - sum;

                // 7.比较三数之和与目标值之间的差是否减少，如果减少，就更新答案
                if(Math.abs(dif) < Math.abs(target - ans)){
                    ans = sum;
                }

                // 8.假如差值大于0，需要将右指针左移,反之左指针右移
                if(dif > 0){
                    left = left+1;
                }
                else{
                    right = right-1;
                }

            }
        }
        return ans;
    }
}
