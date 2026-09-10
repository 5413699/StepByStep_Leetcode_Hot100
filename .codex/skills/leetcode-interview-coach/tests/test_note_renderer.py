"""Focused compatibility and fidelity tests for the shared learning renderer."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from render_learning_note import build_sections, normalize_title, render_markdown


def sample_payload():
    return {
        "problemTitle": "E070. 爬楼梯",
        "problemUrl": "https://leetcode.cn/problems/climbing-stairs/",
        "statementMarkdown": "每次爬 **1 或 2** 阶。\n\n示例：n = 2，输出 2。",
        "teachingTranscript": [
            {"role": "assistant", "contentMarkdown": "先定义 `dp[i]`。\n\n```java\nint[] dp = new int[n + 1];\n```"},
            {"role": "user", "contentMarkdown": "我的代码：\n\n```java\n// 保留我写的注释\nint lastTwo = 1;\n```"},
            {"role": "assistant", "contentMarkdown": "原来的边界说明有误。", "correctionMarkdown": "n = 1 时长度为 2，dp[1] 合法。这是教练口误。"},
        ],
        "solutionVariants": [
            {"title": "数组 DP", "language": "java", "code": "// 我的数组注释\nint[] dp = new int[n + 1];", "timeComplexity": "O(n)", "spaceComplexity": "O(n)", "isFinal": False},
            {"title": "滚动变量", "language": "java", "code": "// 我的旧注释，必须保留\nint lastTwo = 1;\nint lastOne = 2;", "timeComplexity": "O(n)", "spaceComplexity": "O(1)", "isFinal": True, "correctionMarkdown": "旧注释沿用数组版；当前只保存前两个状态。"},
        ],
        "conversationDigest": {"firstReaction": "首次学习动态规划。", "breakthroughs": ["只依赖前两个状态。"], "edgeCases": ["n = 1 时返回 1。"], "interviewExpression": "按最后一步分类相加。", "reviewAdvice": ["两天后重写。"]},
        "readiness": {"status": ["提示后完成"], "weakPoints": ["独立定义状态"], "interviewExpression": "基本可用", "nextReview": ["两天后重写。"]},
    }


class NoteRendererTests(unittest.TestCase):
    def test_normalizes_leading_zero_title_without_guessing_difficulty(self):
        self.assertEqual(normalize_title({"problemTitle": "E070. 爬楼梯"}), "E70-爬楼梯")
        self.assertEqual(normalize_title({"problemTitle": "70. 爬楼梯"}), "70-爬楼梯")
        self.assertEqual(normalize_title({"problemTitle": "M287-寻找重复数"}), "M287-寻找重复数")

    def test_section_order_and_collapse_are_explicit(self):
        sections = build_sections(sample_payload())
        collapses = [s for s in sections if s["kind"] == "collapse"]
        self.assertEqual([s["title"] for s in collapses], ["题干、示例与限制", "GPT 教学流程", "数组 DP"])
        self.assertTrue(all(s["collapsed"] for s in collapses))
        final = next(s for s in sections if "滚动变量（最终版本）" in s["markdown"])
        self.assertEqual(final["kind"], "markdown")

    def test_preserves_code_comments_names_and_transcript_order(self):
        payload = sample_payload()
        rendered = render_markdown(payload)
        for variant in payload["solutionVariants"]:
            self.assertIn(variant["code"], rendered)
        self.assertIn("// 保留我写的注释\nint lastTwo = 1;", rendered)
        self.assertLess(rendered.index("**GPT · 第 1 条**"), rendered.index("**我 · 第 2 条**"))
        self.assertLess(rendered.index("**我 · 第 2 条**"), rendered.index("**GPT · 第 3 条**"))
        self.assertIn("> 先定义 `dp[i]`。", rendered)
        self.assertIn("> ```java\n> int[] dp = new int[n + 1];\n> ```", rendered)
        self.assertIn("**勘误／更新说明**\n\nn = 1 时长度为 2", rendered)

    def test_code_card_names_are_metadata_not_history_rewrites(self):
        payload = sample_payload()
        original_turns = json.loads(json.dumps(payload["teachingTranscript"]))
        payload["teachingTranscript"][0]["codeBlockNames"] = ["GPT：状态数组初始化"]
        payload["teachingTranscript"][1]["codeBlockNames"] = ["我的滚动变量尝试"]
        sections = build_sections(payload)
        teaching = next(section for section in sections if section.get("title") == "GPT 教学流程")
        self.assertEqual(teaching["codeBlockNames"], ["GPT：状态数组初始化", "我的滚动变量尝试"])
        self.assertEqual([section["codeTitle"] for section in sections if "codeTitle" in section], ["数组 DP", "滚动变量（最终版本）"])
        rendered = render_markdown(payload)
        self.assertIn("> **代码：GPT：状态数组初始化**\n>\n> ```java", rendered)
        self.assertIn("**代码：我的滚动变量尝试**\n\n```java", rendered)
        for before, after in zip(original_turns, payload["teachingTranscript"]):
            self.assertEqual(before["contentMarkdown"], after["contentMarkdown"])
        self.assertIn("> int[] dp = new int[n + 1];\n> ```", rendered)

    def test_code_card_names_keep_positions_when_other_turns_omit_names(self):
        payload = sample_payload()
        payload["teachingTranscript"][0]["correctionMarkdown"] = "```java\n// 补充说明\n```"
        payload["teachingTranscript"][1]["codeBlockNames"] = ["我的实现"]
        teaching = next(section for section in build_sections(payload) if section.get("title") == "GPT 教学流程")
        self.assertEqual(teaching["codeBlockNames"], ["", "", "我的实现"])

    def test_invalid_card_names_fail_before_rendering(self):
        for names in ["一个名称", [""], [], ["第一个", "多余的"]]:
            payload = sample_payload()
            payload["teachingTranscript"][0]["codeBlockNames"] = names
            with self.subTest(names=names), self.assertRaisesRegex(ValueError, "codeBlockNames"):
                build_sections(payload)

    def test_natural_language_digest_and_review_deduplication(self):
        payload = sample_payload()
        payload["readiness"]["internal"] = {"hidden": "不要泄漏"}
        payload["conversationDigest"]["unknown"] = {"hidden": "不要泄漏"}
        rendered = render_markdown(payload)
        for machine_text in ["firstReaction", "weakPoints", "nextReview", "conversationDigest", "不要泄漏", "{'", "当前对话摘要"]:
            self.assertNotIn(machine_text, rendered)
        self.assertIn("掌握状态：提示后完成", rendered)
        self.assertEqual(rendered.count("两天后重写。"), 1)

    def test_old_note_content_is_complete_fallback_without_duplicate_summary(self):
        payload = {"problemTitle": "E070. 爬楼梯", "noteContent": "# E070. 爬楼梯\n\n<!-- codex-leetcode-start -->\n## 本次训练记录\n\n原笔记。\n<!-- codex-leetcode-end -->", "conversationDigest": {"firstReaction": "不要另加摘要。"}, "solutionJava": "return 1;"}
        rendered = render_markdown(payload)
        self.assertEqual(rendered.count("# E70-爬楼梯"), 1)
        self.assertIn("原笔记。", rendered)
        self.assertNotIn("codex-", rendered)
        self.assertNotIn("不要另加摘要", rendered)
        self.assertNotIn("return 1", rendered)

    def test_new_structure_wins_over_stale_note_content(self):
        payload = sample_payload()
        payload["noteContent"] = "不应显示的旧正文"
        rendered = render_markdown(payload, include_title=False)
        self.assertNotIn("不应显示的旧正文", rendered)
        self.assertNotIn("# E70-爬楼梯", rendered)
        self.assertIn("力扣原题", rendered)

    def test_legacy_fields_still_render_without_empty_java_fence(self):
        rendered = render_markdown({"problemTitle": "旧题", "statementMarkdown": "已有题干", "processMarkdown": "已有过程", "thinkingMarkdown": "已有思考", "complexityMarkdown": "时间 O(n)。", "pitfalls": ["检查边界。"]})
        for text in ["已有题干", "已有过程", "已有思考", "时间 O(n)", "检查边界"]:
            self.assertIn(text, rendered)
        self.assertNotIn("```java", rendered)
        self.assertIn("完整教学对话未提供", rendered)

    def test_missing_transcript_is_marked_without_invented_messages(self):
        payload = sample_payload()
        del payload["teachingTranscript"]
        rendered = render_markdown(payload)
        self.assertIn("完整教学对话未提供", rendered)
        self.assertNotIn("**GPT · 第", rendered)
        self.assertIn("首次学习动态规划。", rendered)

    def test_human_sections_override_only_corresponding_digest(self):
        payload = sample_payload()
        payload["trainingMarkdown"] = "已人工整理训练记录。"
        payload["reviewMarkdown"] = "已人工整理复习建议。"
        rendered = render_markdown(payload)
        self.assertNotIn("首次学习动态规划。", rendered)
        self.assertNotIn("两天后重写。", rendered)
        self.assertIn("已人工整理训练记录。", rendered)
        self.assertIn("n = 1 时返回 1。", rendered)

    def test_authored_boundaries_do_not_receive_another_digest_appendix(self):
        payload = sample_payload()
        payload["complexityMarkdown"] = "n = 1 时直接返回初始状态；时间 O(n)。"
        rendered = render_markdown(payload)
        self.assertIn(payload["complexityMarkdown"], rendered)
        self.assertNotIn("- n = 1 时返回 1。", rendered)

    def test_code_backticks_and_literal_markers_are_not_rewritten(self):
        payload = sample_payload()
        code = '    // ``` 不能结束外层代码块\n    String marker = "<!-- codex-literal -->";\n    int lastTwo = 1;  '
        payload["solutionVariants"][1]["code"] = code
        payload["teachingTranscript"][1]["contentMarkdown"] = '```java\n// <!-- codex-literal -->\n```'
        rendered = render_markdown(payload)
        self.assertIn("````java\n" + code + "\n````", rendered)
        self.assertIn("// <!-- codex-literal -->", rendered)

    def test_invalid_transcript_roles_and_final_flags_fail_before_publication(self):
        payload = sample_payload()
        payload["teachingTranscript"][0]["role"] = "system"
        with self.assertRaisesRegex(ValueError, "角色"):
            build_sections(payload)
        payload = sample_payload()
        payload["solutionVariants"][0]["isFinal"] = True
        with self.assertRaisesRegex(ValueError, "最终版本"):
            build_sections(payload)

    def test_cli_writes_utf8_without_bom(self):
        with tempfile.TemporaryDirectory(prefix="note-render-") as temporary:
            source, target = Path(temporary) / "input.json", Path(temporary) / "note.md"
            source.write_text(json.dumps(sample_payload(), ensure_ascii=False), encoding="utf-8")
            subprocess.run([sys.executable, str(SCRIPTS / "render_learning_note.py"), "--input", str(source), "--output", str(target)], check=True)
            data = target.read_bytes()
            self.assertFalse(data.startswith(b"\xef\xbb\xbf"))
            self.assertEqual(data.decode("utf-8"), render_markdown(sample_payload()).replace("\n", "\r\n") if sys.platform == "win32" else render_markdown(sample_payload()))


if __name__ == "__main__":
    unittest.main()
