package com.czf.linkedlist;

import java.util.ArrayList;
import java.util.List;

/**
 * ClassName: E234_Palindrome_Linkedlist
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/1 13:54
 * @Version 1.0
 */
public class E234_Palindrome_Linkedlist {
    public static class ListNode{
        int val;
        ListNode next;
        ListNode(int val){
            this.val = val;
        }
        ListNode(int val, ListNode next){
            this.val = val;
            this.next = next;
        }
    }
    public static void main(String[] args) {
        ListNode head = new ListNode(1,
                new ListNode(2,
                        new ListNode(2,
                                new ListNode(1))));
        boolean ans = isPalindrome(head);
        System.out.println(ans);

    }

    /**
     * 常规做法：将链表的值存到数组中，然后用双指针检查数组是否对称
     *
     * @param head 链表头节点
     * @return 是否为回文链表
     */
    public static boolean isPalindrome(ListNode head) {
        List<Integer> vals = new ArrayList<>();
        ListNode cur = head;
        // 将链表的值存到arraylist
        while(cur != null){
            vals.add(cur.val);
            cur = cur.next;
        }
        // 用双指针检查数组是否对称
        for(int i = 0, j = vals.size()-1; i < j; i++, j--){
            if(vals.get(i) != vals.get(j)){
                return false;
            }
        }
        return true;
    }

}
