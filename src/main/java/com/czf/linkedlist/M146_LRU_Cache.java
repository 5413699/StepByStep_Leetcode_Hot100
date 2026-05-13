package com.czf.linkedlist;

import java.util.HashMap;
import java.util.Map;

/**
 * ClassName: M146_LRU_Cache
 * Package: com.czf.hash
 * Description:
 *
 * @Author 陈智锋
 * @Create 2026/5/11 00:00
 * @Version 1.0
 */
public class M146_LRU_Cache {



    class LRUCache {

        /*
        双向链表
        假设链表头部放置最经常使用的节点
        链表尾部方要被删除的节点
    */
        class Node {
            int key;
            int value;
            Node prev;
            Node next;

            Node(int key, int value) {
                this.key = key;
                this.value = value;
            }

        }

        Node dummy = new Node(0, 0); //虚拟头结点
        private final int capacity;
        private final Map<Integer, Node> keyToNode;

        public LRUCache(int capacity) {
            this.capacity = capacity;
            this.keyToNode = new HashMap<>();
            dummy.next = dummy;
            dummy.prev = dummy;

        }

        /**
         * 如果关键字 key 存在于缓存中，则返回关键字的值，否则返回 -1 。
         */
        public int get(int key) {
            if (!keyToNode.containsKey(key)) {
                return -1;
            } else {
                Node goal = keyToNode.get(key);
                moveToHead(goal);
                return goal.value;
            }
        }

        /**
         * 如果关键字 key 已经存在，
         * 则变更其数据值 value ；
         * 如果不存在，则向缓存中插入该组 key-value 。
         * 如果插入操作导致关键字数量超过 capacity ，
         * 则应该 逐出 最久未使用的关键字。
         */
        public void put(int key, int value) {
            if (keyToNode.containsKey(key)) {
                Node goal = keyToNode.get(key);
                goal.value = value;
                moveToHead(goal);
            } else {
                if (keyToNode.size() >= capacity) {
                    //删除最后一个元素
                    Node delete = dummy.prev;
                    removeNode(delete);
                    keyToNode.remove(delete.key);
                }
                Node goal = new Node(key, value);
                addToHead(goal);
                keyToNode.put(key, goal);

            }

        }


        /**
         * 将当前访问的节点放到链表头部
         */
        private void addToHead(Node node) {
            node.prev = dummy;
            node.next = dummy.next;
            node.prev.next = node;
            node.next.prev = node;
        }

        /**
         * 删除当前访问的节点
         */
        private void removeNode(Node node) {
            node.prev.next = node.next;
            node.next.prev = node.prev;
        }

        /**
         * 将当前节点移动到链表头部
         */
        private void moveToHead(Node node) {
            // 先删除该节点
            removeNode(node);
            // 再将该节点移动到链表头部
            addToHead(node);
        }


    }
}
