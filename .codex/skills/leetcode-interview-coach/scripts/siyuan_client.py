#!/usr/bin/env python3
"""Shared UTF-8 SiYuan HTTP client for LeetCode workflow scripts."""

from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path.home() / ".codex" / "leetcode-hot100-workflow.local.json"
DEFAULT_URL = "http://127.0.0.1:6806"
DEFAULT_WORKSPACE = r"F:\就业资料-陈智飞\SiYuan_czf"
DEFAULT_SYSTEM_ROOT = "/算法题/面试手撕训练系统"


class SiyuanError(RuntimeError):
    pass


class SiyuanClient:
    def __init__(self, base_url: str, token: str, push_notification: bool = True) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.push_notification = push_notification

    def call(self, endpoint: str, payload: dict[str, Any] | None = None, *, strict: bool = True) -> dict[str, Any]:
        request = urllib.request.Request(
            self.base_url + endpoint,
            data=json.dumps(payload or {}, ensure_ascii=False).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {self.token}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise SiyuanError(f"无法连接思源 API：{self.base_url}{endpoint}：{exc}") from exc
        except json.JSONDecodeError as exc:
            raise SiyuanError(f"思源 API 返回非 JSON 内容：{endpoint}") from exc

        if strict and result.get("code") != 0:
            raise SiyuanError(f"{endpoint} failed: code={result.get('code')} msg={result.get('msg')}")
        return result

    def data(self, endpoint: str, payload: dict[str, Any] | None = None) -> Any:
        return self.call(endpoint, payload).get("data")

    def push_message(self, message: str, *, error: bool = False) -> None:
        if not self.push_notification:
            return
        endpoint = "/api/notification/pushErrMsg" if error else "/api/notification/pushMsg"
        try:
            self.call(endpoint, {"msg": message, "timeout": 7000}, strict=False)
        except SiyuanError:
            pass


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def default_config() -> dict[str, Any]:
    return {
        "siyuan": {
            "enabled": True,
            "url": DEFAULT_URL,
            "urlAutoDetect": True,
            "lastWorkingUrl": "",
            "workspacePath": DEFAULT_WORKSPACE,
            "tokenSource": "env:SIYUAN_TOKEN",
            "notebookId": "",
            "autoCreateConceptPage": True,
            "autoUpdateConceptIndex": True,
            "pushNotification": True,
        },
        "wikiPolicy": {
            "systemRootHPath": DEFAULT_SYSTEM_ROOT,
            "auditLogEnabled": True,
        },
    }


def merge_defaults(config: dict[str, Any]) -> dict[str, Any]:
    merged = default_config()
    for section, values in config.items():
        if isinstance(values, dict) and isinstance(merged.get(section), dict):
            merged[section].update(values)
        else:
            merged[section] = values
    return merged


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    if path.exists():
        return merge_defaults(load_json(path))
    return default_config()


def resolve_token(token_source: str) -> str:
    if token_source.startswith("env:"):
        env_name = token_source.split(":", 1)[1]
        token = os.environ.get(env_name, "")
        if not token:
            raise SiyuanError(f"缺少环境变量 {env_name}。请在思源 设置 > 关于 > API Token 获取 token 后设置。")
        return token
    if token_source.startswith("token:"):
        return token_source.split(":", 1)[1]
    raise SiyuanError(f"不支持的 tokenSource：{token_source}")


def normalize_hpath(*parts: str) -> str:
    chunks: list[str] = []
    for part in parts:
        for chunk in str(part).replace("\\", "/").split("/"):
            stripped = chunk.strip()
            if stripped:
                chunks.append(stripped)
    return "/" + "/".join(chunks)


def block_ref(block_id: str, text: str) -> str:
    escaped = text.replace('"', '\\"')
    return f'(({block_id} "{escaped}"))'


def test_url(base_url: str, token: str) -> bool:
    try:
        client = SiyuanClient(base_url, token, push_notification=False)
        result = client.call("/api/system/version", {}, strict=False)
        return result.get("code") == 0
    except SiyuanError:
        return False


def siyuan_kernel_pids() -> set[str]:
    try:
        output = subprocess.check_output(
            ["tasklist", "/FI", "IMAGENAME eq SiYuan-Kernel.exe", "/FO", "CSV", "/NH"],
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except (OSError, subprocess.CalledProcessError):
        return set()

    pids: set[str] = set()
    for line in output.splitlines():
        parts = [part.strip().strip('"') for part in line.split('","')]
        if len(parts) >= 2 and parts[0].lower() == "siyuan-kernel.exe":
            pids.add(parts[1])
    return pids


def listening_ports_for_pids(pids: set[str]) -> list[int]:
    if not pids:
        return []
    try:
        output = subprocess.check_output(
            ["netstat", "-ano", "-p", "tcp"],
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except (OSError, subprocess.CalledProcessError):
        return []

    ports: set[int] = set()
    for line in output.splitlines():
        if "LISTENING" not in line:
            continue
        parts = line.split()
        if len(parts) < 5 or parts[-1] not in pids:
            continue
        local = parts[1]
        match = re.search(r":(\d+)$", local)
        if match:
            ports.add(int(match.group(1)))
    return sorted(ports)


def candidate_urls(config: dict[str, Any]) -> list[str]:
    siyuan = config.get("siyuan") or {}
    urls: list[str] = []
    for value in [siyuan.get("lastWorkingUrl"), siyuan.get("url"), DEFAULT_URL]:
        if value and value not in urls:
            urls.append(str(value))
    for port in listening_ports_for_pids(siyuan_kernel_pids()):
        url = f"http://127.0.0.1:{port}"
        if url not in urls:
            urls.append(url)
    return urls


def open_client_from_config(
    config: dict[str, Any],
    *,
    config_path: Path | None = None,
    update_config: bool = False,
) -> tuple[SiyuanClient, dict[str, Any]]:
    config = merge_defaults(config)
    siyuan = config["siyuan"]
    token = resolve_token(siyuan.get("tokenSource", "env:SIYUAN_TOKEN"))
    candidates = candidate_urls(config) if siyuan.get("urlAutoDetect", True) else [siyuan.get("url", DEFAULT_URL)]

    diagnostics = {
        "candidateUrls": candidates,
        "kernelPids": sorted(siyuan_kernel_pids()),
        "tokenSource": siyuan.get("tokenSource", "env:SIYUAN_TOKEN"),
        "tokenAvailable": bool(token),
    }
    for url in candidates:
        if test_url(url, token):
            siyuan["lastWorkingUrl"] = url
            siyuan["url"] = url
            resolved = dict(siyuan)
            resolved["diagnostics"] = diagnostics
            if update_config and config_path:
                write_json(config_path, config)
            return SiyuanClient(url, token, bool(siyuan.get("pushNotification", True))), resolved

    raise SiyuanError(f"无法定位可用思源 API。诊断信息：{json.dumps(diagnostics, ensure_ascii=False)}")


def ensure_doc(client: SiyuanClient, notebook: str, hpath: str, initial_markdown: str = "") -> tuple[str, bool]:
    ids = client.data("/api/filetree/getIDsByHPath", {"notebook": notebook, "path": hpath}) or []
    if ids:
        return str(ids[0]), False
    doc_id = client.data(
        "/api/filetree/createDocWithMd",
        {"notebook": notebook, "path": hpath, "markdown": initial_markdown},
    )
    return str(doc_id), True


def export_doc(client: SiyuanClient, doc_id: str) -> str:
    data = client.data("/api/export/exportMdContent", {"id": doc_id}) or {}
    return data.get("content") or ""


def update_doc(client: SiyuanClient, doc_id: str, markdown: str) -> None:
    client.data("/api/block/updateBlock", {"id": doc_id, "dataType": "markdown", "data": markdown})


def append_doc(client: SiyuanClient, doc_id: str, markdown: str) -> None:
    client.data("/api/block/appendBlock", {"parentID": doc_id, "dataType": "markdown", "data": markdown})

