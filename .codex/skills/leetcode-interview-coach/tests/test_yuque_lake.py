"""Read-only native Lake rendering and preservation regressions."""

from pathlib import Path
import json
import re
import sys
import unittest
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from render_yuque_lake import LakeRenderer, inspect_lake, render_lake, verify_lake, _LakeParser, _walk


CODE = '''class Solution {
    public int climbStairs(int n) {
        // 原注释：保留 n+1、dp[1] 与中文标点
        int lastTwo = 1;
        int lastOne = 2;
        if (n == 1) return lastTwo;
        for (int i = 3; i <= n; i++) {
            int answer = lastOne + lastTwo;
            lastTwo = lastOne;
            lastOne = answer;
        }
        return lastOne;
    }
}'''


def record():
    return {
        "problemTitle": "E070. 爬楼梯",
        "problemUrl": "https://leetcode.cn/problems/climbing-stairs/",
        "statementMarkdown": "每次爬 `1` 或 `2` 阶。\n\n**限制**：`1 <= n <= 45`。",
        "teachingTranscript": [
            {"role": "assistant", "contentMarkdown": "先定义**状态**。\n\n```java\nint answer = lastOne + lastTwo;\n```\n\n怎样更新？"},
            {"role": "user", "contentMarkdown": "我的代码：\n\n```java\n" + CODE + "\n```"},
        ],
        "solutionVariants": [
            {"title": "数组 DP", "explanation": "保留每一级状态。", "language": "java", "code": "int[] dp = new int[n + 1];", "timeComplexity": "O(n)", "spaceComplexity": "O(n)", "isFinal": False},
            {"title": "滚动变量", "language": "java", "code": CODE, "timeComplexity": "O(n)", "spaceComplexity": "O(1)", "isFinal": True},
        ],
    }


