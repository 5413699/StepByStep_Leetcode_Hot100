#!/usr/bin/env python3
"""Configure local options for the LeetCode interview-training workflow."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import argparse
from pathlib import Path

sys.dont_write_bytecode = True

from siyuan_client import (
    DEFAULT_CONFIG,
    DEFAULT_SYSTEM_ROOT,
    DEFAULT_URL,
    discover_siyuan_workspace,
    is_siyuan_workspace,
    load_config,
    open_client_from_config,
    write_json,
)


def mask_token(token: str) -> str:
    if not token:
        return ""
    if len(token) <= 8:
        return "*" * len(token)
    return f"{token[:4]}...{token[-4:]}"


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


def list_open_notebooks(client) -> list[dict]:
    data = client.data("/api/notebook/lsNotebooks", {}) or {}
    return [nb for nb in data.get("notebooks", []) if not nb.get("closed")]


def resolve_notebook_id(client, *, notebook_id: str = "", notebook_name: str = "") -> str:
    if notebook_id:
        return notebook_id
    if not notebook_name:
        return ""
    notebooks = list_open_notebooks(client)
    matches = [nb for nb in notebooks if nb.get("name") == notebook_name]
    if len(matches) == 1:
        return str(matches[0].get("id") or "")
    if not matches:
        raise RuntimeError(f"未找到已打开笔记本：{notebook_name}")
    raise RuntimeError(f"存在多个同名已打开笔记本：{notebook_name}")


def run_check(config_path: Path) -> int:
    config = load_config(config_path)
    siyuan = config["siyuan"]
    workspace = discover_siyuan_workspace(siyuan.get("workspacePath"))
    token = os.environ.get("SIYUAN_TOKEN", "")

    print("LeetCode workflow local setup check")
    print(f"- configPath: {config_path}")
    print(f"- configExists: {config_path.exists()}")
    print(f"- siyuanEnabled: {bool(siyuan.get('enabled', True))}")
    print(f"- workspacePath: {workspace}")
    print(f"- workspaceValid: {is_siyuan_workspace(workspace)}")
    print(f"- tokenSource: env:SIYUAN_TOKEN")
    print(f"- tokenAvailable: {bool(token)}")
    if token:
        print(f"- tokenPreview: {mask_token(token)}")
    print(f"- configuredNotebookId: {siyuan.get('notebookId') or ''}")
    print(f"- systemRootHPath: {config['wikiPolicy'].get('systemRootHPath') or DEFAULT_SYSTEM_ROOT}")

    try:
        client, resolved = open_client_from_config(config, config_path=config_path, update_config=False)
        print(f"- apiReachable: true")
        print(f"- apiUrl: {resolved.get('url')}")
        notebooks = list_open_notebooks(client)
        print(f"- openNotebookCount: {len(notebooks)}")
        for index, notebook in enumerate(notebooks, start=1):
            print(f"  {index}. {notebook.get('name')} ({notebook.get('id')})")
        if not resolved.get("notebookId"):
            print("- missing: notebookId")
    except Exception as exc:
        print("- apiReachable: false")
        print(f"- apiError: {exc}")

    missing = []
    if not is_siyuan_workspace(workspace):
        missing.append("思源工作空间路径：打开思源，设置 > 关于，查看工作空间；或找到包含 conf、data、repo 的目录。")
    if not token:
        missing.append("思源 API Token：打开思源，设置 > 关于 > API Token；建议用 setx SIYUAN_TOKEN \"你的 token\" 设置。")
    if not siyuan.get("notebookId"):
        missing.append("目标笔记本：启动思源并打开要写入的笔记本，然后运行本脚本交互选择。")

    if missing:
        print("\n需要补充的信息：")
        for index, item in enumerate(missing, start=1):
            print(f"{index}. {item}")
        print("\n可以把这些信息发给 Codex，由 Codex 使用 --workspace/--notebook-name/--notebook-id/--system-root 完成本机配置。")
        print("也可以补齐后运行：python .codex\\skills\\leetcode-interview-coach\\scripts\\configure_workflow.py")
        return 1

    print("\n本机配置看起来已具备思源同步所需信息。")
    return 0


def run_apply(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    siyuan = config["siyuan"]
    wiki = config["wikiPolicy"]

    if args.workspace:
        siyuan["workspacePath"] = discover_siyuan_workspace(args.workspace)
    else:
        siyuan["workspacePath"] = discover_siyuan_workspace(siyuan.get("workspacePath"))
    if args.url:
        siyuan["url"] = args.url
    if args.no_url_auto_detect:
        siyuan["urlAutoDetect"] = False
    if args.system_root:
        wiki["systemRootHPath"] = args.system_root

    if args.notebook_id:
        siyuan["notebookId"] = args.notebook_id

    if args.notebook_name:
        client, resolved = open_client_from_config(config, config_path=args.config, update_config=False)
        siyuan["url"] = resolved.get("url", siyuan.get("url", DEFAULT_URL))
        siyuan["lastWorkingUrl"] = resolved.get("url", siyuan.get("lastWorkingUrl", ""))
        siyuan["notebookId"] = resolve_notebook_id(client, notebook_name=args.notebook_name)

    if args.verify:
        client, resolved = open_client_from_config(config, config_path=args.config, update_config=False)
        siyuan["url"] = resolved.get("url", siyuan.get("url", DEFAULT_URL))
        siyuan["lastWorkingUrl"] = resolved.get("url", siyuan.get("lastWorkingUrl", ""))

    if args.write:
        write_json(args.config, config)
        print(f"配置已写入：{args.config}")
    else:
        print(json.dumps(config, ensure_ascii=False, indent=2))
        print("\n未写入配置；如需写入，请加 --write。")
    return 0


def run_interactive(config_path: Path) -> int:
    config = load_config(config_path)
    siyuan = config["siyuan"]
    wiki = config["wikiPolicy"]

    siyuan["enabled"] = prompt_bool("是否启用思源同步", bool(siyuan.get("enabled", True)))
    if siyuan["enabled"]:
        siyuan["url"] = prompt("思源 API 默认地址（可自动发现真实端口）", siyuan.get("url") or DEFAULT_URL)
        siyuan["urlAutoDetect"] = prompt_bool("是否启用思源 API 端口自动发现", bool(siyuan.get("urlAutoDetect", True)))
        discovered_workspace = discover_siyuan_workspace(siyuan.get("workspacePath"))
        siyuan["workspacePath"] = prompt("思源工作空间路径（包含 conf、data、repo 的目录）", discovered_workspace)
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure local options for the LeetCode interview-training workflow.")
    parser.add_argument("--check", action="store_true", help="diagnose local SiYuan setup and list missing information")
    parser.add_argument("--config", type=Path, default=Path(os.environ.get("LEETCODE_WORKFLOW_CONFIG", DEFAULT_CONFIG)))
    parser.add_argument("--workspace", help="SiYuan workspace root, or a conf/data/repo child path")
    parser.add_argument("--url", help="default SiYuan API URL")
    parser.add_argument("--no-url-auto-detect", action="store_true", help="disable local SiYuan API port discovery")
    parser.add_argument("--system-root", help="target wiki root HPath")
    parser.add_argument("--notebook-id", help="target notebook id")
    parser.add_argument("--notebook-name", help="target open notebook name; requires reachable SiYuan API")
    parser.add_argument("--verify", action="store_true", help="verify API connectivity while applying provided options")
    parser.add_argument("--write", action="store_true", help="write non-interactive options to local config")
    args = parser.parse_args()

    if args.check:
        return run_check(args.config)
    if any([args.workspace, args.url, args.no_url_auto_detect, args.system_root, args.notebook_id, args.notebook_name, args.verify]):
        return run_apply(args)
    return run_interactive(args.config)


if __name__ == "__main__":
    raise SystemExit(main())
