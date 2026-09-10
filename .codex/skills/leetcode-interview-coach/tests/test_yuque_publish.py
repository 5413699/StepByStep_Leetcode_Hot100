"""No-network tests for identity, recovery and partial-publication failures."""

from __future__ import annotations

import copy
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sync_leetcode_to_yuque import render_publish_body, slug_for_title, sync
from render_yuque_lake import inspect_lake
from yuque_client import YuQueClient, YuQueError, find_toc_document, flatten_toc, resolve_parent_uuid, retry_after_seconds


class Response:
    def __init__(self, data):
        self.raw = json.dumps(data).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.raw


def rate_limited(delay="2"):
    return urllib.error.HTTPError("https://www.yuque.com/api/v2/test", 429, "limited", {"Retry-After": delay}, io.BytesIO(b"rate limited"))


class FakeClient:
    def __init__(self, *, exists=True):
        self.doc = {"id": 70, "title": "旧题名", "slug": "leetcode-70", "format": "markdown", "body": "原笔记\n"} if exists else None
        self.toc = [{"uuid": "parent", "title": "待整理产出", "type": "TITLE", "parent_uuid": ""}]
        if exists:
            self.toc.append({"uuid": "node70", "type": "DOC", "doc_id": 70, "parent_uuid": "parent", "url": "leetcode-70"})
        self.calls = []
        self.writes = 0
        self.create_count = 0
        self.verification_error = None
        self.write_error = None
        self.on_write = None
        self.invalid_body = False

    def get_toc(self, namespace, repo):
        self.calls.append(("GET", "toc"))
        return copy.deepcopy(self.toc)

    def find_doc(self, namespace, repo, slug, **kwargs):
        self.calls.append(("GET", "list"))
        return copy.deepcopy(self.doc) if self.doc and self.doc["slug"] == slug else None

    def get_doc(self, namespace, repo, target, **kwargs):
        self.calls.append(("GET", "doc", str(target)))
        if self.writes and self.verification_error:
            raise self.verification_error
        if self.doc is None:
            raise YuQueError("not found", status_code=404)
        result = copy.deepcopy(self.doc)
        if self.writes and self.invalid_body:
            result["body"] = "different"
        return result

    def _write(self, body):
        if self.on_write:
            self.on_write()
        self.writes += 1
        if self.write_error:
            raise self.write_error
        self.doc = {"id": 70, **copy.deepcopy(body)}
        if body["format"] == "lake":
            self.doc["body_lake"] = body["body"]
        return copy.deepcopy(self.doc)

    def update_doc(self, namespace, repo, target, body):
        self.calls.append(("PUT", "doc", str(target)))
        return self._write(body)

    def create_doc(self, namespace, repo, body):
        self.calls.append(("POST", "doc"))
        self.create_count += 1
        return self._write(body)

    def update_toc(self, namespace, repo, body):
        self.calls.append(("PUT", "toc"))
        if body["action"] != "appendNode" or body["action_mode"] != "child":
            raise AssertionError("Unexpected TOC mutation")
        self.toc.append({"uuid": "new70", "type": "DOC", "doc_id": body["doc_id"], "parent_uuid": body["target_uuid"]})


