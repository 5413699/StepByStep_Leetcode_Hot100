package com.czf.graph;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

/**
 * ClassName: M207_Course_Schedule
 * Package: com.czf.graph
 * Description:
 *
 * @Author 陈智飞
 * @Create 2026/6/5 00:00
 * @Version 1.0
 */
public class M207_Course_Schedule {

    public static void main(String[] args) {
        M207_Course_Schedule solution = new M207_Course_Schedule();

        int[][] prerequisites1 = {
                {1, 0}
        };
        System.out.println("示例1 actual: " + solution.canFinish(2, prerequisites1));
        System.out.println("示例1 expected: true");

        int[][] prerequisites2 = {
                {1, 0},
                {0, 1}
        };
        System.out.println("示例2 actual: " + solution.canFinish(2, prerequisites2));
        System.out.println("示例2 expected: false");
    }

    // region LeetCode solution
    public boolean canFinish(int numCourses, int[][] prerequisites) {
        List<List<Integer>> graph = new ArrayList<>();
        int[] indegree = new int[numCourses];
        Queue<Integer> queue = new LinkedList<>();

        for (int i = 0; i < numCourses; i++) {
            graph.add(new ArrayList<>());
        }

        for (int[] prerequisite : prerequisites) {
            int course = prerequisite[0];
            int pre = prerequisite[1];

            graph.get(pre).add(course);
            indegree[course]++;
        }

        for (int i = 0; i < numCourses; i++) {
            if (indegree[i] == 0) {
                queue.offer(i);
            }
        }

        int learned = 0;
        while (!queue.isEmpty()) {
            int cur = queue.poll();
            learned++;

            for (int nextCourse : graph.get(cur)) {
                indegree[nextCourse]--;
                if (indegree[nextCourse] == 0) {
                    queue.offer(nextCourse);
                }
            }
        }

        return learned == numCourses;
    }
    // endregion
}
