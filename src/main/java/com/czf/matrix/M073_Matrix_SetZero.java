package com.czf.matrix;

import java.util.Arrays;

/**
 * ClassName: M073_Matrix_SetZero
 * Package: com.czf.matrix
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/14 18:15
 * @Version 1.0
 */
public class M073_Matrix_SetZero {
    public static void main(String[] args) {
        int[][] matrix = {
                {1, 2, 3, 4},
                {5, 0, 7, 8},
                {9,10,0,12}
        };

        setZeroes(matrix);
        System.out.println(Arrays.deepToString(matrix));
    }

    public static void setZeroes(int[][] matrix) {
        // 记录第一行、第一列是否含0
        int firstRowZero = 1;
        int firstColZero = 1;

        // 遍历矩阵的第一行，判断其是否含0
        for(int i = 0; i < matrix[0].length; i++){
            if(matrix[0][i] == 0){
                firstRowZero = 0;
            }
        }

        // 遍历矩阵的第一列，判断其是否含0
        for(int i = 0; i < matrix.length; i++){
            if(matrix[i][0] == 0){
                firstColZero = 0;
            }
        }

        // 遍历剩余范围的矩阵，为其中含0的行或列做标记
        for(int i = 1; i < matrix.length; i++){
            for(int j = 1; j < matrix[0].length; j++){
                // 判断其是否含0
                if(matrix[i][j] == 0){
                    matrix[i][0] = 0;
                    matrix[0][j] = 0;
                }
            }
        }

        // 根据标记，将除第一行和第一列之外的矩阵按行置0
        for(int i = 1; i < matrix.length; i++){
            // 假如第i行，第0列是0
            if(matrix[i][0] == 0){
                // 将第i行的每一列置0
                for(int j = 1; j < matrix[0].length; j++){
                    matrix[i][j] = 0;
                }
            }
        }

        // 根据标记，将矩阵按列置0
        for(int i = 0; i < matrix[0].length; i++){
            // 假如第0行，第i列是0
            if(matrix[0][i] == 0){
                // 将第i列的每行置0
                for(int j = 1; j < matrix.length; j++){
                    matrix[j][i] = 0;
                }
            }
        }

        // 根据标记，将第一行和第一列置0
        // 将第一行置0
        for(int i = 0; i < matrix[0].length; i++){
            if(firstRowZero == 0){
                matrix[0][i] = 0;
            }
        }

        // 将第一列置0
        for(int i = 0; i < matrix.length; i++){
            if(firstColZero == 0){
                matrix[i][0] = 0;
            }
        }

    }
}
