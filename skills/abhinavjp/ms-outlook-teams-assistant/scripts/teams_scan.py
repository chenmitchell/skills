"""Scan Microsoft Teams for recent items that likely need a reply.

This uses Microsoft Graph + MSAL device code flow (delegated permissions).

Notes:
- Tenant policy may restrict what can be read.
- Start minimal (mentions in chats) and expand permissions as needed.

Usage:
  python scripts/teams_scan.py --config references/config.json --days 7

Output: JSON with items.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import msal
import requests


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _strip_html(s: str) -> str:
    # Graph message bodies are HTML. Keep it simple.
    return (
        s.replace("<br>", "\n")
        .replace("<br/>", "\n")
        .replace("<br />", "\n")
        .replace("&nbsp;", " ")
    )


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def graph_get(token: str, url: str, params: dict | None = None) -> dict:
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Graph GET failed {r.status_code}: {r.text}")
    return r.json()


def acquire_token(cfg: dict) -> str:
    tcfg = cfg.get("teams", {})
    tenant_id = tcfg.get("tenantId")
    client_id = tcfg.get("clientId")
    scopes = tcfg.get("scopes") or ["User.Read"]
    if not tenant_id or not client_id:
        raise RuntimeError("Missing teams.tenantId or teams.clientId in config")

    cache_path = tcfg.get("tokenCachePath") or os.path.join("state", "teams_token_cache.bin")
    cache = msal.SerializableTokenCache()
    if os.path.exists(cache_path):
        cache.deserialize(open(cache_path, "r", encoding="utf-8").read())

    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        token_cache=cache,
    )

    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])

    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise RuntimeError(f"Failed to initiate device flow: {flow}")
        print(flow["message"], file=sys.stderr)
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise RuntimeError(f"Token acquisition failed: {result}")

    if cache.has_state_changed:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(cache.serialize())

    return result["access_token"]


def _parse_graph_dt(s: str) -> datetime:
    """Parse Graph timestamps reliably on Python 3.10.

    Graph may return fractional seconds with 1–7 digits.
    Python 3.10's datetime.fromisoformat is pickier in some builds, so we normalize
    the fraction to 6 digits.
    """
    s = s.replace("Z", "+00:00")
    if "." in s:
        head, tail = s.split(".", 1)
        # tail like: "37+00:00" or "3701234+00:00"
        if "+" in tail:
            frac, tz = tail.split("+", 1)
            tz = "+" + tz
        elif "-" in tail[1:]:
            # negative offset
            frac, tz = tail.split("-", 1)
            tz = "-" + tz
        else:
            frac, tz = tail, ""
        frac = (frac + "000000")[:6]
        s = f"{head}.{frac}{tz}"
    return datetime.fromisoformat(s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join("references", "config.json"))
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()

    cfg = load_config(args.config)
    token = acquire_token(cfg)

    since = datetime.now(timezone.utc) - timedelta(days=args.days)

    # Cache /me once
    me = graph_get(token, "https://graph.microsoft.com/v1.0/me")
    my_id = me.get("id")

    tcfg = cfg.get("teams", {})
    action_keywords = [k.lower() for k in (tcfg.get("actionKeywords") or [])]
    monitor = tcfg.get("monitor", {}) or {}
    include_one_on_one = bool(monitor.get("includeOneOnOne", True))
    include_group = bool(monitor.get("includeGroup", True))

    items = []

    # 1) Get recent chats
    # Requires: Chat.Read (delegated)
    max_chats = int(monitor.get("maxChats", 20))
    max_msgs = int(monitor.get("maxMessagesPerChat", 20))

    chats = graph_get(token, "https://graph.microsoft.com/v1.0/me/chats", params={"$top": max_chats})
    for chat in chats.get("value", []):
        chat_id = chat.get("id")
        if not chat_id:
            continue

        chat_type = (chat.get("chatType") or "").lower()  # oneOnOne|group|meeting
        is_group = chat_type in ("group", "meeting")
        if is_group and not include_group:
            continue
        if (not is_group) and (not include_one_on_one):
            continue

        # 2) Get last messages in the chat
        msgs = graph_get(
            token,
            f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages",
            params={"$top": max_msgs, "$orderby": "createdDateTime desc"},
        )
        for m in msgs.get("value", []):
            created = m.get("createdDateTime")
            if not created:
                continue
            created_dt = _parse_graph_dt(created)
            if created_dt < since:
                continue

            body_html = ((m.get("body") or {}).get("content")) or ""
            body_text = _strip_html(body_html)
            body_l = body_text.lower()

            frm = ((m.get("from") or {}).get("user") or {})
            from_name = frm.get("displayName", "")
            from_id = frm.get("id", "")

            # Skip your own messages
            if my_id and from_id and from_id == my_id:
                continue

            mentions = m.get("mentions") or []
            mentioned_me = (
                any((((x.get("mentioned") or {}).get("user") or {}).get("id")) == my_id for x in mentions)
                if my_id
                else False
            )

            # Broadcast-ish: mentions include a non-user entity like "Everyone" / "Team" or body contains @everyone
            mentioned_all = False
            for x in mentions:
                mentioned = (x.get("mentioned") or {})
                # Sometimes Graph returns conversation identity mentions
                display = (mentioned.get("displayName") or "")
                if display and display.lower() in ("everyone", "all", "team"):
                    mentioned_all = True
            if "@everyone" in body_l or "@all" in body_l:
                mentioned_all = True

            is_question = "?" in body_text
            keyword_hits = [k for k in action_keywords if k and k in body_l]

            # Determine if it likely warrants a reply.
            # - 1:1 chats: treat questions/keywords as needing a reply
            # - group chats: only if you are mentioned OR broadcast-ish (flag separately)
            needs_reply = False
            reason = []
            if not is_group:
                if is_question:
                    needs_reply = True
                    reason.append("question")
                if keyword_hits:
                    needs_reply = True
                    reason.append("keywords: " + ", ".join(sorted(set(keyword_hits))[:5]))
            else:
                if mentioned_me and bool(monitor.get("flagGroupIfMentionedMe", True)):
                    needs_reply = True
                    reason.append("mentioned_you")
                if mentioned_all and bool(monitor.get("flagGroupBroadcast", True)):
                    # Broadcast messages might not need reply, but you asked to highlight them.
                    reason.append("broadcast")
                    # Do not force needs_reply unless also a question.
                    if is_question or keyword_hits:
                        needs_reply = True

            # Still "monitor all" means we keep items even if not needing reply,
            # but we only emit items that are within last N days and from others.
            # We include a classification so the nagger can decide.
            items.append(
                {
                    "kind": "teams.chat.message",
                    "chatId": chat_id,
                    "chatType": chat.get("chatType"),
                    "topic": chat.get("topic"),
                    "messageId": m.get("id"),
                    "created": created,
                    "from": from_name,
                    "mentionedMe": bool(mentioned_me),
                    "broadcast": bool(mentioned_all),
                    "question": bool(is_question),
                    "keywordHits": keyword_hits[:8],
                    "needsReply": bool(needs_reply),
                    "reason": "; ".join(reason) if reason else "",
                }
            )

    print(
        json.dumps(
            {
                "generatedAt": iso_now(),
                "since": since.isoformat(timespec="seconds"),
                "count": len(items),
                "items": items[:50],
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
