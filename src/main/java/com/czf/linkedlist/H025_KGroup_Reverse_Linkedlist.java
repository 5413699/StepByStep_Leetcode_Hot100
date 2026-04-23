package com.czf.linkedlist;

/**
 * ClassName: H025_KGroup_Reverse_Linkedlist
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/23 17:25
 * @Version 1.0
 */
public class H025_KGroup_Reverse_Linkedlist {

    private static class ListNode {
        int val;
        ListNode next;
        ListNode() {}
        ListNode(int val) { this.val = val; }
        ListNode(int val, ListNode next) { this.val = val; this.next = next; }

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
                                        new ListNode(5)))));
        ListNode ans = reverseKGroup(head,2);

        System.out.println(ans);


    }

    public static ListNode reverseKGroup(ListNode head, int k) {
        /**
         递归方法
         */
        // 用nextHead探测下一组链表的起始节点
        ListNode nextHead = head;
        // 终止条件：如果当前链表中剩余的节点不足k个，保持原有顺序
        for(int i = 0; i < k; i++){
            if(nextHead == null){
                return head;
            }
            nextHead = nextHead.next;
        }

        // 下一组链表的翻转由递归实现，下一组链表的结果应在1后
        ListNode head4 = reverseKGroup(nextHead, k);
        // 对前k个节点进行翻转，以k=3为例
        // 1-2-3-4...
        // 3-2-1-4...
        // 记录1的位置，从该位置开始翻转
        ListNode head1 = head;
        // 通过n次头插法完成翻转
        for(int i= 0; i < k; i++){
            // 第一次循环，改变2指针的朝向....
            // 记录2的位置
            ListNode head2 = head1.next;
            // 1指向下一组链表的结果
            head1.next = head4;
            // 更新下一次插入节点时，下一组链表的范围（1已经插入链表）
            head4 = head1;
            // 下一次处理节点2
            head1 = head2;
        }

        // 交换后，2是头节点
        return head4;
    }

}
