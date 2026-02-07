package com.czf.arraylist;

import java.util.Arrays;
import java.util.Iterator;
import java.util.function.Consumer;
import java.util.stream.IntStream;


public class DynamicArray implements Iterable<Integer> {
    private int size = 0; // 逻辑大小
    private int capacity = 8; // 容量
    private int[] array = {};

    public int[] array() {
        return Arrays.copyOf(array, size);
    }

    /**
     * 向最后位置 [size] 添加元素
     *
     * @param element 待添加元素
     */
    public void addLast(int element) {
//        array[size] = element;
//        size++;
        add(size, element);
    }

    /**
     * 向 [0 .. size] 位置添加元素
     *
     * @param index   索引位置
     * @param element 待添加元素
     */
    public void add(int index, int element) {
        // 添加逻辑
        if (index >= 0 && index < size) {
            // 向后挪动, 空出待插入位置
            System.arraycopy(array, index,
                    array, index + 1, size - index);
        }
        array[index] = element;
        size++;
    }


    /**
     * 从 [0 .. size) 范围删除元素
     *
     * @param index 索引位置
     * @return 被删除元素
     */
    public int remove(int index) {//假设只输入有效的索引
        // 1.先编写返回值，找到被删除的元素,将其作为返回值
        int removed = array[index];
        // 2.删除逻辑
        // 先找到后面的元素，将其往前移，最后将size-1
        // 数组内移动元素，用system.arraycopy即可
        // 3.当前代码存在可优化的地方，当删除的元素是最后一个元素时，会变成移动0个元素
        // 并不会报错，但添加if进行判断后，逻辑上更合理
        if (index < size - 1) {
            System.arraycopy(array, index + 1,
                array,index,size-index-1);
        }
        size--;
        return removed;
    }


    /**
     * 查询元素
     *
     * @param index 索引位置, 在 [0..size) 区间内
     * @return 该索引位置的元素
     */
    public int get(int index) {
        return array[index];
    }

    /**
     * 遍历方法1
     *
     * @param consumer 遍历要执行的操作, 入参: 每个元素
     */
    public void foreach(Consumer<Integer> consumer) {
        for (int i = 0; i < size; i++) {
            // 提供 array[i]
            // 返回 void
            consumer.accept(array[i]);
        }
    }


    @Override
    public Iterator<Integer> iterator() {
        /**
         * 根据接口的抽象方法签名可以看出，我们需要返回一个Iterator<Integer>类型的变量，
         * 因此我们创建对象返回。（匿名内部类）
         * Iterator有两个需要实现的方法：
         * 1. boolean hasNext()：判断是否还有下一个元素。
         * 2. E next()：返回下一个元素。
         */

        return new Iterator<Integer>() {
            // i代表当前索引的位置，从数组头部开始遍历
            int i=0;
            @Override
            public boolean hasNext() {//判断是否还有下一个元素。
                // 判断当前索引是否小于数组长度
                return i<size;
            }

            // 返回当前元素的位置
            @Override
            public Integer next() {//先返回当前元素。再移动到下一个元素。
                return array[i++];
            }
        };
    }

    /**
     * 遍历方法3 - stream 遍历
     *
     * @return stream 流
     */
    public IntStream stream(){
        // .of方法可以将数组转换成stream流
        // 但是不能将array当成数组传给of方法
        // 因为这样数组的有效部分还是无效部分都会被遍历
        // 所以需要使用Arrays.copyOfRange方法, 将array的有效部分转换成stream流
        // 注意这里的区间是含头不含尾的
        return IntStream.of(Arrays.copyOfRange(array, 0, size));
    }
}