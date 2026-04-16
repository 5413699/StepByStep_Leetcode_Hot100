package com.czf.matrix;

import com.sun.tools.javac.Main;

import java.util.Arrays;

/**
 * ClassName: M048_Rotate_Image
 * Package: com.czf.matrix
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/16 14:19
 * @Version 1.0
 */
public class M048_Rotate_Image {

    public static void main(String[] args) {
        int[][] matrix = {{1, 2, 3},{4, 5, 6},{7, 8, 9}};
        rotate(matrix);
        System.out.println(Arrays.deepToString(matrix));
    }
    public static void rotate(int[][] matrix) {

        // 旋转后，第一行成了最后一列，第二行成了倒数第二列
        // 可将旋转分解为转置和列切换两个步骤

        // 转置
        for(int i = 0; i < matrix.length; i++){
            for(int j = 0 ; j < i; j++){
                int temp = matrix[i][j];
                matrix[i][j] = matrix[j][i];
                matrix[j][i] = temp ;
            }
        }

        // 列切换，将第一列换到最后...
        for(int i = 0 , j = matrix.length-1; i < j; i++ ,j--){
            for(int k = 0 ; k < matrix.length; k++){
                int temp = matrix[k][i];
                matrix[k][i] = matrix[k][j];
                matrix[k][j] = temp;
            }
        }

    }
}
