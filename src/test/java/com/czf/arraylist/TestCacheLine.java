package com.czf.arraylist;

import org.springframework.util.StopWatch;

public class TestCacheLine {

    /**
     * 矩阵的行优先
     * 外层遍历行，内层遍历列的效率远高于外层遍历列，内层遍历行
     *
     * @param a:二维数组
     * @param rows：外层遍历行
     * @param columns：内层遍历列
     */
    public static void ij(int[][] a, int rows, int columns) {
        long sum = 0L;
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < columns; j++) {
                sum += a[i][j];
            }
        }
        System.out.println(sum);
    }

    /**
     * 矩阵的列优先
     *
     * @param a:二维数组
     * @param rows：内层遍历列
     * @param columns：内层遍历行
     */
    public static void ji(int[][] a, int rows, int columns) {
        long sum = 0L;
        for (int j = 0; j < columns; j++) {
            for (int i = 0; i < rows; i++) {
                sum += a[i][j];
            }
        }
        System.out.println(sum);
    }

    /*
        CPU      缓存     内存
        皮秒              纳秒
                 64字节
                 缓存行 cache line

                 空间局部性
     */

    //测试外层遍历行，内层遍历列与外层遍历列，内层遍历行的效率差
    public static void main(String[] args) {
        int rows = 1_000_000;
        int columns = 14;
        //未初始化，默认值0，因此这里累加结果为0，结果不重要，这里主要观察执行效率
        int[][] a = new int[rows][columns];

        //引入StopWatch工具类，用其start()和stop()方法，记录时间
        StopWatch sw = new StopWatch();

        //记录ij方法的执行时间
        sw.start("ij");
        ij(a, rows, columns);
        sw.stop();
        //记录ji方法的执行时间
        sw.start("ji");
        ji(a, rows, columns);
        sw.stop();
        //对比二者的执行时间
        System.out.println(sw.prettyPrint());
        //---------------------------------------------
        //ns         %     Task name
        //---------------------------------------------
        //008991800  014%  ij
        //054550600  086%  ji
        //ij明显快
    }
}
