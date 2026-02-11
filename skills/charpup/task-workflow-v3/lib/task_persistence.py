"""
Task Workflow V3 - Persistence Module
任务持久化模块 - 支持文件落盘和进度追踪
"""

import os
import yaml
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    MIGRATED = "migrated"


@dataclass
class TaskRecord:
    """任务记录 - 可序列化的任务数据"""
    id: str
    name: str
    description: str = ""
    depends_on: List[str] = field(default_factory=list)
    estimated_time: str = "medium"
    tool_calls_estimate: int = 5
    decision_points: int = 0
    complexity_score: float = 0.0
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    batch_number: int = 0
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskRecord':
        return cls(**data)


@dataclass
class ProgressSnapshot:
    """进度快照"""
    timestamp: str
    total_tasks: int
    completed_tasks: int
    running_tasks: int
    pending_tasks: int
    completion_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TaskPersistenceManager:
    """任务持久化管理器"""
    
    DEFAULT_BACKLOG_DIR = "/root/.openclaw/workspace/task_backlog"
    FILENAME_FORMAT = "task-workflow-progress-{date}.md"
    
    def __init__(self, backlog_dir: Optional[str] = None):
        self.backlog_dir = Path(backlog_dir or self.DEFAULT_BACKLOG_DIR)
        self.backlog_dir.mkdir(parents=True, exist_ok=True)
        self._current_date = datetime.now().strftime("%Y-%m-%d")
        self._current_file: Optional[Path] = None
        self._tasks: Dict[str, TaskRecord] = {}
    
    def _get_filename(self, date_str: Optional[str] = None) -> str:
        """生成文件名"""
        date = date_str or datetime.now().strftime("%Y-%m-%d")
        return self.FILENAME_FORMAT.format(date=date)
    
    def _get_filepath(self, date_str: Optional[str] = None) -> Path:
        """获取完整文件路径"""
        return self.backlog_dir / self._get_filename(date_str)
    
    def initialize_daily_file(self, date_str: Optional[str] = None) -> Path:
        """初始化每日任务文件"""
        filepath = self._get_filepath(date_str)
        
        if not filepath.exists():
            # 检查前一天是否有未完成任务需要迁移
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            migrated_tasks = self._migrate_incomplete_tasks(yesterday)
            
            # 创建新文件
            self._create_markdown_file(filepath, migrated_tasks)
        else:
            # 文件已存在，解析现有任务
            content = filepath.read_text(encoding='utf-8')
            existing_tasks = self._parse_tasks_from_markdown(content)
            for task in existing_tasks:
                self._tasks[task.id] = task
        
        self._current_file = filepath
        return filepath
    
    def _migrate_incomplete_tasks(self, from_date: str) -> List[TaskRecord]:
        """迁移前一天未完成的任务"""
        old_file = self._get_filepath(from_date)
        migrated = []
        
        if old_file.exists():
            content = old_file.read_text(encoding='utf-8')
            tasks = self._parse_tasks_from_markdown(content)
            
            for task in tasks:
                if task.status not in ["completed", "migrated"]:
                    task.status = "migrated"
                    task.notes += f"\n[Auto-migrated from {from_date}]"
                    migrated.append(task)
        
        return migrated
    
    def _create_markdown_file(self, filepath: Path, migrated_tasks: List[TaskRecord] = None):
        """创建 Markdown 任务文件"""
        date_str = filepath.stem.split("-")[-3:]
        date = "-".join(date_str)
        
        content = f"""# Task Workflow Progress - {date}

**Generated**: {datetime.now().isoformat()}  
**Status**: 🟢 Active  
**Auto-archive**: CST 00:00 next day

---

## 📋 Task List

| ID | Task | Complexity | Dependencies | Status | Batch |
|----|------|-----------|--------------|--------|-------|
"""
        
        # 添加迁移的任务
        if migrated_tasks:
            content += "\n### 🔄 Migrated from Previous Day\n\n"
            for task in migrated_tasks:
                task.status = "pending"  # 重置为待执行
                deps = ", ".join(task.depends_on) if task.depends_on else "-"
                content += f"| {task.id} | {task.name} | {task.complexity_score:.1f} | {deps} | ⏳ Pending | - |\n"
                self._tasks[task.id] = task
        
        content += f"""

## 📊 Progress Tracking

| Timestamp | Event | Details |
|-----------|-------|---------|
| {datetime.now().strftime("%H:%M")} | File Created | Daily workflow initialized |

---

## 📈 Statistics

- **Total Tasks**: {len(migrated_tasks) if migrated_tasks else 0}
- **Completed**: 0
- **Pending**: {len(migrated_tasks) if migrated_tasks else 0}
- **Completion Rate**: 0%

---

## ✅ Completion Checklist

- [ ] All tasks completed
- [ ] Progress reviewed
- [ ] File archived

---

*Auto-generated by Task Workflow V3*
"""
        
        filepath.write_text(content, encoding='utf-8')
    
    def add_task(self, task: TaskRecord):
        """添加任务到当前文件"""
        self._tasks[task.id] = task
        self._update_markdown()
    
    def update_task_status(self, task_id: str, status: TaskStatus, notes: str = ""):
        """更新任务状态"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = status.value
            
            if status == TaskStatus.RUNNING and not task.started_at:
                task.started_at = datetime.now().isoformat()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task.completed_at = datetime.now().isoformat()
            
            if notes:
                task.notes += f"\n{notes}"
            
            self._update_markdown()
    
    def _update_markdown(self):
        """更新 Markdown 文件内容"""
        if not self._current_file or not self._current_file.exists():
            return
        
        # 构建任务表格
        task_rows = []
        status_icons = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "migrated": "📦"
        }
        
        for task in self._tasks.values():
            icon = status_icons.get(task.status, "⏳")
            deps = ", ".join(task.depends_on) if task.depends_on else "-"
            batch = str(task.batch_number) if task.batch_number > 0 else "-"
            task_rows.append(
                f"| {task.id} | {task.name} | {task.complexity_score:.1f} | {deps} | {icon} {task.status.title()} | {batch} |"
            )
        
        # 统计信息
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks.values() if t.status == "completed")
        pending = sum(1 for t in self._tasks.values() if t.status == "pending")
        running = sum(1 for t in self._tasks.values() if t.status == "running")
        rate = (completed / total * 100) if total > 0 else 0
        
        # 读取当前文件
        content = self._current_file.read_text(encoding='utf-8')
        
        # 解析并重建整个文件
        sections = self._parse_sections(content)
        
        # 重建任务列表部分
        task_section = ["## 📋 Task List", ""]
        task_section.append("| ID | Task | Complexity | Dependencies | Status | Batch |")
        task_section.append("|----|------|-----------|--------------|--------|-------|")
        task_section.extend(task_rows)
        
        # 重建文件内容
        new_content = sections['header'] + '\n\n'
        new_content += '\n'.join(task_section) + '\n\n'
        new_content += sections['progress'] + '\n\n'
        new_content += self._build_statistics_section(total, completed, pending, running, rate) + '\n\n'
        new_content += sections['footer']
        
        self._current_file.write_text(new_content, encoding='utf-8')
    
    def _parse_sections(self, content: str) -> dict:
        """解析 markdown 文件为各个部分"""
        sections = {
            'header': '',
            'progress': '',
            'footer': ''
        }
        
        lines = content.split('\n')
        current_section = 'header'
        section_lines = []
        
        for line in lines:
            if line.startswith("## 📋 Task List"):
                sections['header'] = '\n'.join(section_lines).rstrip()
                current_section = 'tasks'
                section_lines = []
            elif line.startswith("## 📊 Progress Tracking") and current_section == 'tasks':
                current_section = 'progress'
                section_lines = [line]
            elif line.startswith("## 📈 Statistics") and current_section == 'progress':
                sections['progress'] = '\n'.join(section_lines).rstrip()
                current_section = 'stats'
                section_lines = [line]
            elif line.startswith("## ✅ Completion") and current_section in ['stats', 'progress']:
                if current_section == 'stats':
                    section_lines = []
                current_section = 'footer'
                section_lines = [line]
            else:
                section_lines.append(line)
        
        if current_section == 'progress':
            sections['progress'] = '\n'.join(section_lines).rstrip()
        elif current_section == 'footer':
            sections['footer'] = '\n'.join(section_lines).rstrip()
        
        # 确保 progress 部分有基本结构
        if not sections['progress']:
            sections['progress'] = """## 📊 Progress Tracking

