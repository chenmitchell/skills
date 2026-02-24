#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_BIN="${OPENCLAW_BIN:-$(command -v openclaw 2>/dev/null || echo /opt/homebrew/bin/openclaw)}"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3 2>/dev/null || echo /usr/bin/python3)}"

BASE_DIR="${GW_WATCHDOG_BASE_DIR:-$HOME/.openclaw/watchdogs/gateway-discord}"
STATE_FILE="$BASE_DIR/state.json"
BACKUP_DIR="$BASE_DIR/backups"
EVENT_LOG="$BASE_DIR/events.jsonl"
LOCK_DIR="$BASE_DIR/lock"
CONFIG_ENV_FILE="$BASE_DIR/config.env"

FAIL_THRESHOLD="${GW_WATCHDOG_FAIL_THRESHOLD:-2}"
COOLDOWN_SECONDS="${GW_WATCHDOG_COOLDOWN_SECONDS:-300}"
HEALTH_TIMEOUT_MS="${GW_WATCHDOG_HEALTH_TIMEOUT_MS:-10000}"
ENABLE_RESTART="${GW_WATCHDOG_ENABLE_RESTART:-0}"
MAX_RESTART_ATTEMPTS="${GW_WATCHDOG_MAX_RESTART_ATTEMPTS:-2}"
KEEP_BACKUPS="${GW_WATCHDOG_KEEP_BACKUPS:-50}"

DISCORD_WEBHOOK_URL="${DISCORD_WEBHOOK_URL:-}"
DISCORD_BOT_TOKEN="${DISCORD_BOT_TOKEN:-}"
DISCORD_CHANNEL_ID="${DISCORD_CHANNEL_ID:-}"

mkdir -p "$BASE_DIR" "$BACKUP_DIR"

