#!/usr/bin/env python3
"""
heartbeat-manager 主入口

用法:
    python heartbeat_run.py beat     # 执行一次心跳
    python heartbeat_run.py reset    # 执行每日重置（0点日报）
    python heartbeat_run.py weekly   # 生成并发送周报
    python heartbeat_run.py status   # 查看当前状态
"""

import sys
import os
import logging
import logging.handlers
import fcntl
import time
from datetime import datetime
from pathlib import Path

# 确保项目根目录在 Python 路径中
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs"
LOCK_FILE = PROJECT_ROOT / ".heartbeat.lock"


def setup_logging():
    """配置日志：控制台 + 文件轮转（保留7天）"""
    LOG_DIR.mkdir(exist_ok=True)

    root_logger = logging.getLogger("heartbeat")
    root_logger.setLevel(logging.INFO)

    # 避免重复添加 handler
    if root_logger.handlers:
        return root_logger

    # 控制台输出
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(
        "[%(asctime)s] %(name)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    ))
    root_logger.addHandler(console)

    # 文件轮转（按日，保留7天）
    log_file = LOG_DIR / "heartbeat.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when="midnight", backupCount=7, encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(name)s %(levelname)s: %(message)s",
    ))
    root_logger.addHandler(file_handler)

    return root_logger


