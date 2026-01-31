---
name: turix-mac
description: Computer Use Agent (CUA) for macOS automation using TuriX. Use when you need to perform visual tasks on the desktop, such as opening apps, clicking buttons, or navigating UIs that don't have a CLI or API.
---

# TuriX-Mac Skill

This skill allows Clawdbot to control the macOS desktop visually using the TuriX Computer Use Agent.

## When to Use

- When asked to perform actions on the Mac desktop (e.g., "Open Spotify and play my liked songs").
- When navigating applications that lack command-line interfaces.
- For multi-step visual workflows (e.g., "Find the latest invoice in my email and upload it to the company portal").
- When you need the agent to plan, reason, and execute complex tasks autonomously.

## Key Features

### 🤖 Multi-Model Architecture
TuriX uses a sophisticated multi-model system:
- **Brain**: Understands the task and generates step-by-step plans
- **Actor**: Executes precise UI actions based on visual understanding
- **Planner**: Coordinates high-level task decomposition (when `use_plan: true`)
- **Memory**: Maintains context across task steps

### 📋 Skills System
Skills are markdown playbooks that guide the agent for specific domains:
- `github-web-actions`: GitHub navigation, repo search, starring
- `browser-tasks`: General web browser operations
- Custom skills can be added to the `skills/` directory

### 🔄 Resume Capability
The agent can resume interrupted tasks by setting a stable `agent_id`.

## Running TuriX

### Basic Task
```bash
skills/local/turix-mac/scripts/run_turix.sh "Open Chrome and go to github.com"
```

### Resume Interrupted Task
```bash
skills/local/turix-mac/scripts/run_turix.sh --resume my-task-001
```

### Tips for Effective Tasks

**✅ Good Examples:**
- "Open Safari, go to google.com, search for 'TuriX AI', and click the first result"
- "Open System Settings, click on Dark Mode, then return to System Settings"
- "Open Finder, navigate to Documents, and create a new folder named 'Project X'"

**❌ Avoid:**
- Vague instructions: "Help me" or "Fix this"
- Impossible actions: "Delete all files"
- Tasks requiring system-level permissions without warning

**💡 Best Practices:**
1. Be specific about the target application
2. Break complex tasks into clear steps, but do not mention the precise coordinates on the screen.

## Hotkeys

- **Force Stop**: `Cmd+Shift+2` - Immediately stops the agent

## Monitoring & Logs

Logs are saved to `.turix_tmp/logging.log` in the project directory. Check this for:
- Step-by-step execution details
- LLM interactions and reasoning
- Errors and recovery attempts

## Troubleshooting

### Common Issues

| Error | Solution |
|-------|----------|
| `NoneType has no attribute 'save'` | Screen recording permission missing. Grant in System Settings and restart Terminal. |
| `Screen recording access denied` | Run: `osascript -e 'tell application "Safari" to do JavaScript "alert(1)"'` and click Allow |
| `Conda environment not found` | Ensure `turix_env` exists: `conda create -n turix_env python=3.12` |
| Module import errors | Activate environment: `conda activate turix_env` then `pip install -r requirements.txt` |
| Permission errors for keyboard listener | Add Terminal/IDE to **Accessibility** permissions |

### Debug Mode

Logs include DEBUG level by default. Check:
```bash
tail -f your_dir/TuriX-CUA/.turix_tmp/logging.log
```

## Architecture

```
User Request
     ↓
[Clawdbot] → [TuriX Skill] → [run_turix.sh] → [TuriX Agent]
                                              ↓
                    ┌─────────────────────────┼─────────────────────────┐
                    ↓                         ↓                         ↓
               [Planner]                 [Brain]                  [Memory]
                    ↓                         ↓                         ↓
                                         [Actor] ───→ [Controller] ───→ [macOS UI]
```

## Skill System Details

Skills are markdown files with YAML frontmatter in the `skills/` directory:

```md
---
name: skill-name
description: When to use this skill
---
# Skill Instructions
High-level workflow like: Open Safari,then go to Google.
```

The Planner selects relevant skills based on name/description; the Brain uses full content for step guidance.

## Advanced Options

| Option | Description |
|--------|-------------|
| `use_plan: true` | Enable planning for complex tasks |
| `use_skills: true` | Enable skill selection |
| `resume: true` | Resume from previous interruption |
| `max_steps: N` | Limit total steps (default: 100) |
| `max_actions_per_step: N` | Actions per step (default: 5) |
| `force_stop_hotkey` | Custom hotkey to stop agent |

---

## TuriX Skills System

TuriX 支持 **Skills** - Markdown 格式的任务手册，让 agent 在特定领域表现更稳定。

### 1. 内置 Skills

| Skill | 用途 |
|-------|------|
| `github-web-actions` | GitHub 网页操作（搜索仓库、Star 等） |

### 2. 创建自定义 Skill

在 TuriX 项目的 `skills/` 目录下创建 `.md` 文件：

```md
---
name: my-custom-skill
description: When performing X specific task
---
# Custom Skill

## Guidelines
- Step 1: Do this first
- Step 2: Then do that
- Step 3: Verify the result
```

