#!/usr/bin/env python3
"""Sync a completed LeetCode problem into SiYuan via public HTTP APIs."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path.home() / ".codex" / "leetcode-hot100-workflow.local.json"
START = "<!-- codex-leetcode-start -->"
END = "<!-- codex-leetcode-end -->"
INDEX_START = "<!-- codex-leetcode-index-start -->"
INDEX_END = "<!-- codex-leetcode-index-end -->"


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
            raise SiyuanError(f"无法连接思源 API：{exc}") from exc
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
        for chunk in part.replace("\\", "/").split("/"):
            stripped = chunk.strip()
            if stripped:
                chunks.append(stripped)
    return "/" + "/".join(chunks)


def block_ref(block_id: str, text: str) -> str:
    return f'(({block_id} "{text.replace(chr(34), chr(92) + chr(34))}"))'


def unique(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            result.append(item)
            seen.add(item)
    return result


def extract_tags(payload: dict[str, Any]) -> dict[str, list[str]]:
    tags = payload.get("tags") or {}
    return {
        "dataStructures": unique(tags.get("dataStructures") or []),
        "methods": unique(tags.get("methods") or []),
        "patterns": unique(tags.get("patterns") or []),
    }


def ensure_doc(client: SiyuanClient, notebook: str, hpath: str, initial_markdown: str) -> tuple[str, bool]:
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


def update_doc(client: SiyuanClient, doc_id: str, markdown: str) -> bool:
    result = client.call(
        "/api/block/updateBlock",
        {"id": doc_id, "dataType": "markdown", "data": markdown},
        strict=False,
    )
    return result.get("code") == 0


def append_doc(client: SiyuanClient, doc_id: str, markdown: str) -> None:
    client.data("/api/block/appendBlock", {"parentID": doc_id, "dataType": "markdown", "data": markdown})


def replace_region(existing: str, region_body: str, start: str = START, end: str = END) -> str:
    region = f"{start}\n\n{region_body.strip()}\n\n{end}"
    if start in existing and end in existing:
        before, rest = existing.split(start, 1)
        _, after = rest.split(end, 1)
        return f"{before.rstrip()}\n\n{region}\n\n{after.lstrip()}".strip() + "\n"
    if existing.strip():
        return existing.rstrip() + "\n\n" + region + "\n"
    return region + "\n"


def render_problem_region(payload: dict[str, Any], concept_refs: dict[str, str]) -> str:
    tags = extract_tags(payload)
    data_structures = "、".join(concept_refs[name] for name in tags["dataStructures"] if name in concept_refs) or "未标注"
    method_names = tags["methods"] + tags["patterns"]
    methods = "、".join(concept_refs[name] for name in method_names if name in concept_refs) or "未标注"
    git = payload.get("git") or {}

    lines = [
        f"相关数据结构：{data_structures}",
        f"方法：{methods}",
        f"记录：{datetime.now().strftime('%y%m%d')}",
        "",
        "## 题干",
        payload.get("statementMarkdown", "").strip() or "（未提供）",
        "",
        "## 思路",
        payload.get("thinkingMarkdown", "").strip() or "（未提供）",
        "",
        "## 思考过程",
        payload.get("processMarkdown", "").strip() or "（未提供）",
        "",
        "## 题解",
        "```java",
        payload.get("solutionJava", "").rstrip(),
        "```",
        "",
        "## 复杂度",
        payload.get("complexityMarkdown", "").strip() or "（未提供）",
        "",
        "## 易错点",
    ]
    pitfalls = payload.get("pitfalls") or []
    lines.extend([f"- {pitfall}" for pitfall in pitfalls] or ["- （未提供）"])
    lines.extend(
        [
            "",
            "## 同步记录",
            f"- Git 分支：{git.get('branch') or '未提供'}",
            f"- Commit：{git.get('commit') or '未提供'}",
            f"- 同步时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]
    )
    return "\n".join(lines).strip()


def update_concept_index(client: SiyuanClient, concept_id: str, problem_id: str, problem_title: str) -> bool:
    existing = export_doc(client, concept_id)
    if problem_id in existing:
        return False
    problem_ref = block_ref(problem_id, problem_title)
    if INDEX_START in existing and INDEX_END in existing:
        before, rest = existing.split(INDEX_START, 1)
        inside, after = rest.split(INDEX_END, 1)
        updated_inside = (inside.strip() + "\n" + problem_ref).strip()
        updated = f"{before.rstrip()}\n\n{INDEX_START}\n\n{updated_inside}\n\n{INDEX_END}\n{after.lstrip()}"
    else:
        addition = f"## 题集\n\n{INDEX_START}\n\n{problem_ref}\n\n{INDEX_END}"
        updated = existing.rstrip() + "\n\n" + addition + "\n" if existing.strip() else addition + "\n"
    if not update_doc(client, concept_id, updated):
        append_doc(client, concept_id, f"{INDEX_START}\n\n{problem_ref}\n\n{INDEX_END}")
    return True


def sync(payload_path: Path, config_path: Path) -> dict[str, Any]:
    config = load_json(config_path)
    siyuan = config.get("siyuan") or {}
    if not siyuan.get("enabled", False):
        return {"enabled": False, "message": "SiYuan sync is disabled."}

    token = resolve_token(siyuan.get("tokenSource", "env:SIYUAN_TOKEN"))
    client = SiyuanClient(
        siyuan.get("url", "http://127.0.0.1:6806"),
        token,
        bool(siyuan.get("pushNotification", True)),
    )
    payload = load_json(payload_path)
    notebook = siyuan.get("notebookId", "")
    if not notebook:
        raise SiyuanError("配置缺少 notebookId，请运行 configure_workflow.py。")

    problem_title = payload["problemTitle"]
    problem_hpath = normalize_hpath(siyuan["problemRootHPath"], problem_title)
    problem_id, problem_created = ensure_doc(client, notebook, problem_hpath, "")

    tags = extract_tags(payload)
    concepts = tags["dataStructures"] + tags["methods"] + tags["patterns"]
    concept_refs: dict[str, str] = {}
    concept_results: list[dict[str, Any]] = []
    for concept in concepts:
        concept_hpath = normalize_hpath(siyuan["conceptRootHPath"], concept)
        concept_id, concept_created = ensure_doc(client, notebook, concept_hpath, "")
        concept_refs[concept] = block_ref(concept_id, concept)
        index_updated = update_concept_index(client, concept_id, problem_id, problem_title)
        concept_results.append(
            {
                "name": concept,
                "id": concept_id,
                "url": f"siyuan://blocks/{concept_id}",
                "created": concept_created,
                "indexUpdated": index_updated,
            }
        )

    existing = export_doc(client, problem_id)
    updated = replace_region(existing, render_problem_region(payload, concept_refs))
    if not update_doc(client, problem_id, updated):
        append_doc(client, problem_id, updated)

    client.data("/api/sqlite/flushTransaction", {})
    client.push_message(f"LeetCode 笔记已同步：{problem_title}")
    return {
        "enabled": True,
        "problem": {
            "title": problem_title,
            "id": problem_id,
            "hPath": problem_hpath,
            "url": f"siyuan://blocks/{problem_id}",
            "created": problem_created,
        },
        "concepts": concept_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Completed problem JSON payload.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Workflow config path.")
    args = parser.parse_args()

    try:
        result = sync(Path(args.input), Path(args.config))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"SiYuan sync failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
