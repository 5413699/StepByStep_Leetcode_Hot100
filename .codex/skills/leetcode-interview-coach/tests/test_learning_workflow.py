"""Isolated workflow checks: authored records, providers and scoped commits."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from render_learning_note import render_markdown


def ps_literal(path):
    return "'" + str(path).replace("'", "''") + "'"


class LearningWorkflowTests(unittest.TestCase):
    def record(self):
        return {
            "problemTitle": "E070. 爬楼梯", "thinking": "先计算，再更新。",
            "statementMarkdown": "原题。", "solutionJava": "public int climbStairs(int n) { return n; }",
            "teachingTranscript": [{"role": "user", "contentMarkdown": "```java\n// 我的原注释\nint lastTwo = 1;\n```"}],
            "solutionVariants": [{"title": "原版本", "code": "// 保留注释\nint lastTwo = 1;", "language": "java", "isFinal": True}],
            "conversationDigest": {"firstReaction": "真实摘要"},
            "sourceMetadata": {"source": "原始对话"},
        }

    def test_builder_preserves_structured_source_and_legacy_body(self):
        for record in [self.record(), {"problemTitle": "70. 爬楼梯", "thinking": "旧思路", "noteContent": "# 70. 爬楼梯\n\n旧正文。", "solutionJava": "return 1;"}]:
            with self.subTest(structured="teachingTranscript" in record), tempfile.TemporaryDirectory(prefix="learning-builder-") as temporary:
                folder = Path(temporary)
                source, output = folder / "source.json", folder / "built.json"
                source.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
                subprocess.run([sys.executable, str(SCRIPTS / "build_siyuan_payload.py"), "--metadata-json", str(source), "--output", str(output)], check=True, capture_output=True)
                actual = json.loads(output.read_text(encoding="utf-8"))
                for key in ["teachingTranscript", "solutionVariants", "conversationDigest", "sourceMetadata", "noteContent"]:
                    if key in record:
                        self.assertEqual(actual[key], record[key])
                self.assertEqual(render_markdown(actual), render_markdown(record))

    @unittest.skipUnless(shutil.which("pwsh") or shutil.which("powershell"), "PowerShell is required")
    def test_workflow_uses_one_record_and_preserves_source_on_partial_publish(self):
        with tempfile.TemporaryDirectory(prefix="learning-workflow-") as temporary:
            folder = Path(temporary)
            scripts = folder / "scripts"
            shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
            (folder / ".git").mkdir()
            record = self.record()
            source = folder / "source.json"
            source.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            original = source.read_bytes()
            (folder / "metadata.json").write_text(json.dumps({"problemTitle":record["problemTitle"], "thinking":record["thinking"]}, ensure_ascii=False), encoding="utf-8")
            (folder / "config.json").write_text(json.dumps({"siyuan":{"enabled":True}, "yuque":{"enabled":True}}), encoding="utf-8")
            (folder / "Problem.java").write_text("class Problem {}", encoding="utf-8")
            (folder / "note.md").write_text("old note", encoding="utf-8")
            # Only external/mutating boundaries are stubbed; real orchestration,
            # rendering, metadata copying and result aggregation run unchanged.
            (scripts / "update_common_function_notes.py").write_text('import json,sys\nfrom pathlib import Path\np=Path(sys.argv[sys.argv.index("--output-json")+1]);p.write_text(json.dumps({"updatedPaths":[],"usages":[]}))\n', encoding="utf-8")
            (scripts / "finish_problem.ps1").write_text('param($JavaPath,$NotePath,$Paths,$CommitMetadataJson,[switch]$NoPush,[switch]$AllowUnrelatedChanges)\nCopy-Item -LiteralPath $NotePath -Destination "at-commit.md"\n', encoding="utf-8")
            provider = '''import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[sys.argv.index('--input') + 1]).read_text(encoding='utf-8-sig'))
dry = '--dry-run' in sys.argv
name = Path(__file__).stem
result = {'provider':name,'input':str(Path(sys.argv[sys.argv.index('--input')+1])),'record':data}
Path(name + ('-dry' if dry else '-write') + '.json').write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
if name.endswith('yuque') and not dry:
    print(json.dumps({'writeStatus':'written','directoryStatus':'verified','verificationStatus':'failed','success':False}))
    sys.exit(2)
print(json.dumps({'success':True}))
'''
            for name in ["sync_leetcode_to_siyuan.py", "sync_leetcode_to_yuque.py"]:
                (scripts / name).write_text(provider, encoding="utf-8")
            wrapper = folder / "run.ps1"
            wrapper.write_text("function python { & " + ps_literal(sys.executable) + " @args }\nfunction git { if ($args[0] -eq 'branch') { 'codex/test' } else { 'abc1234' } }\n$result = & " + ps_literal(scripts / "finish_leetcode_workflow.ps1") + " -JavaPath Problem.java -NotePath note.md -WorkflowMetadataJson metadata.json -SyncInputJson source.json -WorkflowConfigPath config.json -ReplaceWholeNote -AllowUnrelatedChanges -NoPush\n[System.IO.File]::WriteAllText((Join-Path $PWD 'result.json'), ($result -join \"`n\"), [System.Text.UTF8Encoding]::new($false))\n", encoding="utf-8-sig")
            result = subprocess.run([shutil.which("pwsh") or shutil.which("powershell"), "-NoProfile", "-File", str(wrapper)], cwd=folder, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual((folder / "note.md").read_text(encoding="utf-8"), render_markdown(record))
            self.assertEqual((folder / "at-commit.md").read_bytes(), (folder / "note.md").read_bytes())
            sy = json.loads((folder / "sync_leetcode_to_siyuan-write.json").read_text(encoding="utf-8"))
            yq = json.loads((folder / "sync_leetcode_to_yuque-write.json").read_text(encoding="utf-8"))
            self.assertEqual(sy, {**yq, "provider":"sync_leetcode_to_siyuan"})
            self.assertEqual(yq["record"]["teachingTranscript"], record["teachingTranscript"])
            final = json.loads((folder / "result.json").read_text(encoding="utf-8"))
            self.assertEqual(final["yuqueSync"]["writeStatus"], "written")
            self.assertEqual(final["yuqueSync"]["verificationStatus"], "failed")
            self.assertTrue(final["failures"])


if __name__ == "__main__":
    unittest.main()
