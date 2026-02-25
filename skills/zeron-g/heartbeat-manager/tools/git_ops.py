#!/usr/bin/env python3
"""Git 同步操作模块"""

import subprocess
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("heartbeat.git")


def _get_repo_root() -> Path:
    """获取 Git 仓库根目录"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
            cwd=Path(__file__).parent.parent,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        # 如果不在 git 仓库中，使用 skill 根目录
        return Path(__file__).parent.parent


def _load_config() -> dict:
    """加载 git 配置"""
    import yaml
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg.get("git", {})


def git_add_workspace() -> bool:
    """暂存工作区文件"""
    repo = _get_repo_root()
    workspace = Path(__file__).parent.parent / "workspace"

    try:
        subprocess.run(
            ["git", "add", str(workspace)],
            capture_output=True, text=True, check=True,
            cwd=repo,
        )
        logger.info("git add workspace 成功")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("git add 失败: %s", e.stderr)
        return False


def git_commit(message: str = "") -> bool:
    """提交更改"""
    config = _load_config()
    if not config.get("auto_commit", True):
        logger.info("自动提交已禁用，跳过")
        return True

    repo = _get_repo_root()
    prefix = config.get("commit_prefix", "[heartbeat]")
    if not message:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"{prefix} beat @ {now}"
    else:
        message = f"{prefix} {message}"

    try:
        # 先检查是否有需要提交的更改
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, check=True,
            cwd=repo,
        )
        if not status.stdout.strip():
            logger.info("无更改需要提交")
            return True

        subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True, text=True, check=True,
            cwd=repo,
        )
        logger.info("git commit 成功: %s", message)
        return True

    except subprocess.CalledProcessError as e:
        logger.error("git commit 失败: %s", e.stderr)
        return False


def git_push() -> bool:
    """推送到远程"""
    config = _load_config()
    if not config.get("auto_push", True):
        logger.info("自动推送已禁用，跳过")
        return True

    repo = _get_repo_root()

    try:
        subprocess.run(
            ["git", "push"],
            capture_output=True, text=True, check=True,
            cwd=repo,
            timeout=30,
        )
        logger.info("git push 成功")
        return True

    except subprocess.TimeoutExpired:
        logger.error("git push 超时")
        return False
    except subprocess.CalledProcessError as e:
        logger.error("git push 失败: %s", e.stderr)
        return False


def sync() -> dict:
    """
    完整同步流程：add → commit → push

    返回:
        {"add": bool, "commit": bool, "push": bool, "error": str | None}
    """
    result = {"add": False, "commit": False, "push": False, "error": None}

    result["add"] = git_add_workspace()
    if not result["add"]:
        result["error"] = "git add 失败"
        return result

    result["commit"] = git_commit()
    if not result["commit"]:
        result["error"] = "git commit 失败"
        return result

    result["push"] = git_push()
    if not result["push"]:
        result["error"] = "git push 失败"

    return result
