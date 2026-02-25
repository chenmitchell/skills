# Feishu File Sender

Upload a local file to Feishu OpenAPI and send it into a chat.

## Why this skill

OpenClaw agents can generate files, but they can only output a **local path**. In Feishu, users cannot see or download that file directly. This skill solves the gap by uploading the local file to Feishu and sending it as a downloadable attachment.

## 为什么需要这个 skill

OpenClaw agent 生成文件后只能输出**本地路径**，飞书端用户无法直接看到或下载该文件。本 skill 将本地文件上传到飞书并发送为可下载的附件，解决“看不到/下不了”的问题。

## Features

- 📎 Upload local files and send as Feishu file messages
- 🔑 Auto-resolve appId/appSecret from OpenClaw config
- 🧭 Works across **all agents** based on workspace
- 🧰 Simple CLI for quick use

## Requirements

- Python 3.6+
- `requests` installed
- OpenClaw with Feishu channel configured

## Install

```bash
python3 -m pip install requests
```

## Usage

### Send to current chat (recommended)

```bash
# If your runtime provides the chat id via environment
export OPENCLAW_CHAT_ID=oc_xxx

python3 scripts/feishu_file_sender.py \
  --file /absolute/path/to/report.xlsx
```

### Send to a specific chat

```bash
python3 scripts/feishu_file_sender.py \
  --file /absolute/path/to/report.xlsx \
  --receive-id oc_xxx \
  --receive-id-type chat_id
```

### Send to a user

```bash
python3 scripts/feishu_file_sender.py \
  --file /absolute/path/to/report.xlsx \
  --receive-id ou_xxx \
  --receive-id-type open_id
```

## How It Works

1. Resolve current agent id by matching `cwd` to the configured workspace.
2. Read Feishu `appId/appSecret` from `~/.openclaw/openclaw.json` via bindings.
3. Upload the file to Feishu (`im/v1/files`) and get `file_key`.
4. Send a file message (`im/v1/messages`) to the target chat/user.

## Error Handling

| Issue | Cause | Fix |
|------|------|-----|
| `Missing receive_id` | No `--receive-id` and no env | Set `OPENCLAW_CHAT_ID` or pass `--receive-id` |
| `No Feishu account binding` | Agent binding missing | Ensure bindings map agentId → accountId in OpenClaw config |
| `Bot/User can NOT be out of the chat (230002)` | Bot not in chat | Add the bot to the chat or send to a different chat |
| `HTTPError` | API failure | Check response `log_id` and Feishu troubleshooting link |

## Configuration

OpenClaw should already have Feishu accounts configured in `~/.openclaw/openclaw.json`.
This skill only **reads** config; it does not modify any files.

## Security

This skill reads Feishu credentials from your local OpenClaw config
(`~/.openclaw/openclaw.json`):

- `channels.feishu.accounts.*.appId`
- `channels.feishu.accounts.*.appSecret`

These values are used only to obtain a tenant access token and send the file.
The skill does not store or transmit credentials anywhere else.

## License

MIT

---

# 飞书文件发送器

将本地文件上传到飞书 OpenAPI 并发送到聊天中。

## 功能亮点

- 📎 上传本地文件并发送为飞书文件消息
- 🔑 自动从 OpenClaw 配置读取 appId/appSecret
- 🧭 基于工作区对 **所有 agent** 通用
- 🧰 简洁的命令行工具，方便快速使用

## 运行要求

- Python 3.6+
- 已安装 `requests`
- OpenClaw 已配置飞书渠道

## 安装

```bash
python3 -m pip install requests
```

## 用法

### 发送到当前聊天（推荐）

```bash
# 如果运行环境通过环境变量提供 chat id
export OPENCLAW_CHAT_ID=oc_xxx

python3 scripts/feishu_file_sender.py \
  --file /absolute/path/to/report.xlsx
```

### 发送到指定聊天

```bash
python3 scripts/feishu_file_sender.py \
  --file /absolute/path/to/report.xlsx \
  --receive-id oc_xxx \
  --receive-id-type chat_id
```

### 发送给指定用户

```bash
python3 scripts/feishu_file_sender.py \
  --file /absolute/path/to/report.xlsx \
  --receive-id ou_xxx \
  --receive-id-type open_id
```

## 工作原理

1. 通过 `cwd` 匹配配置的工作区，解析当前 agent id。
2. 通过绑定关系从 `~/.openclaw/openclaw.json` 读取 Feishu `appId/appSecret`。
3. 上传文件到飞书（`im/v1/files`），获取 `file_key`。
4. 调用消息发送接口（`im/v1/messages`）发送到目标聊天/用户。

## 常见错误处理

| 问题 | 原因 | 解决办法 |
|------|------|---------|
| `Missing receive_id` | 未传 `--receive-id` 且无环境变量 | 设置 `OPENCLAW_CHAT_ID` 或传入 `--receive-id` |
| `No Feishu account binding` | 缺少 agent 绑定 | 确保 OpenClaw 配置中 agentId → accountId 绑定存在 |
| `Bot/User can NOT be out of the chat (230002)` | 机器人不在群内 | 将机器人加入群或发送到其他群 |
| `HTTPError` | API 调用失败 | 查看响应中的 `log_id` 与飞书排障链接 |

## 配置说明

OpenClaw 应已在 `~/.openclaw/openclaw.json` 中配置飞书账号。
本技能只**读取**配置，不会修改任何文件。

## 安全说明

本技能会从本机 OpenClaw 配置中读取飞书凭证
（`~/.openclaw/openclaw.json`）：

- `channels.feishu.accounts.*.appId`
- `channels.feishu.accounts.*.appSecret`

这些凭证仅用于获取 tenant access token 并发送文件。
技能不会存储或向其他地方传输凭证。

## 许可证

MIT
