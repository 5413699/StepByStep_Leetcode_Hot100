package com.czf.arraylist;

import java.util.Arrays;
import java.util.Iterator;
import java.util.function.Consumer;
import java.util.stream.IntStream;


public class DynamicArray implements Iterable<Integer> {
    /**
     * 动态数组
     * 根据索引查询：O(1),根据索引，直接计算元素地址
     * 根据值查询：O(n),只能通过遍历查找
     * 插入：头部/中间：O(n),需要将其他元素向后移动1位
     * 尾部插入：O(1),直接在数组最后添加元素（扩容频率低，被均摊了）
     *
     */

    private int size = 0; // 逻辑大小
    private int capacity = 8; // 容量
    // 用这种写法，假如创建后没有给数组赋值，也会额外占用capacity个元素的空间
    // 就白白浪费了，private int[] array = new int[capacity];
    // 因此我们选择先创建一个空数组，添加元素时再通过扩容方法创建空间
    // 懒汉式创建数组
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
        // 检查容量，容量不足时进行扩容
        // 选中要转换为函数的代码，鼠标右键 ->重构->提取方法即可将代码转换为函数
        checkAndGrow();
        // 添加逻辑
        if (index >= 0 && index < size) {
            // 向后挪动, 空出待插入位置
            System.arraycopy(array, index,
                    array, index + 1, size - index);
        }
        array[index] = element;
        size++;
    }

    private void checkAndGrow() {
        // 实现懒汉式初始化数组
        // 从0扩容到初始容量8
        if (size == 0) {
            array = new int[capacity];
        }
        // 在添加前，需要做容量检查，若容量不够，则扩容
        // 当size=capacity时，需要扩容
        else if (size >= capacity) {
            //进行扩容
            //1.新的容量比旧的容量大多少合适
            //Java中是扩容为1.5倍，但我们不能直接乘以1.5，因为容量是整数，不能乘小数
            //因此我们采用移位的方法进行扩容，右移一位相当于除以2，再加上原容量，就相当于1.5倍了
            //capacity = capacity + (capacity >> 1);
            capacity += capacity >> 1;
            //2.创建新的数组
            int[] newArray = new int[capacity];
            //3.将原数组的元素复制到新的数组中
            System.arraycopy(array, 0, newArray, 0, size);
            //4,用新数组指向旧数组
            array = newArray;
        }
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