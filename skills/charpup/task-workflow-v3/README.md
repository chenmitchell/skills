# Task Workflow V3

智能任务调度系统 V3 - 支持文件持久化、进度追踪和自动归档。

## 特性

- ✅ DAG 依赖分析和拓扑排序
- ✅ 任务复杂度自动计算
- ✅ 动态任务插入
- ✅ **文件持久化追踪** (V3 新增)
- ✅ **自动归档机制** (V3 新增)
- ✅ **OpenClaw Cron 集成** (V3 新增)

## 快速开始

```python
from lib.task_scheduler import TaskScheduler, TaskNode

# 创建任务
tasks = [
    TaskNode(id="research", name="技术调研", estimated_time="medium"),
    TaskNode(id="implement", name="实现方案", depends_on=["research"], estimated_time="long")
]

# 调度 (自动落盘)
scheduler = TaskScheduler(enable_persistence=True)
batches = scheduler.schedule_tasks(tasks)
```

## CLI 使用

```bash
# 初始化今日任务文件
python cli.py init-daily

# 列出任务
python cli.py list

# 添加任务
python cli.py add task-id "Task Name" --time medium

# 更新状态
python cli.py update task-id completed

# 运行演示
python cli.py demo
```

## 文件落盘

任务文档自动保存到:
```
/root/.openclaw/workspace/task_backlog/task-workflow-progress-YYYY-MM-DD.md
```

## Cron 配置

```bash
# 生成配置
python cli.py setup-cron
```

默认配置:
- `0 0 * * *` - 每日初始化新文件
- `0 1 * * *` - 清理30天前的旧文件

## 测试

```bash
pytest tests/ -v
```

## 文档

详见 [SKILL.md](SKILL.md)