| Timestamp | Event | Details |
|-----------|-------|---------|"""
        
        # 确保 footer 存在
        if not sections['footer']:
            sections['footer'] = """## ✅ Completion Checklist

- [ ] All tasks completed
- [ ] Progress reviewed
- [ ] File archived

---

*Auto-generated by Task Workflow V3*"""
        
        return sections
    
    def _build_statistics_section(self, total: int, completed: int, pending: int, running: int, rate: float) -> str:
        """构建统计部分"""
        return f"""## 📈 Statistics

- **Total Tasks**: {total}
- **Completed**: {completed}
- **Running**: {running}
- **Pending**: {pending}
- **Completion Rate**: {rate:.1f}%"""
    
    def _update_statistics_section(self, content: str, total: int, completed: int, 
                                    pending: int, running: int, rate: float) -> str:
        """更新统计部分"""
        lines = content.split('\n')
        new_lines = []
        in_stats = False
        
        for line in lines:
            if "## 📈 Statistics" in line:
                in_stats = True
                new_lines.append(line)
                new_lines.append(f"\n- **Total Tasks**: {total}")
                new_lines.append(f"- **Completed**: {completed}")
                new_lines.append(f"- **Running**: {running}")
                new_lines.append(f"- **Pending**: {pending}")
                new_lines.append(f"- **Completion Rate**: {rate:.1f}%")
                continue
            
            if in_stats and line.startswith("- **"):
                continue  # 跳过旧统计
            if in_stats and line.strip().startswith("*Auto-generated"):
                in_stats = False
            
            if not in_stats or line.strip().startswith("*Auto-generated"):
                new_lines.append(line)
        
        return '\n'.join(new_lines)
    
    def _parse_tasks_from_markdown(self, content: str) -> List[TaskRecord]:
        """从 Markdown 解析任务"""
        tasks = []
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('| ') and not line.startswith('|----') and not line.startswith('| ID'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 5:
                    task = TaskRecord(
                        id=parts[0],
                        name=parts[1],
                        complexity_score=float(parts[2]) if parts[2] != '-' else 0.0,
                        depends_on=parts[3].split(', ') if parts[3] != '-' else [],
                        status=parts[4].split()[-1].lower() if ' ' in parts[4] else parts[4].lower()
                    )
                    tasks.append(task)
        
        return tasks
    
    def log_progress(self, event: str, details: str = ""):
        """记录进度事件"""
        if not self._current_file or not self._current_file.exists():
            return
        
        timestamp = datetime.now().strftime("%H:%M")
        new_line = f"| {timestamp} | {event} | {details} |"
        
        content = self._current_file.read_text(encoding='utf-8')
        
        # 找到 Progress Tracking 表格并插入新行
        lines = content.split('\n')
        new_lines = []
        in_progress_table = False
        table_header_found = False
        
        for i, line in enumerate(lines):
            if "## 📊 Progress Tracking" in line:
                in_progress_table = True
                new_lines.append(line)
                continue
            
            if in_progress_table and line.startswith("|----"):
                table_header_found = True
                new_lines.append(line)
                continue
            
            if table_header_found and line.startswith("|") and not line.startswith("|----"):
                new_lines.append(line)
                continue
            
            if table_header_found and line.strip() == "" and not line.startswith("|"):
                # 表格结束，插入新行
                new_lines.append(new_line)
                new_lines.append("")
                table_header_found = False
                in_progress_table = False
            
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
        self._current_file.write_text(content, encoding='utf-8')
    
    def get_current_tasks(self) -> List[TaskRecord]:
        """获取当前所有任务"""
        return list(self._tasks.values())
    
    def archive_completed(self):
        """归档已完成的任务"""
        # 标记完成状态
        if self._current_file and self._current_file.exists():
            content = self._current_file.read_text(encoding='utf-8')
            content = content.replace("**Status**: 🟢 Active", "**Status**: 🔵 Archived")
            self._current_file.write_text(content, encoding='utf-8')


class CronConfigManager:
    """Cron 配置管理器"""
    
    CONFIG_FILE = "/root/.openclaw/workspace/skills/task-workflow-v3/config/cron.yaml"
    
    def __init__(self):
        self.config_path = Path(self.CONFIG_FILE)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    def generate_default_config(self) -> Dict[str, Any]:
        """生成默认 cron 配置"""
        return {
            "cron_jobs": [
                {
                    "name": "task-workflow-daily-init",
                    "schedule": "0 0 * * *",  # CST 0:00
                    "command": "python -m task_workflow_v3.cli init-daily",
                    "description": "Initialize daily task workflow file",
                    "enabled": True
                },
                {
                    "name": "task-workflow-cleanup",
                    "schedule": "0 1 * * *",
                    "command": "python -m task_workflow_v3.cli cleanup-old-files --days 30",
                    "description": "Clean up old task files older than 30 days",
                    "enabled": True
                }
            ],
            "settings": {
                "timezone": "Asia/Shanghai",
                "auto_migrate": True,
                "retention_days": 30
            }
        }
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """保存配置到 YAML 文件"""
        config = config or self.generate_default_config()
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return self.generate_default_config()
    
    def get_openclaw_cron_api_payload(self) -> List[Dict[str, Any]]:
        """生成 OpenClaw Cron API 格式的配置"""
        config = self.load_config()
        jobs = []
        
        for job in config.get("cron_jobs", []):
            if job.get("enabled", False):
                jobs.append({
                    "name": job["name"],
                    "schedule": job["schedule"],
                    "command": job["command"],
                    "enabled": True
                })
        
        return jobs


# 便捷函数
def get_today_file_path() -> Path:
    """获取今日任务文件路径"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    return Path(TaskPersistenceManager.DEFAULT_BACKLOG_DIR) / f"task-workflow-progress-{date_str}.md"


def ensure_daily_file_exists() -> Path:
    """确保今日文件存在，不存在则创建"""
    manager = TaskPersistenceManager()
    return manager.initialize_daily_file()
