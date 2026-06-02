# SiYuan Sync Validation

Use this module after writing any SiYuan learning record.

## Required Checks

Export every touched page through `/api/export/exportMdContent` and verify:

- Chinese text is readable.
- Content does not contain `????`.
- Content does not contain visible `<!-- codex-`.
- Problem page contains the problem title, thinking, solution code, complexity, readiness status, and commit hash.
- Concept and review pages contain exactly one visible problem link for the current problem.

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

