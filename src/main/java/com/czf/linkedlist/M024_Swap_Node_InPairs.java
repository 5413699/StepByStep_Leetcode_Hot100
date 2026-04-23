package com.czf.linkedlist;

/**
 * ClassName: M024_Swap_Node_InPairs
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/23 15:09
 * @Version 1.0
 */
public class M024_Swap_Node_InPairs {



    public static class ListNode{
        int val;
        ListNode next;
        ListNode(){};
        ListNode(int val){
            this.val = val;
        }
        ListNode(int val, ListNode next){
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
                                new ListNode(4))));
        ListNode ans = swapPairs(head);
        System.out.println(ans);
    }



    /**
     * 迭代方法
     *
     */
    public static ListNode swapPairs(ListNode head) {
        // 因为要对链表的头结点进行修改，创建虚拟头结点进行操作
        ListNode dummy = new ListNode(0);
        dummy.next = head;
        // 记录当前链表处理到了哪个节点
        ListNode temp = dummy;

        // 从链表中不断取出两个节点进行操作
        // 确保链表中还有两个节点可供交换位置
        while(temp.next != null && temp.next.next != null){
            //          dump - 1 - 2 - 3
            // 要交换成 dump - 2 - 1 - 3
            //          temp
            // 首先要将节点1，节点2表示出来
            ListNode temp1 = temp.next;
            ListNode temp2 = temp1.next;
            // 执行指针的交换流程
            // dump指向2,节点1指向3，节点2指向1
            temp.next = temp2;
            temp1.next = temp2.next;
            temp2.next = temp1;
            // 更新temp指针使其指向1节点
            temp = temp1;
        }

        return dummy.next;
    }


    public static ListNode swapPairs2(ListNode head) {
        /**
         递归方法
         */

        // 终止条件：如果head或者head.next为空(链表没有待处理节点，或者只有一个待处理节点)，无需交换，直接返回原值
        if(head == null || head.next ==null){
            return head;
        }

        // 递归逻辑，假如有两个节点1-2-3-4，处理后应该为2-1-3-4
        // 节点2
        ListNode swapNode = head.next;
        // 交换后，1的next应该指向后续需要交换的节点群
        head.next = swapPairs(swapNode.next);
        // 交换后，2的next应该指向1
        swapNode.next = head;

        // 在递归函数中，return 的值代表的是这一层处理完后的“新头节点”。
        // 这样上一层递归（如果有的话）才能正确地连接到它。
        return swapNode;

    }

}
