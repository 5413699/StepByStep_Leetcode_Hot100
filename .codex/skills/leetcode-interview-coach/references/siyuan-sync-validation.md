# SiYuan Sync Validation

Use this module after writing any SiYuan learning record.

## Required Checks

Validate every touched user-facing page through `/api/block/getBlockKramdown`, strip SiYuan Kramdown attributes, and verify:

- Chinese text is readable.
- Content does not contain `????`.
- Content does not contain the Unicode replacement character `U+FFFD`.
- Metadata used to create pages does not contain ASCII `?`, Unicode replacement characters, or visible mojibake detected by the sync script. This check must run before creating/updating SiYuan pages.
- Content does not contain visible `<!-- codex-`.
- Content does not contain leaked `title:`, `date:`, or `lastmod:` metadata.
- Content does not contain exported footnote references such as `[^1]`.
- Content does not contain literal HTML link source such as `<a href=`.
- User-facing pages do not contain `来源索引`, `迁移记录`, `旧笔记内容`, `迁移补充`, or raw source HPaths.
- Problem page contains the problem title, thinking, solution code, complexity, readiness status, and commit hash.
- If a current-problem conversation digest was provided, the problem page contains its first reaction, stuck points or breakthrough, and interview/review content in the proper sections.
- Concept and review pages contain exactly one visible problem link for the current problem.
- Every touched category page contains the current sync's concept names for that category.
- The knowledge home page contains the current sync's touched category names and concept names.
- The root home page, problem index page, and expression home page contain the current problem title.
- Concept pages contain `## 来自题目的理解` when digest concept updates are provided.
- Home pages and category pages are not blank and contain useful entry links or section descriptions.
- Review home page does not list empty/generic review labels. Empty review label pages should not exist.
- Audit log entries are newest-first and older than 7 days are pruned.

`/api/export/exportMdContent` may serialize native SiYuan block references as `[^1]` footnote-style Markdown and may include child document content. Do not use it as a write-back or validation source for user-facing pages. If `[^1]` appears in current-block Markdown, treat it as leaked export pollution.

`/api/block/getBlockKramdown` includes SiYuan Kramdown block attributes like `{: id="..." updated="..."}`. Strip those attributes before judging visible content length or presenting a preview to the user.

## Failure Policy

- If validation fails before Git commit, stop.
- If validation fails after Git commit, do not roll back Git.
- Keep outgoing Markdown and sync payload files with ASCII paths.
- Report the failed block id, check name, and a short exported-content preview.

## Encoding Rule

All SiYuan body writes must use Python UTF-8 HTTP requests:

```python
json.dumps(payload, ensure_ascii=False).encode("utf-8")
```

PowerShell may launch scripts and pass ASCII paths, but it must not construct Chinese page bodies.
