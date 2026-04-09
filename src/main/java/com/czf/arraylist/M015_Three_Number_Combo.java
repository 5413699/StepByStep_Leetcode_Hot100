package com.czf.arraylist;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * ClassName: M015_Three_Number_Combo
 * Package: com.czf.arraylist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/8 20:14
 * @Version 1.0
 */
public class M015_Three_Number_Combo {
    public static void main(String[] args) {
        int[] nums = new int[]{-1,0,1,2,-1,-4};
        List ans = threeSum(nums);
        ans.forEach(System.out::println);

    }
    public static List<List<Integer>> threeSum(int[] nums) {
        List<List<Integer>> ans = new ArrayList<>();
        int length = nums.length;
        // 1.排序
        Arrays.sort(nums);

        // 2.固定一个数的位置为i
        for(int i = 0; i < length-2; i++){
            // 3.初始化指针位置，左指针初始指向第i+1个数，右指针初始指向最后一个数
            int left = i+1;
            int right = length-1;
            // 假如遇到重复的数，无需重复计算三数之和
            if(i>0 && nums[i] == nums[i-1]){
                continue;
            }
            // 4.不断根据结果更新左右指针
            while(left < right){
                int sum = nums[i] + nums[left] + nums[right];
                // 5.假如和为0，将该三元组加入答案
                if(sum == 0){
                    ans.add(Arrays.asList(nums[i],nums[left],nums[right]));
                    // 因为数组按序排列，所以在找到一个和为 0 的组合后,
                    // 可同时移动左指针和右指针（小的变大，大的变小），以寻找新的和为0的组合
                    left = left + 1;
                    right = right - 1;
                    // 若移动前后数组元素重复，可直接跳过该元素，直到找到新元素
                    while (left < right && nums[left] == nums[left - 1]){
                        left = left + 1;
                    }
                    while (left < right && nums[right] == nums[right + 1]){
                        right = right - 1;
                    }
                }else if(sum > 0){
                    // 6.由于已经数组排好序，假如总和偏大，就将右指针左移
                    right = right - 1;
                }
                else{// 7.若总和偏小，就将左指针右移
                    left = left + 1;
                }
            }

        }
        return ans;
    }


}

