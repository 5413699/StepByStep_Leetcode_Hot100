#!/usr/bin/env python3
"""Small UTF-8 Yuque Open API v2 client used by the interview workflow."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any


DEFAULT_API_BASE = "https://www.yuque.com/api/v2"
DEFAULT_CONFIG = Path.home() / ".codex" / "leetcode-hot100-workflow.local.json"


class YuQueError(RuntimeError):
    """An actionable Yuque API or configuration error."""

    def __init__(self, message: str, *, status_code: int | None = None, retry_after: float | None = None, uncertain: bool = False) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after
        self.uncertain = uncertain


def retry_after_seconds(value: str | None, *, now: datetime | None = None) -> float | None:
    """Parse both Retry-After forms. Never retry sooner than the server asks."""
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            when = parsedate_to_datetime(value)
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            return max(0.0, (when - (now or datetime.now(timezone.utc))).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None


def resolve_token(token_source: str = "env:YuQue") -> str:
    """Resolve a PAT from the process environment, then the Windows user environment."""
    source = token_source or "env:YuQue"
    if source.startswith("token:"):
        token = source.split(":", 1)[1]
    elif source.startswith("env:"):
        name = source.split(":", 1)[1]
        token = os.environ.get(name, "")
        if not token and os.name == "nt":
            try:
                import winreg

                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                    token = str(winreg.QueryValueEx(key, name)[0] or "")
            except (FileNotFoundError, OSError):
                token = ""
    else:
        raise YuQueError(f"不支持的 tokenSource：{source}")
    if not token:
        name = source.split(":", 1)[1] if source.startswith("env:") else "YuQue"
        raise YuQueError(f"缺少语雀 PAT（{name}）。请设置用户环境变量 YuQue。")
    return token.strip()


def _data(result: Any) -> Any:
    if isinstance(result, dict) and "data" in result:
        return result["data"]
    return result


class YuQueClient:
    def __init__(self, api_base: str = DEFAULT_API_BASE, token: str | None = None, *, timeout: int = 20, read_retries: int = 2) -> None:
        self.api_base = (api_base or DEFAULT_API_BASE).rstrip("/")
        self.token = token or resolve_token()
        self.timeout = timeout
        self.read_retries = min(2, max(0, read_retries))

    def request(self, method: str, endpoint: str, payload: dict[str, Any] | None = None) -> Any:
        method = method.upper()
        url = endpoint if endpoint.startswith("http") else self.api_base + "/" + endpoint.lstrip("/")
        if urllib.parse.urlsplit(url).netloc != urllib.parse.urlsplit(self.api_base).netloc:
            raise YuQueError("拒绝向其他主机发送语雀 PAT。")
        body = None if payload is None or method == "GET" else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={"X-Auth-Token": self.token, "Content-Type": "application/json", "Accept": "application/json"},
            method=method,
        )
        for attempt in range(self.read_retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    raw = response.read().decode("utf-8")
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:500].replace(self.token, "[redacted]")
                retry_after = retry_after_seconds(exc.headers.get("Retry-After") if exc.headers else None)
                delay = retry_after if retry_after is not None else float(2 ** attempt)
                # Writes, including ambiguous failures, are deliberately never retried.
                # A longer server delay is reported instead of sleeping or retrying early.
                if method == "GET" and exc.code == 429 and attempt < self.read_retries and delay <= 30:
                    time.sleep(delay)
                    continue
                raise YuQueError(
                    f"YuQue API {method} {endpoint} failed: HTTP {exc.code} {detail}",
                    status_code=exc.code, retry_after=retry_after, uncertain=method != "GET" and exc.code >= 500,
                ) from exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                raise YuQueError(f"无法连接语雀 API：{url}：{exc}", uncertain=method != "GET") from exc
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise YuQueError(f"语雀 API 返回非 JSON 内容：{endpoint}", uncertain=method != "GET") from exc
        raise YuQueError("语雀读取重试次数已用完。")

    def get_user(self) -> dict[str, Any]:
        result = _data(self.request("GET", "/user"))
        if not isinstance(result, dict):
            raise YuQueError("语雀用户接口返回格式无效。")
        return result

    def list_repos(self, login: str = "", *, offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """List repositories; pass the user login for Yuque's documented user scope."""
        scope = f"/users/{urllib.parse.quote(login, safe='')}/repos" if login else "/repos"
        result = _data(self.request("GET", f"{scope}?offset={offset}&limit={limit}"))
        if not isinstance(result, list) or any(not isinstance(item, dict) for item in result):
            raise YuQueError("语雀知识库列表返回格式无效。")
        return result

    def list_docs(self, namespace: str, repo: str, *, offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        path = f"/repos/{urllib.parse.quote(namespace, safe='')}/{urllib.parse.quote(repo, safe='')}/docs?offset={offset}&limit={limit}"
        result = _data(self.request("GET", path))
        if not isinstance(result, list) or any(not isinstance(item, dict) for item in result):
            raise YuQueError("语雀文档列表返回格式无效；未将失败当成空列表。")
        return result

    def get_toc(self, namespace: str, repo: str) -> list[dict[str, Any]]:
        path = f"/repos/{urllib.parse.quote(namespace, safe='')}/{urllib.parse.quote(repo, safe='')}/toc"
        result = _data(self.request("GET", path))
        if not isinstance(result, list) or any(not isinstance(item, dict) for item in result):
            raise YuQueError("语雀目录返回格式无效。")
        return result

    def get_doc(self, namespace: str, repo: str, doc_id_or_slug: str | int, *, include_lake: bool = True) -> dict[str, Any]:
        """Read the actual document, not its list summary, including recovery bodies."""
        path = f"/repos/{urllib.parse.quote(namespace, safe='')}/{urllib.parse.quote(repo, safe='')}/docs/{urllib.parse.quote(str(doc_id_or_slug), safe='')}"
        if include_lake:
            path += "?include_lake=1"
        result = _data(self.request("GET", path))
        if not isinstance(result, dict) or not result:
            raise YuQueError("语雀读取文档返回格式无效。")
        return result

    def get_ymd_doc(self, doc_id: str | int) -> dict[str, Any]:
        """Read the official YMD view by numeric ID (not a Lake backup).

        Source: yuque/yuque-mcp-server src/services/yuque-client.ts. The
        Markdown endpoint has independent format semantics; callers must not
        silently substitute this for raw Lake recovery or native-block checks.
        """
        if not str(doc_id).isdigit():
            raise YuQueError("YMD 读取要求数字 doc ID。")
        result = _data(self.request("GET", f"/yfm/docs?doc_id={doc_id}"))
        if isinstance(result, dict) and "data" in result and "body" not in result:
            result = _data(result)
        if not isinstance(result, dict) or not result:
            raise YuQueError("语雀 YMD 文档返回格式无效。")
        return result

    def update_toc(self, namespace: str, repo: str, payload: dict[str, Any]) -> Any:
        path = f"/repos/{urllib.parse.quote(namespace, safe='')}/{urllib.parse.quote(repo, safe='')}/toc"
        return _data(self.request("PUT", path, payload))

    def create_doc(self, namespace: str, repo: str, payload: dict[str, Any]) -> dict[str, Any]:
        path = f"/repos/{urllib.parse.quote(namespace, safe='')}/{urllib.parse.quote(repo, safe='')}/docs"
        result = _data(self.request("POST", path, payload))
        if not isinstance(result, dict):
            raise YuQueError("语雀创建文档返回格式无效。")
        return result

    def update_doc(self, namespace: str, repo: str, slug: str, payload: dict[str, Any]) -> dict[str, Any]:
        path = f"/repos/{urllib.parse.quote(namespace, safe='')}/{urllib.parse.quote(repo, safe='')}/docs/{urllib.parse.quote(slug, safe='')}"
        result = _data(self.request("PUT", path, payload))
        if not isinstance(result, dict):
            raise YuQueError("语雀更新文档返回格式无效。")
        return result

    def find_doc(self, namespace: str, repo: str, slug: str, *, title: str = "") -> dict[str, Any] | None:
        """Search every page by stable slug only. A reference's title is not identity.

        ``title`` remains accepted for older callers, but is never used to select
        a document. Pagination errors must fail rather than imply 'create'.
        """
        seen_pages: set[tuple[str, ...]] = set()
        for offset in range(0, 100000, 100):
            docs = self.list_docs(namespace, repo, offset=offset, limit=100)
            fingerprint = tuple(str(doc.get("id") or doc.get("slug") or "") for doc in docs)
            if docs and fingerprint in seen_pages:
                raise YuQueError("语雀文档分页重复，无法可靠判断目标是否存在。")
            seen_pages.add(fingerprint)
            matches = [doc for doc in docs if str(doc.get("slug") or "") == slug]
            if len(matches) > 1:
                raise YuQueError(f"语雀返回重复 slug，无法唯一定位：{slug}")
            if matches:
                return matches[0]
            if len(docs) < 100:
                return None
        raise YuQueError("语雀文档分页超出上限，未执行写入。")


def flatten_toc(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten nested or flat Yuque TOC responses while retaining parent UUIDs."""
    result: list[dict[str, Any]] = []

    def visit(items: list[dict[str, Any]], parent_uuid: str = "") -> None:
        depth_stack: list[tuple[int, str]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            current = dict(item)
            if "parent_uuid" not in current:
                if "parentUuid" in current:
                    current["parent_uuid"] = current["parentUuid"]
                elif "depth" in current:
                    depth = int(current["depth"])
                    while depth_stack and depth_stack[-1][0] >= depth:
                        depth_stack.pop()
                    current["parent_uuid"] = depth_stack[-1][1] if depth_stack else parent_uuid
                else:
                    current["parent_uuid"] = parent_uuid
            result.append(current)
            if "depth" in current:
                depth_stack.append((int(current["depth"]), str(item.get("uuid") or item.get("id") or "")))
            children = item.get("children") or item.get("nodes") or []
            if isinstance(children, list):
                visit(children, str(item.get("uuid") or item.get("id") or ""))

    visit(nodes)
    return result


def resolve_parent_uuid(toc: list[dict[str, Any]], parent_path: str, configured_uuid: str = "") -> str:
    path = [part.strip() for part in (parent_path or "").replace("\\", "/").split("/") if part.strip()]
    flat = flatten_toc(toc)
    if configured_uuid and len([node for node in flat if str(node.get("uuid") or "") == configured_uuid]) != 1:
        raise YuQueError("配置的语雀 parentUuid 不在当前知识库目录中或不唯一。")
    if not path:
        return configured_uuid
    parent = ""
    for name in path:
        matches = [item for item in flat if str(item.get("title") or item.get("name") or "") == name and str(item.get("parent_uuid") or "") == parent]
        if len(matches) != 1:
            raise YuQueError(f"无法在语雀知识库目录中唯一定位父目录：{parent_path}")
        parent = str(matches[0].get("uuid") or matches[0].get("id") or "")
        if not parent:
            raise YuQueError(f"语雀目录缺少 uuid：{name}")
    if configured_uuid and configured_uuid != parent:
        raise YuQueError("语雀 parentPath 与 parentUuid 指向不同目录。")
    return parent


def find_toc_document(toc: list[dict[str, Any]], doc_id: str | int, slug: str = "") -> dict[str, Any] | None:
    """Resolve a document node by doc ID, falling back only to an exact slug."""
    flat = flatten_toc(toc)
    wanted = str(doc_id or "")
    matches = [node for node in flat if wanted and str(node.get("doc_id") or "") == wanted]
    if not matches and slug:
        matches = [node for node in flat if str(node.get("type") or "").upper() == "DOC" and str(node.get("slug") or node.get("url") or "").rstrip("/").rsplit("/", 1)[-1] == slug]
    if len(matches) > 1:
        raise YuQueError("同一语雀文档存在多个目录项，无法安全确认目录位置。")
    return matches[0] if matches else None
