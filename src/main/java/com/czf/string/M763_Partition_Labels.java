package com.czf.string;

import java.util.ArrayList;
import java.util.List;

/**
 * ClassName: M763_Partition_Labels
 * Package: com.czf.string
 * Description: 763. 划分字母区间
 *
 * @Author 陈智飞
 * @Create 2026/9/2
 * @Version 1.0
 */
public class M763_Partition_Labels {

    public static void main(String[] args) {
        M763_Partition_Labels solution = new M763_Partition_Labels();

        String example1 = "ababcbacadefegdehijhklij";
        System.out.println("example 1 actual: " + solution.partitionLabels(example1));
        System.out.println("example 1 expected: [9, 7, 8]");

        String example2 = "eccbbbbdec";
        System.out.println("example 2 actual: " + solution.partitionLabels(example2));
        System.out.println("example 2 expected: [10]");
    }

    // region LeetCode solution
public List<Integer> partitionLabels(String s) {
    int[] last = new int[26];
    for (int i = 0; i < s.length(); i++) {
        last[s.charAt(i) - 'a'] = i;
    }

    List<Integer> list = new ArrayList<>();
    int start = 0;
    int end = 0;

    for (int i = 0; i < s.length(); i++) {
        end = Math.max(end, last[s.charAt(i) - 'a']);

        if (i == end) {
            list.add(end - start + 1);
            start = end + 1;
        }
    }

    return list;
}
    // endregion
}
