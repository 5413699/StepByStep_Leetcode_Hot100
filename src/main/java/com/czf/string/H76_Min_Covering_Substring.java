package com.czf.string;

/**
 * ClassName: H76_Min_Covering_Substring
 * Package: com.czf.string
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/14 16:52
 * @Version 1.0
 */
public class H76_Min_Covering_Substring {
    public static void main(String[] args) {
        String s = "ADOBECODEBANC";
        String t = "ABC";
        String ans = minWindow(s, t);
        System.out.println(ans);

    }
    public static String minWindow(String s, String t) {
        // 记录t中各个字符的数量,128是为了涵盖ascii码
        int[] need = new int[128];
        // 记录t中不同字符的总数,用于后续判断子串是否满足需求
        int goal = 0;
        // 统计t中各个字符的要求数量和字符种类的数量
        for(int i = 0; i < t.length(); i++){
            if(need[t.charAt(i)] == 0){
                goal = goal + 1;
            }
            need[t.charAt(i)] = need[t.charAt(i)] + 1;
        }

        // 记录当前窗口内字符的频率
        int[] window = new int[128];
        // 记录多少种字符达到了need中的要求
        int match = 0;
        // 左右指针
        int left = 0;
        int right = 0;
        // 记录当前的最短子串长度
        int min = Integer.MAX_VALUE;
        int minl = 0;
        int minr = 0;

        // 第一阶段：扩张窗口
        while(right < s.length()){
            // 将right指针加入窗口
            window[s.charAt(right)] = window[s.charAt(right)] + 1;
            // 如果加入窗口后,该字符数量达标,记录达标数
            if(window[s.charAt(right)] == need[s.charAt(right)]){
                match = match +1;
            }

            // 如果达标数合格，尝试找最优解
            while(match == goal){
                // 记录最短长度
                if(right - left + 1 < min){
                    min = right - left + 1;
                    minl = left;
                    minr = right;
                }

                // 将left指针右移后，若使得当前子串无法完成覆盖，减少匹配数
                if(window[s.charAt(left)] <= need[s.charAt(left)]){
                    match = match - 1;
                }
                // 移动左指针
                window[s.charAt(left)] = window[s.charAt(left)] - 1;
                left = left + 1;

            }

            // 移动right指针
            right = right + 1;

        }

        // 最终由minl和minr之间的就是最小覆盖子串
        if(min == Integer.MAX_VALUE){
            return "";
        }

        return s.substring(minl, minr + 1);

    }

}
