"""
Unit Tests for Task Persistence Module
任务持久化模块单元测试
"""

import sys
import os
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# 添加 lib 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))

from task_persistence import (
    TaskPersistenceManager, TaskRecord, TaskStatus,
    CronConfigManager, get_today_file_path
)


class TestTaskRecord:
    """测试 TaskRecord 数据类"""
    
    def test_task_record_creation(self):
        """测试创建任务记录"""
        record = TaskRecord(
            id="test-1",
            name="Test Task",
            description="A test task",
            complexity_score=5.5,
            status="pending"
        )
        
        assert record.id == "test-1"
        assert record.name == "Test Task"
        assert record.complexity_score == 5.5
        assert record.status == "pending"
        assert record.created_at is not None
    
    def test_task_record_to_dict(self):
        """测试转换为字典"""
        record = TaskRecord(
            id="test-1",
            name="Test Task",
            depends_on=["dep1", "dep2"]
        )
        
        data = record.to_dict()
        assert data["id"] == "test-1"
        assert data["name"] == "Test Task"
        assert data["depends_on"] == ["dep1", "dep2"]
    
    def test_task_record_from_dict(self):
        """测试从字典创建"""
        data = {
            "id": "test-1",
            "name": "Test Task",
            "description": "Test",
            "depends_on": [],
            "estimated_time": "medium",
            "tool_calls_estimate": 5,
            "decision_points": 0,
            "complexity_score": 3.0,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "batch_number": 0,
            "notes": ""
        }
        
        record = TaskRecord.from_dict(data)
        assert record.id == "test-1"
        assert record.name == "Test Task"


class TestTaskPersistenceManager:
    """测试任务持久化管理器"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def manager(self, temp_dir):
        """创建测试用的管理器"""
        return TaskPersistenceManager(backlog_dir=temp_dir)
    
    def test_initialization(self, manager, temp_dir):
        """测试初始化"""
        assert manager.backlog_dir == Path(temp_dir)
        assert manager.backlog_dir.exists()
    
    def test_get_filename(self, manager):
        """测试文件名生成"""
        filename = manager._get_filename("2026-02-11")
        assert filename == "task-workflow-progress-2026-02-11.md"
    
    def test_initialize_daily_file(self, manager):
        """测试初始化每日文件"""
        filepath = manager.initialize_daily_file("2026-02-11")
        
        assert filepath.exists()
        assert filepath.name == "task-workflow-progress-2026-02-11.md"
        
        content = filepath.read_text()
        assert "# Task Workflow Progress - 2026-02-11" in content
        assert "📋 Task List" in content
        assert "📊 Progress Tracking" in content
    
    def test_add_task(self, manager):
        """测试添加任务"""
        manager.initialize_daily_file("2026-02-11")
        
        task = TaskRecord(
            id="task-1",
            name="Test Task",
            complexity_score=5.0,
            status="pending"
        )
        
        manager.add_task(task)
        
        assert "task-1" in manager._tasks
        assert manager._tasks["task-1"].name == "Test Task"
    
    def test_update_task_status(self, manager):
        """测试更新任务状态"""
        manager.initialize_daily_file("2026-02-11")
        
        task = TaskRecord(id="task-1", name="Test Task")
        manager.add_task(task)
        
        manager.update_task_status("task-1", TaskStatus.RUNNING)
        assert manager._tasks["task-1"].status == "running"
        assert manager._tasks["task-1"].started_at is not None
        
        manager.update_task_status("task-1", TaskStatus.COMPLETED)
        assert manager._tasks["task-1"].status == "completed"
        assert manager._tasks["task-1"].completed_at is not None
    
    def test_log_progress(self, manager):
        """测试记录进度"""
        manager.initialize_daily_file("2026-02-11")
        
        manager.log_progress("Test Event", "Test details")
        
        content = manager._current_file.read_text()
        assert "Test Event" in content
        assert "Test details" in content
    
    def test_migrate_incomplete_tasks(self, manager, temp_dir):
        """测试迁移未完成任务"""
        # 创建昨天的文件
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_file = Path(temp_dir) / f"task-workflow-progress-{yesterday}.md"
        
        # 写入昨天的内容
        content = f"""# Task Workflow Progress - {yesterday}

## 📋 Task List

| ID | Task | Complexity | Dependencies | Status | Batch |
|----|------|-----------|--------------|--------|-------|
| task-1 | Incomplete Task | 5.0 | - | ⏳ pending | - |
| task-2 | Running Task | 3.0 | - | 🔄 running | 1 |
| task-3 | Completed Task | 4.0 | - | ✅ completed | 1 |
"""
        yesterday_file.write_text(content)
        
        # 初始化今天的文件（应该迁移未完成任务）
        today_file = manager.initialize_daily_file()
        
        # 检查今天文件内容
        today_content = today_file.read_text()
        assert "Migrated from Previous Day" in today_content or "Incomplete Task" in today_content
    
    def test_get_current_tasks(self, manager):
        """测试获取当前任务"""
        manager.initialize_daily_file("2026-02-11")
        
        manager.add_task(TaskRecord(id="task-1", name="Task 1"))
        manager.add_task(TaskRecord(id="task-2", name="Task 2"))
        
        tasks = manager.get_current_tasks()
        assert len(tasks) == 2
        assert all(isinstance(t, TaskRecord) for t in tasks)
    
    def test_archive_completed(self, manager):
        """测试归档功能"""
        manager.initialize_daily_file("2026-02-11")
        manager.archive_completed()
        
        content = manager._current_file.read_text()
        assert "🔵 Archived" in content


class TestCronConfigManager:
    """测试 Cron 配置管理器"""
    
    @pytest.fixture
    def temp_config(self):
        """创建临时配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
cron_jobs:
  - name: test-job
    schedule: '0 0 * * *'
    command: echo test
    enabled: true
settings:
  timezone: UTC
""")
            temp_path = f.name
        
        yield temp_path
        os.unlink(temp_path)
    
    def test_generate_default_config(self):
        """测试生成默认配置"""
        manager = CronConfigManager()
        config = manager.generate_default_config()
        
        assert "cron_jobs" in config
        assert "settings" in config
        assert len(config["cron_jobs"]) == 2
        assert config["settings"]["timezone"] == "Asia/Shanghai"
    
    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CronConfigManager()
            manager.config_path = Path(tmpdir) / "test.yaml"
            
            config = manager.generate_default_config()
            manager.save_config(config)
            
            loaded = manager.load_config()
            assert loaded["settings"]["timezone"] == "Asia/Shanghai"
    
    def test_get_openclaw_cron_api_payload(self):
        """测试生成 OpenClaw Cron API 格式"""
        manager = CronConfigManager()
        payload = manager.get_openclaw_cron_api_payload()
        
        assert len(payload) == 2
        assert all("name" in job for job in payload)
        assert all("schedule" in job for job in payload)
        assert all("command" in job for job in payload)


class TestUtilityFunctions:
    """测试工具函数"""
    
    def test_get_today_file_path(self):
        """测试获取今日文件路径"""
        path = get_today_file_path()
        
        today = datetime.now().strftime("%Y-%m-%d")
        assert f"task-workflow-progress-{today}.md" in str(path)
        assert "task_backlog" in str(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
