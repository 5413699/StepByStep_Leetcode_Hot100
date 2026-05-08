package com.czf.linkedlist;

/**
 * ClassName: M148_Sort_Linkedlist
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智锋
 * @Create 2026/5/7 18:58
 * @Version 1.0
 */
public class M148_Sort_Linkedlist {

    public static void main(String[] args) {
        ListNode head = new ListNode(4,
                new ListNode(2,
                        new ListNode(1,
                                new ListNode(3))));
        System.out.println(sortList(head));
    }

    public static class ListNode {
        int val;
        ListNode next;

        ListNode() {
        }

        ListNode(int val) {
            this.val = val;
        }

        ListNode(int val, ListNode next) {
            this.val = val;
            this.next = next;
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder("[");
            ListNode cur = this;
            while (cur != null) {
                sb.append(cur.val);
                if (cur.next != null) {
                    sb.append(",");
                }
                cur = cur.next;
            }
            sb.append("]");
            return sb.toString();
        }
    }

    public static ListNode sortList(ListNode head) {

        // 1. 递归终止条件:如果链表为空或只有一个节点，那么链表天然有序，直接返回头结点
        if(head == null || head.next ==null){
            return head;
        }
        // 2. 快慢指针找中点，同时记录 slow 的前一个节点 prev
        ListNode prev = null;
        ListNode slow = head;
        ListNode fast = head;
        while(fast != null && fast.next!=null){
            prev = slow;
            slow = slow.next;
            fast = fast.next.next;
        }
        // 3. 断开左右链表
        prev.next = null;
        // 4. 递归排序左右两边
        ListNode left = sortList(head);
        ListNode right = sortList(slow);
        // 5. 合并两个有序链表并返回
        return merge(left,right);
    }

    private static ListNode merge(ListNode left, ListNode right) {
        ListNode dummy = new ListNode(0);
        ListNode cur = dummy;
        // 合并两个升序链表
        while(left != null && right != null){
            if(left.val < right.val){
                cur.next = left;
                left = left.next;
            }else{
                cur.next = right;
                right = right.next;
            }
            cur = cur.next;
        }
        if (left != null) {
            cur.next = left;
        }
        if (right != null) {
            cur.next = right;
        }
        return dummy.next;
    }

}
