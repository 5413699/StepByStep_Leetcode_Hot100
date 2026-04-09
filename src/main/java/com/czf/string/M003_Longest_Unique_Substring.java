package com.czf.string;

import java.util.HashSet;
import java.util.Set;

/**
 * ClassName: M003_Longest_Unique_Substring
 * Package: com.czf.hash
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/9 22:01
 * @Version 1.0
 */
public class M003_Longest_Unique_Substring {
    public static void main(String[] args) {
        String s ="abcacbb";
        int ans = lengthOfLongestSubstring1(s);
        System.out.println(ans);
    }
    public static int lengthOfLongestSubstring1(String s) {
        // 记录答案
        int ans = 0;
        // 字符串长度
        int length = s.length();
        // 滑动窗口指针
        int left = 0;
        int right = 0;

        // 处理空字符串的情况
        if(s==null || s.length()== 0){
            return 0;
        }
        // 初始化当前子串
        Set<Character> charSet = new HashSet<Character>();

        // 若输入非空，对窗口进行滑动
        while(right < length){
            // 添加右指针元素时，如果待添加元素不在集合中
            if(!charSet.contains(s.charAt(right))){
                // 将右指针元素加入set中
                charSet.add(s.charAt(right));
                right = right + 1;
                // 如果当前字串长度超过前面计算的最大值，进行更新
                ans = Math.max(right-left, ans);
            }else{// 如果待添加元素在集合中,重复了
                // 删除左侧指针元素
                charSet.remove(s.charAt(left));
                // 左侧指针向右移动
                left = left + 1;
            }

        }
        return ans;
    }
}
