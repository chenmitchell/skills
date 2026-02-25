# OpenClaw 品牌舆情监控 Skill

> � 专为新能源汽车品牌打造的零代码舆情监控解决方案

## ✨ 特性

- ✅ **零代码**：纯提示词驱动，无需编程
- ✅ **国内平台**：小红书、微博、汽车之家、懂车帝、易车网、知乎、百度贴吧、抖音/快手
- ✅ **行业定制**：专为新能源汽车行业优化，识别汽车媒体大V
- ✅ **智能分析**：LLM 驱动的情感分析和影响力评估
- ✅ **实时警报**：自动检测负面提及、群体投诉、病毒式传播
- ✅ **趋势分析**：历史数据对比和趋势预测
- ✅ **飞书集成**：富文本卡片报告推送
- ✅ **自动化**：定时任务，无需人工干预
- ✅ **可扩展**：易于添加新平台和功能

## 📸 效果预览

### 每日监控报告

<img src="docs/images/daily-report.png" width="600" alt="每日监控报告">

### 实时警报

<img src="docs/images/alert.png" width="600" alt="实时警报">

### 趋势分析

<img src="docs/images/trend-analysis.png" width="600" alt="趋势分析">

## 🚀 快速开始

### 前置要求

- OpenClaw v2026.2.0+
- 飞书账号（已集成到 OpenClaw）
- 适用于新能源汽车品牌

### 安装

**方式 A：从 ClawHub 安装（推荐）**

```bash
# 1. 安装 ClawHub CLI（如果还没安装）
npm i -g clawhub

# 2. 搜索 skill
clawhub search "brand monitor"

# 3. 安装 skill
npx clawhub install brand-monitor

# 4. 重启 OpenClaw
openclaw restart
```

**方式 B：使用安装脚本**

```bash
# 1. 克隆或下载 Skill
git clone https://github.com/your-repo/brand-monitor-skill.git
cd brand-monitor-skill

# 2. 运行安装脚本（只复制必需文件）
chmod +x install.sh
./install.sh

# 3. 按提示创建配置文件
cd ~/.openclaw/skills/brand-monitor
cp config.example.json config.json
nano config.json

# 4. 重启 OpenClaw
openclaw restart
```

**方式 C：手动安装**

```bash
# 1. 克隆或下载 Skill
git clone https://github.com/your-repo/brand-monitor-skill.git
cd brand-monitor-skill

# 2. 创建目标目录
mkdir -p ~/.openclaw/skills/brand-monitor/prompts

# 3. 只复制必需的文件
cp SKILL.md ~/.openclaw/skills/brand-monitor/
cp config.example.json ~/.openclaw/skills/brand-monitor/
cp prompts/*.md ~/.openclaw/skills/brand-monitor/prompts/

# 4. 验证安装
ls ~/.openclaw/skills/brand-monitor/
# 应该看到: SKILL.md, config.example.json, prompts/

# 5. 重启 OpenClaw
openclaw restart
```

**必需文件清单：**
- `SKILL.md` - Skill 元数据和文档
- `config.example.json` - 配置示例
- `prompts/monitor.md` - 每日监控
- `prompts/alert.md` - 实时警报
- `prompts/analyze-trend.md` - 趋势分析

**注意：** 其他文档文件（README.md、部署指南.md 等）仅供参考，不需要复制到 OpenClaw。

### 配置

复制配置示例并修改：

```bash
cd ~/.openclaw/skills/brand-monitor
cp config.example.json config.json
nano config.json
```

配置内容：

```json
{
  "brand_name": "你的品牌名",
  "brand_aliases": ["车型1", "车型2"],
  "exclude_keywords": ["招聘", "代理", "二手车"],
  "platforms": [
    "xiaohongshu",
    "weibo",
    "autohome",
    "dongchedi",
    "yiche",
    "zhihu",
    "tieba",
    "douyin"
  ],
  "monitor_hours": 24,
  "min_engagement": 10,
  "negative_threshold": -0.5,
  "viral_threshold": 5000,
  "report_language": "zh-CN",
  
  "industry_specific": {
    "focus_keywords": [
      "续航", "充电", "智能驾驶", "辅助驾驶",
      "电池", "安全", "空间", "舒适性"
    ],
    "kol_min_followers": 100000,
    "media_accounts": [
      "汽车之家", "懂车帝", "易车网",
      "新出行", "电动邦", "42号车库"
    ]
  }
}
```

### 使用

在 Telegram/WhatsApp 对 OpenClaw 说：

```
执行品牌监控
```

3-5 分钟后，你会在飞书收到第一份监控报告！

## 📚 文档

