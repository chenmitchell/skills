---
name: feishu-file-sender
description: OpenClaw agents can generate files (Excel, Word, PPT, PDF, images, code, etc.) but cannot send them directly to Feishu chat — they can only output a local file path. This skill bridges that gap: it uploads any local file to Feishu via OpenAPI and sends it as a downloadable attachment in the current chat. Works for all agents by auto-detecting credentials from openclaw.json. Supports any file format.
license: MIT
compatibility: openclaw
metadata:
  version: "1.0.4"
  tags: [feishu, file, upload, im, messaging, openapi]
  author: wen-ai
  openclaw:
    emoji: "📎"
    requires:
      bins: [python3]
      config:
        - ~/.openclaw/openclaw.json
---

# Feishu File Sender

Upload a local file to Feishu and send it as a file message.

## Quick Start

```bash
python3 scripts/feishu_file_sender.py \
  --file /absolute/path/to/report.xlsx \
  --receive-id oc_xxx
```

## Usage

```bash
python3 scripts/feishu_file_sender.py \
  --file /absolute/path/to/file \
  --receive-id <chat_id|open_id> \
  --receive-id-type <chat_id|open_id|user_id>
```

### Arguments

- `--file` (required): Absolute path to the local file.
- `--receive-id` (optional): Target chat_id or open_id. If omitted, the script
  reads `OPENCLAW_CHAT_ID` (or `OPENCLAW_RECEIVE_ID` / `FEISHU_CHAT_ID`).
- `--receive-id-type` (optional): If omitted, auto-detect by prefix:
  - `oc_` → chat_id
  - `ou_` → open_id
  - `on_` → user_id
- `--file-type` (optional): Feishu file upload type, default `stream`.

## How It Works

1. Resolve the current agent id by matching `cwd` to OpenClaw workspace path.
2. Read appId/appSecret from `~/.openclaw/openclaw.json` based on the agent id.
3. Call Feishu **Upload File** API to get `file_key`.
4. Call Feishu **Send Message** API to deliver the file.

## Error Handling

- **Missing credentials** → Ensure `channels.feishu.accounts` exists in
  `~/.openclaw/openclaw.json` and bindings map agentId → accountId.
- **Bot not in chat (code 230002)** → Add the bot to the target chat or use a
  chat where the bot is present.
- **Missing receive_id** → Pass `--receive-id` or set `OPENCLAW_CHAT_ID`.
- **HTTP errors** → Check the returned `log_id` in Feishu error payload.

## Security

This skill reads Feishu credentials from the local OpenClaw config
(`~/.openclaw/openclaw.json`) on the machine where it runs:

- `channels.feishu.accounts.*.appId`
- `channels.feishu.accounts.*.appSecret`

These values are used only to obtain a tenant access token and send the file.
The skill does not store or transmit credentials anywhere else.

## Notes

- This skill is designed for **all agents**; it reads the active workspace to
  choose the correct Feishu app credentials automatically.
- Prefer sending to the **current chat** by passing the inbound `chat_id`.

## Bundled Script

- `scripts/feishu_file_sender.py`

---

# 飞书文件发送器

将本地文件上传到飞书并作为文件消息发送。

## 快速开始

```bash
python3 scripts/feishu_file_sender.py \
  --file /absolute/path/to/report.xlsx \
  --receive-id oc_xxx
```

## 使用方法

```bash
python3 scripts/feishu_file_sender.py \
  --file /absolute/path/to/file \
  --receive-id <chat_id|open_id> \
  --receive-id-type <chat_id|open_id|user_id>
```

### 参数说明

- `--file`（必填）：本地文件绝对路径。
- `--receive-id`（可选）：目标 chat_id 或 open_id。若省略，脚本会读取
  `OPENCLAW_CHAT_ID`（或 `OPENCLAW_RECEIVE_ID` / `FEISHU_CHAT_ID`）。
- `--receive-id-type`（可选）：若省略，将根据前缀自动识别：
  - `oc_` → chat_id
  - `ou_` → open_id
  - `on_` → user_id
- `--file-type`（可选）：飞书上传的文件类型，默认 `stream`。

## 工作原理

1. 通过 `cwd` 匹配 OpenClaw 工作区，解析当前 agent id。
2. 根据 agent id 从 `~/.openclaw/openclaw.json` 读取 appId/appSecret。
3. 调用飞书 **上传文件** API 获取 `file_key`。
4. 调用飞书 **发送消息** API 发送文件。

## 错误处理

- **缺少凭证** → 确保 `~/.openclaw/openclaw.json` 中存在
  `channels.feishu.accounts`，且 bindings 映射 agentId → accountId。
- **机器人不在群内（230002）** → 将机器人加入目标群或换一个群。
- **缺少 receive_id** → 传入 `--receive-id` 或设置 `OPENCLAW_CHAT_ID`。
- **HTTP 错误** → 查看飞书错误返回中的 `log_id` 进行排查。

## 安全说明

本技能会从本机 OpenClaw 配置中读取飞书凭证
（`~/.openclaw/openclaw.json`）：

- `channels.feishu.accounts.*.appId`
- `channels.feishu.accounts.*.appSecret`

这些凭证仅用于获取 tenant access token 并发送文件。
技能不会存储或向其他地方传输凭证。

## 备注

- 本技能面向 **所有 agent** 设计，会自动读取当前工作区来选择正确的
  飞书应用凭证。
- 建议通过入站 `chat_id` 发送到 **当前聊天**。

## 随附脚本

- `scripts/feishu_file_sender.py`
