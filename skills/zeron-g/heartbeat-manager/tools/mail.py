#!/usr/bin/env python3
"""邮件收发模块：IMAP 读取 + SMTP 发送"""

import smtplib
import imaplib
import email
import email.utils
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger("heartbeat.mail")


def _load_config():
    """加载邮件配置"""
    import yaml
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_password() -> str:
    """从 .env 文件读取邮件密码"""
    from dotenv import dotenv_values
    env_path = Path(__file__).parent.parent / "config" / ".env"
    if not env_path.exists():
        raise FileNotFoundError(
            f"未找到 .env 文件: {env_path}\n"
            "请复制 .env.example 为 .env 并填写 EMAIL_APP_PASSWORD"
        )
    values = dotenv_values(env_path)
    pwd = values.get("EMAIL_APP_PASSWORD", "")
    if not pwd or pwd == "your_app_password_here":
        raise ValueError("EMAIL_APP_PASSWORD 未配置或仍为示例值")
    return pwd


def _decode_header_value(value: str) -> str:
    """解码邮件头"""
    if not value:
        return ""
    parts = decode_header(value)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)


def check_mail(since_hours: int = 1) -> dict:
    """
    检查邮箱，返回邮件摘要

    返回:
        {
            "unread_count": int,
            "flagged_count": int,
            "flagged_from": [str],  # 带标记的发件人
            "high_priority": [{"from": str, "subject": str, "date": str}],
            "last_check": str,
            "error": str | None
        }
    """
    config = _load_config()
    email_cfg = config["email"]
    result = {
        "unread_count": 0,
        "flagged_count": 0,
        "flagged_from": [],
        "high_priority": [],
        "last_check": datetime.now().strftime("%H:%M"),
        "error": None,
    }

    try:
        password = _get_password()
    except (FileNotFoundError, ValueError) as e:
        result["error"] = str(e)
        logger.warning("邮件密码加载失败: %s", e)
        return result

    conn = None
    try:
        conn = imaplib.IMAP4_SSL(email_cfg["imap_host"], email_cfg["imap_port"])
        conn.login(email_cfg["sender"], password)
        conn.select("INBOX", readonly=True)

        # 搜索未读邮件
        status, data = conn.search(None, "UNSEEN")
        if status == "OK" and data[0]:
            unread_ids = data[0].split()
            result["unread_count"] = len(unread_ids)

        # 搜索最近的带标记邮件
        since_date = (datetime.now() - timedelta(hours=since_hours)).strftime("%d-%b-%Y")
        status, data = conn.search(None, f'(FLAGGED SINCE {since_date})')
        if status == "OK" and data[0]:
            flagged_ids = data[0].split()
            result["flagged_count"] = len(flagged_ids)

            for mid in flagged_ids[-5:]:  # 最多取5封
                status2, msg_data = conn.fetch(mid, "(RFC822.HEADER)")
                if status2 == "OK":
                    msg = email.message_from_bytes(msg_data[0][1])
                    from_addr = _decode_header_value(msg.get("From", ""))
                    result["flagged_from"].append(from_addr)

        # 检查高优先级发件人的最近邮件
        hp_senders = email_cfg.get("high_priority_senders", [])
        for sender_keyword in hp_senders:
            status, data = conn.search(
                None, f'(FROM "{sender_keyword}" SINCE {since_date})'
            )
            if status == "OK" and data[0]:
                msg_ids = data[0].split()
                for mid in msg_ids[-3:]:  # 每个高优先发件人最多3封
                    status2, msg_data = conn.fetch(mid, "(RFC822.HEADER)")
                    if status2 == "OK":
                        msg = email.message_from_bytes(msg_data[0][1])
                        result["high_priority"].append({
                            "from": _decode_header_value(msg.get("From", "")),
                            "subject": _decode_header_value(msg.get("Subject", "")),
                            "date": msg.get("Date", ""),
                        })

        conn.logout()
        logger.info("邮件检查完成: 未读=%d, 标记=%d", result["unread_count"], result["flagged_count"])

    except Exception as e:
        result["error"] = f"IMAP错误: {e}"
        logger.error("邮件检查异常: %s", e)
        if conn:
            try:
                conn.logout()
            except Exception:
                pass

    return result


def send_mail(
    subject: str,
    body: str,
    recipients: Optional[list] = None,
    html: bool = False,
) -> bool:
    """
    发送邮件

    参数:
        subject: 邮件主题
        body: 邮件正文
        recipients: 收件人列表（None 则使用配置中的默认收件人）
        html: 是否为 HTML 格式

    返回:
        是否发送成功
    """
    config = _load_config()
    email_cfg = config["email"]

    if recipients is None:
        recipients = email_cfg["recipients"]

    try:
        password = _get_password()
    except (FileNotFoundError, ValueError) as e:
        logger.error("发送邮件失败——密码未配置: %s", e)
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = email_cfg["sender"]
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg["Date"] = email.utils.formatdate(localtime=True)

        content_type = "html" if html else "plain"
        msg.attach(MIMEText(body, content_type, "utf-8"))

        with smtplib.SMTP(email_cfg["smtp_host"], email_cfg["smtp_port"]) as server:
            server.starttls()
            server.login(email_cfg["sender"], password)
            server.send_message(msg)

        logger.info("邮件发送成功: %s -> %s", subject, recipients)
        return True

    except Exception as e:
        logger.error("邮件发送失败: %s", e)
        return False


def send_alert(title: str, details: str) -> bool:
    """发送告警邮件（带 [ALERT] 前缀）"""
    subject = f"[ALERT] EVA Heartbeat: {title}"
    body = (
        f"⚠️ 心跳告警\n"
        f"{'=' * 40}\n"
        f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"告警: {title}\n"
        f"{'=' * 40}\n\n"
        f"{details}\n"
    )
    return send_mail(subject, body)
