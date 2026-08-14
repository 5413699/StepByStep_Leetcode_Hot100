package com.czf.heap;

import java.util.PriorityQueue;

/**
 * ClassName: H295_Find_Median_from_Data_Stream
 * Package: com.czf.heap
 * Description: 295. 数据流的中位数
 *
 * @Author 陈智飞
 * @Create 2026/8/15 00:00
 * @Version 1.0
 */
public class H295_Find_Median_from_Data_Stream {

    public static void main(String[] args) {
        MedianFinder medianFinder = new MedianFinder();
        medianFinder.addNum(1);
        medianFinder.addNum(2);
        System.out.println("example median 1 actual: " + medianFinder.findMedian());
        System.out.println("example median 1 expected: 1.5");

        medianFinder.addNum(3);
        System.out.println("example median 2 actual: " + medianFinder.findMedian());
        System.out.println("example median 2 expected: 2.0");

        MedianFinder negativeFinder = new MedianFinder();
        negativeFinder.addNum(-1);
        negativeFinder.addNum(-2);
        negativeFinder.addNum(-3);
        negativeFinder.addNum(-4);
        System.out.println("negative values actual: " + negativeFinder.findMedian());
        System.out.println("negative values expected: -2.5");

        MedianFinder duplicateFinder = new MedianFinder();
        duplicateFinder.addNum(2);
        duplicateFinder.addNum(2);
        duplicateFinder.addNum(2);
        System.out.println("duplicate values actual: " + duplicateFinder.findMedian());
        System.out.println("duplicate values expected: 2.0");
    }
}

// region LeetCode solution
class MedianFinder {

    private PriorityQueue<Integer> small;
    private PriorityQueue<Integer> large;

    public MedianFinder() {
        // 较小的一半，最大元素置于堆顶
        small = new PriorityQueue<>(
                (a, b) -> Integer.compare(b, a)
        );

        // 较大的一半，最小元素置于堆顶
        large = new PriorityQueue<>();
    }

    public void addNum(int num) {
        // small 为空，或者 num 不大于较小一半的最大值，就加入 small
        if (small.isEmpty() || num <= small.peek()) {
            small.offer(num);
        } else {
            large.offer(num);
        }

        // 加入元素后，对两边进行平衡
        if (small.size() > large.size() + 1) {
            large.offer(small.poll());
        }
        if (large.size() > small.size()) {
            small.offer(large.poll());
        }
    }

    public double findMedian() {
        if (small.size() == large.size()) {
            return (small.peek() + large.peek()) / 2.0;
        } else {
            return (double) small.peek();
        }
    }
}
// endregion
