---
name: fanfic-writer
version: 2.0.0
description: 自动化小说写作助手 v2.0 - 基于证据的状态管理、多视角QC、原子I/O、自动救援/中止安全机制
homepage: https://github.com/openclaw/clawd
metadata:
  openclaw:
    emoji: "📖"
    category: "creative"
---
# Fanfic Writer v2.0 - 自动化小说写作系统 / Automated Novel Writing System

**版本 Version**: 2.0.0  
**架构 Architecture**: 基于证据的状态管理 with atomic I/O  
**安全机制 Safety**: Auto-Rescue, Auto-Abort Guardrail, FORCED 连击熔断

---

## 系统概览 / System Overview

Fanfic Writer v2.0 是一套生产级的小说写作流水线：

/ Fanfic Writer v2.0 is a production-grade novel writing pipeline:

- **9 阶段流水线 / 9 Phase Pipeline**: 从初始化到最终QC
- **7 状态面板 / 7 State Panels**: 角色、剧情线、时间线、道具、地点、POV规则、会话记忆
- **证据链 / Evidence Chain**: 所有状态变更带有 (章节, 片段, 置信度) 追踪
- **原子I/O / Atomic I/O**: temp → fsync → rename 模式 + 快照回滚
- **多视角QC / Multi-Perspective QC**: 3-评审协议 + 100分制评分
- **安全机制 / Safety Mechanisms**: Auto-Rescue 可恢复错误处理, Auto-Abort 卡死检测

---

## 快速开始 / Quick Start

```bash
# 初始化新书 / Initialize a new book
python -m scripts.v2.cli init --title "我的小说" --genre "都市异能" --words 100000

# 运行阶段1-5 (设置到世界观) / Run phases 1-5 (setup through worldbuilding)
python -m scripts.v2.cli setup --run-dir <path>

# 写章节 (阶段6) / Write chapters (Phase 6)
python -m scripts.v2.cli write --run-dir <path> --mode auto --chapters 1-10

# 合并最终书籍 (阶段8-9) / Merge final book (Phases 8-9)
python -m scripts.v2.cli finalize --run-dir <path>

# 断点续写 / Resume writing
python -m scripts.v2.cli write --run-dir <path> --resume auto
```

---

## 架构 / Architecture

### 目录结构 / Directory Structure

```
novels/
└── {book_title_slug}__{book_uid}/
    └── runs/
        └── {run_id}/
            ├── 0-config/          # 配置层 / Configuration layer
            │   ├── 0-book-config.json
            │   ├── intent_checklist.json
            │   ├── style_guide.md
            │   └── price-table.json
            ├── 1-outline/         # 大纲层 / Outline layer
            │   ├── 1-main-outline.md
            │   └── 5-chapter-outlines.json
            ├── 2-planning/        # 规划层 / Planning layer
            │   └── 2-chapter-plan.json
            ├── 3-world/           # 世界观层 / Worldbuilding layer
            │   └── 3-world-building.md
            ├── 4-state/           # 运行时状态 (7面板) / Runtime state (7 panels)
            │   ├── 4-writing-state.json      # 真相源 / Source of truth
            │   ├── characters.json           # 角色状态 / Character states
            │   ├── plot_threads.json         # 剧情线索 / Plot threads
            │   ├── timeline.json             # 时间线 / Timeline
            │   ├── inventory.json            # 道具 / Items
            │   ├── locations_factions.json   # 地点 / Locations
            │   ├── pov_rules.json            # POV规则 / POV rules
            │   ├── session_memory.json       # 滚动窗口 / Rolling window
            │   ├── user_interactions.jsonl   # 用户指令 / User commands
            │   ├── backpatch.jsonl           # 待修复 / Pending fixes
            │   └── sanitizer_output.jsonl    # 清洗日志 / Sanitizer logs
            ├── drafts/            # 草稿层 / Draft layer
            │   ├── alignment/
            │   ├── outlines/
            │   ├── chapters/
            │   └── qc/
            ├── chapters/          # 最终章节 / Final chapters
            ├── anchors/           # 锚点文档 / Anchor documents
            ├── logs/              # 审计日志 / Audit logs
            │   ├── token-report.jsonl
            │   ├── cost-report.jsonl
            │   ├── events.jsonl
            │   ├── errors.jsonl
            │   ├── rescue.jsonl
            │   └── prompts/       # 提示词审计追踪 / Prompt audit trail
            ├── archive/           # 快照与回滚 / Snapshots & reverts
            │   ├── snapshots/
            │   ├── reverted/
            │   └── backpatch_resolved.jsonl
            └── final/             # 最终输出 / Final outputs
                ├── {book_title}_完整版.txt
                ├── quality-report.md
                ├── auto_abort_report.md
                ├── auto_rescue_report.md
                └── 7-whole-book-check.md
```

