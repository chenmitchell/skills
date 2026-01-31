#!/bin/bash
# TuriX-CUA Helper Script for Clawdbot
# Supports dynamic task injection, resume, skills system, and planning

set -e

# ---------- Configuration ----------
PROJECT_DIR="your_dir/TuriX-CUA"
CONFIG_FILE="$PROJECT_DIR/examples/config.json"
CONDA_PATH="/opt/anaconda3/bin/conda"
ENV_NAME="mlx_env1"

export PATH="/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/homebrew/bin:$PATH"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ---------- Help ----------
show_help() {
    cat << EOF
Usage: run_turix.sh [OPTIONS] [TASK]

OPTIONS:
    -r, --resume ID     Resume task with agent_id
    -c, --config FILE   Use custom config
    -h, --help          Show help
    --no-plan           Disable planning (use_skills also disabled)
    --enable-skills     Enable skills (requires --enable-plan)
    --dry-run           Show command without running

EXAMPLES:
    run_turix.sh "Open Chrome go to github.com"
    run_turix.sh --enable-skills --resume my-task "Continue task"
EOF
}

# ---------- Parse Arguments ----------
RESUME_ID=""
CUSTOM_CONFIG=""
TASK_DESCRIPTION=""
DRY_RUN=false
USE_PLAN=true
USE_SKILLS=true

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--resume)
            RESUME_ID="$2"
            shift 2
            ;;
        -c|--config)
            CUSTOM_CONFIG="$2"
            shift 2
            ;;
        --no-plan)
            USE_PLAN=false
            USE_SKILLS=false
            shift
            ;;
        --enable-skills)
            USE_SKILLS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            log_error "Unknown option: $1"
            exit 1
            ;;
        *)
            TASK_DESCRIPTION="$*"
            break
            ;;
    esac
done

# ---------- Validation ----------
if [[ -z "$RESUME_ID" && -z "$TASK_DESCRIPTION" ]]; then
    log_error "Task or --resume required"
    exit 1
fi

if [[ -n "$CUSTOM_CONFIG" && ! -f "$CUSTOM_CONFIG" ]]; then
    log_error "Config not found: $CUSTOM_CONFIG"
    exit 1
fi

[[ -n "$CUSTOM_CONFIG" ]] && CONFIG_FILE="$CUSTOM_CONFIG"

if [[ ! -d "$PROJECT_DIR" ]]; then
    log_error "TuriX project not found: $PROJECT_DIR"
    exit 1
fi

# ---------- Update Config (Skills-Compatible) ----------
update_config() {
    python3 << PYEOF
import json
import sys

config_path = '$CONFIG_FILE'
with open(config_path, 'r') as f:
    data = json.load(f)

# Update task if provided
task = '''${TASK_DESCRIPTION}'''
if task:
    data['agent']['task'] = task

# Update resume settings
resume_id = '''${RESUME_ID}'''
if resume_id:
    data['agent']['resume'] = True
    data['agent']['agent_id'] = resume_id

# Update feature flags (skills requires plan)
use_plan = '''${USE_PLAN}'''
use_skills = '''${USE_SKILLS}'''

data['agent']['use_plan'] = (use_plan == 'True')
data['agent']['use_skills'] = (use_skills == 'True')

# Ensure skills_dir exists if skills enabled
if data['agent']['use_skills']:
    skills_dir = data['agent'].get('skills_dir', 'skills')
    if not data['agent'].get('skills_max_chars'):
        data['agent']['skills_max_chars'] = 4000

with open(config_path, 'w') as f:
    json.dump(data, f, indent=2)

print('Config updated: plan={}, skills={}'.format(
    data['agent']['use_plan'], 
    data['agent']['use_skills']
))
PYEOF
}

# ---------- Pre-flight Checks ----------
preflight_checks() {
    log_info "Running pre-flight checks..."

    # Conda env check
    if ! "$CONDA_PATH" env list | grep -q "$ENV_NAME"; then
        log_warn "Conda env '$ENV_NAME' not found"
    fi

    # Config check
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log_error "Config not found: $CONFIG_FILE"
        exit 1
    fi

    # Screen recording permission check
    if ! python3 -c "
import ctypes
CoreGraphics = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics')
exit(0 if CoreGraphics.CGPreflightScreenCaptureAccess() else 1)
" 2>/dev/null; then
        log_warn "Screen recording permission may be missing"
        log_warn "Grant in System Settings → Privacy & Security → Screen Recording"
    fi

    log_info "Pre-flight complete"
}

# ---------- Main ----------
main() {
    cd "$PROJECT_DIR"
    log_info "TuriX CUA"
    log_info "Project: $PROJECT_DIR"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY RUN]"
        echo "  Task: ${TASK_DESCRIPTION:-'(resume) ${RESUME_ID}'}"
        echo "  Plan: $USE_PLAN"
        echo "  Skills: $USE_SKILLS"
        echo "  Command: $CONDA_PATH run -n $ENV_NAME python examples/main.py"
        exit 0
    fi

    update_config
    preflight_checks

    log_info "Starting TuriX..."
    log_info "Press Cmd+Shift+2 to force stop"

    "$CONDA_PATH" run -n "$ENV_NAME" python examples/main.py
}

main