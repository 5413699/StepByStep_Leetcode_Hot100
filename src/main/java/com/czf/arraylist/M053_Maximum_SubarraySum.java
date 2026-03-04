package com.czf.arraylist;


import java.util.Scanner;

/**
 * ClassName: M053_Maximum_SubarraySum
 * Package: com.czf.arraylist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/3/3 21:47
 * @Version 1.0
 */
public class M053_Maximum_SubarraySum {

    public static void main(String[] args) {
        M053_Maximum_SubarraySum solution = new M053_Maximum_SubarraySum();

        // ACM 模式 - 从控制台读取输入
        System.out.println("\n=== ACM 模式 ===");
        System.out.println("请输入数组长度：");
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
            
        System.out.println("请输入 " + n + " 个整数（用空格分隔）：");
        int[] nums3 = new int[n];
        for (int i = 0; i < n; i++) {
            nums3[i] = sc.nextInt();
        }
            
        int result = solution.maxSubArray_brute(nums3);
        System.out.println("最大子数组和：" + result);
        int result2 = solution.maxSubArray(nums3);
        System.out.println("最大子数组和：" + result2);

        sc.close();
    }

    public int maxSubArray_brute(int[] nums) {
        int max =  Integer.MIN_VALUE;    // 用max记录最大子数组和，这里用Min_VALUE是为了避免数组全是负数

        // 遍历每个起点的所有子数组
        for (int i = 0; i < nums.length; i++) {
            int sum = 0;    // 记录当前数组的和
            // 逐个添加元素，比较大小
            for (int j = i; j< nums.length ; j++){
                // 记录当前数组的和
                sum += nums[j];
                // 记录最大的最大子数组
                max = Math.max(max,sum);
            }

        }
        return max;
    }
    /**
     * 动态规划思路
     */

    public int maxSubArray(int[] nums) {
        int max =  nums[0];  // 用max记录整个数组的最大子数组和，这里用Min_VALUE是为了避免数组全是负数
        int dp = nums[0];   //记录以当前元素结尾的，最大子数组和
        // 遍历每个元素，计算以该元素结尾的最大子数组
        for (int i = 1; i < nums.length; i++) {
            // 假如每次只添加一个元素，
            // 以该元素结尾的最大子数组和
            // 要么是以上一个元素结尾的数组的最大子数组和(>0时)加上该元素
            // 要么是该元素本身【以上一个元素结尾的数组的最大子数组和(<0时)】
            dp = Math.max(dp+nums[i],nums[i]);
            // 找出最大的子数组和
            max = Math.max(max,dp);
        }
        return max;
    }

}