---

## 阶段参考 / Phase Reference

| 阶段 Phase | 名称 Name | 描述 Description |
|-----------|-----------|------------------|
| 1 | Initialization | 创建工作空间、配置、意图清单 / Create workspace, config, intent checklist |
| 2 | Style Guide | 定义叙事风格、风格约束 / Define narrative voice, style constraints |
| 3 | Main Outline | 生成书籍级情节结构 / Generate book-level plot structure |
| 4 | Chapter Planning | 详细章节列表与钩子 / Detailed chapter list with hooks |
| 5 | World Building | 角色、阵营、规则、道具 / Characters, factions, rules, items |
| 5.5 | Alignment Check | 验证世界观匹配意图清单 / Verify world matches intent checklist |
| 6 | Writing Loop | 清洗→草稿→QC→提交 (循环) / Sanitize→Draft→QC→Commit (repeats) |
| 7 | Backpatch Pass | FORCED章节的回补修复 / Retcon fixes for FORCED chapters |
| 8 | Merge Book | 合并章节为最终版本 / Concatenate chapters to final |
| 9 | Whole-Book QC | 最终7点质量检查 / Final 7-point quality check |

---

## 阶段6: 写作循环 (核心) / Phase 6: Writing Loop (Core)

写作循环是v2.0的核心：

/ The writing loop is the heart of v2.0:

```
6.1 Sanitizer ──→ 6.2 Outline ──→ 6.3 Draft ──→ 6.4 QC ──→ 6.5 Save ──→ 6.6 Commit
                      ↑                                              │
                      └────────────-- (若需重写 / if REVISE) ←────────┘
```

### 6.1 Sanitizer (清洗器)

读取状态面板，提取 **不变项 Invariants** (必须延续) vs **软回退 Soft Retcons** (可调整)。

/ Reads state panels and extracts **Invariants** (must continue) vs **Soft Retcons** (can adjust).

输出到 / Outputs to: `4-state/sanitizer_output.jsonl`

### 6.2 大纲生成 / Outline Generation

生成带上下文块的详细章节大纲。

/ Generates detailed chapter outline with context blocks.

- Manual模式: 等待用户确认
- Auto模式: 保存到 `drafts/outlines/` 并继续

### 6.3 草稿生成 / Draft Generation

分段生成章节正文。

/ Generates chapter text segment by segment.

使用 `prompts/v1/` 中的模板 (chapter_draft_first, chapter_draft_continue)。

### 6.4 质量检查 / Quality Check

**多视角协议 (Auto模式必须):**

/ **Multi-Perspective Protocol (blocking requirement in Auto mode):**

1. **苛刻主编视角**: 节奏、钩子、可出版性 / Pacing, hooks, publishability
2. **逻辑审计视角**: 因果关系、动机一致性 / Causality, motivation consistency
3. **连续性审计视角**: 时间线、角色状态、道具 / Timeline, character state, items

**评分 (100分制, 加权):**

/ **Scoring (100-point, weighted):**

| 维度 Dimension | 权重 Weight | 标准 Criteria |
|---------------|------------|---------------|
| 大纲符合度 Outline Adherence | 20 | 遵循大纲要求 / Follows outline requirements |
| 主线推进 Main Plot | 15 | 服务主线故事 / Advances main storyline |
| 人物一致性 Character | 15 | 与角色设定一致 / Consistent with character setup |
| 逻辑自洽 Logic | 20 | 因果连贯 / Causally coherent |
| 前后衔接 Continuity | 10 | 与上章自然连接 / Connects naturally to previous |
| 节奏/钩子 Pacing/Hook | 10 | 节奏和悬念 / Rhythm and cliffhanger |
| 文笔/重复 Style/Repetition | 10 | 无重复、风格统一 / No repetition, consistent style |

**判定映射 / Verdict Mapping:**

| 分数 Score | 状态 Status | 动作 Action |
|-----------|------------|------------|
| ≥85 | PASS | 保存，继续 / Save, continue |
| 75-84 | WARNING | 保存（带警告），继续 / Save with note, continue |
| <75 | REVISE | 重试 (Attempt++) / Retry (Attempt++) |
| 第三次<75 | FORCED | 保存（带⚠️），进入Backpatch / Save with ⚠️, queue for Backpatch |

### 6.5 内容确认 / Content Confirmation

- Manual模式: 等待 "OK/保存/继续"
- Auto模式: 带元数据保存到 `chapters/`

### 6.6 状态提交 / State Commit

用证据链更新所有状态面板。