class ClientTests(unittest.TestCase):
    def test_leading_zero_normalization(self):
        for title in ["E070. 爬楼梯", "70. 爬楼梯", "E70-爬楼梯"]:
            self.assertEqual(slug_for_title(title), "leetcode-70")

    def test_all_pages_by_slug_never_title(self):
        client = YuQueClient(token="test")
        pages = [[{"id": i, "slug": f"old-{i}", "title": "Same"} for i in range(100)], [{"id": 170, "slug": "leetcode-70", "title": "Other"}]]
        with patch.object(client, "list_docs", side_effect=pages) as listing:
            self.assertEqual(client.find_doc("u", "r", "leetcode-70", title="Same")["id"], 170)
            self.assertEqual(listing.call_args.kwargs["offset"], 100)
        with patch.object(client, "list_docs", return_value=[{"id": 2, "slug": "reference", "title": "Same"}]):
            self.assertIsNone(client.find_doc("u", "r", "leetcode-70", title="Same"))

    def test_repeated_pages_fail_not_missing(self):
        client = YuQueClient(token="test")
        with patch.object(client, "list_docs", return_value=[{"id": i} for i in range(100)]):
            with self.assertRaisesRegex(YuQueError, "分页重复"):
                client.find_doc("u", "r", "missing")

    def test_malformed_list_is_not_empty(self):
        client = YuQueClient(token="test")
        with patch.object(client, "request", return_value={"data": {"error": "bad"}}):
            with self.assertRaisesRegex(YuQueError, "返回格式无效"):
                client.list_docs("u", "r")

    def test_get_rate_limit_retries_twice(self):
        client = YuQueClient(token="test")
        with patch("yuque_client.urllib.request.urlopen", side_effect=[rate_limited("1"), rate_limited("2"), Response({"data": []})]) as opened, patch("yuque_client.time.sleep") as slept:
            self.assertEqual(client.request("GET", "/test"), {"data": []})
            self.assertEqual(opened.call_count, 3)
            self.assertEqual([call.args[0] for call in slept.call_args_list], [1, 2])

    def test_get_retry_budget_is_bounded(self):
        client = YuQueClient(token="test", read_retries=99)
        with patch("yuque_client.urllib.request.urlopen", side_effect=[rate_limited("0"), rate_limited("0"), rate_limited("0")]) as opened, patch("yuque_client.time.sleep"):
            with self.assertRaises(YuQueError):
                client.request("GET", "/test")
            self.assertEqual(opened.call_count, 3)

    def test_long_retry_after_reports_without_retrying_early(self):
        client = YuQueClient(token="test")
        with patch("yuque_client.urllib.request.urlopen", side_effect=rate_limited("120")) as opened, patch("yuque_client.time.sleep") as slept:
            with self.assertRaises(YuQueError) as caught:
                client.request("GET", "/test")
            self.assertEqual(caught.exception.retry_after, 120)
            self.assertEqual(opened.call_count, 1)
            slept.assert_not_called()

    def test_retry_after_http_date(self):
        self.assertEqual(retry_after_seconds("Wed, 09 Sep 2026 00:00:10 GMT", now=datetime(2026, 9, 9, tzinfo=timezone.utc)), 10)

    def test_no_write_retry(self):
        for method in ["POST", "PUT"]:
            client = YuQueClient(token="test")
            with patch("yuque_client.urllib.request.urlopen", side_effect=rate_limited("0")) as opened, patch("yuque_client.time.sleep") as slept:
                with self.assertRaises(YuQueError):
                    client.request(method, "/test", {"body": "hello"})
                self.assertEqual(opened.call_count, 1)
                slept.assert_not_called()

    def test_network_write_failure_is_uncertain(self):
        client = YuQueClient(token="test")
        with patch("yuque_client.urllib.request.urlopen", side_effect=TimeoutError("timeout")):
            with self.assertRaises(YuQueError) as caught:
                client.request("PUT", "/test", {})
            self.assertTrue(caught.exception.uncertain)

    def test_cross_host_token_not_sent(self):
        client = YuQueClient(token="test")
        with patch("yuque_client.urllib.request.urlopen") as opened:
            with self.assertRaises(YuQueError):
                client.request("GET", "https://example.com/test")
            opened.assert_not_called()

    def test_actual_toc_parent_and_identity(self):
        toc = [{"uuid": "p", "title": "待整理产出", "children": [{"uuid": "d", "doc_id": 70, "type": "DOC"}]}]
        self.assertEqual(find_toc_document(toc, 70)["parent_uuid"], "p")
        self.assertEqual(resolve_parent_uuid(toc, "待整理产出", "p"), "p")
        with self.assertRaises(YuQueError):
            resolve_parent_uuid(toc, "待整理产出", "other")
        depth_toc = [{"uuid": "p", "depth": 1}, {"uuid": "d", "depth": 2}, {"uuid": "r", "depth": 1}]
        self.assertEqual([item["parent_uuid"] for item in flatten_toc(depth_toc)], ["", "p", ""])

    def test_ymd_route_is_read_only_numeric(self):
        client = YuQueClient(token="test")
        with patch.object(client, "request", return_value={"data": {"data": {"id": 70, "body": "text"}}}) as request:
            self.assertEqual(client.get_ymd_doc(70)["body"], "text")
            request.assert_called_once_with("GET", "/yfm/docs?doc_id=70")
        with self.assertRaises(YuQueError):
            client.get_ymd_doc("leetcode-70")


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.input = self.base / "input.json"
        self.config = self.base / "config.json"
        self.backups = self.base / "backups"
        self.payload = {"problemTitle": "E070. 爬楼梯", "statementMarkdown": "共 n 阶。", "solutionJava": "int answer = 2; // 我的注释"}
        self.input.write_text(json.dumps(self.payload, ensure_ascii=False), encoding="utf-8")
        self.config.write_text(json.dumps({"yuque": {"enabled": True, "namespace": "u", "repoSlug": "r", "parentPath": "待整理产出", "parentUuid": "parent"}}, ensure_ascii=False), encoding="utf-8")

    def run_sync(self, client, **kwargs):
        return sync(self.input, self.config, client=client, backup_dir=self.backups, **kwargs)

    def test_dry_run_all_get_and_no_backup(self):
        client = FakeClient()
        result = self.run_sync(client, dry_run=True, target_doc_id=70)
        self.assertTrue(result["success"])
        self.assertEqual(result["writeStatus"], "skipped_dry_run")
        self.assertTrue(all(call[0] == "GET" for call in client.calls))
        self.assertFalse(self.backups.exists())

    def test_backup_is_complete_and_written_before_update(self):
        client = FakeClient()
        old_doc, old_toc = copy.deepcopy(client.doc), copy.deepcopy(client.toc)

        def inspect_backup():
            saved = list(self.backups.glob("*.json"))
            self.assertEqual(len(saved), 1)
            record = json.loads(saved[0].read_text(encoding="utf-8"))
            self.assertEqual(record["document"], old_doc)
            self.assertEqual(record["toc"], old_toc)

        client.on_write = inspect_backup
        result = self.run_sync(client, target_doc_id=70)
        self.assertTrue(result["success"], result)
        self.assertEqual((result["writeStatus"], result["directoryStatus"], result["verificationStatus"]), ("written", "verified", "verified"))
        self.assertEqual(client.create_count, 0)

    def test_repeated_publish_updates_same_id(self):
        client = FakeClient()
        for _ in range(2):
            self.assertTrue(self.run_sync(client)["success"])
        self.assertEqual(client.create_count, 0)
        self.assertEqual([call for call in client.calls if call[0] == "PUT"], [("PUT", "doc", "70"), ("PUT", "doc", "70")])

    def test_fixed_id_cannot_overwrite_reference(self):
        client = FakeClient()
        client.doc["slug"] = "reference"
        with self.assertRaisesRegex(YuQueError, "参考稿"):
            self.run_sync(client, target_doc_id=70)
        self.assertEqual(client.writes, 0)

    def test_require_existing_never_creates(self):
        client = FakeClient(exists=False)
        with self.assertRaises(YuQueError):
            self.run_sync(client, require_existing=True)
        self.assertEqual(client.writes, 0)

    def test_body_read_failure_keeps_written_state_and_never_creates(self):
        client = FakeClient()
        client.verification_error = YuQueError("rate limited", status_code=429, retry_after=120)
        result = self.run_sync(client)
        self.assertEqual(result["writeStatus"], "written")
        self.assertEqual(result["directoryStatus"], "verified")
        self.assertEqual(result["verificationStatus"], "failed")
        self.assertFalse(result["success"])
        self.assertEqual(client.create_count, 0)

    def test_incorrect_parent_is_not_proven_by_doc_field(self):
        client = FakeClient()
        client.toc[1]["parent_uuid"] = "somewhere-else"
        result = self.run_sync(client)
        self.assertEqual(client.doc["parent_uuid"], "parent")
        self.assertEqual(result["directoryStatus"], "failed")
        self.assertEqual(result["verificationStatus"], "verified")
        self.assertNotIn(("PUT", "toc"), client.calls)

    def test_new_doc_gets_one_explicit_toc_append(self):
        client = FakeClient(exists=False)
        result = self.run_sync(client)
        self.assertTrue(result["success"], result)
        self.assertEqual(client.create_count, 1)
        self.assertEqual(client.calls.count(("PUT", "toc")), 1)

    def test_incomplete_lake_backup_blocks_write(self):
        client = FakeClient()
        client.doc["format"] = "lake"
        with self.assertRaisesRegex(YuQueError, "body_lake"):
            self.run_sync(client)
        self.assertEqual(client.writes, 0)

    def test_uncertain_write_keeps_recovery_and_does_not_retry(self):
        client = FakeClient()
        client.write_error = YuQueError("timeout", uncertain=True)
        result = self.run_sync(client)
        self.assertEqual(result["writeStatus"], "uncertain")
        self.assertTrue(Path(result["backupPath"]).exists())
        self.assertEqual(client.writes, 1)
        self.assertEqual(result["verificationStatus"], "not_started")

    def test_mismatched_readback_fails(self):
        client = FakeClient()
        client.invalid_body = True
        result = self.run_sync(client)
        self.assertEqual(result["verificationStatus"], "failed")
        self.assertEqual(result["writeStatus"], "written")

    def test_legacy_markdown_readable_without_false_native_folds(self):
        format_name, body = render_publish_body(self.payload)
        self.assertEqual(format_name, "markdown")
        self.assertNotIn("<details", body)
        self.assertNotIn("# E70-爬楼梯", body)
        self.assertIn("// 我的注释", body)

    def test_structured_record_uses_verified_native_lake(self):
        payload = {**self.payload, "teachingTranscript": [{"role": "user", "contentMarkdown": "我写的代码。"}]}
        self.input.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        client = FakeClient()
        result = self.run_sync(client)
        self.assertTrue(result["success"], result)
        self.assertEqual(result["format"], "lake")
        actual = inspect_lake(client.doc["body_lake"])
        self.assertTrue(all(closed and native for _, closed, native in actual["collapses"]))
        self.assertIn("我写的代码。", actual["text"])

    def test_legacy_markdown_write_can_be_stored_as_lake(self):
        class ConvertingClient(FakeClient):
            def _write(self, body):
                result = super()._write(body)
                self.doc["format"] = result["format"] = "lake"
                self.doc["body_lake"] = "<!doctype lake><p>converted</p>"
                return result
        result = self.run_sync(ConvertingClient())
        self.assertTrue(result["success"], result)


if __name__ == "__main__":
    unittest.main()
