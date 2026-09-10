"""Validate the real E70 record without modifying its learner-authored code."""

import json
from math import comb
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


FIXTURE = Path(__file__).parent / "fixtures" / "e070_learning_record.json"


class E070LearningRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_transcript_order_and_source_corrections(self):
        transcript = self.payload["teachingTranscript"]
        self.assertEqual([entry["role"] for entry in transcript], ["user", "assistant"] * 4)
        self.assertIn("第一次学习动态规划，教教我", transcript[0]["contentMarkdown"])
        self.assertIn("dp[2]+dp[3] = 2+3 = 5", transcript[2]["contentMarkdown"])
        self.assertIn("教练", transcript[5]["correctionMarkdown"])
        self.assertIn("口误", transcript[5]["correctionMarkdown"])
        self.assertIn("保留自己的注释", transcript[7]["correctionMarkdown"])
        self.assertEqual(self.payload["sourceMetadata"]["missingContent"], [])

    def test_answer_versions_preserve_every_comment_from_the_attempts(self):
        for position, variant in zip([4, 6], self.payload["solutionVariants"]):
            attempt = self.payload["teachingTranscript"][position]["contentMarkdown"]
            original_code = re.search(r"```java\n(.*?)\n```", attempt, re.DOTALL).group(1)
            self.assertEqual(variant["code"], original_code)
            comments = [line.strip() for line in variant["code"].splitlines() if line.strip().startswith("//")]
            self.assertIn("// 记录爬到每一级台阶各有几种方法", comments)
            self.assertTrue(any("创建有n+1个元素的数组" in line for line in comments))
        self.assertEqual(self.payload["solutionJava"], self.payload["solutionVariants"][1]["code"])
        self.assertEqual(self.payload["conversationDigest"]["misconceptions"], [])

    def test_both_copyable_java_versions_for_all_45_inputs(self):
        bundled = Path("G:/APP_ScienceDeveloper/JDK21/bin")
        javac = str(bundled / "javac.exe") if (bundled / "javac.exe").is_file() else shutil.which("javac")
        java = str(bundled / "java.exe") if (bundled / "java.exe").is_file() else shutil.which("java")
        if not javac or not java:
            self.skipTest("A JDK is required for the complete Java verification.")
        expected = [sum(comb(n - twos, twos) for twos in range(n // 2 + 1)) for n in range(1, 46)]
        runner = """public class Runner {
    public static void main(String[] args) {
        Solution solution = new Solution();
        for (int n = 1; n <= 45; n++) {
            System.out.println(solution.climbStairs(n));
        }
    }
}
"""
        for variant in self.payload["solutionVariants"]:
            with self.subTest(variant=variant["title"]), tempfile.TemporaryDirectory(prefix="e070-variant-") as temporary:
                location = Path(temporary)
                (location / "Solution.java").write_text(variant["code"], encoding="utf-8")
                (location / "Runner.java").write_text(runner, encoding="utf-8")
                compile_result = subprocess.run([javac, "-encoding", "UTF-8", "Solution.java", "Runner.java"], cwd=location, capture_output=True, timeout=30)
                self.assertEqual(compile_result.returncode, 0, compile_result.stderr.decode("utf-8", errors="replace"))
                run_result = subprocess.run([java, "-cp", str(location), "Runner"], cwd=location, capture_output=True, timeout=30)
                self.assertEqual(run_result.returncode, 0, run_result.stderr.decode("utf-8", errors="replace"))
                self.assertEqual([int(line) for line in run_result.stdout.splitlines()], expected)


if __name__ == "__main__":
    unittest.main()
