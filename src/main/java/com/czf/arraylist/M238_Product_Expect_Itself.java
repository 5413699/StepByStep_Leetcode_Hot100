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
     * 常规方法，时间复杂度高
     * @param nums
     * @return
     */
    public static int[] productExceptSelf(int[] nums) {
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
