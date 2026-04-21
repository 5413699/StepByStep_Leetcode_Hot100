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
    private static class ListNode {
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
        ListNode ans = mergeTwoLists2(list1, list2);
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


    /**
     * 方法2，迭代法
     */
    public static ListNode mergeTwoLists2(ListNode list1, ListNode list2) {

        // 当你比较两个队首的人时，如果发现 list1 的第一个值更小。
        // 既然要升序，list1 的这个节点理所应当成为第一个
        // 谁该排在 list1 这个人的后面呢？我们还不知道。
        // 但我们知道剩下要排序的名单：list1 后面剩下的所有人（即 list1.next）以及 list2 里的所有人。
        // 于是我们将list1 后面剩下的所有人看成一队，list2里的所有人看成一队继续比较，
        // 他们排队的结果作为list的第二个人（list.next）
        if(list1 == null){
            return list2;
        }else if(list2 == null){
            return list1;
        }

        if(list1.val < list2.val){
            list1.next = mergeTwoLists2(list1.next , list2);
            return list1;
        }else{
            list2.next = mergeTwoLists2(list1 , list2.next);
            return list2;
        }



    }
}
