package com.czf.arraylist;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * ClassName: M056_合并区间
 * Package: com.czf.arraylist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/3/26 16:47
 * @Version 1.0
 */
public class M056_Merging_Intervals {



    public static int[][] merge(int[][] intervals) {
        // 输入intervals {{1,3},{2,6}，{8，10}，{15，18}}
        // 特殊情况处理：空数组或只有一个区间
        if (intervals == null || intervals.length <= 1) {
            return intervals;
        }
        // 将数组区间按序排列，方便我们进行合并区间
        Arrays.sort(intervals,(a,b)->a[0]-b[0]);

        // 记录将加入最终结果区间的左区间与右区间
        int start = intervals[0][0];
        int end = intervals[0][1];

        // 用ArrayList来记录最终合并后的结果，因为arraylist是可变长度的数组
        // 直接用intervals，无法修改数组大小，这会导致残留旧数据，有效区间难以维护
        List<int[]> result = new ArrayList<int[]>();

        // 从第二个区间开始比较
        for (int i = 1; i < intervals.length; i++) {
            // 假如第一个区间的最大值大于第二个区间的最小值【1.4】【2，3】
            if (end >= intervals[i][0]){
                // 说明两区间发生重叠，更新后的区间应为【1，[4与3之间的最大值]】
                end = Math.max(end , intervals[i][1]);
            }

            // 假如当前区间没有重合：[1,6]、[8,10]
            else {
                // 那么[1,6]可以作为结果的一部分加入结果数组中
                result.add(new int[]{start, end});
                // 并使得新的区间为下一区间
                start = intervals[i][0];
                end = intervals[i][1];
            }
        }
        // 循环结束后，最后那个区间 [start, end] 没有被加入 result
        result.add(new int[]{start, end});

        // result 是 List<int[]>，但函数返回值要求是 int[][]，因此返回时要手动转换
        return result.toArray(new int[result.size()][]);
    }

    public static void main(String[] args) {
        // 示例1输入
        int[][] intervals = {
                {1, 3},
                {2, 6},
                {8, 10},
                {15, 18}
        };

        // 调用核心算法函数
        int[][] result = merge(intervals);

        // 输出结果
        print(result);
    }

    /**
     * 打印二维数组（按题目格式）
     */
    public static void print(int[][] arr) {
        System.out.print("[");
        for (int i = 0; i < arr.length; i++) {
            System.out.print("[" + arr[i][0] + "," + arr[i][1] + "]");
            if (i != arr.length - 1) {
                System.out.print(",");
            }
        }
        System.out.println("]");
    }


}
