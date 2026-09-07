package com.czf.arraylist;

/**
 * ClassName: M287_Find_The_Duplicate_Number
 * Package: com.czf.arraylist
 * Description: 287. 寻找重复数
 *
 * @Author 陈智飞
 * @Create 2026/9/7
 * @Version 1.0
 */
public class M287_Find_The_Duplicate_Number {
    public static void main(String[] args) {
        M287_Find_The_Duplicate_Number solution = new M287_Find_The_Duplicate_Number();
        check(solution, new int[]{1, 3, 4, 2, 2}, 2);
        check(solution, new int[]{3, 1, 3, 4, 2}, 3);
        check(solution, new int[]{3, 3, 3, 3, 3}, 3);
        check(solution, new int[]{1, 1}, 1);

        int cases = 0;
        for (int n = 2; n <= 500; n++) {
            int duplicate = n / 2 + 1;
            int[] nums = new int[n + 1];
            for (int i = 0; i < n; i++) {
                nums[i] = i + 1;
            }
            nums[n] = duplicate;
            // Deterministic in-place shuffle for a variety of graph shapes.
            for (int i = nums.length - 1; i > 0; i--) {
                int j = (i * 37 + n * 17) % (i + 1);
                int temp = nums[i];
                nums[i] = nums[j];
                nums[j] = temp;
            }
            check(solution, nums, duplicate);
            cases++;
        }
        System.out.println("Passed: 4 named cases and " + cases + " generated cases.");
    }

    private static void check(M287_Find_The_Duplicate_Number solution,
                              int[] nums, int expected) {
        int[] before = nums.clone();
        int actual = solution.findDuplicate(nums);
        if (actual != expected) {
            throw new AssertionError("Expected " + expected + ", got " + actual);
        }
        for (int i = 0; i < nums.length; i++) {
            if (nums[i] != before[i]) {
                throw new AssertionError("Input array was modified");
            }
        }
    }

    // region LeetCode solution
    public int findDuplicate(int[] nums) {
        // 把下标看成节点，nums[i] 看成指向下一节点的指针。
        int slow = 0;
        int fast = 0;

        // 第一阶段：在环内寻找相遇点。
        do {
            slow = nums[slow];
            fast = nums[nums[fast]];
        } while (slow != fast);

        // 第二阶段：一个指针回到起点，二者同步前进，在环入口相遇。
        fast = 0;
        while (slow != fast) {
            slow = nums[slow];
            fast = nums[fast];
        }

        return slow;
    }
    // endregion
}
