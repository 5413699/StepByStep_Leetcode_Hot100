package com.czf.string;

import java.util.ArrayList;
import java.util.List;

/**
 * ClassName: M438_Anagram
 * Package: com.czf.string
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/11 15:37
 * @Version 1.0
 */
public class M438_Anagram {
    public static void main(String[] args) {

    }

    class Solution {
        public List<Integer> findAnagrams(String s, String p) {
            // 统计p中字母出现的频率
            int[] fp = new int[26];
            int goal = 0;
            // 统计s中字母出现的频率
            int[] fs = new int[26];
            int curgoal =0;
            // 滑动窗口长度
            int length = p.length();
            // 记录答案
            List<Integer> ans = new ArrayList<Integer>();

            // 特殊情况：如果 s 比 p 还短，那绝对不可能有异位词。
            if (s.length() < p.length()) {return ans;}

            // 1.完成对p中字母出现的频率的统计,
            // 记录总共有多少个不同种类的字符需要达标
            for(int i = 0; i < length; i++){
                if(fp[p.charAt(i) - 'a'] == 0){
                    goal++;
                }
                fp[p.charAt(i) - 'a'] = fp[p.charAt(i) - 'a'] +1;
            }

            // 对p进行滑动，寻找异位词字串
            int left = 0;
            int right = length-1;
            // 初始化s的子串
            for(int i = 0; i < length; i++){
                fs[s.charAt(i) - 'a'] = fs[s.charAt(i) - 'a'] +1;
                if(fp[s.charAt(i) - 'a'] == fs[s.charAt(i) - 'a']){
                    curgoal++;
                }
            }
            while(right < s.length()){
                // 假如两子串相同，将其加到答案
                if(goal == curgoal){
                    ans.add(left);
                }
                if(right < s.length()-1){
                    // 将窗口向右进行滑动，删除最左侧元素
                    if(fp[s.charAt(left) - 'a'] == fs[s.charAt(left) - 'a']){
                        curgoal--;
                    }
                    fs[s.charAt(left) - 'a'] = fs[s.charAt(left) - 'a'] - 1;
                    left = left + 1;
                    // 向右侧新增元素
                    right = right + 1;
                    fs[s.charAt(right) - 'a'] = fs[s.charAt(right) - 'a'] + 1;
                    if(fp[s.charAt(right) - 'a'] == fs[s.charAt(right) - 'a']){
                        curgoal++;
                    }
                }else{
                    break;
                }
            }


            return ans;

        }
    }
}
