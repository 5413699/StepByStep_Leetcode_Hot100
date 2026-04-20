package com.czf.linkedlist;

/**
 * ClassName: E021_Merge_Two_SortedLinkedlist
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/20 16:48
 * @Version 1.0
 */
public class E021_Merge_Two_SortedLinkedlist {
    public static class ListNode {
        int val;
        ListNode next;
        ListNode() {}
        ListNode(int val) { this.val = val; }
        ListNode(int val, ListNode next) { this.val = val; this.next = next; }
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

    public static void main(String[] args) {
        ListNode list1 = new ListNode(1,
                                new ListNode(2,
                                        new ListNode(4)));
        ListNode list2 = new ListNode(1,
                new ListNode(3,
                        new ListNode(4)));
        ListNode ans = mergeTwoLists(list1, list2);
        System.out.println(ans);
    }



    /**
     * 方法1：迭代法
     */
    public static ListNode mergeTwoLists(ListNode list1, ListNode list2) {
        // 新建一个虚拟头结点作为新链表的头节点
        ListNode dummy = new ListNode(0);

        // 记录新链表当前构建到哪个位置
        ListNode cur;
        cur = dummy;

        // 遍历两个链表
        while(list1 != null && list2 != null){
            // 假如list1比较小，先放入list1
            if(list1.val <= list2.val){
                // 将list1连接到新链表中
                cur.next = list1;
                // 切换下一个节点
                list1 = list1.next;
            }else{
                // 将list2连接到新链表中
                cur.next = list2;
                // 切换下一个节点
                list2 = list2.next;
            }
            // 新链表跳到下一个位置
            cur = cur.next;
        }

        // 将list1加入完后，将list2的剩余部分链接到cur上即可
        if(list2 != null){
            cur.next = list2;
        }
        if(list1 != null){
            cur.next = list1;
        }

        return dummy.next;
    }

}
