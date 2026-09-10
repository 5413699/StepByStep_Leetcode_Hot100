#!/usr/bin/env python3
"""Publish one learning record, with recoverable writes and explicit verification."""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from render_learning_note import build_sections, normalize_title, render_markdown
from yuque_client import DEFAULT_API_BASE, DEFAULT_CONFIG, YuQueClient, YuQueError, find_toc_document, resolve_parent_uuid, resolve_token


DEFAULT_BACKUP_DIR = Path.home() / ".codex" / "yuque-backups"


def load_json(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(result, dict):
        raise YuQueError(f"JSON 顶层必须是对象：{path}")
    return result


def as_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def slug_for_title(title: str) -> str:
    match = re.search(r"(?:leetcode\s*)?(?:[a-zA-Z]*\s*)?(\d{1,6})", title)
    if match:
        return f"leetcode-{int(match.group(1))}"
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not slug:
        raise YuQueError("题目标题没有可用于稳定 slug 的题号。")
    return f"leetcode-{slug}"


def render_publish_body(payload: dict[str, Any]) -> tuple[str, str]:
    """Structured records require real native folds. Legacy records stay readable."""
    if "teachingTranscript" in payload or "solutionVariants" in payload:
        from render_yuque_lake import render_lake

        return "lake", render_lake(payload)
    # Old records have no transcript/version contract. Flatten any generated
    # collapse section into ordinary Markdown, without claiming native folding.
    parts: list[str] = []
    for section in build_sections(payload):
        if section.get("heading"):
            parts.append(f"## {section['heading']}")
        if section["kind"] == "collapse":
            parts.append(f"## {section['title']}")
        parts.append(section["markdown"])
    body = "\n\n".join(parts).rstrip() + "\n"
    if re.search(r"<details(?:\s|>)", body, re.I):
        raise YuQueError("旧正文含折叠 HTML；请提供结构化教学记录后使用原生 Lake 发布。")
    return "markdown", body


def load_config(path: Path) -> dict[str, Any]:
    return load_json(path) if path.exists() else {"yuque": {}}


def _doc_body_for_backup(doc: dict[str, Any]) -> str:
    format_name = as_text(doc.get("format"))
    if not format_name:
        raise YuQueError("目标文档缺少 format，不能建立可靠备份。")
    if format_name == "lake":
        # Converted HTML cannot preserve every editor card; require raw Lake.
        if "body_lake" not in doc or not isinstance(doc["body_lake"], str):
            raise YuQueError("目标为 Lake 文档，但未读取到 body_lake；备份不完整，未写入。")
        return doc["body_lake"]
    if "body" not in doc or not isinstance(doc["body"], str):
        raise YuQueError("未读取到目标完整正文，不能先写入再补备份。")
    return doc["body"]


def save_backup(directory: Path, namespace: str, repo: str, doc: dict[str, Any], toc: list[dict[str, Any]]) -> Path:
    _doc_body_for_backup(doc)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = directory / f"{stamp}-doc-{int(doc['id'])}-{uuid.uuid4().hex[:8]}.json"
    backup = {"createdAt": datetime.now(timezone.utc).isoformat(), "namespace": namespace, "repoSlug": repo, "document": doc, "toc": toc}
    # Runtime recovery artifact, never a repository or configuration mutation.
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(backup, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return path


def _verification_errors(doc: dict[str, Any], *, expected_id: str, title: str, slug: str, format_name: str, body: str) -> list[str]:
    errors: list[str] = []
    for key, expected in [("id", expected_id), ("title", title), ("slug", slug)]:
        if str(doc.get(key) or "") != expected:
            errors.append(f"文档 {key} 与目标不一致。")
    # YuQue converts Markdown writes into Lake storage while retaining a
    # Markdown body view. Validate the view's content, not an assumed format.
    if doc.get("format") not in ({"lake", "markdown"} if format_name == "markdown" else {format_name}):
        errors.append("文档 format 与目标不一致。")
    if format_name == "lake":
        from render_yuque_lake import verify_lake

        errors.extend(verify_lake(body, doc))
    else:
        observed = doc.get("body")
        if not isinstance(observed, str) or observed.replace("\r\n", "\n").strip() != body.replace("\r\n", "\n").strip():
            errors.append("回读 Markdown 正文与发送内容不一致。")
    return errors


def _record_failure(result: dict[str, Any], stage: str, exc: Exception) -> None:
    result[f"{stage}Status"] = "uncertain" if getattr(exc, "uncertain", False) else "failed"
    result.setdefault("errors", []).append(str(exc))
    if getattr(exc, "retry_after", None) is not None:
        result["retryAfterSeconds"] = exc.retry_after
    result["success"] = False


def sync(input_path: Path, config_path: Path, *, dry_run: bool = False, target_doc_id: str | int | None = None, backup_dir: Path | None = None, require_existing: bool = False, client: YuQueClient | None = None) -> dict[str, Any]:
    payload = load_json(input_path)
    config = load_config(config_path)
    yuque = config.get("yuque") or {}
    if not yuque.get("enabled", True):
        return {"enabled": False, "skipped": True, "success": True}
    namespace = as_text(yuque.get("namespace"))
    if not namespace:
        raise YuQueError("语雀配置缺少 namespace，请先运行首次配置。")
    repo = as_text(yuque.get("repoSlug") or yuque.get("repository") or yuque.get("repo"))
    if "/" in namespace:
        namespace, embedded_repo = namespace.split("/", 1)
        repo = repo or embedded_repo
    if not repo:
        raise YuQueError("语雀配置缺少知识库标识 repoSlug。")
    title = normalize_title(payload)
    slug = slug_for_title(title)
    format_name, body = render_publish_body(payload)
    if not body.strip():
        raise YuQueError("正文为空，未执行语雀写入。")
    settings = payload.get("yuque") if isinstance(payload.get("yuque"), dict) else {}
    target_id = as_text(target_doc_id or settings.get("targetDocId") or payload.get("targetDocId") or yuque.get("targetDocId"))
    if target_id and not target_id.isdigit():
        raise YuQueError("targetDocId 必须是数字文档 ID。")
    if client is None:
        client = YuQueClient(as_text(yuque.get("apiBase")) or DEFAULT_API_BASE, resolve_token(as_text(yuque.get("tokenSource")) or "env:YuQue"))
    # Real TOC is required even for a root document; document parent fields
    # alone cannot prove placement or provide a reliable recovery snapshot.
    toc = client.get_toc(namespace, repo)
    parent_uuid = resolve_parent_uuid(toc, as_text(yuque.get("parentPath")), as_text(yuque.get("parentUuid")))
    existing: dict[str, Any] | None
    if target_id:
        existing = client.get_doc(namespace, repo, target_id)
        if str(existing.get("id") or "") != target_id or str(existing.get("slug") or "") != slug:
            raise YuQueError("targetDocId 对应文档的 ID/稳定 slug 不符；未覆盖可能的参考稿。")
    else:
        summary = client.find_doc(namespace, repo, slug)
        existing = client.get_doc(namespace, repo, summary.get("id") or slug) if summary else None
        if existing and str(existing.get("slug") or "") != slug:
            raise YuQueError("文档列表与正文接口的 slug 不一致，未写入。")
    if not existing and (target_id or require_existing or settings.get("requireExisting") or yuque.get("requireExisting")):
        raise YuQueError("指定为仅更新已有文档，但未找到稳定 slug；未新建文档。")
    if existing:
        _doc_body_for_backup(existing)
    result: dict[str, Any] = {
        "enabled": True, "namespace": namespace, "repoSlug": repo, "title": title,
        "slug": slug, "targetDocId": str(existing.get("id") or "") if existing else "",
        "parentPath": as_text(yuque.get("parentPath")), "parentUuid": parent_uuid,
        "action": "update" if existing else "create", "format": format_name, "bodyLength": len(body),
        "dryRun": dry_run, "writeStatus": "not_started", "directoryStatus": "not_started",
        "directoryWriteStatus": "not_needed",
        "verificationStatus": "not_started", "success": False,
    }
    observed_before = find_toc_document(toc, (existing or {}).get("id", ""), slug) if existing else None
    result["directoryBefore"] = as_text((observed_before or {}).get("parent_uuid")) if observed_before else None
    result["url"] = f"https://www.yuque.com/{namespace}/{repo}/{slug}"
    if dry_run:
        result.update({"bodyPreview": body[:1000], "writeStatus": "skipped_dry_run", "directoryStatus": "not_changed", "verificationStatus": "preflight_only", "success": True})
        if existing:
            result["backupPlanned"] = True
        return result
    if existing:
        result["backupPath"] = str(save_backup(backup_dir or DEFAULT_BACKUP_DIR, namespace, repo, existing, toc))
    outgoing: dict[str, Any] = {"title": title, "slug": slug, "format": format_name, "body": body}
    if parent_uuid:
        outgoing["parent_uuid"] = parent_uuid
    try:
        document = client.update_doc(namespace, repo, str(existing["id"]), outgoing) if existing else client.create_doc(namespace, repo, outgoing)
        result["writeStatus"] = "written"
        result["documentId"] = str(document.get("id") or (existing or {}).get("id") or "")
        if not result["documentId"]:
            raise YuQueError("写入响应未提供文档 ID；需按稳定 slug 回读确认，不能再次创建。", uncertain=True)
        if existing and result["documentId"] != str(existing["id"]):
            raise YuQueError("写入响应的文档 ID 与指定目标不一致。", uncertain=True)
    except Exception as exc:
        _record_failure(result, "write", exc)
        result["retryAdvice"] = "先按目标 ID 或稳定 slug 只读核验；不要因写入响应不确定而重复创建。"
        return result
    # Checks remain independent, and a failed read can never create another doc.
    try:
        current_toc = client.get_toc(namespace, repo)
        node = find_toc_document(current_toc, result["documentId"], slug)
        if node is None and parent_uuid:
            # Existing successful placement flow in e070-place.py establishes
            # this appendNode contract. Never guess a move for existing nodes.
            result["directoryWriteStatus"] = "started"
            client.update_toc(namespace, repo, {"action": "appendNode", "action_mode": "child", "type": "DOC", "doc_id": int(result["documentId"]), "target_uuid": parent_uuid})
            result["directoryWriteStatus"] = "associated"
            result["directoryStatus"] = "associated"
            current_toc = client.get_toc(namespace, repo)
            node = find_toc_document(current_toc, result["documentId"], slug)
        if node is None or as_text(node.get("parent_uuid")) != parent_uuid:
            raise YuQueError("正文已写入，但真实 TOC 未确认目标父目录；未移动其他目录项。")
        result["directoryStatus"] = "verified"
    except Exception as exc:
        _record_failure(result, "directory", exc)
        if result["directoryWriteStatus"] == "started":
            result["directoryWriteStatus"] = "uncertain" if getattr(exc, "uncertain", False) else "failed"
    try:
        current = client.get_doc(namespace, repo, result["documentId"])
        errors = _verification_errors(current, expected_id=result["documentId"], title=title, slug=slug, format_name=format_name, body=body)
        if errors:
            raise YuQueError("正文回读验证失败：" + "；".join(errors))
        result["verificationStatus"] = "verified"
        result["verifiedBodyLength"] = len(current.get("body_lake") or current.get("body") or "")
    except Exception as exc:
        _record_failure(result, "verification", exc)
    result["success"] = result["directoryStatus"] == "verified" and result["verificationStatus"] == "verified"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--config", default=DEFAULT_CONFIG, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--target-doc-id", help="Pin one numeric document ID; the stable slug must also match.")
    parser.add_argument("--require-existing", action="store_true", help="Fail instead of creating a missing stable slug.")
    parser.add_argument("--backup-dir", type=Path, default=DEFAULT_BACKUP_DIR)
    parser.add_argument("--output-json", type=Path, help="Persist the separate write/directory/verification statuses.")
    args = parser.parse_args()
    try:
        result = sync(args.input, args.config, dry_run=args.dry_run, target_doc_id=args.target_doc_id, require_existing=args.require_existing, backup_dir=args.backup_dir)
        if args.output_json:
            args.output_json.parent.mkdir(parents=True, exist_ok=True)
            args.output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("success") else 2
    except Exception as exc:
        print(f"YuQue sync failed before confirmed publication: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
