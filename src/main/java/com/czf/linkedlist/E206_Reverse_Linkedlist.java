package com.czf.linkedlist;
public class E206_Reverse_Linkedlist {

    /** 链表节点定义 */
    static class ListNode {
        int val;
        ListNode next;

        ListNode(int val) {
            this.val = val;
        }
    }

    /**
     * 反转链表中第 m 到第 n 个节点
     * 核心算法函数
     */
    public static ListNode reverseBetween(ListNode head, int m, int n) {
        // 特殊情况处理
        if (head == null || head.next == null || m >= n || m <= 0) {
            return head;
        }

        // 虚拟头节点，方便处理 m=1 的情况
        ListNode dummy = new ListNode(0);
        dummy.next = head;

        // 1. 找到第 m-1 个节点 1
        ListNode pre = dummy;
        for (int i = 1; i < m && pre != null; i++) {
            pre = pre.next;
        }

        // 若 m 越界，直接返回原链表
        if (pre == null || pre.next == null) {
            return dummy.next;
        }

        // 2. 从第 m 个节点开始做局部反转（头插法）
        ListNode cur = pre.next;//2
        for (int i = 0; i < n - m && cur != null && cur.next != null; i++) {
//            dummy -> 1 -> 2 -> 3 -> 4 -> 5
//                  ↑    ↑    ↑
//                 pre  cur  next
            ListNode next = cur.next;
 //            dummy -> 1 -> 2  3 -> 4 -> 5
//                  ↑         ↑    ↑
//                 pre      next  cur.next
            cur.next = next.next;
//            dummy -> 1 -> 2  3 -> 4 -> 5
//                          ↑    ↑
//                      next  cur.next
            next.next = pre.next;
            pre.next = next;
        }

        return dummy.next;
    }

    /** 根据数组构建链表 */
    public static ListNode buildList(int[] arr) {
        if (arr == null || arr.length == 0) {
            return null;
        }
        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        for (int num : arr) {
            tail.next = new ListNode(num);
            tail = tail.next;
        }
        return dummy.next;
    }

    /** 按要求格式输出链表 */
    public static void printList(ListNode head) {
        ListNode cur = head;
        while (cur != null) {
            System.out.print(cur.val);
            if (cur.next != null) {
                System.out.print(" -> ");
            }
            cur = cur.next;
        }
        System.out.println();
    }

    public static void main(String[] args) {
        // 示例1输入
        int[] arr = {1, 2, 3, 4, 5};
        int m = 2;
        int n = 4;

        // 构建链表
        ListNode head = buildList(arr);

        // 调用核心函数
        ListNode result = reverseBetween(head, m, n);

        // 输出结果
        printList(result);
    }
}