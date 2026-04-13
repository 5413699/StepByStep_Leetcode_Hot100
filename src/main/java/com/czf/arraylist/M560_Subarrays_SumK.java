package com.czf.arraylist;

import java.util.HashMap;
import java.util.Map;

/**
 * ClassName: M560_Subarrays_SumK
 * Package: com.czf.arraylist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/13 17:06
 * @Version 1.0
 */
public class M560_Subarrays_SumK {

    public static void main(String[] args) {
        int[] nums = new int[]{1, 1, 1};
        int k = 2;
        int ans = subarraySum(nums, k);
        System.out.println(ans);
    }
    public static int subarraySum(int[] nums, int k) {
        // 计数器
        int count = 0;
        // 累加器
        int sum = 0;
        // 1.使用哈希表，用于存储前缀和
        // key:前缀和的值，value：该前缀和出现的次数
        Map<Integer , Integer> map = new HashMap<>();
        map.put(0,1);

        // 2.遍历整个数组计算前缀和
        for(int i = 0; i < nums.length; i++){
            // 2.1 首先计算加入当前元素的前缀和
            sum = sum + nums[i];
            // 2.2 计算map中有多少为sum - k
            // （能使得x+1到当前位置和为k）的子数组
            // 并加到答案中
            count = count + map.getOrDefault(sum - k,0);
            // 2.3 将当前的前缀和加入hashmap
            map.put(sum, map.getOrDefault(sum, 0) + 1);
        }
        return count;
    }


}
