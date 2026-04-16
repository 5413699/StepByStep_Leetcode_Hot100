package com.czf.matrix;

import java.util.ArrayList;
import java.util.List;
import java.util.Spliterators;

/**
 * ClassName: M054_Spiral_Matrix
 * Package: com.czf.matrix
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/15 16:21
 * @Version 1.0
 */
public class M054_Spiral_Matrix {

    public static void main(String[] args) {
        int[][] matrix = {{1,2,3},{4,5,6},{7,8,9}};
        List<Integer> ans = spiralOrder(matrix);
        System.out.println(ans);
    }

    /**
     * 解法2
     */
    public static List<Integer> spiralOrder(int[][] matrix) {
        // 方向数组
        int[][] dirs = {
                {0, 1},  // 右 ➡️
                {1, 0},  // 下 ⬇️
                {0, -1}, // 左 ⬅️
                {-1, 0}  // 上 ⬆️
        };

        // 数组元素个数
        int leftBound = 0;
        int rightBound = matrix[0].length - 1;
        int upBound = 0;
        int downBound = matrix.length - 1;
        int size = (rightBound + 1) * (downBound +1);

        // 答案
        List<Integer> ans = new ArrayList<Integer>();

        // 从(0,-1)开始添加元素
        int i = 0;
        int j = -1;

        // 初始方向为右
        int dir = 0;

        while(ans.size() < size){
            // 走一步
            i = i + dirs[dir][0];
            j = j + dirs[dir][1];
            // 假如没撞墙
            if(j >= leftBound && j <= rightBound && i >= upBound && i <= downBound){
                ans.add(matrix[i][j]);
            }else{//撞墙了
                // 撤回上一步
                i = i - dirs[dir][0];
                j = j - dirs[dir][1];
                // 换方向
                dir = (dir + 1) % 4;
                // 更新边界
                if(dir == 0){ leftBound++; }
                if(dir == 1){ upBound++; }
                if(dir == 2){ rightBound--; }
                if(dir == 3){ downBound--; }
            }

        }

        return ans;

    }

    /**
     * 解法1
     * @param matrix
     * @return
     */
    public List<Integer> spiralOrder2(int[][] matrix) {
            int leftBound = 0;
            int rightBound = matrix[0].length - 1;
            int upBound = 0;
            int downBound = matrix.length - 1;
            List<Integer> ans = new ArrayList<Integer>();


            while(leftBound <= rightBound && upBound <= downBound){
                // 从左到右
                for(int i = leftBound; i <= rightBound; i++){
                    ans.add(matrix[upBound][i]);
                }
                upBound++;
                // 从上到下
                for(int i = upBound; i <= downBound; i++){
                    ans.add(matrix[i][rightBound]);
                }
                rightBound--;

                if(downBound >= upBound){
                    // 从右回左
                    for(int i = rightBound; i >= leftBound; i--){
                        ans.add(matrix[downBound][i]);
                    }
                    downBound--;
                }


                if(rightBound >= leftBound){
                    // 从下回上
                    for(int i = downBound; i >= upBound; i--){
                        ans.add(matrix[i][leftBound]);
                    }
                    leftBound++;
                }


            }

            return ans;


        }

}
