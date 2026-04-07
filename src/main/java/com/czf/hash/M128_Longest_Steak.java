package com.czf.hash;

import java.util.HashSet;
import java.util.Set;

/**
 * ClassName: M128_Longest_Steak
 * Package: com.czf.hash
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/7 21:32
 * @Version 1.0
 */
public class M128_Longest_Steak {
    public static void main(String[] args) {
        int[] nums = new int[]{100, 4, 200, 1, 3, 2};
        int ans = longestConsecutive(nums);
        System.out.println(ans);
    }
    public static int longestConsecutive(int[] nums) {
        // 1.将数组存入hashset中，实现去重
        Set<Integer> set= new HashSet<>();
        for(int num : nums){
            set.add(num);
        }

        // 记录最长的连续序列长度
        int ans = 0;

        // 2.遍历集合的每一个数
        for(int num : set){
            // 如果当前集合元素为3，那么如果集合中有2，则3不是最长连续序列的起点
            // 如果集合中没有2，那么3可能是最长连续序列的起点，开始统计可能的最长序列数
            if(!set.contains(num - 1)){
                int curAns = 1;
                // 假如集合中有4
                int curNum = num+1;
                while(set.contains(curNum)){
                    curAns = curAns+1;
                    curNum = curNum+1;
                }
                ans = Math.max(curAns,ans);
            }


        }

        return ans;
    }
}
