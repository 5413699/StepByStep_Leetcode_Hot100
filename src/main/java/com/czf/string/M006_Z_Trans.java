package com.czf.string;

import java.util.ArrayList;
import java.util.List;

/**
 * ClassName: test
 * Package: com.czf.string
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/24 11:10
 * @Version 1.0
 */
public class M006_Z_Trans {

    public static void main(String[] args) {
        String s = "PAYPALISHIRING";
        int nUmRows = 3;
        int col = s.length();
        String ans = convert(s, nUmRows);
        System.out.println(ans);
    }

    public static String convert(String s, int numRows) {
        // 行索引
        int rowIndex = 0;
        // 移动方向
        // 等于1时,代表向下移动，等于-1时，代表向上移动
        int dir = 1;
        // 记录每一行的字符串，将其拼接到一起即为最终答案
        List<StringBuilder> rows = new ArrayList<StringBuilder>();
        // 初始化每一行的字符串
        for(int i = 0; i < Math.min(numRows, s.length());i++){
            rows.add(new StringBuilder());
        }
        // 记录最终答案
        StringBuilder ans = new StringBuilder();

        //如果 numRows = 1（也就是只有一行）。
        // 在这种情况下，rowIndex 会一直加 dir，
        // 但它永远不会触发“调头”逻辑（因为 0 既是起点也是终点）。这可能会导致程序去访问不存在的行。
        if(numRows == 1){
            return s;
        }


        // 遍历字符串s，记录其z字形排列后每行的字符串
        for(char c : s.toCharArray()){
            // 将当前字母加入对应行的字符串
            rows.get(rowIndex).append(c);
            // 根据方向调整行索引
            rowIndex += dir;
            // 若到达首行或尾行调整方向
            if(rowIndex == 0){
                dir = 1;
            }
            if(rowIndex == numRows - 1){
                dir = -1;
            }
        }

        // 合并结果
        for(StringBuilder row:rows){
            ans.append(row);
        }

        return ans.toString();

    }

    public String convert2(String s, int numRows) {
        // 行索引
        int rowIndex = 0;
        // 记录最终答案
        StringBuilder ans = new StringBuilder();

        // 通过找规律的方式填充字符串
        // 用i代表z字形变换后的每一行
        // 周期
        int T = 2*(numRows - 1);


        if(numRows ==1){
            return s;
        }

        for(int i = 0; i < numRows; i++){
            // j 代表的是每一个“周期”的起始下标
            // j + i < s.length()确保当前行有元素
            for(int j = 0; j + i < s.length(); j += T){
                // 无论是否是首尾行，在第i行都存在索引为j+i的元素
                ans.append(s.charAt(j + i));
                // 如果不是首尾行，且当前周期内存在第二个字符。添加该字符
                if(i != 0 && i != numRows - 1 && j + T - i < s.length()){
                    ans.append(s.charAt(j + T - i));
                }

            }

        }


        return ans.toString();

    }

}