/ Updates all state panels with Evidence chain.

**forced_streak 管理:**
- FORCED后 +1
- PASS/WARNING后 重置为0
- Backpatch成功关闭后 -1

**熔断:** 若 forced_streak ≥ 2，暂停等待人工审查。

---

## 安全机制 / Safety Mechanisms

### Auto-Rescue (自动救援)

在可恢复错误时触发 (qc_low, drift, minor_inconsistency, budget_warning)。

/ Triggered on recoverable errors (qc_low, drift, minor_inconsistency, budget_warning).

**策略 Strategies:**
- S1: 缩小范围 (字数 -20-40%) / Reduce scope
- S2: 回归锚点 / Rebase to anchor points
- S3: 优先Backpatch / Backpatch first
- S4: 模型降级 / Model downgrade
- S5: 兜底模板 / Fallback template

最多3轮，之后升级到Auto-Abort或人工处理。

### Auto-Abort Guardrail (自动中止)

检测卡死循环:
- 连续3轮字数<200
- 连续3轮QC<75且无改善

**动作:** 暂停运行，生成 `final/auto_abort_report.md`。

### Backpatch (阶段7)

仅回退修复FORCED章节:
1. 在 `backpatch.jsonl` 中排队问题
2. 每5章或阶段9前触发
3. 通过后续章节对话/闪回/揭示修复
4. 需要QC≥75才能关闭问题

---

## 配置 / Configuration

### 0-book-config.json

```json
{
  "version": "2.0.0",
  "book": {
    "title": "书名",
    "title_slug": "book_slug",
    "book_uid": "8char_hash",
    "genre": "都市灵异",
    "target_word_count": 100000,
    "chapter_target_words": 2500
  },
  "generation": {
    "model": "nvidia/moonshotai/kimi-k2.5",
    "mode": "auto",
    "max_attempts": 3,
    "auto_threshold": 85,
    "auto_rescue_enabled": true,
    "auto_rescue_max_rounds": 3
  },
  "qc": {
    "pass_threshold": 85,
    "warning_threshold": 75,
    "weights": { ... }
  },
  "run_id": "YYYYMMDD_HHMMSS_RAND6"
}
```

---

## 提示词模板 / Prompt Templates

模板位置 / Templates located in:
- `prompts/v1/` - 核心模板 (Auto模式必须使用) / Core templates (MUST use for Auto mode)
- `prompts/v2_addons/` - 额外评审、QC、Backpatch / Additional critics, QC, Backpatch

**注册表:** `4-state/prompt_registry.json` 追踪使用的模板。

**审计:** 每次模型调用记录最终提示词到 `logs/prompts/{phase}_{chapter}_{event_id}.md`

---

## 状态面板 (基于证据) / State Panels (Evidence-Based)

所有状态变更需要证据:
```json
{
  "value": "...",
  "evidence_chapter": "第015章",
  "evidence_snippet": "张大胆说：...",
  "confidence": 0.85
}
```

**置信度阈值:** 0.7
- ≥0.7: 直接更新到活跃状态
- <0.7: 进入 `pending_changes` 待审核

---

## 开发 / Development

### 模块结构 / Module Structure

```
scripts/v2/
├── utils.py              # ID生成、slug、路径 / IDs, slugs, paths
├── atomic_io.py          # 原子写入、快照 / Atomic writes, snapshots
├── workspace.py          # 目录管理 / Directory management
├── config_manager.py     # 配置I/O / Config I/O
├── state_manager.py      # 7面板 / 7 panels
├── prompt_registry.py    # 模板注册表 / Template registry
├── prompt_assembly.py    # 提示词构建 / Prompt building
├── price_table.py       # 费率表管理 / Price table management
├── resume_manager.py     # 断点续传、锁管理 / Resume, lock management
├── phase_runner.py       # 阶段1-5 / Phases 1-5
├── writing_loop.py       # 阶段6 / Phase 6
├── safety_mechanisms.py  # 阶段7-9, 救援/中止 / Phases 7-9, rescue/abort
└── cli.py               # CLI入口 / CLI entry point
```

### 测试 / Testing

```bash
python scripts/v2/test_v2.py
```

---

## 从v1.0迁移 / Migration from v1.0

v2.0保持与v1.0的兼容性:
- `token-report.json` 格式保留
- 阶段编号对齐 (6.2/6.5 确认闸门不变)
- 可用 `--resume` 恢复v1.0书籍

v2.0新增:
- 运行级隔离 (`runs/{run_id}/`)
- 基于证据的状态面板
- 原子I/O + 回滚
- 多视角QC
- Auto-Rescue/Abort

---

## 许可证 / License

MIT License - 参见 LICENSE 文件
