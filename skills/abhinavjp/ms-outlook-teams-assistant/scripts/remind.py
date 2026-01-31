"""Generate a Telegram reminder message for pending Outlook/Teams items.

This script:
- Reads cached scan results from state/latest_outlook.json + state/latest_teams.json (written by scan_all.py)
- Applies nagging rules
- Uses a local state file to avoid spamming (per-item cooldown)

It DOES NOT send messages itself.

Usage:
  python scripts/scan_all.py --config references/config.json
  python scripts/remind.py --config references/config.json

Output:
  Prints either an empty string (no reminder) or a ready-to-send message.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _run_json(cmd: list[str], cwd: str, timeout_s: int = 60) -> dict:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout_s)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
    out = (p.stdout or "").strip()
    return json.loads(out) if out else {}


def _load_state(path: str) -> dict:
    if not os.path.exists(path):
        return {"last_sent": {}, "dismissed": {}}
    return _load_json(path)


def _save_state(path: str, state: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _now() -> float:
    return time.time()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join("references", "config.json"))
    ap.add_argument("--cooldown-hours", type=float, default=None)
    ap.add_argument("--max-items", type=int, default=8)
    args = ap.parse_args()

    cfg_path = os.path.abspath(args.config)
    skill_dir = os.path.dirname(os.path.dirname(cfg_path))  # .../ms-outlook-teams-assistant

    cfg = _load_json(cfg_path)
    cooldown_h = args.cooldown_hours
    if cooldown_h is None:
        cooldown_h = float(cfg.get("reminders", {}).get("repeatHours", 6))
    cooldown_s = cooldown_h * 3600

    state_path = os.path.join(skill_dir, "state", "reminders.json")
    st = _load_state(state_path)
    last_sent: dict[str, float] = st.get("last_sent", {})
    dismissed: dict[str, float] = st.get("dismissed", {})

    now = _now()

    # Collect candidates
    candidates: list[dict] = []

    cache_dir = os.path.join(skill_dir, "state")

    # Outlook (from cache)
    out_cache = os.path.join(cache_dir, "latest_outlook.json")
    if os.path.exists(out_cache):
        out_json = _load_json(out_cache)
        for it in out_json.get("items", []) or []:
            key = f"outlook:{it.get('key')}"
            candidates.append(
                {
                    "source": "outlook",
                    "key": key,
                    "title": it.get("subject", "(no subject)"),
                    "who": it.get("sender", ""),
                    "when": it.get("received", ""),
                    "why": it.get("reason", ""),
                    "needsReply": True,
                    "meta": it,
                }
            )

    # Teams (from cache)
    teams_cache = os.path.join(cache_dir, "latest_teams.json")
    if os.path.exists(teams_cache):
        t_json = _load_json(teams_cache)
        for it in t_json.get("items", []) or []:
            key = f"teams:{it.get('chatId')}:{it.get('messageId')}"
            is_group = (it.get("chatType") or "").lower() in ("group", "meeting")
            mentioned_me = bool(it.get("mentionedMe"))
            needs_reply = bool(it.get("needsReply"))

            # User selection "2":
            # - 1:1 chats: needsReply
            # - group chats: mentionedMe AND needsReply
            if is_group:
                should_nag = mentioned_me and needs_reply
            else:
                should_nag = needs_reply

            candidates.append(
                {
                    "source": "teams",
                    "key": key,
                    "title": it.get("topic") or "(Teams chat)",
                    "who": it.get("from", ""),
                    "when": it.get("created", ""),
                    "why": it.get("reason", ""),
                    "broadcast": bool(it.get("broadcast")),
                    "mentionedMe": mentioned_me,
                    "needsReply": needs_reply,
                    "shouldNag": should_nag,
                    "meta": it,
                }
            )

    # Filter to nag set
    nag = [c for c in candidates if c.get("source") == "outlook" or c.get("shouldNag")]

    # Apply dismissal (forever)
    nag = [c for c in nag if c.get("key") not in dismissed]

    # Apply cooldown
    send = []
    for c in nag:
        ls = float(last_sent.get(c["key"], 0) or 0)
        if now - ls >= cooldown_s:
            send.append(c)

    if not send:
        return 0

    send = send[: args.max_items]

    lines = []
    lines.append("Reminder: pending messages (needs reply)")
    lines.append("")

    for idx, c in enumerate(send, start=1):
        if c["source"] == "outlook":
            lines.append(f"{idx}) [Outlook] {c['title']} — {c.get('who','')} ({c.get('when','')})")
        else:
            flags = []
            if c.get("broadcast"):
                flags.append("broadcast")
            if c.get("mentionedMe"):
                flags.append("tagged")
            ftxt = f" [{' / '.join(flags)}]" if flags else ""
            lines.append(f"{idx}) [Teams]{ftxt} {c['title']} — {c.get('who','')} ({c.get('when','')})")

    lines.append("")
    lines.append("Reply here with: 'dismiss <number>' to stop nagging for an item.")

    # Update state
    for c in send:
        last_sent[c["key"]] = now
    st["last_sent"] = last_sent
    st["dismissed"] = dismissed
    st["updated_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    _save_state(state_path, st)

    # Save last batch mapping for dismiss-by-number
    batch_path = os.path.join(skill_dir, "state", "last_batch.json")
    _save_state(batch_path, {"keys": [c["key"] for c in send], "updated_at": st["updated_at"]})

    print("\n".join(lines).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
