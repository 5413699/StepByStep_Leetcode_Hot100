package com.czf.linkedlist;

import java.util.HashMap;

/**
 * ClassName: E141_Cycle_Linkedlist
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/1 16:59
 * @Version 1.0
 */
public class E141_Cycle_Linkedlist {
    private static class ListNode{
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
        ListNode head = new ListNode(3);
        ListNode head1 = new ListNode(2);
        ListNode head2 = new ListNode(0);
        ListNode head3 = new ListNode(-4);
        head.next = head1;
        head1.next = head2;
        head2.next = head3;
        head3.next = head1;

        boolean ans = hasCycle(head);
        ListNode ans2 = detectCycle(head);
        System.out.println(ans);
        System.out.println(ans2.val);
    }

    public static ListNode detectCycle(ListNode head) {
        ListNode fast = head;
        ListNode slow = head;

        while(fast != null && fast.next != null){
            fast = fast.next.next;
            slow = slow.next;
            // 相遇,该链表一定含环
            if(fast == slow){
                // 快指针回到链表头
                fast = head;
                // 不断移动直到相遇
                while(fast != slow){
                    fast = fast.next;
                    slow = slow.next;
                }
                // 再次相遇的点一定为入环点
                return slow;
            }
        }

        return null;
    }

    public static boolean hasCycle(ListNode head) {
        ListNode fast = head;
        ListNode slow = head;

        while(fast != null && fast.next != null){
            fast = fast.next.next;
            slow = slow.next;
            if(fast == slow){
                return true;
            }

        }

        return false;
    }
}