if [[ -f "$CONFIG_ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$CONFIG_ENV_FILE"
fi

SOURCE_TAG="${GW_WATCHDOG_SOURCE:-unknown}"

if [[ ! -x "$OPENCLAW_BIN" ]]; then
  "$PYTHON_BIN" - "$EVENT_LOG" <<PY
import json
entry = {
  "time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "event": "error",
  "severity": "critical",
  "reason": "openclaw_bin_missing",
  "source": "$SOURCE_TAG",
  "details": "OPENCLAW_BIN=$OPENCLAW_BIN is not executable"
}
with open("$EVENT_LOG", "a", encoding="utf-8") as f:
  f.write(json.dumps(entry, ensure_ascii=True) + "\\n")
PY
  exit 2
fi

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "watchdog lock exists, exiting"
  exit 0
fi
cleanup() { rmdir "$LOCK_DIR" >/dev/null 2>&1 || true; }
trap cleanup EXIT

now_epoch() { date +%s; }
now_iso() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

load_state() {
  if [[ ! -f "$STATE_FILE" ]]; then
    cat <<EOF
healthy 0 none 0 0 0 none
EOF
    return
  fi
  "$PYTHON_BIN" - "$STATE_FILE" <<'PY'
import json, sys
path = sys.argv[1]
try:
    obj = json.load(open(path, "r", encoding="utf-8"))
except Exception:
    print("healthy 0 none 0 0 0 none")
    raise SystemExit(0)

status = str(obj.get("status", "healthy")).replace(" ", "_")
consecutive = int(obj.get("consecutive_failures", 0))
reason = str(obj.get("last_reason", "none")).replace(" ", "_")
last_alert = int(obj.get("last_alert_at", 0))
last_recovered = int(obj.get("last_recovered_at", 0))
restart_attempts = int(obj.get("restart_attempts", 0))
last_alert_key = str(obj.get("last_alert_key", "none")).replace(" ", "_")
print(status, consecutive, reason, last_alert, last_recovered, restart_attempts, last_alert_key)
PY
}

backup_state() {
  if [[ -f "$STATE_FILE" ]]; then
    cp "$STATE_FILE" "$BACKUP_DIR/state-$(date +%Y%m%d-%H%M%S).json"
  fi
  "$PYTHON_BIN" - "$BACKUP_DIR" "$KEEP_BACKUPS" <<'PY'
import glob, os, sys
base = sys.argv[1]
keep = int(sys.argv[2])
files = sorted(glob.glob(os.path.join(base, "state-*.json")))
if len(files) > keep:
    for p in files[:-keep]:
        try:
            os.remove(p)
        except OSError:
            pass
PY
}

write_state() {
  local status="$1"
  local consecutive="$2"
  local reason="$3"
  local last_alert_at="$4"
  local last_recovered_at="$5"
  local restart_attempts="$6"
  local last_alert_key="$7"
  backup_state
  "$PYTHON_BIN" - "$STATE_FILE" <<PY
import json
obj = {
  "status": "$status",
  "consecutive_failures": int("$consecutive"),
  "last_reason": "$reason",
  "last_alert_at": int("$last_alert_at"),
  "last_recovered_at": int("$last_recovered_at"),
  "restart_attempts": int("$restart_attempts"),
  "last_alert_key": "$last_alert_key",
  "updated_at": "$(now_iso)",
  "source": "$SOURCE_TAG"
}
open("$STATE_FILE", "w", encoding="utf-8").write(json.dumps(obj, ensure_ascii=True, indent=2))
PY
}

append_event() {
  local event_type="$1"
  local severity="$2"
  local reason="$3"
  local details="$4"
  "$PYTHON_BIN" - "$EVENT_LOG" <<PY
import json
entry = {
  "time": "$(now_iso)",
  "event": "$event_type",
  "severity": "$severity",
  "reason": "$reason",
  "source": "$SOURCE_TAG",
  "details": "$details",
}
with open("$EVENT_LOG", "a", encoding="utf-8") as f:
  f.write(json.dumps(entry, ensure_ascii=True) + "\\n")
PY
}

classify_reason() {
  local raw="$1"
  local lowered
  lowered="$(echo "$raw" | tr '[:upper:]' '[:lower:]')"
  if [[ "$lowered" == *"unauthorized"* || "$lowered" == *"forbidden"* || "$lowered" == *"token"* ]]; then
    echo "auth_mismatch"
  elif [[ "$lowered" == *"invalid config"* || "$lowered" == *"config"* ]]; then
    echo "config_invalid"
  elif [[ "$lowered" == *"rpc probe"* ]]; then
    echo "rpc_probe_failed"
  elif [[ "$lowered" == *"runtime: stopped"* ]]; then
    echo "runtime_stopped"
  elif [[ "$lowered" == *"timeout"* || "$lowered" == *"unreachable"* ]]; then
    echo "health_unreachable"
  else
    echo "gateway_check_failed"
  fi
}

send_discord_webhook() {
  local title="$1"
  local message="$2"
  if [[ -n "$DISCORD_WEBHOOK_URL" ]]; then
    "$PYTHON_BIN" - "$title" "$message" <<'PY' | curl -sS -X POST "$DISCORD_WEBHOOK_URL" -H "Content-Type: application/json" --data @- >/dev/null || true
import json
import sys
title = sys.argv[1]
message = sys.argv[2]
payload = {
  "content": f"**{title}**\\n{message}"
}
print(json.dumps(payload, ensure_ascii=True))
PY
    return 0
  fi

  if [[ -n "$DISCORD_BOT_TOKEN" && -n "$DISCORD_CHANNEL_ID" ]]; then
    local api_url="https://discord.com/api/v10/channels/${DISCORD_CHANNEL_ID}/messages"
    "$PYTHON_BIN" - "$title" "$message" <<'PY' | curl -sS -X POST "$api_url" -H "Authorization: Bot $DISCORD_BOT_TOKEN" -H "Content-Type: application/json" --data @- >/dev/null || true
import json
import sys
title = sys.argv[1]
message = sys.argv[2]
payload = {
  "content": f"**{title}**\\n{message}"
}
print(json.dumps(payload, ensure_ascii=True))
PY
  fi
}

attempt_restart() {
  local output
  if output="$("$OPENCLAW_BIN" gateway restart 2>&1)"; then
    append_event "restart_attempt" "warn" "restart_requested" "restart ok"
    echo "restart_ok"
  else
    append_event "restart_attempt" "error" "restart_failed" "$output"
    echo "restart_failed"
  fi
}

check_gateway() {
  local status_json=""
  local status_err=""
  local health_err=""
  local reason="none"
  local runtime_state=""
  local rpc_state=""
  local health_ok=0
  local status_err_file="$BASE_DIR/.status.err"
  local health_err_file="$BASE_DIR/.health.err"

  if ! status_json="$("$OPENCLAW_BIN" gateway status --json 2>"$status_err_file")"; then
    status_err="$(<"$status_err_file")"
    if [[ -z "$status_err" ]]; then
      status_err="$("$OPENCLAW_BIN" gateway status 2>&1 || true)"
    fi
    reason="$(classify_reason "$status_err")"
    if [[ "$reason" == "gateway_check_failed" ]]; then
      reason="runtime_stopped"
    fi
    echo "fail|critical|$reason|status_command_failed"
    return 0
  fi

  runtime_state="$("$PYTHON_BIN" - "$status_json" <<'PY'
import json
import sys
doc = json.loads(sys.argv[1])
runtime = doc.get("service", {}).get("runtime", {}).get("status", "unknown")
print(str(runtime).strip().lower())
PY
)"

  rpc_state="$("$PYTHON_BIN" - "$status_json" <<'PY'
import json
import sys
doc = json.loads(sys.argv[1])
rpc = doc.get("rpc", {})
if isinstance(rpc, dict) and rpc.get("ok") is True:
    print("ok")
elif isinstance(rpc, dict) and rpc.get("ok") is False:
    print("failed")
else:
    print("unknown")
PY
)"

  if [[ "$runtime_state" != "running" ]]; then
    echo "fail|critical|runtime_stopped|runtime_not_running"
    return 0
  fi

  if [[ "$rpc_state" == "unknown" ]]; then
    # Accept unknown rpc field, but require health endpoint below.
    :
  elif [[ "$rpc_state" != "ok" ]]; then
    echo "fail|warn|rpc_probe_failed|rpc_probe_not_ok"
    return 0
  fi

  if "$OPENCLAW_BIN" health --json --timeout "$HEALTH_TIMEOUT_MS" >/dev/null 2>"$health_err_file"; then
    health_ok=1
  else
    health_err="$(<"$health_err_file")"
  fi

  if [[ "$health_ok" -ne 1 ]]; then
    reason="$(classify_reason "${health_err:-health_unreachable}")"
    echo "fail|critical|$reason|health_probe_failed"
    return 0
  fi

  echo "pass|info|healthy|all_checks_ok"
}

