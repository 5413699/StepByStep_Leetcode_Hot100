package com.czf.linkedlist;

/**
 * ClassName: M002_Add_TwoNumbers
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/21 17:12
 * @Version 1.0
 */
public class M002_Add_TwoNumbers {
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
        ListNode l1 = new ListNode(2,
                new ListNode(4,
                        new ListNode(3)));
        ListNode l2 = new ListNode(9,
                new ListNode(6,
                        new ListNode(9)));

        ListNode ans = addTwoNumbers(l1 , l2);

        System.out.println(ans);


    }

    public static ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        // 1.虚拟头节点，用于存答案
        ListNode dummy = new ListNode(0);
        // 进位标志符
        int carry = 0;
        // 用于记录当前创建的节点
        ListNode cur = dummy;

        // 2.当两个链表都还有数时，或者进位标志不为0时，说明新链表还未组装完成
        while(l1 != null || l2 != null || carry !=0){
            // 3.使用三元运算符，如果链表节点还在，则取原值，不在则取0
            int v1 = (l1 != null) ? l1.val : 0;
            int v2 = (l2 != null) ? l2.val : 0;

            // 4.计算新节点的值，以及下一个节点的进位值
            int sum = v1 + v2 + carry;
            int v3 = sum % 10;
            carry = sum / 10;
            // 5.插入新节点
            cur.next = new ListNode(v3);

            // 6.跳转到下一个节点
            if(l1 != null){
                l1 = l1.next;
            }
            if(l2 != null){
                l2 = l2.next;
            }
            cur = cur.next;
        }



        return dummy.next;

    }


}
