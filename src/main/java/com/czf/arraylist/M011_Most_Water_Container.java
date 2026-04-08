package com.czf.arraylist;

/**
 * ClassName: M011_乘最多水的容器
 * Package: com.czf.arraylist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/8 17:47
 * @Version 1.0
 */
public class M011_Most_Water_Container {


    public static void main(String[] args) {
        int[] height = new int[]{1, 8, 6, 2, 5, 4, 8, 3, 7};
        int ans = maxArea(height);
        System.out.println(ans);

    }


    public static int maxArea(int[] height) {
        /**
         容量的计算
         宽 = 索引left,right之差
         高 = Math.min(height[left], height[right])
         */
        int length = height.length;
        int left = 0;
        int right = length - 1;
        int ans = 0;

        while(left != right){
            // 计算当前的容积
            int cur = (right - left) * Math.min(height[left], height[right]);
            // 假如当前容积大于以前的结果,更新答案
            if(cur > ans){
                ans = cur;
            }
            // 更新指针时，思考，假如height[left]=1, height[right]=3，1<3
            // 那么应该将左指针向右移动
            if(height[left] < height[right]){
                left = left + 1;
            }else{
                right = right - 1;
            }
        }

        return ans;


    }

}
