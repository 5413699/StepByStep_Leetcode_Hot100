#!/usr/bin/env python3
"""Configure local options for the LeetCode Hot100 workflow skill."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path.home() / ".codex" / "leetcode-hot100-workflow.local.json"
DEFAULT_SIYUAN_URL = "http://127.0.0.1:6806"
DEFAULT_WORKSPACE = r"F:\就业资料-陈智飞\SiYuan_czf"


def prompt(text: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value or (default or "")


def prompt_bool(text: str, default: bool = True) -> bool:
    default_text = "Y/n" if default else "y/N"
    value = input(f"{text} [{default_text}]: ").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "y", "yes", "是", "启用"}


def call_api(base_url: str, token: str, endpoint: str, payload: dict[str, Any] | None = None) -> Any:
    req = urllib.request.Request(
        base_url.rstrip("/") + endpoint,
        data=json.dumps(payload or {}, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    if result.get("code") != 0:
        raise RuntimeError(f"{endpoint} failed: code={result.get('code')} msg={result.get('msg')}")
    return result.get("data")


def choose_notebook(base_url: str, token: str) -> str:
    data = call_api(base_url, token, "/api/notebook/lsNotebooks", {})
    notebooks = [nb for nb in (data or {}).get("notebooks", []) if not nb.get("closed")]
    if not notebooks:
        print("未找到已打开的思源笔记本，notebookId 暂留空。")
        return ""

    print("\n可用笔记本：")
    for index, notebook in enumerate(notebooks, start=1):
        print(f"{index}. {notebook.get('name')} ({notebook.get('id')})")

    while True:
        raw = prompt("选择用于 LeetCode Wiki 的笔记本序号", "1")
        try:
            return notebooks[int(raw) - 1]["id"]
        except (ValueError, IndexError):
            print("序号无效，请重新输入。")


def main() -> int:
    config_path = Path(os.environ.get("LEETCODE_WORKFLOW_CONFIG", DEFAULT_CONFIG))
    enabled = prompt_bool("是否启用思源同步", True)
    siyuan: dict[str, Any] = {
        "enabled": enabled,
        "url": DEFAULT_SIYUAN_URL,
        "workspacePath": DEFAULT_WORKSPACE,
        "tokenSource": "env:SIYUAN_TOKEN",
        "notebookId": "",
        "problemRootHPath": "/算法/LeetCode Hot100/题集",
        "conceptRootHPath": "/算法/LeetCode Hot100/知识点",
        "indexHPath": "/算法/LeetCode Hot100 Wiki",
        "autoCreateConceptPage": True,
        "autoUpdateConceptIndex": True,
        "pushNotification": True,
    }

    if enabled:
        siyuan["url"] = prompt("思源 API 地址", DEFAULT_SIYUAN_URL)
        siyuan["workspacePath"] = prompt("思源工作空间路径（包含 conf、data、repo 的目录）", DEFAULT_WORKSPACE)
        siyuan["problemRootHPath"] = prompt("题目页根路径", siyuan["problemRootHPath"])
        siyuan["conceptRootHPath"] = prompt("概念页根路径", siyuan["conceptRootHPath"])
        siyuan["indexHPath"] = prompt("总索引页路径", siyuan["indexHPath"])

        token = os.environ.get("SIYUAN_TOKEN", "")
        if not token:
            print("\n未检测到环境变量 SIYUAN_TOKEN。")
            print("请在思源 设置 > 关于 > API Token 中复制 token。")
            token = prompt("临时输入 API Token 以完成验证（不会写入配置文件）")
            print('建议之后执行：setx SIYUAN_TOKEN "你的 API Token"')

        if token:
            try:
                version = call_api(siyuan["url"], token, "/api/system/version", {})
                print(f"思源连接成功，版本：{version}")
                siyuan["notebookId"] = choose_notebook(siyuan["url"], token)
            except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as exc:
                print(f"思源连接验证失败：{exc}")
                print("仍会写入配置；修复 token 或启动思源后可重新运行本脚本。")

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps({"siyuan": siyuan}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n配置已写入：{config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
