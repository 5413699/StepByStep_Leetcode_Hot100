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


if __name__ == "__main__":
    unittest.main()
