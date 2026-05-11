package com.czf.string;

import java.util.*;

/**
 * ClassName: M049_Group_Anagrams
 * Package: com.czf.string
 * Description:
 *
 * @Author 陈智锋
 * @Create 2026/5/8 15:06
 * @Version 1.0
 */
public class M049_Group_Anagrams {

    public static void main(String[] args) {
        String[] strs = {"eat", "tea", "tan", "ate", "nat", "bat"};
        List<List<String>> ans = groupAnagrams(strs);
        System.out.println(ans);
    }
    public static List<List<String>> groupAnagrams(String[] strs) {

        // 使用hashmap，key存字母组合，value存该组合对应的字母异位词
        Map<String, List<String>> map = new HashMap<>();

        // 遍历字符串数组中的每个字符串
        for (String str : strs) {
            // 1. 对当前字符串进行排序，生成 key
            char[] chars = str.toCharArray();
            Arrays.sort(chars);
            String key = new String(chars);

            // 2. 如果 key 不存在，初始化列表
            if(!map.containsKey(key)){
                map.put(key , new ArrayList());
            }

            // 3. 加入原始字符串
            map.get(key).add(str);

        }

        return new ArrayList<>(map.values());

    }
}
