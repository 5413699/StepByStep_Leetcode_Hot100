package com.czf.string;

/**
 * ClassName: M208_Implement_Trie
 * Package: com.czf.string
 * Description: 208. 实现 Trie（前缀树）
 *
 * @Author 陈智飞
 * @Create 2026/6/10 00:00
 * @Version 1.0
 */
public class M208_Implement_Trie {

    public static void main(String[] args) {
        Trie trie = new Trie();
        trie.insert("apple");
        System.out.println("search(\"apple\") actual: " + trie.search("apple"));
        System.out.println("search(\"apple\") expected: true");
        System.out.println("search(\"app\") actual: " + trie.search("app"));
        System.out.println("search(\"app\") expected: false");
        System.out.println("startsWith(\"app\") actual: " + trie.startsWith("app"));
        System.out.println("startsWith(\"app\") expected: true");
        trie.insert("app");
        System.out.println("search(\"app\") actual: " + trie.search("app"));
        System.out.println("search(\"app\") expected: true");
    }

    // region LeetCode solution
    static class Trie {
        private final Trie[] children;
        private boolean isEnd;

        public Trie() {
            children = new Trie[26];
            isEnd = false;
        }

        public void insert(String word) {
            Trie cur = this;
            for (char c : word.toCharArray()) {
                int index = c - 'a';
                if (cur.children[index] == null) {
                    cur.children[index] = new Trie();
                }
                cur = cur.children[index];
            }
            cur.isEnd = true;
        }

        public boolean search(String word) {
            Trie cur = findNode(word);
            return cur != null && cur.isEnd;
        }

        public boolean startsWith(String prefix) {
            return findNode(prefix) != null;
        }

        private Trie findNode(String word) {
            Trie cur = this;
            for (char c : word.toCharArray()) {
                int index = c - 'a';
                if (cur.children[index] == null) {
                    return null;
                }
                cur = cur.children[index];
            }
            return cur;
        }
    }
    // endregion
}
