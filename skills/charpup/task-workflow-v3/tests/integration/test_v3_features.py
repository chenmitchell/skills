"""
Integration Tests for Task Workflow V3
V3 集成测试
"""

import sys
import os
import pytest
import tempfile
from pathlib import Path

# 添加 lib 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))

from task_scheduler import TaskScheduler, DynamicTaskManager, TaskNode, TaskStatus
from task_persistence import TaskPersistenceManager


class TestSchedulerWithPersistence:
    """测试调度器与持久化集成"""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_schedule_tasks_with_persistence(self, temp_dir):
        """测试带持久化的任务调度"""
        # 修改默认 backlog 目录
        original_dir = TaskPersistenceManager.DEFAULT_BACKLOG_DIR
        TaskPersistenceManager.DEFAULT_BACKLOG_DIR = temp_dir
        
        try:
            tasks = [
                TaskNode(id="task-1", name="Task 1", estimated_time="short"),
                TaskNode(id="task-2", name="Task 2", estimated_time="long"),
                TaskNode(id="task-3", name="Task 3", depends_on=["task-1"], 
                        estimated_time="medium")
            ]
            
            scheduler = TaskScheduler(max_batch_size=10, enable_persistence=True)
            batches = scheduler.schedule_tasks(tasks)
            
            # 验证批次
            assert len(batches) == 2
            assert len(batches[0]) == 2  # task-1, task-2 (无依赖)
            assert len(batches[1]) == 1  # task-3 (依赖 task-1)
            
            # 验证文件创建
            today_file = Path(temp_dir) / f"task-workflow-progress-{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}.md"
            assert today_file.exists()
            
        finally:
            TaskPersistenceManager.DEFAULT_BACKLOG_DIR = original_dir
    
    def test_task_status_update_cascades_to_file(self, temp_dir):
        """测试任务状态更新同步到文件"""
        original_dir = TaskPersistenceManager.DEFAULT_BACKLOG_DIR
        TaskPersistenceManager.DEFAULT_BACKLOG_DIR = temp_dir
        
        try:
            tasks = [
                TaskNode(id="task-1", name="Task 1"),
            ]
            
            scheduler = TaskScheduler(enable_persistence=True)
            scheduler.schedule_tasks(tasks)
            
            tasks[0].update_status(TaskStatus.RUNNING)
            tasks[0].update_status(TaskStatus.COMPLETED, "Done!")
            
            # 验证文件内容
            today_file = Path(temp_dir) / f"task-workflow-progress-{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}.md"
            content = today_file.read_text()
            assert "running" in content.lower() or "completed" in content.lower()
            
        finally:
            TaskPersistenceManager.DEFAULT_BACKLOG_DIR = original_dir


class TestDynamicTaskManagerWithPersistence:
    """测试动态任务管理器与持久化集成"""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_dynamic_insert_and_persistence(self, temp_dir):
        """测试动态插入和持久化"""
        original_dir = TaskPersistenceManager.DEFAULT_BACKLOG_DIR
        TaskPersistenceManager.DEFAULT_BACKLOG_DIR = temp_dir
        
        try:
            manager = DynamicTaskManager(enable_persistence=True)
            
            initial_tasks = [
                TaskNode(id="task-1", name="Initial Task")
            ]
            manager.initialize(initial_tasks)
            
            # 动态插入
            new_task = TaskNode(id="task-2", name="Dynamic Task")
            manager.insert_task(new_task)
            
            # 验证
            assert "task-2" in manager.all_tasks
            
            # 验证文件
            today_file = Path(temp_dir) / f"task-workflow-progress-{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}.md"
            content = today_file.read_text()
            assert "Dynamic Task" in content
            
        finally:
            TaskPersistenceManager.DEFAULT_BACKLOG_DIR = original_dir
    
    def test_progress_tracking(self, temp_dir):
        """测试进度追踪"""
        original_dir = TaskPersistenceManager.DEFAULT_BACKLOG_DIR
        TaskPersistenceManager.DEFAULT_BACKLOG_DIR = temp_dir
        
        try:
            manager = DynamicTaskManager(enable_persistence=True)
            
            tasks = [
                TaskNode(id="task-1", name="Task 1"),
                TaskNode(id="task-2", name="Task 2"),
                TaskNode(id="task-3", name="Task 3")
            ]
            manager.initialize(tasks)
            
            # 完成部分任务
            manager.mark_running("task-1")
            manager.mark_completed("task-1")
            manager.mark_running("task-2")
            
            # 获取进度
            progress = manager.get_progress_summary()
            assert progress["total"] == 3
            assert progress["completed"] == 1
            assert progress["running"] == 1
            assert progress["pending"] == 1
            
        finally:
            TaskPersistenceManager.DEFAULT_BACKLOG_DIR = original_dir
    
    def test_complete_workflow(self, temp_dir):
        """测试完整工作流"""
        original_dir = TaskPersistenceManager.DEFAULT_BACKLOG_DIR
        TaskPersistenceManager.DEFAULT_BACKLOG_DIR = temp_dir
        
        try:
            manager = DynamicTaskManager(max_batch_size=2, enable_persistence=True)
            
            # 初始化任务
            tasks = [
                TaskNode(id="a", name="Task A", estimated_time="short"),
                TaskNode(id="b", name="Task B", estimated_time="short"),
                TaskNode(id="c", name="Task C", depends_on=["a", "b"]),
            ]
            manager.initialize(tasks)
            
            # 第一批
            batch1 = manager.get_next_batch()
            assert len(batch1) == 2
            
            for task in batch1:
                manager.mark_running(task.id)
                manager.mark_completed(task.id)
            
            # 第二批
            batch2 = manager.get_next_batch()
            assert len(batch2) == 1
            
            manager.mark_running(batch2[0].id)
            manager.mark_completed(batch2[0].id)
            
            # 验证完成
            assert manager.get_progress_summary()["is_complete"]
            
        finally:
            TaskPersistenceManager.DEFAULT_BACKLOG_DIR = original_dir


class TestDailyFileMigration:
    """测试每日文件迁移功能"""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_migration_of_incomplete_tasks(self, temp_dir):
        """测试未完成任务的迁移"""
        original_dir = TaskPersistenceManager.DEFAULT_BACKLOG_DIR
        TaskPersistenceManager.DEFAULT_BACKLOG_DIR = temp_dir
        
        try:
            from datetime import datetime, timedelta
            
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 创建昨天的文件
            yesterday_file = Path(temp_dir) / f"task-workflow-progress-{yesterday}.md"
            yesterday_content = f"""# Task Workflow Progress - {yesterday}

## 📋 Task List

| ID | Task | Complexity | Dependencies | Status | Batch |
|----|------|-----------|--------------|--------|-------|
| incomplete-task | Incomplete Task | 5.0 | - | ⏳ pending | - |
| running-task | Running Task | 3.0 | - | 🔄 running | 1 |
| completed-task | Completed Task | 4.0 | - | ✅ completed | 1 |

## 📈 Statistics

- **Total Tasks**: 3
- **Completed**: 1
"""
            yesterday_file.write_text(yesterday_content)
            
            # 初始化今天的文件
            manager = TaskPersistenceManager()
            today_file = manager.initialize_daily_file(today)
            
            # 验证迁移
            today_content = today_file.read_text()
            # 应该包含迁移的任务
            assert "Incomplete Task" in today_content or "Migrated" in today_content
            
        finally:
            TaskPersistenceManager.DEFAULT_BACKLOG_DIR = original_dir


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