def acquire_lock():
    """文件锁防并发"""
    try:
        lock_fd = open(LOCK_FILE, "w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()
        return lock_fd
    except (IOError, OSError):
        return None


def release_lock(lock_fd):
    """释放文件锁"""
    if lock_fd:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            lock_fd.close()
            LOCK_FILE.unlink(missing_ok=True)
        except Exception:
            pass


def cmd_beat():
    """
    执行一次心跳

    流程:
    1. 读取 MASTER.md
    2. 检查 daily.md
    3. 检查 todo.md（含超期告警）
    4. 检查 ongoing.json（含智能超时分析）
    5. 检查邮件
    6. 计算健康度
    7. 更新 MASTER.md
    8. git commit + push
    9. 全绿 → HEARTBEAT_OK；有问题 → 告警
    """
    logger = logging.getLogger("heartbeat.beat")
    logger.info("===== 心跳开始 =====")
    start_time = time.time()

    alerts = []
    all_ok = True

    # 1. 检查 daily.md
    logger.info("[1/7] 检查 daily.md")
    from tools.checker import check_daily
    daily_result = check_daily()
    if daily_result.get("error"):
        alerts.append(f"daily: {daily_result['error']}")

    # 2. 检查 todo.md（含超期告警）
    logger.info("[2/7] 检查 todo.md")
    from tools.checker import check_todo
    todo_result = check_todo()
    if todo_result.get("error"):
        alerts.append(f"todo: {todo_result['error']}")

    # 超期告警
    if todo_result.get("overdue"):
        all_ok = False
        for od in todo_result["overdue"]:
            alerts.append(f"TODO超期: {od['text']} (due:{od['due']})")
        from tools.mail import send_alert
        overdue_texts = "\n".join(
            f"  - {od['text']} (due:{od['due']})" for od in todo_result["overdue"]
        )
        send_alert("TODO 超期告警", f"以下任务已超期:\n{overdue_texts}")

    # 3. 检查 ongoing.json
    logger.info("[3/7] 检查 ongoing.json")
    from tools.checker import check_ongoing
    ongoing_result = check_ongoing()
    if ongoing_result.get("error"):
        alerts.append(f"ongoing: {ongoing_result['error']}")

    # 4. 智能超时分析
    logger.info("[4/7] 智能超时分析")
    from tools.task_analyzer import analyze_all
    analysis = analyze_all()
    if analysis["stuck"]:
        all_ok = False
        for s in analysis["stuck"]:
            alerts.append(f"任务卡死: [{s['task_id']}] {s['title']}")
    for action in analysis.get("actions_taken", []):
        logger.info("  动作: %s", action)

    # 5. 检查邮件
    logger.info("[5/7] 检查邮件")
    from tools.mail import check_mail
    mail_result = check_mail()
    if mail_result.get("error"):
        alerts.append(f"mail: {mail_result['error']}")
        # 邮件失败不算致命错误，降级继续

    # 6. 计算健康度
    logger.info("[6/7] 计算健康度")
    from tools.health_score import calculate_score, record_score
    # git_result 稍后获取，先传 None
    score = calculate_score(daily_result, todo_result, ongoing_result, mail_result, None)

    health_info = record_score(score)
    logger.info("  健康度: %d 分 (streak:%d)", score, health_info["streak"])

    # 健康度告警
    if health_info["alert_needed"]:
        all_ok = False
        alerts.append(
            f"健康度告警: 连续 {health_info['consecutive_low']} 次低于阈值"
        )
        from tools.mail import send_alert
        send_alert(
            "健康度持续低分",
            f"连续 {health_info['consecutive_low']} 次健康度低于 60 分\n"
            f"当前分数: {score}",
        )

    # 7. 更新 MASTER.md
    logger.info("[7/7] 更新 MASTER.md")
    from tools.renderer import render_master, write_master
    master_content = render_master(
        daily_result, todo_result, ongoing_result,
        mail_result, health_info, alerts,
    )
    write_master(master_content)

    # 8. 清理已完成 todo
    from tools.checker import clean_done_todos
    cleaned = clean_done_todos()
    if cleaned:
        logger.info("清理了 %d 条已完成 todo", cleaned)

    # 9. git 同步
    logger.info("[+] Git 同步")
    from tools.git_ops import sync
    git_result = sync()
    if git_result.get("error"):
        alerts.append(f"git: {git_result['error']}")

    # 最终状态
    elapsed = time.time() - start_time
    if all_ok and not alerts:
        logger.info("===== HEARTBEAT_OK (%.1fs) =====", elapsed)
        return True
    else:
        logger.warning(
            "===== 心跳完成（有告警: %d 条, %.1fs） =====",
            len(alerts), elapsed,
        )
        for a in alerts:
            logger.warning("  告警: %s", a)
        return False


def cmd_reset():
    """执行每日重置 + 日报"""
    logger = logging.getLogger("heartbeat.reset")
    logger.info("===== 每日重置开始 =====")

    from tools.daily_reset import reset_daily
    result = reset_daily()

    if result.get("error"):
        logger.error("每日重置异常: %s", result["error"])
    else:
        logger.info(
            "每日重置完成: 日报=%s, daily重置=%s, 清理=%d",
            "已发送" if result["report_sent"] else "未发送",
            "成功" if result["daily_reset"] else "失败",
            result["cleanup_count"],
        )

    # 重置后执行一次心跳
    cmd_beat()


def cmd_weekly():
    """生成并发送周报"""
    logger = logging.getLogger("heartbeat.weekly")
    logger.info("===== 周报生成 =====")

    from tools.weekly_report import send_weekly_report
    sent = send_weekly_report()

    if sent:
        logger.info("周报发送成功")
    else:
        logger.error("周报发送失败")


def cmd_status():
    """输出当前状态摘要"""
    from tools.health_score import get_stats
    from tools.checker import check_daily, check_todo, check_ongoing

    stats = get_stats()
    daily = check_daily()
    todo = check_todo()
    ongoing = check_ongoing()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"\n📊 EVA Heartbeat Status | {now}")
    print("=" * 40)
    print(f"  健康度: {stats['current']} (avg:{stats['average']})")
    print(f"  连续OK: {stats['streak']} | 总心跳: {stats['total_beats']}")
    print(f"  Daily: {daily['done']}/{daily['total']}")
    print(f"  Todo: {todo['done']}/{todo['total']} (超期:{len(todo.get('overdue', []))})")
    print(f"  Ongoing: {ongoing['total']} (状态:{ongoing['by_status']})")
    print()


def main():
    """主入口"""
    setup_logging()
    logger = logging.getLogger("heartbeat")

    # 解析命令
    cmd = sys.argv[1] if len(sys.argv) > 1 else "beat"
    cmd = cmd.lower().strip()

    if cmd == "status":
        # status 不需要锁
        cmd_status()
        return

    # 获取文件锁
    lock_fd = acquire_lock()
    if not lock_fd:
        logger.error("无法获取锁，可能有另一个实例在运行")
        sys.exit(1)

    try:
        if cmd == "beat":
            ok = cmd_beat()
            sys.exit(0 if ok else 1)
        elif cmd == "reset":
            cmd_reset()
        elif cmd == "weekly":
            cmd_weekly()
        else:
            print(f"未知命令: {cmd}")
            print("可用命令: beat, reset, weekly, status")
            sys.exit(2)
    except Exception as e:
        logger.exception("执行异常: %s", e)
        # 单步失败不阻断——尝试发送告警
        try:
            from tools.mail import send_alert
            send_alert("心跳异常", f"命令 {cmd} 执行异常:\n{e}")
        except Exception:
            pass
        sys.exit(1)
    finally:
        release_lock(lock_fd)


if __name__ == "__main__":
    main()
