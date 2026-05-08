package com.czf.linkedlist;

import java.util.ArrayList;
import java.util.List;

/**
 * ClassName: H023_Merge_K_SortedLinkedlist
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智锋
 * @Create 2026/5/8 14:10
 * @Version 1.0
 */
public class H023_Merge_K_SortedLinkedlist {

    public static void main(String[] args) {
        List<ListNode> list = new ArrayList<ListNode>();
        list.add(new ListNode(1,new ListNode(4,new ListNode(5))));
        list.add(new ListNode(1,new ListNode(3,new ListNode(4))));
        list.add(new ListNode(2,new ListNode(6)));
        ListNode[] lists = list.toArray(new ListNode[list.size()]);
        ListNode ans = mergeKLists(lists);
        System.out.println(ans);
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

    public static ListNode mergeKLists(ListNode[] lists) {
        // 处理数组为空引用或空数组的情况
        if(lists == null || lists.length == 0){
            return null;
        }
        // 将0到lists.length-1范围内的链表合并
        return merge(lists , 0, lists.length-1);
    }

    /**
     将 lists[left...right] 范围内的所有升序链表合并成一条升序链表
     */
    private static ListNode merge(ListNode[] lists, int left, int right) {
        // 如果区间内只有一个链表，天然有序，无需合并
        if(left == right){
            return lists[left];
        }
        // 将区间二分
        int mid = left + (right - left)/2;

        // 合并二分后区间的链表
        ListNode l1 = merge(lists, left, mid);
        ListNode l2 = merge(lists, mid+1, right);

        // 将二分后的两个有序链表合并
        return mergeTwoLists(l1, l2);
    }

    /**
     合并两个升序链表
     */
    private static ListNode mergeTwoLists(ListNode l1, ListNode l2) {
        // 虚拟头节点
        ListNode dummy = new ListNode(0);
        ListNode cur = dummy;

        while(l1 != null && l2 != null){
            // 将小的节点加入合并后的链表，并移动对应链表的指针
            if(l1.val < l2.val){
                cur.next = l1;
                l1 = l1.next;
            }else{
                cur.next = l2;
                l2 = l2.next;
            }
            cur = cur.next;
        }

        // 将剩余节点加入链表
        if(l1 != null){
            cur.next = l1;
        }
        if(l2 != null){
            cur.next = l2;
        }
        return dummy.next;
    }
}
