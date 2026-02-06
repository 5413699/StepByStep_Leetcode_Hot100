package com.czf.arraylist;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import static org.junit.jupiter.api.Assertions.*;

public class TestDynamicArray {

    @Test
    @DisplayName("测试添加")
    public void test1() {
        DynamicArray dynamicArray = new DynamicArray();
        dynamicArray.addLast(1);
        dynamicArray.addLast(2);
        dynamicArray.addLast(3);
        dynamicArray.addLast(4);

        dynamicArray.forEach((element)-> {
            System.out.println(element);
        });
    }

    @Test
    @DisplayName("测试使用迭代器进行遍历")
    public void test2() {
        DynamicArray dynamicArray = new DynamicArray();
        dynamicArray.addLast(1);
        dynamicArray.addLast(2);
        dynamicArray.addLast(3);
        dynamicArray.addLast(4);

        // 使用增强for循环进行遍历
        // 增强for循环的内部就是
        // 在每次循环时调用迭代器的hasnext方法看看有没有下一个元素，如果有，就继续循环
        // 每次循环时调用next方法，将获取到的当前元素赋值给element，并移动指针
        //！因此如果没有实现迭代器，增强for循环就无法使用。
        for (Integer element : dynamicArray) {
            System.out.println(element);
        }

    }

    @Test
    @DisplayName("测试使用流的方式进行遍历")
    public void test3() {
        DynamicArray dynamicArray = new DynamicArray();
        dynamicArray.addLast(1);
        dynamicArray.addLast(2);
        dynamicArray.addLast(3);
        dynamicArray.addLast(4);

        //既然是流了，我们就可以调用stream里的一些方法，比如forEach
        //修改后，会发现此次仅遍历了有效的1234，成功
        dynamicArray.stream().forEach(element -> {
            System.out.println(element);
        });
    }


    @Test
    @DisplayName("测试删除")
    public void test4() {
        DynamicArray dynamicArray = new DynamicArray();
        dynamicArray.addLast(1);
        dynamicArray.addLast(2);
        dynamicArray.addLast(3);
        dynamicArray.addLast(4);
        // 删除索引为2的元素进行测试
        int removed = dynamicArray.remove(2);
        System.out.println(removed);
        System.out.println("-------");
        // 使用流的方法进行打印，遍历删除后的数组元素
        dynamicArray.stream().forEach(element -> {
            System.out.println(element);
        });
    }
}