read -r prev_status prev_failures prev_reason prev_alert_at prev_recovered_at prev_restart_attempts prev_alert_key <<<"$(load_state)"
now="$(now_epoch)"

IFS="|" read -r check_result severity reason details <<<"$(check_gateway)"

if [[ "$check_result" == "pass" ]]; then
  if [[ "$prev_status" != "healthy" ]]; then
    msg="source=$SOURCE_TAG reason=recovered previous_reason=$prev_reason"
    send_discord_webhook "Gateway RECOVERED" "$msg"
    append_event "recovered" "info" "recovered" "$msg"
    write_state "healthy" 0 "none" "$prev_alert_at" "$now" 0 "none"
  else
    write_state "healthy" 0 "none" "$prev_alert_at" "$prev_recovered_at" 0 "$prev_alert_key"
  fi
  exit 0
fi

new_failures=$((prev_failures + 1))
new_status="degraded"
[[ "$severity" == "critical" ]] && new_status="critical"
alert_key="${reason}:${new_status}"
should_alert=0

if [[ "$new_failures" -ge "$FAIL_THRESHOLD" ]]; then
  if [[ "$prev_alert_key" != "$alert_key" ]]; then
    should_alert=1
  elif (( now - prev_alert_at >= COOLDOWN_SECONDS )); then
    should_alert=1
  fi
fi

restart_attempts="$prev_restart_attempts"
if [[ "$ENABLE_RESTART" == "1" && "$new_failures" -ge "$FAIL_THRESHOLD" && "$restart_attempts" -lt "$MAX_RESTART_ATTEMPTS" ]]; then
  restart_attempts=$((restart_attempts + 1))
  restart_result="$(attempt_restart)"
  details="$details restart=$restart_result"
fi

if [[ "$should_alert" -eq 1 ]]; then
  msg="source=$SOURCE_TAG severity=$new_status reason=$reason failures=$new_failures details=$details"
  send_discord_webhook "Gateway ALERT" "$msg"
  append_event "alert" "$new_status" "$reason" "$msg"
  write_state "$new_status" "$new_failures" "$reason" "$now" "$prev_recovered_at" "$restart_attempts" "$alert_key"
else
  append_event "suppressed" "$new_status" "$reason" "cooldown_or_threshold_not_met failures=$new_failures"
  write_state "$new_status" "$new_failures" "$reason" "$prev_alert_at" "$prev_recovered_at" "$restart_attempts" "$prev_alert_key"
fi
