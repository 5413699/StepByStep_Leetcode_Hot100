"""Regression checks for Math.min discovery and reusable note preservation."""

from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from common_function_usage import (
    common_function_tags_from_usages,
    detect_function_usages,
    render_function_note,
)


class MathMinUsageTests(unittest.TestCase):
    def test_discovers_math_min_in_actual_perfect_squares_solution(self):
        repo = Path(__file__).resolve().parents[4]
        java = (repo / "src/main/java/com/czf/arraylist/M279_Perfect_Squares.java").read_text(encoding="utf-8")
        usages = detect_function_usages(java, problem_title="M279-完全平方数")
        math_usage = next(item for item in usages if item["functionName"] == "Math.min")
        self.assertEqual(math_usage["commonFunction"], "数学Math的常用函数")
        self.assertIn("数学Math的常用函数", common_function_tags_from_usages(usages))
        self.assertIn("dp[i - j * j] + 1", math_usage["exampleCode"])
        self.assertEqual(math_usage["problemTitle"], "M279-完全平方数")
        self.assertTrue(any("docs.oracle.com" in item["url"] for item in math_usage["sources"]))

    def test_handles_whitespace_without_confusing_other_methods(self):
        usages = detect_function_usages("int answer = Math \n . min (a, b);")
        self.assertEqual([item["functionName"] for item in usages], ["Math.min"])
        for code in ["Math.max(a, b);", "MyMath.min(a, b);", "Math.minimum(a, b);"]:
            with self.subTest(code=code):
                self.assertNotIn("Math.min", [item["functionName"] for item in detect_function_usages(code)])

    def test_rendering_preserves_user_additions_and_deduplicates_problem(self):
        usage = detect_function_usages("Math.min(a, b);", problem_title="M279-完全平方数")[0]
        first = render_function_note(usage)
        existing = "我的前言。\n\n" + first + "\n我的自定义补充。\n"
        rendered = render_function_note(usage, existing)
        rendered_again = render_function_note(usage, rendered)
        self.assertEqual(rendered, rendered_again)
        self.assertTrue(rendered.startswith("我的前言。"))
        self.assertTrue(rendered.rstrip().endswith("我的自定义补充。"))
        self.assertEqual(rendered.count("- M279-完全平方数："), 1)
        self.assertIn("## 常见代码结构", rendered)
        self.assertIn("```java", rendered)
        self.assertIn("依赖状态均已求解", rendered)


class CoinChangeUsageTests(unittest.TestCase):
    def test_actual_solution_uses_amount_dp_and_int_fill_examples(self):
        repo = Path(__file__).resolve().parents[4]
        java = (repo / "src/main/java/com/czf/arraylist/M322_Coin_Change.java").read_text(encoding="utf-8")
        usages = detect_function_usages(java, problem_title="M322-零钱兑换")
        by_id = {usage["id"]: usage for usage in usages}
        self.assertEqual(set(by_id), {"math-min", "arrays-fill"})
        math_usage = by_id["math-min"]
        self.assertIn("dp[i - coin] + 1", math_usage["exampleCode"])
        self.assertIn("continue;", math_usage["exampleCode"])
        self.assertIn("amount + 1 ? -1", math_usage["exampleCode"])
        fill_usage = by_id["arrays-fill"]
        self.assertEqual(fill_usage["signature"], "Arrays.fill(int[] a, int val)")
        self.assertLess(fill_usage["exampleCode"].index("Arrays.fill"), fill_usage["exampleCode"].index("dp[0] = 0"))
        self.assertIn("int[]", fill_usage["sources"][0]["note"])
        for usage in usages:
            with self.subTest(function=usage["functionName"]):
                self.assertEqual(usage["problemTitle"], "M322-零钱兑换")
                self.assertIn("零钱兑换", usage["exampleTitle"])
                rendered = render_function_note(usage)
                self.assertNotIn("完全平方数", rendered)
                self.assertNotIn("char[][]", rendered)
                self.assertIn("- M322-零钱兑换：", rendered)

    def test_method_body_context_works_without_method_name(self):
        usages = detect_function_usages(
            "int[] dp = new int[amount + 1]; Arrays.fill(dp, amount + 1); "
            "dp[i] = Math.min(dp[i], dp[i - coins[j]] + 1);"
        )
        self.assertEqual(len(usages), 2)
        self.assertTrue(all("零钱兑换" in usage["exampleTitle"] for usage in usages))

    def test_specialization_does_not_change_other_problem_defaults(self):
        default_code = "Math.min(a, b); Arrays.fill(board[i], '.');"
        before = detect_function_usages(default_code)
        detect_function_usages("coinChange(coins, amount); " + default_code)
        after = detect_function_usages(default_code)
        self.assertEqual(before, after)
        self.assertIn("完全平方数", after[0]["exampleTitle"])
        self.assertEqual(after[1]["signature"], "Arrays.fill(char[] a, char val)")
        self.assertIn("char[][] board", after[1]["exampleCode"])


if __name__ == "__main__":
    unittest.main()
