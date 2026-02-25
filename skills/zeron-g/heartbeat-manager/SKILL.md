# Heartbeat Manager

> EVA Agent 心跳管理系统 — 自动化任务监控、智能超时分析、健康度评分与邮件告警

## Quick Start

### 1. 安装依赖

```bash
pip install pyyaml jinja2 python-dotenv
```

### 2. 配置邮件

```bash
cp config/.env.example config/.env
# 编辑 config/.env，填入 Gmail App Password
```

### 3. 运行心跳

```bash
# 执行一次心跳
python tools/heartbeat_run.py beat

# 查看状态
python tools/heartbeat_run.py status
```

### 4. 配置定时任务（可选）

```bash
# 编辑 crontab
crontab -e

# 添加以下内容：
# 每30分钟心跳
*/30 * * * * cd /path/to/heartbeat-manager && python tools/heartbeat_run.py beat >> logs/cron.log 2>&1
# 每天0点重置+日报
0 0 * * * cd /path/to/heartbeat-manager && python tools/heartbeat_run.py reset >> logs/cron.log 2>&1
# 每周日23:59周报
59 23 * * 0 cd /path/to/heartbeat-manager && python tools/heartbeat_run.py weekly >> logs/cron.log 2>&1
```

## 功能概览

### 心跳检查 (`beat`)

每次心跳执行以下步骤：

1. **检查 daily.md** — 例行任务完成情况
2. **检查 todo.md** — 待办事项 + `@due:HH:MM` 超期检测
3. **检查 ongoing.json** — 任务状态机 + 智能超时分析
4. **检查邮件** — IMAP 未读/标记/高优先级
5. **计算健康度** — 0-100 分综合评分
6. **更新 MASTER.md** — token 极简主控表
7. **Git 同步** — 自动 commit + push
8. **结果判定** — 全绿 → `HEARTBEAT_OK`；有问题 → 邮件告警

### 智能超时分析

基于 `ongoing.json` 中的 `history` 字段：

- **正常推进但慢**（progress 在增加）→ 仅记录，不告警
- **完全卡死**（N 个心跳无 progress/context 变化）→ 标记 BLOCK + 邮件告警

### 每日重置 (`reset`)

每天 00:00 执行：
- 发送昨日完成回顾邮件（日报）
- 重置 daily.md
- 清理已完成的 ongoing 任务

### 周报 (`weekly`)

每周日 23:59：
- 汇总本周健康度趋势
- 任务完成/阻塞统计
- 亮点与关注点

### 健康度评分

| 维度 | 分值 | 说明 |
|------|------|------|
| Daily 完成率 | 25分 | 例行任务完成比例 |
| Todo 完成率 | 20分 | 待办完成比例，超期扣分 |
| Ongoing 状态 | 25分 | BLOCK/超期扣分，完成加分 |
| 邮件状态 | 15分 | 未读过多扣分 |
| Git 同步 | 15分 | push 成功满分 |

连续 3 次低于 60 分触发告警。

## OpenClaw 集成

在 `HEARTBEAT.md` 中调用：

```
heartbeat_run.py beat
```

OpenClaw 内置心跳会自动同步调用此 skill。

## 文件结构

```
heartbeat-manager/
├── SKILL.md              # 本文件
├── _meta.json            # skill 元数据
├── config/
│   ├── settings.yaml     # 配置项
│   └── .env              # 邮件密码（不纳入版本控制）
├── workspace/
│   ├── MASTER.md         # 主控表（自动更新）
│   ├── daily.md          # 例行任务（每日重置）
│   ├── todo.md           # 待办事项（完成即删）
│   ├── ongoing.json      # 任务状态机
│   └── state.json        # 持久化状态
├── templates/
│   ├── daily_template.md # daily.md 重置模板
│   └── email_review.j2   # 日报邮件模板
├── tools/
│   ├── heartbeat_run.py  # 主入口
│   ├── checker.py        # 检查逻辑
│   ├── mail.py           # 邮件收发
│   ├── task_analyzer.py  # 智能超时分析
│   ├── git_ops.py        # Git 同步
│   ├── daily_reset.py    # 每日重置
│   ├── weekly_report.py  # 周报生成
│   ├── health_score.py   # 健康度评分
│   └── renderer.py       # MASTER.md 渲染
└── logs/                 # 日志（按日轮转，保留7天）
```

## 状态机

```
ongoing.json 任务状态流转：

IDLE → WIP → DONE
       WIP → WAIT → WIP
       WIP → BLOCK（智能检测卡死）
       ANY → DROP
```

## 配置说明

编辑 `config/settings.yaml` 可调整：

- 心跳间隔、邮件配置、高优先级发件人
- 超时分析参数（宽限时间、卡死心跳数、进度阈值）
- 健康度告警阈值和连续次数
- Git 自动提交/推送开关
- 日志级别和保留天数

## 邮件配置

使用 Gmail SMTP/IMAP，需要开启"应用专用密码"：

1. 访问 Google Account → Security → 2-Step Verification → App passwords
2. 生成一个 App Password
3. 填入 `config/.env` 的 `EMAIL_APP_PASSWORD`

## 异常处理

- **单步失败不阻断**：任何一步检查失败会降级继续，不会中断整个心跳
- **网络不通**：告警加入 pending 队列，下次心跳重试
- **原子写入**：所有文件更新使用 tmp + rename，防止写入中断导致数据损坏
- **文件锁**：防止并发执行冲突
- **日志轮转**：按日轮转，保留最近 7 天

## 许可

MIT License
