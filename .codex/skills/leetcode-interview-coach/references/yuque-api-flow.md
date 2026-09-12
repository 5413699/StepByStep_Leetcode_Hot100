# 语雀直接发布流程

语雀发布使用官方 Open API v2，PAT 从当前进程的 `YuQue` 用户环境变量读取；Windows 下若进程尚未继承新设置，会回退读取 `HKCU\Environment`。token 只用于请求头 `X-Auth-Token`，不会写入配置或日志。

首次配置读取 `/user`、`/users/{login}/repos`（客户端也兼容 `/repos`）和目标知识库 `/toc`，由用户选择知识库 owner namespace、repo slug 和父目录；配置只保存这些标识，不创建远程内容。

先阅读 `note-template.md`。每题稳定 slug 为 `leetcode-<数字题号>`，先整数标准化再拼接：`E070` 与 `70` 都得到 `leetcode-70`。标题如 `E70-爬楼梯`，语雀正文不再重复标题。按稳定 slug 分页查询；**绝不按相似或相同标题选择文档**。重排已有文档优先用 `--target-doc-id` 固定数字 ID，且同时核对 slug；`--require-existing` 禁止找不到时另建副本。

## 正文与原生排版

- 新 `teachingTranscript` / `solutionVariants` payload：共享 `render_learning_note.build_sections()`，经独立 `render_yuque_lake.render_lake()` 输出 `format=lake`。源是主代理提取的真实学习记录，渲染器不总结聊天。
- 原生结构依据用户参考稿实际 Open API `body_lake` 核对：`<!doctype lake>`、`<details class="lake-collapse" open="false">`、`<summary class="lake-summary">`，代码为 URI 编码 JSON 的 `codeblock` 卡片。代码卡片的 `name` 填入具体用途或解法名称，回读时一并核验，避免编辑器显示空白“请输入代码块名称”。引用、代码、链接、加粗分别渲染，代码字符与原注释不改写。
- 引用讲解中的代码卡片必须与引用段平级，按「引用讲解 → 独立代码卡片 → 后续引用讲解」输出。语雀阅读器会把嵌在引用内的卡片移到整段引用之后；raw Lake 回读不一定反映这种重排。浏览器验收需展开教学流程，核对示例／代码与前后讲解的实际位置。
- 纯文本代码块的源 Markdown 保留 `text`，Lake 卡片适配为 `plain`，不要把 `text` 原样传入后误显示 LaTeX。该映射已在 E118 语雀阅读器中实测为 Plain Text；同结构编辑器亦有 [Plain Text 模式定义](https://cdn.jsdelivr.net/npm/@aomao/plugin-codeblock@2.10.1/src/component/mode.ts)。这是实现与实测依据，不是语雀官方格式保证。
- 仓库 Markdown 的 `<details>` 只是可读表示，不能作为普通 Markdown 直接上传并宣称原生折叠完成。旧 payload 保持可读兼容；无法可靠转换的旧 HTML 折叠应先改为结构化素材，不静默降级。
- [官方格式接口说明](https://github.com/yuque/yuque-mcp-server/blob/main/docs/capability-scope.md)：Lake/html 使用 legacy `/repos/{owner}/{repo}/docs/{id}`；Markdown 的 YMD 读取使用 `/yfm/docs?doc_id=<数字 ID>`。Lake 备份及排版验证必须取 raw `body_lake`，不能拿导出的 Markdown 当完整恢复依据。

## 发布及恢复

1. 生成本地 Markdown 和 Lake 预览，校核真实对话、原注释、各有效版本及勘误。新旧 payload 都应通过渲染测试。
2. `--dry-run` 只进行文档／目录读取，展示精确目标、操作和预览，不发送 POST/PUT，也不生成远端内容。
3. 写入前读取完整文档、格式、raw Lake 和知识库 TOC，以唯一文件名保存到默认 `~/.codex/yuque-backups`（或 `--backup-dir`）。备份缺少关键正文则不写；不覆盖已有恢复文件。恢复时只针对该文档 ID 使用所备份格式及正文，恢复不是自动重试行为。
4. 执行一次 create/update。现有文档按 ID 更新，URL 保持稳定；当前目录正确则保留。目录以 `/toc` 回读为准，不能凭写接口中的 `parent_uuid` 就认定已归档。无目录项且明确指定父目录时可 `appendNode`；已存在于别处则报告未验证，不猜测移动其他节点。
5. 独立记录 `writeStatus`、`directoryWriteStatus`、`directoryStatus`、`verificationStatus`；可用 `--output-json <path>` 保留结果。HTTP 写入成功仅表示“已写入”；`verificationStatus=verified` 仅表示 API 回读核验通过，报告中仍需另外标明浏览器交互实测。必须重新读取完整正文核对代码、注释、顺序、折叠、标题和链接，并在浏览器实际展开／收起，才可报告原生排版全部验收。

GET 遇 429 最多重试 2 次，遵守 `Retry-After`（秒或 HTTP 日期）；单次等待大于 30 秒时返回建议等待时间，不提前重试。POST/PUT 不自动重试。写入响应不确定或回读失败时保留文档 ID、payload 和备份；先只读核验，**不能因为读取失败再次创建**。

本次 E70 的授权目标固定为 `dcczf/fbtgtc` 的 `leetcode-70`（ID `284587283`），父目录“待整理产出”；参考稿 `mtunxpclg9lt77rt` 保持原样。未来题目按各自题号与实际配置定位，不沿用本题 ID。
