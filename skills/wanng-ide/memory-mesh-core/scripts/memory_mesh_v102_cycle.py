#!/usr/bin/env python3
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run_cmd(args, cwd=None):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    return p.returncode, p.stdout or "", p.stderr or ""


def parse_json_line(text: str):
    for line in reversed((text or "").splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except Exception:
                continue
    return None


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_and_parse(cmd, cwd, name):
    code, out, err = run_cmd(cmd, cwd=cwd)
    result = parse_json_line(out) or {"ok": code == 0, "error": (err or out).strip()[-400:]}
    if code != 0:
        raise SystemExit(f"{name} failed: {(err or out).strip()}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Memory Mesh v1.0.2 cycle: bootstrap + consolidation + local + global + update.")
    parser.add_argument("--workspace", default=".", help="OpenClaw workspace root")
    parser.add_argument("--top-k", type=int, default=20, help="Top promoted memories in local cycle")
    parser.add_argument("--min-score", type=float, default=45.0, help="Promotion threshold in local cycle")
    parser.add_argument("--max-consolidated", type=int, default=400, help="Max consolidated entries before scoring")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    scripts = workspace / "skills" / "memory-mesh-core" / "scripts"
    out_dir = workspace / "memory" / "memory_mesh"
    generated_at = datetime.now(timezone.utc).isoformat()

    bootstrap_result = run_and_parse(
        ["python3", str(scripts / "install_bootstrap.py"), "--workspace", str(workspace)],
        str(workspace),
        "install_bootstrap",
    )

    consolidation_result = run_and_parse(
        [
            "python3",
            str(scripts / "local_memory_consolidation.py"),
            "--workspace",
            str(workspace),
            "--max-entries",
            str(args.max_consolidated),
        ],
        str(workspace),
        "local_memory_consolidation",
    )

    local_result = run_and_parse(
        [
            "python3",
            str(scripts / "memory_mesh_cycle.py"),
            "--workspace",
            str(workspace),
            "--top-k",
            str(args.top_k),
            "--min-score",
            str(args.min_score),
            "--consolidated-json",
            "memory/memory_mesh/consolidated_memory.json",
        ],
        str(workspace),
        "local_cycle",
    )

    export_result = run_and_parse(
        [
            "python3",
            str(scripts / "export_public_feed.py"),
            "--workspace",
            str(workspace),
            "--skill-dir",
            "skills/memory-mesh-core",
            "--max-items",
            "20",
        ],
        str(workspace),
        "export_public_feed",
    )

    global_result = run_and_parse(
        [
            "python3",
            str(scripts / "global_memory_sync.py"),
            "--workspace",
            str(workspace),
            "--config",
            "skills/memory-mesh-core/config/global_sync.json",
        ],
        str(workspace),
        "global_memory_sync",
    )

    summary = {
        "ok": True,
        "version": "1.0.2",
        "generated_at": generated_at,
        "bootstrap": bootstrap_result,
        "consolidation": consolidation_result,
        "local_cycle": local_result,
        "feed_export": export_result,
        "global_sync": global_result,
        "cta": {
            "install": "clawhub install memory-mesh-core",
            "star": "clawhub star memory-mesh-core --yes",
            "share": "Share this skill URL and invite others to join the collective memory network.",
        },
    }
    write_json(out_dir / "v102_last_run.json", summary)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
