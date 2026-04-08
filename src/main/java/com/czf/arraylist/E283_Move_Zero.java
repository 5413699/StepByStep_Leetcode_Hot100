package com.czf.arraylist;

/**
 * ClassName: E283_Move_Zero
 * Package: com.czf.arraylist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/8 17:21
 * @Version 1.0
 */
public class E283_Move_Zero {


    public static void main(String[] args) {
        int[] nums = new int[]{0, 1, 0, 3, 12};
        moveZeroes(nums);
        for (int i = 0; i < nums.length; i++) {
            System.out.println(nums[i]);
        }

    }

    /**
     * 1.用index记录下一个非0元素应放置的索引位置
     * 2.遍历数组，用i记录当前遍历位置
     * 3.遇到非0元素，假如当前遍历位置i与下一个非0元素应放置的索引位置index一致，说明数组暂未出现非0元素，无需交换元素，将下一个非0元素应放置的索引位置+1即可
     * 4.只有当前元素与index位置不一致时，才说明出现过0
     * 此时需要交换该元素和下一个非0索引位置应放置的元素
     */
    public static void moveZeroes(int[] nums) {
        // 1.用index记录下一个非0元素应放置的索引位置
        int index = 0;
        // 2.遍历数组，用i记录当前遍历位置
        for(int i=0; i<nums.length; i++){
            // 3.遇到非0元素，假如当前遍历位置i与下一个非0元素应放置的索引位置index一致
            // 说明数组暂未出现非0元素，无需交换元素，将下一个非0元素应放置的索引位置+1即可
            if(nums[i] != 0){
                // 4.只有当前元素与index位置不一致时，才说明出现过0
                if(i > index){
                    // 此时需要交换该元素和下一个非0索引位置应放置的元素
                    int swap = nums[index];
                    nums[index] = nums[i];
                    nums[i] = swap;
                }
                index = index + 1;
            }
        }
    }
}