- [INSTALL.md](INSTALL.md) - 安装说明（包含 ClawHub 安装方式）
- [PUBLISH.md](PUBLISH.md) - 发布到 ClawHub 指南
- [新能源汽车品牌监控-完整指南](新能源汽车品牌监控-完整指南.md) - 专为新能源汽车定制 ⭐
- [一键配置定时任务](一键配置定时任务.md) - 飞书定时推送配置 ⭐
- [快速开始](快速开始.md) - 5分钟快速部署
- [部署指南](部署指南.md) - 完整的安装和配置说明
- [使用指南](使用指南.md) - 日常使用和高级功能
- [更新说明](更新说明.md) - 国内平台适配更新
- [AgentSkills规范说明](AgentSkills规范说明.md) - 规范详解

## 🎯 核心功能

### 1. 每日监控

自动搜索国内各平台的品牌提及，分析情感和影响力，生成结构化报告。

**监控平台：**
- 📕 小红书（用户真实体验）
- 🔴 微博（实时热点）
- 🚗 汽车之家（专业评测）
- 🎬 懂车帝（视频评测）
- 🚙 易车网（新车资讯）
- 🤔 知乎（深度讨论）
- 💬 百度贴吧（车友交流）
- 🎵 抖音/快手（短视频）

**报告内容：**
- 📊 总览统计（总数、情感分布）
- 🔥 热门提及 Top 5（标注汽车媒体大V）
- 📱 平台分布
- 🔥 热门话题（续航、充电、智驾等）
- 💡 关键洞察
- 🎯 建议行动

### 2. 实时警报

每小时自动检测需要关注的提及：

- 🚨 负面提及（情感 < -0.5，影响力 > 100）
- 🔥 病毒式传播（互动数 > 5000）
- ⚠️ 危机信号（安全、召回、自燃、维权等关键词）
- 👥 群体性投诉（多用户同时反映相同问题）
- 📰 汽车媒体报道（重点关注官方媒体和大V）

**新能源汽车特定问题识别：**
- 续航虚标、充电故障、电池衰减
- 自燃、断轴、异响
- 智驾故障、OTA问题

**警报级别：**
- 🔴 5级：危机事件，立即处理
- 🟠 4级：严重负面，当天处理
- 🟡 3级：中等负面，24小时内
- 🔵 2级：轻微负面，本周内
- ⚪ 1级：仅供参考

### 3. 趋势分析

分析历史数据，生成趋势报告：

- 📈 提及数量趋势
- 😊 情感变化趋势
- 📱 平台分布变化
- 💪 影响力趋势
- 🔥 热门话题演变

**分析周期：**
- 每日对比
- 每周分析
- 每月复盘

## 🔧 工作原理

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw Agent                       │
│  (利用现有的 web_search, web_fetch, LLM, message)      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │   Brand Monitor Skill   │
        │   (纯提示词驱动)         │
        └────────────┬────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌────────┐      ┌────────┐      ┌────────┐
│ 搜索   │      │ 分析   │      │ 报告   │
│ 提及   │ ───> │ 情感   │ ───> │ 推送   │
└────────┘      └────────┘      └────────┘
    │                │                │
    ▼                ▼                ▼
