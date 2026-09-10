#!/usr/bin/env python3
"""Configure local options for the LeetCode interview-training workflow."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
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


def parse_bool_arg(value: str) -> bool:
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "是", "启用"}:
        return True
    if normalized in {"0", "false", "no", "n", "否", "停用"}:
        return False
    raise argparse.ArgumentTypeError("布尔值应为 true/false。")


YUQUE_DEFAULT_API = "https://www.yuque.com/api/v2"


def resolve_yuque_token(yuque: dict | None = None) -> str:
    """Resolve the YuQue PAT from process or Windows user environment."""
    source = str((yuque or {}).get("tokenSource") or "env:YuQue")
    if source.startswith("env:"):
        name = source.split(":", 1)[1]
        token = os.environ.get(name, "")
        if token or os.name != "nt":
            return token.strip()
        # setx writes the Windows user environment but an already-running
        # process does not receive the updated value until the next launch.
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                return str(winreg.QueryValueEx(key, name)[0] or "").strip()
        except (FileNotFoundError, OSError):
            return ""
    # Tokens are deliberately not accepted from config files.  This keeps PATs
    # out of repository/local JSON even when an old config has tokenSource set.
    return os.environ.get("YuQue", "")


def yuque_request(base_url: str, token: str, path: str, *, params: dict | None = None) -> dict | list:
    """Call a YuQue v2 JSON endpoint and raise a useful error on failure."""
    base = base_url.rstrip("/")
    query = urllib.parse.urlencode(params or {})
    url = f"{base}/{path.lstrip('/')}" + (f"?{query}" if query else "")
    request = urllib.request.Request(
        url,
        headers={
            "X-Auth-Token": token,
            "Accept": "application/json",
            "User-Agent": "leetcode-interview-coach",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"YuQue API {exc.code} {exc.reason}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"YuQue API 无法连接：{exc.reason}") from exc
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("YuQue API 返回了无效 JSON。") from exc
    if isinstance(payload, dict) and payload.get("error"):
        raise RuntimeError(f"YuQue API 错误：{payload.get('error')}")
    return payload


def yuque_data(payload: dict | list) -> list | dict:
    """Normalize the common YuQue {data: ...} envelope."""
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def yuque_user(base_url: str, token: str) -> dict:
    payload = yuque_data(yuque_request(base_url, token, "/user"))
    if not isinstance(payload, dict):
        raise RuntimeError("YuQue 用户接口返回格式异常。")
    return payload


def list_yuque_repos(base_url: str, token: str, user: dict | None = None) -> list[dict]:
    user = user or yuque_user(base_url, token)
    login = str(user.get("login") or user.get("username") or user.get("account") or "")
    if not login:
        raise RuntimeError("YuQue 用户信息缺少 login，无法读取知识库。")
    payload = yuque_data(
        yuque_request(base_url, token, f"/users/{urllib.parse.quote(login, safe='')}/repos", params={"limit": 100})
    )
    if not isinstance(payload, list):
        raise RuntimeError("YuQue 知识库接口返回格式异常。")
    return [item for item in payload if isinstance(item, dict)]


def list_yuque_toc(base_url: str, token: str, namespace: str, slug: str) -> list[dict]:
    payload = yuque_data(
        yuque_request(
            base_url,
            token,
            f"/repos/{urllib.parse.quote(namespace, safe='')}/{urllib.parse.quote(slug, safe='')}/toc",
            params={"limit": 1000},
        )
    )
    if not isinstance(payload, list):
        raise RuntimeError("YuQue 知识库目录接口返回格式异常。")
    return [item for item in payload if isinstance(item, dict)]


def normalize_yuque_path(path: str) -> str:
    return "/".join(part.strip() for part in str(path).replace("\\", "/").split("/") if part.strip())


def yuque_toc_paths(entries: list[dict]) -> list[tuple[str, dict]]:
    """Build readable paths from a flat TOC (parent_uuid is optional)."""
    nested_result: list[tuple[str, dict]] = []

    def visit_nested(items: list[dict], prefix: str = "") -> None:
        for entry in items:
            if not isinstance(entry, dict):
                continue
            title = str(entry.get("title") or entry.get("name") or entry.get("slug") or "")
            if not title:
                continue
            path = f"{prefix}/{title}" if prefix else title
            nested_result.append((path, entry))
            children = entry.get("children") or entry.get("nodes")
            if isinstance(children, list):
                visit_nested(children, path)

    if any(isinstance(item.get("children") or item.get("nodes"), list) for item in entries):
        visit_nested(entries)
        return nested_result

    by_parent: dict[str, list[dict]] = {}
    for entry in entries:
        parent = str(entry.get("parent_uuid") or entry.get("parentUuid") or "")
        by_parent.setdefault(parent, []).append(entry)
    result: list[tuple[str, dict]] = []

    def visit(parent: str, prefix: str, seen: set[str]) -> None:
        for entry in by_parent.get(parent, []):
            if str(entry.get("type") or "").upper() == "DOC" or entry.get("url"):
                continue
            uuid = str(entry.get("uuid") or entry.get("id") or "")
            title = str(entry.get("title") or entry.get("name") or entry.get("slug") or "")
            if not title:
                continue
            path = f"{prefix}/{title}" if prefix else title
            result.append((path, entry))
            if uuid and uuid not in seen:
                visit(uuid, path, seen | {uuid})

    visit("", "", set())
    # Some API responses omit parent_uuid but expose depth. Keep those entries
    # selectable rather than silently claiming the directory is unavailable.
    if not result:
        result = [(str(item.get("title") or item.get("name") or item.get("slug") or ""), item) for item in entries]
        result = [(path, item) for path, item in result if path]
    return result


def select_yuque_repo(repos: list[dict], configured_namespace: str = "") -> dict:
    if configured_namespace:
        wanted = configured_namespace.strip()
        matches = [
            repo for repo in repos
            if str(repo.get("namespace") or "") == wanted
            or str(repo.get("namespace") or "").split("/", 1)[0] == wanted
            or str(repo.get("slug") or "") == wanted
        ]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise RuntimeError(f"未找到已配置的语雀知识库：{configured_namespace}")
    if not repos:
        raise RuntimeError("未找到可访问的语雀知识库。")
    print("\n可用语雀知识库：")
    for index, repo in enumerate(repos, start=1):
        namespace = repo.get("namespace") or repo.get("slug") or ""
        print(f"{index}. {repo.get('name') or namespace} ({namespace})")
    while True:
        raw = prompt("选择用于面试手撕训练系统的知识库序号", "1")
        try:
            return repos[int(raw) - 1]
        except (ValueError, IndexError):
            print("序号无效，请重新输入。")


def select_configured_yuque_repo(repos: list[dict], namespace: str, repo_slug: str = "") -> dict:
    """Resolve a configured repository without prompting during --check."""
    wanted = str(namespace or "").strip()
    wanted_full = f"{wanted}/{repo_slug}" if repo_slug and "/" not in wanted else wanted
    matches = [
        repo for repo in repos
        if str(repo.get("namespace") or "") == wanted_full
        or (repo_slug and str(repo.get("namespace") or "").split("/", 1)[0] == wanted and str(repo.get("slug") or "") == repo_slug)
        or (not repo_slug and str(repo.get("slug") or "") == wanted)
    ]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise RuntimeError(f"未找到已配置的语雀知识库：{wanted_full}")
    raise RuntimeError(f"语雀知识库配置不唯一：{wanted_full}")


def configure_yuque(config: dict, *, interactive: bool = True) -> None:
    yuque = config.setdefault("yuque", {})
    yuque.setdefault("apiBase", YUQUE_DEFAULT_API)
    yuque.setdefault("tokenSource", "env:YuQue")
    yuque.setdefault("parentPath", "")
    yuque.setdefault("parentUuid", "")
    yuque.setdefault("autoPublish", True)
    base_url = str(yuque.get("apiBase") or YUQUE_DEFAULT_API)
    token = resolve_yuque_token(yuque)
    if not token:
        print("\n未检测到环境变量 YuQue（语雀 Personal Access Token）。")
        print('请使用 PowerShell 设置用户变量：setx YuQue "你的 token"，然后重新打开终端。')
        if not interactive:
            return
        token = prompt("临时输入语雀 PAT 以完成验证（不会写入配置文件）")
        if token:
            os.environ["YuQue"] = token
        else:
            return
    try:
        user = yuque_user(base_url, token)
        repos = list_yuque_repos(base_url, token, user)
        if not interactive and yuque.get("repoSlug"):
            repo = select_configured_yuque_repo(repos, str(yuque.get("namespace") or ""), str(yuque.get("repoSlug") or ""))
        else:
            repo = select_yuque_repo(repos, str(yuque.get("namespace") or ""))
        raw_namespace = str(repo.get("namespace") or "")
        repo_slug = str(repo.get("slug") or (raw_namespace.rsplit("/", 1)[-1] if raw_namespace else ""))
        # YuQue API paths use the owner's login as namespace and the book slug
        # separately.  Some responses expose namespace as "login/book-slug".
        namespace = raw_namespace.split("/", 1)[0] if "/" in raw_namespace else raw_namespace
        yuque["namespace"] = namespace
        yuque["repoSlug"] = repo_slug
        print(f"语雀连接成功：{user.get('login') or user.get('name') or ''}，知识库：{repo.get('name') or namespace}")
        entries = list_yuque_toc(base_url, token, namespace, repo_slug)
        paths = yuque_toc_paths(entries)
        if interactive and paths:
            print("\n可用语雀目录（可选择根目录）：")
            print("0. /（知识库根目录）")
            for index, (path, _entry) in enumerate(paths, start=1):
                print(f"{index}. /{path}")
            default_path = normalize_yuque_path(str(yuque.get("parentPath") or ""))
            default_index = next(
                (str(index) for index, (path, _entry) in enumerate(paths, start=1)
                 if normalize_yuque_path(path) == default_path),
                "0" if not default_path else "1",
            )
            raw = prompt("选择新题目父目录序号", default_index)
            if raw == "0":
                yuque["parentPath"], yuque["parentUuid"] = "", ""
            else:
                try:
                    selected_path, selected = paths[int(raw) - 1]
                    yuque["parentPath"] = f"/{selected_path}"
                    yuque["parentUuid"] = str(selected.get("uuid") or selected.get("id") or "")
                except (ValueError, IndexError):
                    raise RuntimeError("目录序号无效。")
        elif yuque.get("parentPath"):
            wanted = normalize_yuque_path(str(yuque["parentPath"]))
            matches = [(path, entry) for path, entry in paths if normalize_yuque_path(path) == wanted]
            if len(matches) != 1:
                raise RuntimeError(f"未找到语雀父目录：/{wanted}")
            yuque["parentUuid"] = str(matches[0][1].get("uuid") or matches[0][1].get("id") or "")
    except Exception as exc:
        print(f"语雀连接验证失败：{exc}")
        print("仍会写入配置；修复 PAT、知识库或目录后可重新运行本脚本。")


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
    yuque = config.setdefault("yuque", {})
    siyuan_enabled = bool(siyuan.get("enabled", True))
    yuque_enabled = bool(yuque.get("enabled", False))
    workspace = discover_siyuan_workspace(siyuan.get("workspacePath"))
    token = os.environ.get("SIYUAN_TOKEN", "")
    yuque_token = resolve_yuque_token(yuque)

    print("LeetCode workflow local setup check")
    print(f"- configPath: {config_path}")
    print(f"- configExists: {config_path.exists()}")
    missing = []
    print(f"- siyuanEnabled: {siyuan_enabled}")
    if siyuan_enabled:
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
            print("- siyuanApiReachable: true")
            print(f"- siyuanApiUrl: {resolved.get('url')}")
            notebooks = list_open_notebooks(client)
            print(f"- openNotebookCount: {len(notebooks)}")
            for index, notebook in enumerate(notebooks, start=1):
                print(f"  {index}. {notebook.get('name')} ({notebook.get('id')})")
            if not resolved.get("notebookId"):
                print("- missing: notebookId")
        except Exception as exc:
            print("- siyuanApiReachable: false")
            print(f"- siyuanApiError: {exc}")
            missing.append(f"思源 API 无法访问：{exc}")
        if not is_siyuan_workspace(workspace):
            missing.append("思源工作空间路径：打开思源，设置 > 关于，查看工作空间；或找到包含 conf、data、repo 的目录。")
        if not token:
            missing.append("思源 API Token：打开思源，设置 > 关于 > API Token；建议用 setx SIYUAN_TOKEN \"你的 token\" 设置。")
        if not siyuan.get("notebookId"):
            missing.append("目标笔记本：启动思源并打开要写入的笔记本，然后运行本脚本交互选择。")

    print(f"- yuqueEnabled: {yuque_enabled}")
    if yuque_enabled:
        print(f"- yuqueApiBase: {yuque.get('apiBase') or YUQUE_DEFAULT_API}")
        print("- yuqueTokenSource: env:YuQue")
        print(f"- yuqueTokenAvailable: {bool(yuque_token)}")
        print(f"- yuqueNamespace: {yuque.get('namespace') or ''}")
        print(f"- yuqueParentPath: {yuque.get('parentPath') or '/'}")
        if not yuque_token:
            missing.append('语雀 PAT：设置 Windows 用户变量 YuQue（例如 setx YuQue "你的 token"），再重新打开终端。')
        elif not yuque.get("namespace"):
            missing.append("语雀知识库：运行本脚本交互选择可访问的知识库。")
        else:
            try:
                user = yuque_user(str(yuque.get("apiBase") or YUQUE_DEFAULT_API), yuque_token)
                repos = list_yuque_repos(str(yuque.get("apiBase") or YUQUE_DEFAULT_API), yuque_token, user)
                repo = select_configured_yuque_repo(repos, str(yuque.get("namespace")), str(yuque.get("repoSlug") or ""))
                repo_slug = str(repo.get("slug") or yuque.get("repoSlug") or yuque.get("namespace", "").rsplit("/", 1)[-1])
                owner = str(repo.get("namespace") or "").split("/", 1)[0]
                entries = list_yuque_toc(str(yuque.get("apiBase") or YUQUE_DEFAULT_API), yuque_token, owner, repo_slug)
                paths = yuque_toc_paths(entries)
                parent = normalize_yuque_path(str(yuque.get("parentPath") or ""))
                if parent and not any(normalize_yuque_path(path) == parent for path, _ in paths):
                    missing.append(f"未找到语雀父目录：/{parent}")
                print(f"- yuqueApiReachable: true ({user.get('login') or user.get('name') or ''})")
                print(f"- yuqueDirectoryCount: {len(paths)}")
            except Exception as exc:
                print("- yuqueApiReachable: false")
                print(f"- yuqueApiError: {exc}")
                missing.append(f"语雀 API 无法访问：{exc}")

    if missing:
        print("\n需要补充的信息：")
        for index, item in enumerate(missing, start=1):
            print(f"{index}. {item}")
        print("\n可以把这些信息发给 Codex，由 Codex 使用 --workspace/--notebook-name/--notebook-id/--system-root 完成本机配置。")
        print("也可以补齐后运行：python .codex\\skills\\leetcode-interview-coach\\scripts\\configure_workflow.py")
        return 1

    print("\n本机配置看起来已具备当前启用发布目标所需信息。")
    return 0


def run_apply(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    siyuan = config["siyuan"]
    wiki = config["wikiPolicy"]
    yuque = config.setdefault("yuque", {})
    yuque.setdefault("apiBase", YUQUE_DEFAULT_API)
    yuque.setdefault("tokenSource", "env:YuQue")
    yuque.setdefault("autoPublish", True)

    if args.target:
        target = args.target.lower()
        siyuan["enabled"] = target in {"siyuan", "both"}
        yuque["enabled"] = target in {"yuque", "both"}

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

    if args.yuque_api_base:
        yuque["apiBase"] = args.yuque_api_base
    if args.yuque_namespace:
        namespace_value = args.yuque_namespace.strip()
        if "/" in namespace_value and not args.yuque_repo_slug:
            owner, repo_slug = namespace_value.split("/", 1)
            yuque["namespace"], yuque["repoSlug"] = owner, repo_slug
        else:
            yuque["namespace"] = namespace_value
    if args.yuque_repo_slug:
        yuque["repoSlug"] = args.yuque_repo_slug.strip()
    if args.yuque_parent_path is not None:
        yuque["parentPath"] = args.yuque_parent_path
    if args.yuque_parent_uuid is not None:
        yuque["parentUuid"] = args.yuque_parent_uuid
    if args.yuque_auto_publish is not None:
        yuque["autoPublish"] = args.yuque_auto_publish

    if args.verify:
        if siyuan.get("enabled", True):
            client, resolved = open_client_from_config(config, config_path=args.config, update_config=False)
            siyuan["url"] = resolved.get("url", siyuan.get("url", DEFAULT_URL))
            siyuan["lastWorkingUrl"] = resolved.get("url", siyuan.get("lastWorkingUrl", ""))
        if yuque.get("enabled", False):
            configure_yuque(config, interactive=False)

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
    yuque = config.setdefault("yuque", {})
    yuque.setdefault("apiBase", YUQUE_DEFAULT_API)
    yuque.setdefault("tokenSource", "env:YuQue")
    yuque.setdefault("autoPublish", True)

    current_target = "both" if siyuan.get("enabled", True) and yuque.get("enabled", False) else (
        "siyuan" if siyuan.get("enabled", True) else ("yuque" if yuque.get("enabled", False) else "none")
    )
    print("发布目标：1. 思源  2. 语雀  3. 两者  4. 不发布")
    target_raw = prompt("选择发布目标", {"siyuan": "1", "yuque": "2", "both": "3", "none": "4"}[current_target])
    target = {"1": "siyuan", "2": "yuque", "3": "both", "4": "none"}.get(target_raw, target_raw.lower())
    if target not in {"siyuan", "yuque", "both", "none"}:
        print("目标无效，保留现有发布目标。")
        target = current_target
    siyuan["enabled"] = target in {"siyuan", "both"}
    yuque["enabled"] = target in {"yuque", "both"}

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

    if yuque["enabled"]:
        yuque["apiBase"] = prompt("语雀 API 地址", yuque.get("apiBase") or YUQUE_DEFAULT_API)
        yuque["autoPublish"] = prompt_bool("完成题目后是否自动发布到语雀", bool(yuque.get("autoPublish", True)))
        configure_yuque(config, interactive=True)

    write_json(config_path, config)
    print(f"\n配置已写入：{config_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure local options for the LeetCode interview-training workflow.")
    parser.add_argument("--check", action="store_true", help="diagnose local SiYuan setup and list missing information")
    parser.add_argument("--config", type=Path, default=Path(os.environ.get("LEETCODE_WORKFLOW_CONFIG", DEFAULT_CONFIG)))
    parser.add_argument("--target", choices=["siyuan", "yuque", "both", "none"], help="publish target(s) for non-interactive configuration")
    parser.add_argument("--workspace", help="SiYuan workspace root, or a conf/data/repo child path")
    parser.add_argument("--url", help="default SiYuan API URL")
    parser.add_argument("--no-url-auto-detect", action="store_true", help="disable local SiYuan API port discovery")
    parser.add_argument("--system-root", help="target wiki root HPath")
    parser.add_argument("--notebook-id", help="target notebook id")
    parser.add_argument("--notebook-name", help="target open notebook name; requires reachable SiYuan API")
    parser.add_argument("--verify", action="store_true", help="verify API connectivity while applying provided options")
    parser.add_argument("--yuque-api-base", help="YuQue API base URL")
    parser.add_argument("--yuque-namespace", help="YuQue repository namespace, for example user/book")
    parser.add_argument("--yuque-repo-slug", help="YuQue repository slug, for example algorithms")
    parser.add_argument("--yuque-parent-path", help="YuQue parent directory path")
    parser.add_argument("--yuque-parent-uuid", help="YuQue parent directory UUID")
    parser.add_argument("--yuque-auto-publish", type=parse_bool_arg, default=None, help="whether finish workflow publishes to YuQue")
    parser.add_argument("--write", action="store_true", help="write non-interactive options to local config")
    args = parser.parse_args()

    if args.check:
        return run_check(args.config)
    if any([
        args.target, args.workspace, args.url, args.no_url_auto_detect, args.system_root,
        args.notebook_id, args.notebook_name, args.verify, args.yuque_api_base,
        args.yuque_namespace, args.yuque_repo_slug, args.yuque_parent_path is not None, args.yuque_parent_uuid is not None,
        args.yuque_auto_publish is not None,
    ]):
        return run_apply(args)
    return run_interactive(args.config)


if __name__ == "__main__":
    raise SystemExit(main())
