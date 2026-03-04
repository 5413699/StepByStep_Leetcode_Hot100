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
            
        // 示例 1
        System.out.println("示例 1：-2,1,-3,4,-1,2,1,-5,4");
        int[] nums = new int[]{-2,1,-3,4,-1,2,1,-5,4};
        System.out.println("结果：" + solution.maxSubArray_brute(nums));
            
        // 示例 2
        System.out.println("\n示例 2：-1");
        int[] nums2 = new int[]{-1};
        System.out.println("结果：" + solution.maxSubArray_brute(nums2));
            
        // 示例 3: ACM 模式 - 从控制台读取输入
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



}
