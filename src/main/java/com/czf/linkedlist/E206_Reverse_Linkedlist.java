package com.czf.linkedlist;

import org.springframework.beans.factory.annotation.Value;

import java.util.Scanner;

/**
 * ClassName: E206_Reverse_Linkedlist
 * Package: com.czf.linkedlist
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/3/23 22:10
 * @Version 1.0
 */
public class E206_Reverse_Linkedlist {
    // 构造链表的数据结构
    public static class ListNode{
        // 链表数据
        int val;
        // 指向下一个节点的指针
        ListNode next;
        // 构造函数：初始化节点的值
        ListNode(int val){
            this.val = val;
        }
    }

    public static void main(String [] args){
        Scanner sc= new Scanner(System.in);
        // 节点个数
        int nodeNum = sc.nextInt();
        // 头结点
        ListNode headNode = null;
        ListNode end = null;
        // 向链表中添加节点
        for(int i=1; i<=nodeNum; i++){
            int value = sc.nextInt();
            // 创建头结点
            if (headNode == null){
                headNode = new ListNode(value);
                end = headNode;
            } else {
                // 其他节点
                end.next = new ListNode(value);
                end = end.next;
            }
        }

        // 打印链表
        ListNode current = headNode;
        while(current!= null){
            System.out.print(current.val);
            if(current.next!=null){
                System.out.print('-');
            }
            current = current.next;
        }


    }



}
