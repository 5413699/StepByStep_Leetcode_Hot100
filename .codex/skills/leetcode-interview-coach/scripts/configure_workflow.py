#!/usr/bin/env python3
"""Configure local options for the LeetCode interview-training workflow."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
from pathlib import Path

sys.dont_write_bytecode = True

from siyuan_client import DEFAULT_CONFIG, DEFAULT_SYSTEM_ROOT, DEFAULT_URL, DEFAULT_WORKSPACE, load_config, open_client_from_config, write_json


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


def choose_notebook(client) -> str:
    data = client.data("/api/notebook/lsNotebooks", {}) or {}
    notebooks = [nb for nb in data.get("notebooks", []) if not nb.get("closed")]
    if not notebooks:
        print("未找到已打开的思源笔记本，notebookId 暂留空。")
        return ""

    print("\n可用笔记本：")
    for index, notebook in enumerate(notebooks, start=1):
        print(f"{index}. {notebook.get('name')} ({notebook.get('id')})")

    while True:
        raw = prompt("选择用于面试手撕训练系统的笔记本序号", "1")
        try:
            return notebooks[int(raw) - 1]["id"]
        except (ValueError, IndexError):
            print("序号无效，请重新输入。")


def main() -> int:
    config_path = Path(os.environ.get("LEETCODE_WORKFLOW_CONFIG", DEFAULT_CONFIG))
    config = load_config(config_path)
    siyuan = config["siyuan"]
    wiki = config["wikiPolicy"]

    siyuan["enabled"] = prompt_bool("是否启用思源同步", bool(siyuan.get("enabled", True)))
    if siyuan["enabled"]:
        siyuan["url"] = prompt("思源 API 默认地址（可自动发现真实端口）", siyuan.get("url") or DEFAULT_URL)
        siyuan["urlAutoDetect"] = prompt_bool("是否启用思源 API 端口自动发现", bool(siyuan.get("urlAutoDetect", True)))
        siyuan["workspacePath"] = prompt("思源工作空间路径（包含 conf、data、repo 的目录）", siyuan.get("workspacePath") or DEFAULT_WORKSPACE)
        wiki["systemRootHPath"] = prompt("面试手撕训练系统根路径", wiki.get("systemRootHPath") or DEFAULT_SYSTEM_ROOT)

        token = os.environ.get("SIYUAN_TOKEN", "")
        if not token:
            print("\n未检测到环境变量 SIYUAN_TOKEN。")
            print("请在思源 设置 > 关于 > API Token 中复制 token。")
            token = prompt("临时输入 API Token 以完成验证（不会写入配置文件）")
            if token:
                os.environ["SIYUAN_TOKEN"] = token
            print('建议之后执行：setx SIYUAN_TOKEN "你的 API Token"')

        if token:
            try:
                client, resolved = open_client_from_config(config, config_path=config_path, update_config=False)
                print(f"思源连接成功：{resolved.get('url')}，版本检查通过。")
                siyuan["url"] = resolved.get("url", siyuan["url"])
                siyuan["lastWorkingUrl"] = resolved.get("url", siyuan.get("lastWorkingUrl", ""))
                siyuan["notebookId"] = choose_notebook(client)
            except Exception as exc:
                print(f"思源连接验证失败：{exc}")
                print("仍会写入配置；修复 token 或启动思源后可重新运行本脚本。")

    write_json(config_path, config)
    print(f"\n配置已写入：{config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
