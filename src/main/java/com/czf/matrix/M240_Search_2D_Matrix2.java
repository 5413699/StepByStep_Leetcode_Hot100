package com.czf.matrix;

/**
 * ClassName: M240_Search_2D_Matrix2
 * Package: com.czf.matrix
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/16 15:02
 * @Version 1.0
 */
public class M240_Search_2D_Matrix2 {

    public static void main(String[] args) {
        int[][] matrix = {{1,4,7,11,15}, {2,5,8,12,19}, {3,6,9,16,22}, {10,13,14,17,24},{18,21,23,26,30}};
        int target = 5;
        boolean ans = searchMatrix(matrix,target);
        System.out.println(ans);
    }

    public static boolean searchMatrix(int[][] matrix, int target) {
        // 初始行
        int i = 0;
        // 初始列
        int j = matrix[0].length-1;

        // 只要元素还在矩阵内
        while(i <= matrix.length-1 && j >= 0){
            // 如果元素比目标小，向左移动
            if(matrix[i][j] > target){
                j = j-1;
            }// 如果元素比目标大，向下移动
            else if(matrix[i][j] < target){
                i = i+1;
            }else{
                return true;
            }

        }

        return false;

    }
}
