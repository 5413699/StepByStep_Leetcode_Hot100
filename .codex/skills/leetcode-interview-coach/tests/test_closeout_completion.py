"""Completion needs evidence for every configured destination, not just Git."""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from check_closeout import add_browser_evidence, add_verification_evidence, evaluate, payload_digest, validate_learning_record


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="closeout-status-")
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.payload = self.folder / "record.json"
        self.payload.write_text('{"solutionJava":"return 1;"}', encoding="utf-8")
        self.observation = self.folder / "browser.txt"
        self.observation.write_text("Native section expanded and collapsed; code title and highlighting observed.", encoding="utf-8")

    def report(self):
        passed = {"status":"passed", "evidence":{"observed":True}}
        return {
            "workflowId":"test-run", "payloadPath":str(self.payload), "payloadSha256":payload_digest(self.payload),
            "stages":{name:copy.deepcopy(passed) for name in ("configuration","record","local","commit","push")},
            "providers":{
                "siyuan":{"enabled":False,"stages":{}},
                "yuque":{"enabled":True,"url":"https://www.yuque.com/test/book/leetcode-279","stages":{
                    **{name:copy.deepcopy(passed) for name in ("dryRun","write","directory","readback")},
                    "browser":{"status":"pending","evidence":None},
                }},
            },
            "failures":[],
        }

    def browser_evidence(self, report):
        return {
            "provider":"yuque", "workflowId":report["workflowId"], "payloadSha256":report["payloadSha256"],
            "url":report["providers"]["yuque"]["url"], "checkedAt":"2026-09-18T15:00:00+08:00",
            "checks":{name:True for name in ("nativeCollapse","codeBlockNames","codeHighlight","quotesLinksBold","finalAnswerVisible")},
            "observation":"Expanded and collapsed both native sections; inspected the final named Java block.",
            "evidencePaths":[str(self.observation)],
        }

    def test_written_and_api_verified_still_require_browser_evidence(self):
        report = self.report()
        self.assertFalse(evaluate(report)["complete"])
        self.assertEqual(report["incomplete"], ["yuque.browser: pending"])
        add_browser_evidence(report, self.browser_evidence(report))
        self.assertTrue(evaluate(report)["complete"])

    def test_each_required_stage_cannot_be_omitted_or_skipped(self):
        for provider, stage in [(None,name) for name in ("configuration","record","local","commit","push")] + [("yuque",name) for name in ("dryRun","write","directory","readback","browser")]:
            for state in ("pending","failed","uncertain","skipped"):
                with self.subTest(provider=provider, stage=stage, state=state):
                    report = self.report()
                    add_browser_evidence(report, self.browser_evidence(report))
                    target = report["stages"] if provider is None else report["providers"][provider]["stages"]
                    target[stage]["status"] = state
                    self.assertFalse(evaluate(report)["complete"])

    def test_enabled_second_provider_cannot_disappear_after_other_succeeds(self):
        report = self.report()
        add_browser_evidence(report, self.browser_evidence(report))
        report["providers"]["siyuan"]["enabled"] = True
        self.assertFalse(evaluate(report)["complete"])
        self.assertIn("siyuan.readback: missing", report["incomplete"])
        del report["providers"]["siyuan"]
        self.assertFalse(evaluate(report)["complete"])
        self.assertIn("siyuan: explicit enabled/disabled decision is missing", report["incomplete"])

    def test_evidence_must_match_target_and_payload_and_have_observation_artifact(self):
        for key, value in (("url","https://wrong.example"),("workflowId","another-run"),("payloadSha256","wrong"),("evidencePaths",[]),("checks",{})):
            with self.subTest(key=key):
                report = self.report()
                evidence = self.browser_evidence(report)
                evidence[key] = value
                with self.assertRaises(ValueError):
                    add_browser_evidence(report, evidence)
        report = self.report()
        add_browser_evidence(report, self.browser_evidence(report))
        self.payload.write_text("changed after publication", encoding="utf-8")
        self.assertFalse(evaluate(report)["complete"])

    def test_missing_history_is_explicit_without_rejecting_legacy_rendering(self):
        record = {"solutionJava":"return 1;"}
        self.assertTrue(validate_learning_record(record))
        record["sourceMetadata"] = {"missingTeachingHistory":"Earlier teacher turns are unavailable."}
        self.assertTrue(validate_learning_record(record))
        record["processMarkdown"] = "Earlier teacher turns are unavailable."
        self.assertFalse(validate_learning_record(record))
        record["teachingTranscript"] = [{"role":"user","contentMarkdown":"Surviving implementation.","correctionMarkdown":"Earlier teacher turns are unavailable."}]
        self.assertFalse(validate_learning_record(record))

    def test_checker_cli_can_finish_without_invoking_publishing(self):
        report = self.report()
        path, evidence = self.folder / "report.json", self.folder / "evidence.json"
        path.write_text(json.dumps(report), encoding="utf-8")
        evidence.write_text(json.dumps(self.browser_evidence(report)), encoding="utf-8")
        incomplete = subprocess.run([sys.executable,str(SCRIPTS / "check_closeout.py"),"--report",str(path)], capture_output=True)
        self.assertEqual(incomplete.returncode, 2)
        complete = subprocess.run([sys.executable,str(SCRIPTS / "check_closeout.py"),"--report",str(path),"--browser-evidence",str(evidence)], capture_output=True)
        self.assertEqual(complete.returncode, 0, complete.stdout)
        self.assertTrue(json.loads(path.read_text(encoding="utf-8"))["complete"])

    def test_readonly_recovery_preserves_history_without_permanent_failure(self):
        report = self.report()
        report["providers"]["yuque"]["stages"]["readback"] = {"status":"failed","evidence":"rate limited"}
        report["failures"] = ["YuQue: readback failed after a confirmed write."]
        add_browser_evidence(report, self.browser_evidence(report))
        self.assertFalse(evaluate(report)["complete"])
        evidence = {**self.browser_evidence(report), "readOnly":True, "verifiedStages":["readback"]}
        add_verification_evidence(report, evidence)
        self.assertTrue(evaluate(report)["complete"])
        self.assertTrue(report["failures"])
        self.assertEqual(report["providers"]["yuque"]["recoveryHistory"][0]["previous"]["status"], "failed")

    def test_java_alignment_ignores_wrapper_and_comments_but_rejects_old_solution(self):
        java = self.folder / "Problem.java"
        java.write_text('package test;\nclass Problem {\n// region LeetCode solution\n// original comment\npublic int f(int n) { return n + 1; }\n// endregion\n}', encoding="utf-8")
        record = {"solutionJava":"class Solution { public int f(int n) { /* note */ return n+1; } }", "teachingTranscript":[{"role":"user","contentMarkdown":"My code."}]}
        self.assertFalse(validate_learning_record(record, java))
        record["solutionVariants"] = [{"isFinal":True,"language":"java","code":"class Solution { public int f(int n) { return -1; } }"}]
        self.assertIn("The rendered final Java variant differs from solutionJava", validate_learning_record(record, java))
        del record["solutionVariants"]
        record["solutionJava"] = "class Solution { public int f(int n) { return -1; } }"
        self.assertTrue(validate_learning_record(record, java))

    @unittest.skipUnless(shutil.which("pwsh") or shutil.which("powershell"), "PowerShell is required")
    def test_missing_config_persists_incomplete_before_any_repository_mutation(self):
        (self.folder / ".git").mkdir()
        path = self.folder / "report.json"
        wrapper = self.folder / "run.ps1"
        quote = lambda text: "'" + str(text).replace("'", "''") + "'"
        wrapper.write_text("$ErrorActionPreference='Stop'\nfunction python { & " + quote(sys.executable) + " @args }\n& " + quote(SCRIPTS / "finish_leetcode_workflow.ps1") + " -JavaPath missing.java -NotePath missing.md -WorkflowConfigPath missing-config.json -StatusJson " + quote(path) + "\n", encoding="utf-8-sig")
        completed = subprocess.run([shutil.which("pwsh") or shutil.which("powershell"),"-NoProfile","-File",str(wrapper)], cwd=self.folder, capture_output=True, timeout=30)
        self.assertNotEqual(completed.returncode, 0)
        report = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(report["complete"])
        self.assertEqual(report["stages"]["configuration"]["status"], "failed")
        self.assertFalse((self.folder / "missing.md").exists())

    @unittest.skipUnless(shutil.which("pwsh") or shutil.which("powershell"), "PowerShell is required")
    def test_workflow_records_remote_verification_skip_and_failure(self):
        for scenario in ("verified", "push-failed", "remote-mismatch", "skip-yuque", "compile-failed"):
            with self.subTest(scenario=scenario):
                folder = self.folder / scenario
                folder.mkdir()
                (folder / ".git").mkdir()
                scripts = folder / "scripts"
                shutil.copytree(SCRIPTS, scripts, ignore=shutil.ignore_patterns("__pycache__"))
                record = {"problemTitle":"279. Perfect Squares", "thinking":"Use previous optimal states.", "solutionJava":"public int numSquares(int n) { return n; }", "teachingTranscript":[{"role":"user","contentMarkdown":"My implementation."}]}
                (folder / "source.json").write_text(json.dumps(record), encoding="utf-8")
                (folder / "config.json").write_text(json.dumps({"siyuan":{"enabled":False},"yuque":{"enabled":True}}), encoding="utf-8")
                (folder / "Problem.java").write_text("class Problem {\n// region LeetCode solution\n" + record["solutionJava"] + "\n// endregion\n}", encoding="utf-8")
                (folder / "note.md").write_text("original", encoding="utf-8")
                (scripts / "update_common_function_notes.py").write_text('import json,sys\nfrom pathlib import Path\nPath(sys.argv[sys.argv.index("--output-json")+1]).write_text(json.dumps({"updatedPaths":[]}))\n', encoding="utf-8")
                finish = 'param($JavaPath,$NotePath,$Paths,$CommitMetadataJson,[switch]$NoPush,[switch]$AllowUnrelatedChanges)\n'
                finish += 'throw "Maven compile failed; no files staged or committed."\n' if scenario == "compile-failed" else 'if (-not $NoPush) { throw "Workflow must separate push evidence" }\n'
                (scripts / "finish_problem.ps1").write_text(finish, encoding="utf-8")
                (scripts / "sync_leetcode_to_yuque.py").write_text('''import json,sys
from pathlib import Path
dry = '--dry-run' in sys.argv
Path('provider-' + ('dry' if dry else 'write')).touch()
print(json.dumps({'enabled':True,'dryRun':dry,'success':True,'writeStatus':'written','directoryStatus':'verified','verificationStatus':'verified','url':'https://www.yuque.com/test/book/leetcode-279'}))
''', encoding="utf-8")
                quote = lambda text: "'" + str(text).replace("'", "''") + "'"
                git_stub = '''function git {
    $global:LASTEXITCODE = 0
    switch ($args[0]) {
        'branch' { 'codex/test' }
        'rev-parse' { 'abc1234' }
        'config' { if ($args[1].EndsWith('.remote')) { 'origin' } else { 'refs/heads/codex/test' } }
        'push' { PUSH_RESULT }
        'ls-remote' { 'REMOTE_HASH refs/heads/codex/test' }
    }
}
'''.replace("PUSH_RESULT", "$global:LASTEXITCODE = 1" if scenario == "push-failed" else "$global:LASTEXITCODE = 0").replace("REMOTE_HASH", "different" if scenario == "remote-mismatch" else "abc1234")
                wrapper = folder / "run.ps1"
                wrapper.write_text("$ErrorActionPreference='Stop'\nfunction python { & " + quote(sys.executable) + " @args }\n" + git_stub + "& " + quote(scripts / "finish_leetcode_workflow.ps1") + " -JavaPath Problem.java -NotePath note.md -WorkflowMetadataJson source.json -SyncInputJson source.json -WorkflowConfigPath config.json -StatusJson report.json -ReplaceWholeNote" + (" -SkipYuque" if scenario == "skip-yuque" else "") + "\n", encoding="utf-8-sig")
                # Avoid replacing a solution region: source metadata supplies the
                # two commit fields, while the authored payload supplies code.
                metadata = {key:record[key] for key in ("problemTitle","thinking")}
                (folder / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
                wrapper.write_text(wrapper.read_text(encoding="utf-8-sig").replace("-WorkflowMetadataJson source.json", "-WorkflowMetadataJson metadata.json"), encoding="utf-8-sig")
                result = subprocess.run([shutil.which("pwsh") or shutil.which("powershell"),"-NoProfile","-File",str(wrapper)], cwd=folder, capture_output=True, timeout=30)
                self.assertNotEqual(result.returncode, 0)
                report = json.loads((folder / "report.json").read_text(encoding="utf-8"))
                self.assertFalse(report["complete"])
                if scenario == "verified":
                    self.assertEqual(report["incomplete"], ["yuque.browser: pending"])
                    self.assertEqual(report["stages"]["push"]["evidence"]["commit"], "abc1234")
                    self.assertTrue((folder / "provider-write").exists())
                else:
                    self.assertFalse((folder / "provider-write").exists())
                    expected_stage = "local" if scenario == "compile-failed" else "push"
                    if scenario == "skip-yuque":
                        self.assertEqual(report["providers"]["yuque"]["stages"]["write"]["status"], "skipped")
                    else:
                        self.assertEqual(report["stages"][expected_stage]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
