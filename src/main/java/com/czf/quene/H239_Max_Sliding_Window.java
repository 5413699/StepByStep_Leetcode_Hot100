package com.czf.quene;

import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Deque;

/**
 * ClassName: H239_Max_Sliding_Window
 * Package: com.czf.quene
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/13 18:30
 * @Version 1.0
 */
public class H239_Max_Sliding_Window {

    public static void main(String[] args) {
        int[] nums = new int[]{1,3,-1,-3,5,3,6,7};
        int k =3;
        int[] ans = maxSlidingWindow(nums,k);
        System.out.println(Arrays.toString(ans));
    }
    public static int[] maxSlidingWindow(int[] nums, int k) {
        // 双端队列,其内存储当前窗口的数组下标值
        Deque<Integer> deque = new ArrayDeque<>();
        // 答案
        int[] ans = new int[nums.length - k + 1];
        // 初始化队列(数组下标)
        if(nums == null){
            return null;
        }
        for (int i = 0; i < nums.length; i++) {
            // 1. 清理队尾：只要新元素比队尾元素大，队尾就永远没机会了
            while (!deque.isEmpty() && nums[deque.peekLast()] < nums[i]) {
                deque.pollLast();
            }

            // 2. 将当前下标入队
            deque.addLast(i);

            // 3. 清理队首：判断队首下标是否已经滑出窗口
            if (deque.peekFirst() < i - k + 1) {
                deque.pollFirst();
            }

            // 4. 记录答案
            // 只有当 i 增长到一定程度（窗口形成了），才开始记录最大值
            if(i >= k - 1){
                ans[i - k + 1] = nums[deque.peekFirst()];
            }
        }

        return ans;


    }
}
