#!/usr/bin/env python3
"""Pure learning-record -> YuQue Lake adapter, with semantic read-back checks.

Native storage was checked against the user's read-only E70 reference through
the official get-document API: Lake uses ``details.lake-collapse`` with an
explicit ``open=\"false\"``, and URI-encoded JSON ``codeblock`` cards. This is
not a claim that posting repository Markdown <details> creates native folds.
The publisher must use format=lake and verify the returned body_lake.

Supported authored Markdown: paragraphs, headings, blockquotes, fenced code,
simple/nested lists, tables, links, emphasis, inline code, and horizontal rules.
Raw HTML is escaped rather than interpreted. No network or upload logic here.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from html import escape, unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import quote, unquote, urlsplit

from render_learning_note import build_sections


LAKE_HEADER = ('<!doctype lake><meta name="doc-version" content="1" />'
               '<meta name="viewport" content="fixed" />'
               '<meta name="typography" content="classic" />'
               '<meta name="paragraphSpacing" content="relax" />')
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)$")
_HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
_LIST = re.compile(r"^( *)([-+*]|\d+[.)])\s+(.*)$")


class LakeRenderer:
    def __init__(self) -> None:
        self.sequence = 0

    def identifier(self) -> str:
        self.sequence += 1
        return f"u{self.sequence:08x}"

    def element(self, tag: str, body: str, **attrs: str) -> str:
        identifier = self.identifier()
        attributes = {"data-lake-id": identifier, "id": identifier, **attrs}
        encoded = "".join(f' {key}="{escape(value, quote=True)}"' for key, value in attributes.items())
        return f"<{tag}{encoded}>{body}</{tag}>"

    def text(self, value: str) -> str:
        return self.element("span", escape(value, quote=False)) if value else ""

    @staticmethod
    def _closing(value: str, start: int, opening: str, closing: str) -> int:
        depth = 1
        index = start
        while index < len(value):
            if value[index] == "\\":
                index += 2
                continue
            if value[index] == opening:
                depth += 1
            elif value[index] == closing:
                depth -= 1
                if depth == 0:
                    return index
            index += 1
        return -1

    def inline(self, value: str) -> str:
        result: list[str] = []
        plain: list[str] = []

        def flush() -> None:
            if plain:
                result.append(self.text("".join(plain)))
                plain.clear()

        index = 0
        while index < len(value):
            char = value[index]
            if char == "\\" and index + 1 < len(value) and value[index + 1] in r"\`*{}[]()#+-.!_>|":
                plain.append(value[index + 1])
                index += 2
                continue
            if char == "`":
                run = len(re.match(r"`+", value[index:]).group())
                end = value.find("`" * run, index + run)
                if end >= 0:
                    flush()
                    content = value[index + run:end].replace("\n", " ")
                    if content.startswith(" ") and content.endswith(" ") and content.strip():
                        content = content[1:-1]
                    result.append(self.element("code", self.text(content)))
                    index = end + run
                    continue
            if char == "[":
                label_end = self._closing(value, index + 1, "[", "]")
                if label_end >= 0 and value[label_end + 1:label_end + 2] == "(":
                    url_end = self._closing(value, label_end + 2, "(", ")")
                    if url_end >= 0:
                        target = value[label_end + 2:url_end].strip()
                        if target.startswith("<") and target.endswith(">"):
                            target = target[1:-1]
                        # Reject active schemes. Ordinary text remains visible.
                        if urlsplit(target).scheme.lower() in {"http", "https", "mailto", ""}:
                            flush()
                            result.append(self.element("a", self.inline(value[index + 1:label_end]), href=target))
                            index = url_end + 1
                            continue
            token = next((item for item in ("**", "__", "~~", "*", "_") if value.startswith(item, index)), "")
            if token:
                end = value.find(token, index + len(token))
                # Underscores within identifiers are ordinary characters.
                inside_word = token == "_" and index > 0 and value[index - 1].isalnum()
                if end > index + len(token) and not inside_word:
                    flush()
                    tag = "strong" if len(token) == 2 and token != "~~" else "s" if token == "~~" else "em"
                    result.append(self.element(tag, self.inline(value[index + len(token):end])))
                    index = end + len(token)
                    continue
            if char == "\n":
                flush()
                result.append("<br />")
            else:
                plain.append(char)
            index += 1
        flush()
        return "".join(result)

    def code(self, code: str, language: str) -> str:
        card = {
            "mode": language or "text", "code": code, "autoWrap": False,
            "lineNumbers": True, "heightLimit": False, "collapsed": False,
            "hideToolbar": False, "name": "", "tabSize": 4,
            "indentWithTab": False, "lightLines": [], "foldLines": [],
            "theme": "Github Light", "fontSize": 14, "customStyle": [],
            "__spacing": "both", "id": self.identifier(),
            "margin": {"top": True, "bottom": True},
        }
        encoded = quote(json.dumps(card, ensure_ascii=False, separators=(",", ":")), safe="")
        return f'<card type="inline" name="codeblock" value="data:{encoded}"></card>'

    @staticmethod
    def _table_row(line: str) -> list[str]:
        return [part.strip().replace(r"\|", "|") for part in re.split(r"(?<!\\)\|", line.strip().strip("|"))]

    @classmethod
    def _table_separator(cls, line: str) -> bool:
        cells = cls._table_row(line)
        return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)

    @staticmethod
    def _special(line: str) -> bool:
        return bool(_FENCE.match(line) or _HEADING.match(line) or _LIST.match(line)
                    or re.match(r"^ {0,3}>", line) or re.fullmatch(r"\s*(?:---+|\*\*\*+|___+)\s*", line))

    def markdown(self, source: str) -> str:
        lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        parts: list[str] = []
        index = 0
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
                continue
            fence = _FENCE.match(line)
            if fence:
                token, info = fence.groups()
                language = info.strip().split()[0] if info.strip() else "text"
                code_lines: list[str] = []
                index += 1
                while index < len(lines):
                    closing = _FENCE.match(lines[index])
                    if closing and closing.group(1)[0] == token[0] and len(closing.group(1)) >= len(token) and not closing.group(2).strip():
                        index += 1
                        break
                    code_lines.append(lines[index])
                    index += 1
                parts.append(self.code("\n".join(code_lines), language))
                continue
            heading = _HEADING.match(line)
            if heading:
                parts.append(self.element(f"h{len(heading.group(1))}", self.inline(heading.group(2))))
                index += 1
                continue
            if re.match(r"^ {0,3}>", line):
                quoted: list[str] = []
                while index < len(lines) and re.match(r"^ {0,3}>", lines[index]):
                    quoted.append(re.sub(r"^ {0,3}> ?", "", lines[index], count=1))
                    index += 1
                parts.append(self.element("blockquote", self.markdown("\n".join(quoted))))
                continue
            item = _LIST.match(line)
            if item:
                indent = len(item.group(1))
                ordered = item.group(2)[0].isdigit()
                items: list[str] = []
                while index < len(lines):
                    match = _LIST.match(lines[index])
                    if not match or len(match.group(1)) != indent or match.group(2)[0].isdigit() != ordered:
                        break
                    content = [match.group(3)]
                    content_indent = len(match.group(1)) + len(match.group(2)) + 1
                    index += 1
                    while index < len(lines):
                        following = lines[index]
                        if following.strip() and len(following) - len(following.lstrip()) > indent:
                            content.append(following[min(content_indent, len(following) - len(following.lstrip())):])
                            index += 1
                        elif not following.strip() and index + 1 < len(lines) and len(lines[index + 1]) - len(lines[index + 1].lstrip()) > indent:
                            content.append("")
                            index += 1
                        else:
                            break
                    items.append(self.element("li", self.markdown("\n".join(content))))
                parts.append(self.element("ol" if ordered else "ul", "".join(items)))
                continue
            if index + 1 < len(lines) and "|" in line and self._table_separator(lines[index + 1]):
                rows = [self._table_row(line)]
                index += 2
                while index < len(lines) and "|" in lines[index] and lines[index].strip():
                    rows.append(self._table_row(lines[index]))
                    index += 1
                content = "".join(self.element("tr", "".join(self.element("th" if row_index == 0 else "td", self.element("p", self.inline(cell))) for cell in row)) for row_index, row in enumerate(rows))
                parts.append(self.element("table", self.element("tbody", content)))
                continue
            if re.fullmatch(r"\s*(?:---+|\*\*\*+|___+)\s*", line):
                parts.append("<hr />")
                index += 1
                continue
            paragraph = [line]
            index += 1
            while index < len(lines) and lines[index].strip() and not self._special(lines[index]):
                if index + 1 < len(lines) and "|" in lines[index] and self._table_separator(lines[index + 1]):
                    break
                paragraph.append(lines[index])
                index += 1
            parts.append(self.element("p", self.inline("\n".join(paragraph))))
        return "".join(parts)


def render_lake(payload: dict[str, Any]) -> str:
    renderer = LakeRenderer()
    parts = [LAKE_HEADER]
    for section in build_sections(payload):
        if section.get("heading"):
            parts.append(renderer.element("h2", renderer.inline(section["heading"])))
        content = renderer.markdown(section["markdown"])
        if section["kind"] == "collapse":
            summary = renderer.element("summary", renderer.inline(section["title"]), **{"class": "lake-summary"})
            content = renderer.element("details", summary + content, **{
                "class": "lake-collapse", "open": "false" if section.get("collapsed", True) else "true",
            })
        parts.append(content)
    return "".join(parts)


@dataclass
class _Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)


class _LakeParser(HTMLParser):
    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("root")
        self.stack = [self.root]
        self.feed(source)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = _Node(tag, {key: value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if tag not in {"meta", "br", "hr", "img", "input", "link", "wbr"}:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def _walk(node: _Node):
    yield node
    for child in node.children:
        if isinstance(child, _Node):
            yield from _walk(child)


def _node_text(node: _Node) -> str:
    if node.tag in {"br", "hr"}:
        return "\n"
    content = "".join(child if isinstance(child, str) else _node_text(child) for child in node.children)
    return content + ("\n" if node.tag in {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "summary", "td", "th"} else "")


def _canonical(value: str) -> str:
    return re.sub(r"\s+", "", value.replace("\u200b", "").replace("\ufeff", ""))


def inspect_lake(source: str) -> dict[str, Any]:
    """Semantic fingerprint; IDs/style rewrites do not invalidate read-back."""
    parsed = _LakeParser(source)
    nodes = list(_walk(parsed.root))
    result: dict[str, Any] = {"text": _canonical(_node_text(parsed.root)), "codes": [], "collapses": [], "headings": [], "links": [], "quotes": 0, "bold": []}
    for node in nodes:
        if node.tag == "card":
            try:
                value = node.attrs.get("value", "")
                data = json.loads(unquote(value[5:] if value.startswith("data:") else value))
            except (ValueError, TypeError):
                continue
            if node.attrs.get("name") == "codeblock":
                result["codes"].append((data.get("mode", "text"), data.get("code", "")))
            elif node.attrs.get("name") == "bookmarkInline":
                result["links"].append((data.get("src", ""), _canonical(data.get("text", ""))))
        elif node.tag == "details":
            summary = next((child for child in node.children if isinstance(child, _Node) and child.tag == "summary"), None)
            native = "lake-collapse" in node.attrs.get("class", "").split()
            result["collapses"].append((_canonical(_node_text(summary)) if summary else "", node.attrs.get("open") == "false", native))
        elif node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            result["headings"].append((node.tag, _canonical(_node_text(node))))
        elif node.tag == "a":
            result["links"].append((unescape(node.attrs.get("href", "")), _canonical(_node_text(node))))
        elif node.tag == "blockquote":
            result["quotes"] += 1
        elif node.tag in {"b", "strong"} or re.search(r"font-weight\s*:\s*(?:bold|[7-9]00)", node.attrs.get("style", "")):
            result["bold"].append(_canonical(_node_text(node)))
    return result


def verify_lake(expected_body: str, actual_doc: dict[str, Any]) -> list[str]:
    """Return actionable errors, not success based only on an API write receipt."""
    body = actual_doc.get("body_lake")
    if not isinstance(body, str) or not body.strip():
        body = actual_doc.get("body") if actual_doc.get("format") == "lake" else None
    if not isinstance(body, str) or not body.strip():
        return ["回读未返回 Lake 正文，不能确认原生排版。"]
    expected, actual = inspect_lake(expected_body), inspect_lake(body)
    checks = [
        (expected["text"] == actual["text"], "回读正文与预览的文字或顺序不一致。"),
        (expected["codes"] == actual["codes"], "回读代码块的语言、字符、注释或顺序不一致。"),
        (expected["collapses"] == actual["collapses"], "回读原生折叠的标题、数量或默认收起状态不一致。"),
        (expected["headings"] == actual["headings"], "回读标题层级或顺序不一致。"),
        (expected["links"] == actual["links"], "回读链接地址或文字不一致。"),
        (actual["quotes"] >= expected["quotes"], "回读引用样式缺失。"),
        (expected["bold"] == actual["bold"], "回读加粗内容不一致。"),
    ]
    return [message for passed, message in checks if not passed]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        parser.error("学习记录必须是 JSON 对象。")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_lake(payload), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
