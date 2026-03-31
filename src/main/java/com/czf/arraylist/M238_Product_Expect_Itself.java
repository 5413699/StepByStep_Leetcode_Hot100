package com.czf.arraylist;

/**
 * ClassName: M238_Product_Expect_Itself
 * Package: com.czf.arraylist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/3/31 13:22
 * @Version 1.0
 */
public class M238_Product_Expect_Itself {

    public static void main(String[] args){
        int[] nums = new int[]{1,2,3,4};
        int length = nums.length;
        int[] ans = productExceptSelf(nums);
        for (int i = 0; i < length; i++) {
            System.out.println(ans[i]);
        }

    }

    /**
     *先正序计算左前缀乘积存数组，用变量R表示初始的右后缀乘积，
     * 计算完左前缀后，用最后一个左前缀*R得到初始的数组乘积
     * 再更新R用于为下一轮循环提供正确的右边乘积，迭代进行即可
     */
    public static int[] productExceptSelf(int[] nums) {
        int length = nums.length;
        // 存答案/前缀乘积
        int[] ans = new int[length];
        // 存后缀乘积
        int r = 1;
        // 第一个元素左边没有元素
        ans[0] = 1;
        // 计算左前缀乘积
        for(int i = 1; i < length; i++){
            ans[i] = ans[i-1] * nums[i-1];
        }
        // 从后往前计算后缀乘积（最右侧元素的数组乘积等于其左前缀乘以该最右侧元素）
        for(int j = length-1 ; j >= 0; j--){
            // 计算数组乘积
            ans[j] = ans[j] * r;
            // 更新后缀乘积
            r = r * nums[j];
        }
        return ans;
    }

    /**
     * 常规方法，时间复杂度高
     * @param nums
     * @return
     */
    public static int[] productExceptSelf1(int[] nums) {
        int length = nums.length;
        int[] ans = new int[length];
        // 计算第i个元素的乘积
        for(int i = 0; i < length; i++){
            ans[i] = 1;
            for(int j = 0; j<length; j++){
                if(i == j){
                    ans[i] = ans[i];
                }
                else{
                    ans[i] = ans[i]*nums[j];
                }
            }
        }
        return ans;
    }

}
