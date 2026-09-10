#!/usr/bin/env python3
"""Render one learning record for repository Markdown and publishing adapters.

The active coach supplies the transcript and valid solutions. This module never
reconstructs dialogue, corrects code, or rewrites the learner's comments.
Publishing adapters should consume build_sections(), not parse HTML details.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any, TypedDict


class NoteSection(TypedDict, total=False):
    kind: str
    markdown: str
    heading: str
    title: str
    collapsed: bool


def _text(value: Any) -> str:
    # Deliberately do not stringify dicts: user-facing notes are not JSON dumps.
    return value.strip() if isinstance(value, str) else ""


def _items(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(_text(item) for item in value if _text(item)))


def _bullets(value: Any) -> str:
    return "\n".join("- " + item.replace("\n", "\n  ") for item in _items(value))


def normalize_title(payload: dict[str, Any]) -> str:
    """Normalize E070. 爬楼梯 to E70-爬楼梯 without inferring difficulty."""
    title = _text(payload.get("problemTitle")) or "LeetCode 题目"
    title = re.sub(r"^#\s+", "", title).strip()
    match = re.fullmatch(r"([EMHemh]?)\s*0*(\d+)\s*[.．、:\-：]\s*(.+)", title)
    if match:
        prefix, number, name = match.groups()
        return f"{prefix.upper()}{int(number)}-{name.strip()}"
    return title


def _clean_markdown(value: Any, *, title: str = "") -> str:
    """Remove wrapper markers outside code only; never mutate fenced code."""
    source = _text(value)
    lines = source.splitlines(keepends=True)
    result: list[str] = []
    fence_char = ""
    fence_length = 0
    for line in lines:
        candidate = line.lstrip()
        fence = re.match(r"(`{3,}|~{3,})", candidate)
        if fence:
            token = fence.group(1)
            if not fence_char:
                fence_char, fence_length = token[0], len(token)
            elif token[0] == fence_char and len(token) >= fence_length and not candidate[len(token):].strip():
                fence_char, fence_length = "", 0
            result.append(line)
            continue
        if not fence_char:
            line = re.sub(r"<!--\s*codex-[\s\S]*?-->", "", line)
        result.append(line)
    cleaned = "".join(result).strip()
    if title:
        first, separator, rest = cleaned.partition("\n")
        if first.startswith("# ") and normalize_title({"problemTitle": first[2:]}) == title:
            cleaned = rest.strip() if separator else ""
    return cleaned


def _fenced_code(code: Any, language: Any = "java") -> str:
    if not isinstance(code, str):
        raise ValueError("答案代码必须是字符串。")
    # Preserve indentation, identifiers, and every comment verbatim. Choose a
    # fence longer than any backtick run so even literal Markdown code survives.
    longest = max((len(run) for run in re.findall(r"`+", code)), default=0)
    fence = "`" * max(3, longest + 1)
    label = _text(language) or "java"
    if not re.fullmatch(r"[A-Za-z0-9_+.-]+", label):
        raise ValueError("代码块语言标识不合法。")
    return f"{fence}{label}\n{code.strip(chr(10) + chr(13))}\n{fence}"


def _transcript_markdown(transcript: Any, process: Any) -> str:
    if not isinstance(transcript, list):
        process_text = _clean_markdown(process)
        return "\n\n".join(filter(None, ["完整教学对话未提供；仅保留已有记录，不补造对话。", process_text]))
    if not transcript:
        return "完整教学对话未提供；不补造对话。"
    rendered: list[str] = []
    for index, entry in enumerate(transcript, start=1):
        if not isinstance(entry, dict) or entry.get("role") not in {"assistant", "user"}:
            raise ValueError(f"第 {index} 条教学记录的角色必须为 assistant 或 user。")
        content = _clean_markdown(entry.get("contentMarkdown")) or "本条对话内容未提供。"
        if entry["role"] == "assistant":
            content = "\n".join("> " + line if line else ">" for line in content.splitlines())
            rendered.append(f"**GPT · 第 {index} 条**\n\n{content}")
        else:
            rendered.append(f"**我 · 第 {index} 条**\n\n{content}")
        correction = _clean_markdown(entry.get("correctionMarkdown"))
        if correction:
            rendered.append(f"**勘误／更新说明**\n\n{correction}")
    return "\n\n".join(rendered)


def _training_markdown(payload: dict[str, Any], digest: dict[str, Any]) -> str:
    supplied = _clean_markdown(payload.get("trainingMarkdown"))
    if supplied:
        return supplied
    parts: list[str] = []
    first = _clean_markdown(digest.get("firstReaction") or payload.get("thinkingMarkdown"))
    if first:
        parts.append(f"**第一反应**\n\n{first}")
    for key, label in [("stuckPoints", "卡壳点"), ("breakthroughs", "关键突破"), ("implementationNotes", "实现记录")]:
        content = _bullets(digest.get(key))
        if content:
            parts.append(f"**{label}**\n\n{content}")
    misconceptions = digest.get("misconceptions")
    if isinstance(misconceptions, list):
        corrections = []
        for entry in misconceptions:
            if not isinstance(entry, dict):
                continue
            before, after = _text(entry.get("before")), _text(entry.get("after"))
            if before and after:
                corrections.append(f"- 原先理解：{before}\n  修正后：{after}")
        if corrections:
            parts.append("**理解修正**\n\n" + "\n".join(corrections))
    tags = payload.get("tags")
    if isinstance(tags, dict):
        labels = [("dataStructures", "数据结构"), ("methods", "方法"), ("patterns", "模式"), ("commonFunctions", "常用函数")]
        tag_lines = [f"{label}：{'、'.join(_items(tags.get(key)))}" for key, label in labels if _items(tags.get(key))]
        if tag_lines:
            parts.append("\n\n".join(tag_lines))
    return "\n\n".join(parts)


def _review_markdown(payload: dict[str, Any], digest: dict[str, Any]) -> str:
    supplied = _clean_markdown(payload.get("reviewMarkdown"))
    if supplied:
        return supplied
    parts: list[str] = []
    expression = _clean_markdown(digest.get("interviewExpression"))
    if expression:
        parts.append(f"**面试表达**\n\n{expression}")
    readiness = payload.get("readiness")
    advice = _items(digest.get("reviewAdvice"))
    if isinstance(readiness, dict):
        for key, label in [("status", "掌握状态"), ("skills", "已练习能力"), ("weakPoints", "待加强")]:
            values = _items(readiness.get(key))
            if values:
                parts.append(f"{label}：{'、'.join(values)}。")
        level = _text(readiness.get("interviewExpression"))
        if level:
            parts.append(f"表达熟练度：{level}。")
        advice.extend(_items(readiness.get("nextReview")))
    elif _items(readiness):
        parts.append(f"掌握状态：{'、'.join(_items(readiness))}。")
    if advice:
        parts.append("**复习建议**\n\n" + _bullets(list(dict.fromkeys(advice))))
    return "\n\n".join(parts)


def build_sections(payload: dict[str, Any]) -> list[NoteSection]:
    """Return ordered, provider-neutral Markdown/collapse sections.

    ``heading`` is an optional external level-two heading. A collapse has a
    separate ``title`` and ``collapsed=True``; its Markdown is the inner body.
    Legacy noteContent is already authored body text and must not receive a
    second generated digest. Structured transcript/variants take precedence.
    """
    title = normalize_title(payload)
    structured = "teachingTranscript" in payload or "solutionVariants" in payload
    legacy_body = _clean_markdown(payload.get("noteContent"), title=title)
    if legacy_body and not structured:
        return [{"kind": "markdown", "markdown": legacy_body}]

    sections: list[NoteSection] = []
    url = _text(payload.get("problemUrl") or payload.get("leetcodeUrl"))
    if url:
        if not re.match(r"^https?://", url) or any(char in url for char in "\r\n<>"):
            raise ValueError("题目链接必须是有效的 HTTP(S) 地址。")
        sections.append({"kind": "markdown", "markdown": f"[力扣原题](<{url}>)"})
    statement = _clean_markdown(payload.get("statementMarkdown"), title=title)
    if statement or structured:
        sections.append({"kind": "collapse", "title": "题干、示例与限制", "collapsed": True, "markdown": statement or "题干未提供，请通过原题链接查看。"})
    if structured or _text(payload.get("processMarkdown")):
        sections.append({"kind": "collapse", "title": "GPT 教学流程", "collapsed": True, "markdown": _transcript_markdown(payload.get("teachingTranscript"), payload.get("processMarkdown"))})

    variants = payload.get("solutionVariants")
    if variants is not None and not isinstance(variants, list):
        raise ValueError("solutionVariants 必须是数组。")
    if variants:
        if any(not isinstance(entry, dict) for entry in variants):
            raise ValueError("每个答案版本必须是对象。")
        if sum(entry.get("isFinal") is True for entry in variants) != 1:
            raise ValueError("答案版本必须明确标记且仅标记一个最终版本。")
        for index, variant in enumerate(variants):
            variant_title = _text(variant.get("title")) or f"解法 {index + 1}"
            parts = []
            explanation = _clean_markdown(variant.get("explanation"))
            if explanation:
                parts.append(explanation)
            complexity = []
            for key, label in [("timeComplexity", "时间复杂度"), ("spaceComplexity", "额外空间")]:
                value = _text(variant.get(key))
                if value:
                    complexity.append(f"{label}：{value}")
            if complexity:
                parts.append("；".join(complexity) + "。")
            correction = _clean_markdown(variant.get("correctionMarkdown"))
            if correction:
                parts.append(f"**勘误／更新说明**\n\n{correction}")
            parts.append(_fenced_code(variant.get("code"), variant.get("language", "java")))
            section: NoteSection
            if variant.get("isFinal") is True:
                section = {"kind": "markdown", "markdown": f"### {variant_title}（最终版本）\n\n" + "\n\n".join(parts)}
            else:
                section = {"kind": "collapse", "title": variant_title, "collapsed": True, "markdown": "\n\n".join(parts)}
            if index == 0:
                section["heading"] = "答案版本" if len(variants) > 1 else "最终题解"
            sections.append(section)
    elif _text(payload.get("solutionJava")):
        sections.append({"kind": "markdown", "heading": "最终题解", "markdown": _fenced_code(payload["solutionJava"])})

    digest = payload.get("conversationDigest")
    digest = digest if isinstance(digest, dict) else {}
    training = _training_markdown(payload, digest)
    if training:
        sections.append({"kind": "markdown", "heading": "本次训练记录", "markdown": training})
    complexity = _clean_markdown(payload.get("complexityMarkdown"))
    # A supplied complexity/boundary section is already the authored account.
    # Digest edge cases are a fallback, not another appendix to that account.
    edge_items = [] if complexity and structured else _items(digest.get("edgeCases"))
    edge_items += _items(payload.get("pitfalls"))
    edges = _bullets([item for item in dict.fromkeys(edge_items) if item not in complexity])
    complexity_body = "\n\n".join(filter(None, [complexity, edges]))
    if complexity_body:
        sections.append({"kind": "markdown", "heading": "复杂度与边界", "markdown": complexity_body})
    review = _review_markdown(payload, digest)
    if review:
        sections.append({"kind": "markdown", "heading": "面试表达与复习", "markdown": review})
    return sections


def render_markdown(payload: dict[str, Any], include_title: bool = True) -> str:
    """Render repository Markdown; HTML details is not a YuQue wire format."""
    pieces = [f"# {normalize_title(payload)}"] if include_title else []
    for section in build_sections(payload):
        if section.get("heading"):
            pieces.append(f"## {section['heading']}")
        if section["kind"] == "collapse":
            title = html.escape(section["title"], quote=True)
            pieces.append(f"<details>\n<summary>{title}</summary>\n\n{section['markdown']}\n\n</details>")
        else:
            pieces.append(section["markdown"])
    return "\n\n".join(pieces).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--without-title", action="store_true", help="Render body only for an existing marked note region.")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        parser.error("学习记录必须是 JSON 对象。")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_markdown(payload, include_title=not args.without_title), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