小红书          LLM 分析          飞书卡片
微博            影响力评估        实时警报
汽车之家        媒体识别          趋势图表
懂车帝          警报检测
易车网
知乎
贴吧
抖音
```

### 核心组件

1. **SKILL.md**
   - Skill 元数据（YAML frontmatter）
   - 使用说明和文档
   - 符合 AgentSkills 规范

2. **Prompts（提示词）**
   - `prompts/monitor.md` - 每日监控流程
   - `prompts/analyze-trend.md` - 趋势分析流程
   - `prompts/alert.md` - 实时警报流程

3. **Config（配置）**
   - `config.example.json` - 配置示例
   - `config.json` - 用户配置（需自行创建）

4. **OpenClaw Tools（工具）**
   - `web_search` - 搜索各平台
   - `web_fetch` - 获取详细内容
   - `message` - 推送到飞书

## 💡 使用场景

### 场景 1：日常品牌监控

```
执行品牌监控
```

每天早上 9:00 自动执行，推送报告到飞书。

**适用于：**
- 日常舆情监控
- 用户反馈收集
- 竞品动态跟踪

### 场景 2：新车发布监控

```
每 2 小时检查一次品牌提及和警报
```

新车发布当天密集监控，及时发现和处理问题。

**关注重点：**
- 汽车媒体评测
- 用户试驾反馈
- 对比竞品讨论
- 预订/提车情况

### 场景 3：危机公关

```
立即执行品牌监控，重点搜索"安全问题"相关讨论
```

快速评估危机影响范围，制定应对策略。

**监控内容：**
- 负面提及数量和传播
- 媒体报道角度
- 用户情绪变化
- 竞品趁机营销

### 场景 4：竞品分析

```
同时监控"我的品牌"和"竞品A"，生成对比报告
```

了解竞品动态，发现市场机会。

**对比维度：**
- 提及数量和增长
- 用户情感对比
- 热门话题差异
- 媒体关注度

### 场景 5：用户调研

```
整理过去一个月用户提到的所有产品问题和建议
```

收集用户反馈，指导产品改进。

**分析内容：**
- 续航表现反馈
- 充电体验问题
- 智驾功能评价
- 空间舒适性
- 售后服务质量

## 📊 数据指标

### 情感分数

| 分数 | 标签 | 含义 |
|------|------|------|
| 0.5 ~ 1.0 | 非常正面 | 用户非常满意 |
| 0.2 ~ 0.5 | 偏正面 | 用户基本满意 |
| -0.2 ~ 0.2 | 中性 | 仅提及，无明确态度 |
| -0.5 ~ -0.2 | 偏负面 | 用户有不满 |
| -1.0 ~ -0.5 | 非常负面 | 用户非常不满 |

### 影响力分数

```
影响力 = 粉丝数×0.3 + 点赞数×0.25 + 转发数×0.25 + 评论数×0.2
```

| 分数 | 等级 | 含义 |
|------|------|------|
| 0-100 | 低 | 影响范围小 |
| 100-500 | 中 | 有一定影响 |
| 500-1000 | 高 | 影响较大 |
| 1000+ | 极高 | 可能病毒式传播 |

## 🔄 定时任务

### 推荐配置

```json
{
  "cron": {
    "jobs": [
      {
        "name": "品牌监控-每日",
        "schedule": "0 9 * * *",
        "skill": "brand-monitor",
        "prompt": "monitor"
      },
      {
        "name": "品牌监控-警报",
        "schedule": "0 * * * *",
        "skill": "brand-monitor",
        "prompt": "alert"
      },
      {
        "name": "品牌监控-周报",
        "schedule": "0 10 * * 1",
        "skill": "brand-monitor",
        "prompt": "analyze-trend"
      }
    ]
  }
}
```

## 🎨 自定义

### 添加新平台

编辑 `prompts/monitor.md`，添加新的搜索指令：

```markdown
**微博:**
```
"{{brand_name}}" site:weibo.com after:{{start_date}}
```
```

### 调整情感阈值

编辑 `config.json`：

```json
{
  "negative_threshold": -0.3,  // 更敏感
  "viral_threshold": 5000       // 更高阈值
}
```

### 自定义报告格式

编辑 `prompts/monitor.md` 中的报告模板部分。

## 💰 成本

### 使用 OpenClaw 现有能力

- ✅ 无需额外服务器
- ✅ 无需额外 API
- ✅ 只需 OpenClaw 的正常运行成本

### 估算（每天 100 条提及）

| 项目 | 费用 |
|------|------|
| OpenClaw 运行 | 已有成本 |
| LLM API 调用 | ~$0.01/天 |
| 飞书机器人 | 免费 |
| **总计** | **~$0.30/月** |

## 🤝 贡献

欢迎贡献代码、文档或建议！

### 贡献方式

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发指南

- 遵循提示词最佳实践
- 添加详细的注释
- 更新相关文档
- 测试所有功能

## 📝 更新日志

### v1.0.0 (2026-02-25)

- ✨ 初始版本发布
- ✅ 支持 Twitter、Reddit、Hacker News
- ✅ 情感分析和影响力评估
- ✅ 实时警报系统
- ✅ 趋势分析功能
- ✅ 飞书集成

### v1.1.0 (2026-02-25)

- ✨ 适配国内平台：小红书、微博、汽车之家、懂车帝、易车网、知乎、百度贴吧、抖音/快手
- ✨ 新能源汽车行业定制：续航、充电、智驾等关键词
- ✨ 汽车媒体大V识别：官方媒体、认证编辑、行业KOL
- ✨ 新能源汽车特定问题识别：续航虚标、充电故障、电池衰减、自燃等
- ✨ 飞书集成优化
- ✅ 符合 AgentSkills 规范：使用 SKILL.md 格式

### 计划功能

- [ ] Web 仪表板
- [ ] 邮件报告
- [ ] 企业微信集成
- [ ] 自动回复建议
- [ ] 竞品深度分析
- [ ] 用户画像分析
- [ ] 视频内容分析（抖音/快手）

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [OpenClaw](https://openclaw.ai) - 强大的 AI 代理平台
- [飞书](https://www.feishu.cn/) - 优秀的协作工具
- 所有贡献者和用户

## 📞 支持

- 📖 文档：查看 `docs/` 目录
- 🐛 问题：[GitHub Issues](https://github.com/your-repo/issues)
- 💬 讨论：[GitHub Discussions](https://github.com/your-repo/discussions)
- 📧 邮件：support@example.com

## 🌟 Star History

如果这个项目对你有帮助，请给个 Star ⭐️

---

**Made with ❤️ by OpenClaw Community**
