package com.czf.linkedlist;

/**
 * ClassName: E160_Intersecting_Linkedlist
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/3/31 16:11
 * @Version 1.0
 */
public class E160_Intersecting_Linkedlist {
    public static class ListNode{
        int val;
        ListNode next;
        public ListNode(int val){
            this.val=val;
        }
        public ListNode(int val,ListNode next){
            this.val=val;
            this.next=next;
        }
    }

    public static void main(String[] args) {
        //共享部分
        ListNode headC1 = new ListNode(2);
        ListNode headC2 = new ListNode(4);
        //链表A
        ListNode headA = new ListNode(1);
        ListNode headA2 = new ListNode(9);
        ListNode headA3 = new ListNode(1);

        headA.next = headA2;
        headA2.next = headA3;
        headA3.next = headC1;
        headC1.next = headC2;

        //链表B
        ListNode headB = new ListNode(3);
        headB.next = headC1;
//        headC1.next = headC2;相交部分无需重复构造

        ListNode intersrcting = getIntersectionNode(headA,headB);
        System.out.println(intersrcting.val);



    }
    public static ListNode getIntersectionNode(ListNode headA, ListNode headB) {
        // 双指针
        ListNode pa = headA;
        ListNode pb = headB;
        while(pa !=pb){

            // 到达尾部时，跳到下一个链表头
            if(pa == null){
                pa = headB;
            }
            else{ //没有到达尾部时，跳转到下一个节点
                pa = pa.next;
            }

            if(pb == null){
                pb = headA;
            }
            else{
                pb = pb.next;
            }

        }

        return pa;


    }
}