**字段说明：**
- `name`: Skill 标识符（Planner 用来选择）
- `description`: 何时使用这个 skill（Planner 根据描述匹配）
- 下面的内容: 完整的执行指南（Brain 读取使用）

### 3. 启用 Skills

在 `examples/config.json` 中：

```json
{
  "agent": {
    "use_plan": true,
    "use_skills": true,
    "skills_dir": "skills",
    "skills_max_chars": 4000
  }
}
```

### 4. 运行带 Skills 的任务

```bash
skills/local/turix-mac/scripts/run_turix.sh "Search for turix-cua on GitHub and star it"
```

Agent 会自动：
1. Planner 读取 skill 名称和描述
2. 选择相关的 skill
3. Brain 使用 skill 完整内容指导执行

### 5. 示例：添加新 Skill

创建 `skills/browser-tasks.md`：

```md
---
name: browser-tasks
description: When performing tasks in a web browser (search, navigate, fill forms).
---
# Browser Tasks

## Navigation
- Use the address bar or search box to navigate
- Open new tabs for each distinct task
- Wait for page to fully load before proceeding

## Forms
- Click on input fields to focus
- Type content clearly
- Look for submit/button to complete actions

## Safety
- Confirm before submitting forms
- Do not download files without user permission
```

### 6. Skill 开发建议

1. **描述要精准** - 帮助 Planner 正确选择
2. **步骤要清晰** - Brain 需要明确的执行指引
3. **包含安全检查** - 重要操作的确认步骤
4. **长度适中** - 建议不超过 4000 characters

---

## 监控与调试指南

### 1. 运行任务

```bash
# 在后台运行（推荐）
cd /Users/tonyyan/clawd/skills/local/turix-mac/scripts
./run_turix.sh "Your task description" --background

# 或使用 timeout 设置最大运行时间
./run_turix.sh "Task" &
```

### 2. 监控执行进度

**方法一：查看 session 日志**
```bash
# 列出运行中的 sessions
clawdbot sessions_list

# 查看日志
clawdbot sessions_history <session_key>
```

**方法二：查看 TuriX 日志**
```bash
# 实时查看日志
tail -f Your_dir/TuriX-CUA/.turix_tmp/logging.log

# 或检查已完成的 step 文件
ls -lt Your_dir/TuriX-CUA/examples/.turix_tmp/brain_llm_interactions.log_brain_*.txt
```

**方法三：检查进程**
```bash
ps aux | grep "python.*main.py" | grep -v grep
```

**方法四：检查生成的文件**
```bash
# 查看 agent 创建的记录文件
ls -la Your_dir/TuriX-CUA/examples/.turix_tmp/*.txt
```

### 3. 日志文件说明

| 文件 | 说明 |
|------|------|
| `logging.log` | 主日志文件 |
| `brain_llm_interactions.log_brain_N.txt` | Brain 模型对话（每个 Step 一个） |
| `actor_llm_interactions.log_actor_N.txt` | Actor 模型对话（每个 Step 一个） |

**关键日志标识：**
- `📍 Step N` - 新步骤开始
- `✅ Eval: Success/Failed` - 当前步骤评估
- `🎯 Goal to achieve this step` - 当前目标
- `🛠️  Action` - 执行的具体动作
- `✅ Task completed successfully` - 任务完成

### 4. 常见监控问题

| 问题 | 检查方法 |
|------|----------|
| 进程无响应 | `ps aux | grep main.py` |
| 卡在第一步 | 检查 `.turix_tmp/` 目录是否创建 |
| 模型加载慢 | 首次运行需要 1-2 分钟加载模型 |
| 无日志输出 | 检查 `config.json` 中的 `logging_level` |

### 5. 强制停止

**快捷键**: `Cmd+Shift+2` - 立即停止 agent

**命令停止**:
```bash
pkill -f "python examples/main.py"
```

### 6. 查看执行结果

任务完成后，agent 会：
1. 在 `.turix_tmp/` 生成交互日志
2. 记录文件（如果有 `record_info` 动作）
3. 截图保存在内存中供下一步使用

**示例：查看汇总结果**
```bash
cat your_dir/TuriX-CUA/examples/.turix_tmp/latest_ai_news_summary_jan2026.txt
```

### 7. 调试技巧

1. **检查 Brain 思考过程**: 查看 `brain_llm_interactions.log_brain_*.txt` 中的 `analysis` 和 `next_goal`
2. **检查 Actor 动作**: 查看 `actor_llm_interactions.log_actor_*.txt` 中的具体 action
3. **查看截图**: TuriX 在每个 step 会截图（保存在内存中）
4. **读取记录文件**: agent 会用 `record_info` 保存重要信息到 `.txt` 文件

### 8. 示例监控流程

```bash
# 1. 运行任务
./run_turix.sh "Search AI news and summarize" &

# 2. 等待几秒后检查进程
sleep 5 && ps aux | grep main.py

# 3. 检查是否开始生成日志
ls -la Your_dir/TuriX-CUA/examples/.turix_tmp/

# 4. 实时监控进度
tail -f Your_dir/TuriX-CUA/.turix_tmp/logging.log

# 5. 查看当前 step
ls Your_dir/TuriX-CUA/examples/.turix_tmp/brain_llm_interactions.log_brain_*.txt | wc -l
```
