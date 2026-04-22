package com.czf.linkedlist;

/**
 * ClassName: M019_Delete_LastNthNode
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/21 17:53
 * @Version 1.0
 */
public class M019_Delete_LastNthNode {

    public static class ListNode{
        int val;
        ListNode next;
        ListNode(){};
        ListNode(int val){
            this.val = val;
        }
        ListNode(int val,ListNode next){
            this.val = val;
            this.next = next;
        }
        @Override
        public String toString(){
            StringBuilder sb = new StringBuilder("[");
            ListNode cur = this;
            while (cur != null){
                sb.append(cur.val);
                if(cur.next != null){
                    sb.append(",");
                }
                cur = cur.next;
            }
            sb.append("]");
            return sb.toString();
        }
    }
    public static void main(String[] args) {
        ListNode head = new ListNode(1,
                new ListNode(2,
                        new ListNode(3,
                                new ListNode(4,
                                        new ListNode(5)))
                ));
        int n = 2;
        ListNode ans = removeNthFromEnd(head,n);
        System.out.println(ans);

    }
    public static ListNode removeNthFromEnd(ListNode head, int n) {
        // 初始化虚拟节点，指向链表头部
        ListNode dummy = new ListNode(0);
        dummy.next = head;
        // 初始化快慢指针，快指针比慢指针多走n+1步，这样当快指针指向null时，慢指针会指向应删除节点的前驱节点
        ListNode fast = dummy;
        ListNode slow = dummy;
        for(int i = 0; i < n+1; i++){
            fast = fast.next;
        }
        // 快慢指针一起前进，让慢指针指向应删除节点的前驱节点
        while(fast != null){
            slow = slow.next;
            fast = fast.next;
        }
        // 通过操作慢指针，使得其跳过下一个节点
        slow.next = slow.next.next;

        // 返回链表的头结点
        return dummy.next;
    }

}
