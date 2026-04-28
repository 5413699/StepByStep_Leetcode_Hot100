package com.czf.linkedlist;

import org.w3c.dom.Node;

import java.util.HashMap;
import java.util.Map;

/**
 * ClassName: M138_Copy_Random_Linkedlist
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/4/28 19:04
 * @Version 1.0
 */
public class M138_Copy_Random_Linkedlist {

    public static class Node {
        int val;
        Node next;
        Node random;

        public Node(int val) {
            this.val = val;
            this.next = null;
            this.random = null;
        }

        public Node(int val,Node next,Node random) {
            this.val = val;
            this.next = next;
            this.random = random;
        }

        @Override
        public String toString(){
            StringBuilder sb = new StringBuilder("[");
            Node cur = this;
            while (cur != null){

                sb.append("[");
                sb.append(cur.val);
                sb.append(",");

                if (cur.random==null){
                    sb.append("null");
                }else {
                    sb.append(cur.random.val);
                }

                sb.append("]");

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
        Node head = new Node(7);
        Node node2 = new Node(13);
        Node node3 = new Node(11);
        Node node4 = new Node(10);
        Node node5 = new Node(1);

        head.next = node2;
        node2.next = node3;
        node3.next = node4;
        node4.next = node5;

        node2.random = head;
        node3.random = node5;
        node4.random = node3;
        node5.random = head;

        Node ans = copyRandomList(head);

        System.out.println(ans);
    }

    public static Node copyRandomList(Node head) {
        Node cur = head;
        // 记录原链表节点和新链表节点的对应关系
        Map<Node,Node> nodeMap = new HashMap<>();

        // 遍历原链表,克隆原链表除了指针之外的内容,以创建对象，避免后续连接时出现空指针异常
        while(cur != null){
            nodeMap.put(cur, new Node(cur.val ,null, null));
            cur = cur.next;
        }

        // 重置cur指针，进行第二次遍历
        cur = head;
        // 再次遍历原链表,按照原链表的对应关系连接指针
        while(cur != null){
            // 克隆链表的next
            nodeMap.get(cur).next = nodeMap.get(cur.next);
            nodeMap.get(cur).random = nodeMap.get(cur.random);
            cur = cur.next;
        }

        return nodeMap.get(head);
    }


    public static Node copyRandomList2(Node head) {
        Node cur = head;

        if(head == null){
            return null;
        }

        // 遍历原链表，将克隆节点直接插在原节点后面
        while(cur != null){
            // 创建克隆节点
            Node copy = new Node(cur.val);
            // 修改克隆节点与原节点的next指针，以符合前后顺序
            copy.next = cur.next;
            cur.next = copy;
            // 更新待克隆节点(将克隆节点直接插在原节点后面，原节点的下一个节点要经过两次跳转)
            cur = cur.next.next;
        }


        // 重置cur指针，再次遍历
        cur = head;
        // 遍历原链表
        while(cur != null){
            // 找到克隆节点
            Node copy = cur.next;
            if(cur.random != null){
                // 克隆节点的random指针为其对应原节点random的后继结点
                copy.random = cur.random.next;
            }

            // 更新下一个待克隆节点
            cur = cur.next.next;

        }


        // 重置cur指针，再次遍历，分离原链表和新链表
        cur = head;

        Node newHead = head.next; // 提前存好克隆链表的头

        while (cur != null) {
            // 克隆节点
            Node copy = cur.next;
            // 下一个原链表节点
            Node nextOrigin = copy.next;

            cur.next = nextOrigin; // 原链表节点指向下一个原链表节点
            // 如果下一个原链表节点存在
            if (nextOrigin != null) {
                copy.next = nextOrigin.next; // 克隆节点指向下一个克隆节点
            }

            cur = nextOrigin; // 移动到下一个原节点
        }


        return newHead;
    }

}