class LakeTests(unittest.TestCase):
    def test_native_fold_wire_format_and_expanded_final(self):
        result = render_lake(record())
        self.assertTrue(result.startswith("<!doctype lake>"))
        parsed = inspect_lake(result)
        self.assertEqual(parsed["collapses"], [("题干、示例与限制", True, True), ("GPT教学流程", True, True), ("数组DP", True, True)])
        self.assertIn(("h3", "滚动变量（最终版本）"), parsed["headings"])
        self.assertNotIn("E70-爬楼梯", result)

    def test_exact_code_survives_encoded_cards(self):
        parsed = inspect_lake(render_lake(record()))
        self.assertEqual(parsed["codes"][1], ("java", CODE))
        self.assertEqual(parsed["codes"][-1], ("java", CODE))
        self.assertNotIn(CODE, render_lake(record()))  # Code lives inside URI-encoded JSON.

    def test_solution_cards_use_version_names_and_reference_name_schema(self):
        body = render_lake(record())
        cards = [json.loads(unquote(encoded)) for encoded in re.findall(r'name="codeblock" value="data:([^"]+)"', body)]
        self.assertEqual([card["name"] for card in cards][-2:], ["数组 DP", "滚动变量（最终版本）"])
        self.assertTrue(all(card["name"] and card["search"] == card["name"] for card in cards))
        self.assertEqual(cards[-1]["code"], CODE)

    def test_explicit_teaching_names_survive_quotes_and_do_not_change_code(self):
        payload = record()
        before = inspect_lake(render_lake(payload))
        payload["teachingTranscript"][0]["codeBlockNames"] = ["GPT：先计算当前状态"]
        payload["teachingTranscript"][1]["codeBlockNames"] = ["我的滚动变量版本"]
        after = inspect_lake(render_lake(payload))
        self.assertEqual(after["codeNames"][:2], ["GPT：先计算当前状态", "我的滚动变量版本"])
        self.assertEqual(after["codes"], before["codes"])
        self.assertEqual(after["text"], before["text"])

    def test_teaching_fallback_uses_speaker_heading_and_context(self):
        body = LakeRenderer().markdown("**GPT · 第 1 条**\n\n> ### 状态更新\n>\n> ```java\n> answer = a + b;\n> ```\n\n**我 · 第 2 条**\n\n我的实现：\n\n```java\nreturn answer;\n```")
        names = inspect_lake(body)["codeNames"]
        self.assertEqual(names, ["GPT · 第 1 条 · 状态更新", "我 · 第 2 条 · 我的实现"])

    def test_old_payload_and_unlabelled_code_receive_nonempty_names(self):
        self.assertEqual(inspect_lake(render_lake({"solutionJava": CODE}))["codeNames"], ["最终题解"])
        body = LakeRenderer().markdown("```java\nreturn 1;\n```\n\n```java\nreturn 2;\n```")
        self.assertEqual(inspect_lake(body)["codeNames"], ["Java 示例代码", "Java 示例代码（代码 2）"])

    def test_plain_text_fences_use_plain_mode_without_changing_content_or_name(self):
        code = "  1\n 1 1\n1 2 1  "
        for language in ["", "text", "plaintext", "plain", "java"]:
            with self.subTest(language=language):
                renderer = LakeRenderer()
                body = renderer.markdown(f"```{language}\n{code}\n```", code_names=iter(["三角形示意"]))
                parsed = inspect_lake(body)
                self.assertEqual(parsed["codes"], [("java" if language == "java" else "plain", code)])
                self.assertEqual(parsed["codeNames"], ["三角形示意"])
        self.assertEqual(inspect_lake(LakeRenderer().code(code, ""))["codes"], [("plain", code)])

    def test_code_characters_are_never_markdown_interpreted(self):
        code = '\t// **保留** <xml> & "引号" \\\nString x = "```";  \nint[] a = {1, 2};'
        body = LakeRenderer().markdown("````java\n" + code + "\n````")
        self.assertEqual(inspect_lake(body)["codes"], [("java", code)])
        self.assertEqual(inspect_lake(body)["bold"], [])

    def test_quote_is_split_around_real_code_card(self):
        body = LakeRenderer().markdown("> 一段讲解\n>\n> ~~~~java\n> if (a < b) {\n>     a++;\n> }\n> ~~~~\n>\n> 后续问题")
        parsed = inspect_lake(body)
        self.assertEqual(parsed["quotes"], 2)
        self.assertEqual(parsed["codes"], [("java", "if (a < b) {\n    a++;\n}")])
        self.assertEqual(parsed["text"], "一段讲解后续问题")
        self.assertEqual(parsed["flow"], [("text", "一段讲解"), ("code", "java", "if (a < b) {\n    a++;\n}"), ("text", "后续问题")])
        self.assertEqual([node.tag for node in _LakeParser(body).root.children], ["blockquote", "card", "blockquote"])

    def test_multiple_diagrams_stay_between_their_coach_explanations(self):
        payload = {
            "teachingTranscript": [{
                "role": "assistant",
                "contentMarkdown": "先看第一行。\n\n```text\n1\n```\n\n再看第二行。\n\n```text\n1 1\n```\n\n第三行。\n\n```text\n1 2 1\n```\n\n中间的数字从哪里来？",
                "codeBlockNames": ["第一行", "第二行", "第三行"],
            }],
        }
        body = render_lake(payload)
        parsed = inspect_lake(body)
        self.assertEqual(parsed["codeNames"], ["第一行", "第二行", "第三行"])
        self.assertEqual(parsed["codes"], [("plain", "1"), ("plain", "1 1"), ("plain", "1 2 1")])
        flow = parsed["flow"]
        self.assertTrue(flow[0][1].endswith("先看第一行。"))
        self.assertEqual(flow[1:6], [("code", "plain", "1"), ("text", "再看第二行。"), ("code", "plain", "1 1"), ("text", "第三行。"), ("code", "plain", "1 2 1")])
        self.assertEqual(flow[6], ("text", "中间的数字从哪里来？"))
        for node in _walk(_LakeParser(body).root):
            if node.tag == "blockquote":
                self.assertFalse(any(child.tag == "card" for child in _walk(node)))

    def test_quoted_list_code_does_not_remain_under_a_quote(self):
        body = LakeRenderer().markdown("> - 先解释\n>\n>   ```java\n>   int answer = 1;\n>   ```\n>\n>   再提问")
        parsed = inspect_lake(body)
        self.assertEqual(parsed["flow"], [("text", "先解释"), ("code", "java", "int answer = 1;"), ("text", "再提问")])
        self.assertIn("<ul ", body)
        for node in _walk(_LakeParser(body).root):
            if node.tag == "blockquote":
                self.assertFalse(any(child.tag == "card" for child in _walk(node)))

    def test_readback_detects_cards_moved_after_all_prose(self):
        expected = LakeRenderer().markdown("> 先讲解\n>\n> ```java\n> int answer = 1;\n> ```\n>\n> 再提问")
        card = re.search(r"<card\b.*?</card>", expected).group()
        moved = expected.replace(card, "") + card
        expected_parts, moved_parts = inspect_lake(expected), inspect_lake(moved)
        self.assertEqual(expected_parts["text"], moved_parts["text"])
        self.assertEqual(expected_parts["codes"], moved_parts["codes"])
        self.assertTrue(any("交错顺序" in error for error in verify_lake(expected, {"body_lake": moved})))

    def test_bold_link_inline_code_and_markup_safety(self):
        body = LakeRenderer().markdown("**先计算 `answer`**。 [链接](<https://example.com/a(b)?x=1&y=2>)\n\n<script>alert(1)</script>")
        parsed = inspect_lake(body)
        self.assertEqual(parsed["bold"], ["先计算answer"])
        self.assertEqual(parsed["links"], [("https://example.com/a(b)?x=1&y=2", "链接")])
        self.assertIn("&lt;script&gt;", body)
        self.assertNotIn("<script>", body)
        self.assertIn("<code ", body)

    def test_markdown_link_active_scheme_remains_text(self):
        body = LakeRenderer().markdown("[不执行](javascript:alert(1))")
        self.assertEqual(inspect_lake(body)["links"], [])
        self.assertNotIn('href="javascript:', body)

    def test_list_continuation_and_table(self):
        source = "- 第一条\n  保留补充。\n  - 子条目\n- 第二条\n\n| n | 答案 |\n| --- | --- |\n| 1 | 1 |"
        body = LakeRenderer().markdown(source)
        self.assertEqual(body.count("<ul "), 2)
        self.assertIn("<table ", body)
        self.assertIn("第一条保留补充。子条目第二条n答案11", inspect_lake(body)["text"])

    def test_empty_and_legacy_payload(self):
        self.assertTrue(render_lake({}).startswith("<!doctype lake>"))
        body = render_lake({"problemTitle": "E070. 爬楼梯", "noteContent": "# E70-爬楼梯\n\n## 最终题解\n\n```java\n" + CODE + "\n```", "conversationDigest": {"firstReaction": "不应重复"}})
        self.assertEqual(inspect_lake(body)["codes"], [("java", CODE)])
        self.assertNotIn("不应重复", body)

    def test_verification_ignores_editor_ids_but_checks_semantics(self):
        expected = render_lake(record())
        rewritten = re.sub(r"u[0-9a-f]{8}", "editor-reassigned-id", expected)
        self.assertEqual(verify_lake(expected, {"body_lake": rewritten}), [])
        self.assertEqual(verify_lake(expected, {"format": "lake", "body": rewritten}), [])

    def test_verification_rejects_plain_html_and_markdown(self):
        expected = render_lake(record())
        self.assertTrue(verify_lake(expected, {"format": "markdown", "body": "<details>文字</details>"}))
        self.assertTrue(verify_lake(expected, {"body_html": expected}))

    def test_verification_detects_changed_comments_fold_and_language(self):
        expected = render_lake(record())
        bad_comment = expected.replace("n%2B1", "n%2B2")
        self.assertTrue(any("代码" in error for error in verify_lake(expected, {"body_lake": bad_comment})))
        open_fold = expected.replace('open="false"', 'open="true"', 1)
        self.assertTrue(any("折叠" in error for error in verify_lake(expected, {"body_lake": open_fold})))
        plain_fold = expected.replace('class="lake-collapse"', 'class="ordinary-details"', 1)
        self.assertTrue(any("折叠" in error for error in verify_lake(expected, {"body_lake": plain_fold})))
        wrong_language = expected.replace('%22mode%22%3A%22java%22', '%22mode%22%3A%22text%22', 1)
        self.assertTrue(any("代码" in error for error in verify_lake(expected, {"body_lake": wrong_language})))
        missing_name = re.sub(r"%22name%22%3A%22.*?%22%2C%22search%22", "%22name%22%3A%22%22%2C%22search%22", expected, count=1)
        self.assertTrue(any("名称" in error for error in verify_lake(expected, {"body_lake": missing_name})))

    def test_verification_checks_visual_features(self):
        expected = render_lake(record())
        cases = [
            (expected.replace("blockquote", "div"), "引用"),
            (expected.replace("strong", "span"), "加粗"),
            (expected.replace("https://leetcode.cn/", "https://example.com/"), "链接"),
            (expected.replace("<h3 ", "<h4 ").replace("</h3>", "</h4>"), "标题"),
        ]
        for body, feature in cases:
            with self.subTest(feature=feature):
                self.assertTrue(any(feature in error for error in verify_lake(expected, {"body_lake": body})))


if __name__ == "__main__":
    unittest.main()
