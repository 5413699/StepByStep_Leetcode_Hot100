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

    public static boolean isPalindrome(ListNode head) {

        //1.用快慢指针找到链表中点
        ListNode slow = head, fast = head;
        while(fast != null && fast.next != null){
            slow = slow.next;
            fast = fast.next.next;
        }
        //此时的slow即为链表中点

        //2.从中点开始反转链表
        ListNode pre = null;
        ListNode cur = slow;
        while(cur != null){
            ListNode next = cur.next;
            cur.next = pre;
            pre = cur;
            cur = next;
        }
        // 此时的pre即为翻转后的链表

        //3.比较前半段和后半段链表
        while(pre != null){
            if(head.val != pre.val){
                return false;
            }
            pre = pre.next;
            head = head.next;
        }

        return true;

    }


    /**
     * 常规做法：将链表的值存到数组中，然后用双指针检查数组是否对称
     *
     * @param head 链表头节点
     * @return 是否为回文链表
     */
    public static boolean isPalindrome1(ListNode head) {
        List<Integer> vals = new ArrayList<>();
        ListNode cur = head;
        // 将链表的值存到arraylist
        while(cur != null){
            vals.add(cur.val);
            cur = cur.next;
        }
        // 用双指针检查数组是否对称
        for(int i = 0, j = vals.size()-1; i < j; i++, j--){
            if(vals.get(i).equals( vals.get(j))){
                return false;
            }
        }
        return true;
    }

}
