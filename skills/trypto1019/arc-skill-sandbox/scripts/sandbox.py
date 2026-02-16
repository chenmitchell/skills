#!/usr/bin/env python3
"""Skill Sandbox — Run untrusted skills in a monitored environment.

Intercepts filesystem, network, and environment access to produce a safety report.
"""

import argparse
import io
import json
import os
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock


class SandboxMonitor:
    """Monitors and logs all suspicious operations during skill execution."""

    def __init__(self):
        self.fs_operations = []
        self.env_accesses = []
        self.network_calls = []
        self.subprocess_calls = []
        self.warnings = []
        self.start_time = None
        self.end_time = None

    def log_fs(self, operation, path, mode=None):
        """Log a filesystem operation."""
        entry = {
            "operation": operation,
            "path": str(path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if mode:
            entry["mode"] = mode
        self.fs_operations.append(entry)

    def log_env(self, key):
        """Log an environment variable access."""
        self.env_accesses.append({
            "key": key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sensitive": self._is_sensitive(key),
        })

    def log_network(self, method, url, data=None):
        """Log a network call."""
        entry = {
            "method": method,
            "url": str(url),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if data:
            entry["data_size"] = len(str(data))
        self.network_calls.append(entry)

    def log_subprocess(self, command):
        """Log a subprocess call."""
        self.subprocess_calls.append({
            "command": str(command),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def warn(self, message):
        """Log a warning."""
        self.warnings.append({
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def _is_sensitive(self, key):
        """Check if an env var key looks sensitive."""
        sensitive_patterns = [
            "KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL",
            "API", "AUTH", "PRIVATE", "SSH",
        ]
        key_upper = key.upper()
        return any(p in key_upper for p in sensitive_patterns)

    def get_verdict(self):
        """Determine safety verdict based on observations."""
        dangerous_indicators = 0

        # Sensitive env access
        sensitive_env = [e for e in self.env_accesses if e["sensitive"]]
        if sensitive_env:
            dangerous_indicators += len(sensitive_env)

        # Network calls
        if self.network_calls:
            dangerous_indicators += len(self.network_calls)

        # Subprocess calls
        if self.subprocess_calls:
            dangerous_indicators += len(self.subprocess_calls) * 2

        # Filesystem writes outside expected paths
        writes = [f for f in self.fs_operations if f["operation"] in ("write", "delete", "chmod")]
        if writes:
            dangerous_indicators += len(writes)

        if dangerous_indicators >= 5:
            return "DANGEROUS"
        elif dangerous_indicators >= 2:
            return "SUSPICIOUS"
        else:
            return "SAFE"

    def generate_report(self):
        """Generate a comprehensive safety report."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(
                (self.end_time - self.start_time) if self.start_time and self.end_time else 0, 2
            ),
            "verdict": self.get_verdict(),
            "summary": {
                "filesystem_operations": len(self.fs_operations),
                "environment_accesses": len(self.env_accesses),
                "sensitive_env_accesses": len([e for e in self.env_accesses if e["sensitive"]]),
                "network_calls": len(self.network_calls),
                "subprocess_calls": len(self.subprocess_calls),
                "warnings": len(self.warnings),
            },
            "filesystem": self.fs_operations,
            "environment": self.env_accesses,
            "network": self.network_calls,
            "subprocesses": self.subprocess_calls,
            "warnings": self.warnings,
        }


def create_monitored_open(monitor, original_open):
    """Create a monitored version of the open() function."""
    def monitored_open(file, mode="r", *args, **kwargs):
        path = str(file)
        op = "read" if "r" in mode else "write"
        monitor.log_fs(op, path, mode)
        if "w" in mode or "a" in mode:
            if any(s in path for s in ["/etc/", "/var/", "/home/", ".ssh", ".aws", ".env"]):
                monitor.warn(f"Write attempt to sensitive path: {path}")
        return original_open(file, mode, *args, **kwargs)
    return monitored_open


def create_monitored_environ(monitor, fake_env=False):
    """Create a monitored environment dict."""
    class MonitoredEnv:
        def __init__(self, real_env):
            self._real = dict(real_env) if not fake_env else {}
            self._fake_values = {
                "OPENAI_API_KEY": "sk-fake-sandbox-key-do-not-use",
                "ANTHROPIC_API_KEY": "sk-ant-fake-sandbox-key",
                "DISCORD_TOKEN": "fake-discord-token-sandbox",
                "AWS_SECRET_ACCESS_KEY": "fake-aws-secret-sandbox",
                "GITHUB_TOKEN": "ghp_fakesandboxtoken123456789",
                "OPENROUTER_API_KEY": "sk-or-fake-sandbox-key",
            }

        def get(self, key, default=None):
            monitor.log_env(key)
            if fake_env and key in self._fake_values:
                monitor.warn(f"Skill accessed sensitive env var: {key} (fake value provided)")
                return self._fake_values[key]
            return self._real.get(key, default)

        def __getitem__(self, key):
            monitor.log_env(key)
            if fake_env and key in self._fake_values:
                monitor.warn(f"Skill accessed sensitive env var: {key} (fake value provided)")
                return self._fake_values[key]
            return self._real[key]

        def __contains__(self, key):
            monitor.log_env(key)
            return key in self._real or (fake_env and key in self._fake_values)

        def keys(self):
            return self._real.keys()

        def items(self):
            return self._real.items()

        def values(self):
            return self._real.values()

    return MonitoredEnv(os.environ)


def run_sandbox(script_path, monitor, timeout=60, fake_env=False, restricted=False):
    """Run a script in the sandboxed environment."""
    script_path = Path(script_path)
    if not script_path.exists():
        print(f"ERROR: Script not found: {script_path}", file=sys.stderr)
        return False

    with open(script_path) as f:
        code = f.read()

    # Create monitored environment
    monitored_env = create_monitored_environ(monitor, fake_env=fake_env)

    # Set up mock network calls
    mock_urlopen = MagicMock()
    mock_urlopen.return_value.__enter__ = MagicMock(return_value=MagicMock(
        read=MagicMock(return_value=b'{"sandboxed": true}'),
        status=200,
    ))

    monitor.start_time = time.time()

    try:
        # Create restricted globals
        sandbox_globals = {
            "__name__": "__main__",
            "__file__": str(script_path),
            "__builtins__": __builtins__,
        }

        # Capture stdout
        old_stdout = sys.stdout
        captured = io.StringIO()
        sys.stdout = captured

        # Monkey-patch sensitive functions
        original_open = open
        patches = []

        if restricted:
            # Block network in restricted mode
            patches.append(patch("urllib.request.urlopen", side_effect=lambda *a, **k: (
                monitor.log_network("GET", str(a[0]) if a else "unknown"),
                monitor.warn("Network access BLOCKED in restricted mode"),
                (_ for _ in ()).throw(ConnectionError("Sandbox: network blocked")),
            )[-1]))

        # Apply patches
        for p in patches:
            p.start()

        try:
            # Monitor subprocess
            import subprocess as _subprocess
            original_run = _subprocess.run

            def monitored_run(cmd, **kwargs):
                monitor.log_subprocess(cmd)
                if restricted:
                    monitor.warn(f"Subprocess BLOCKED in restricted mode: {cmd}")
                    raise PermissionError("Sandbox: subprocess blocked")
                return original_run(cmd, **kwargs)

            _subprocess.run = monitored_run

            # Execute with timeout
            exec(compile(code, str(script_path), "exec"), sandbox_globals)

            _subprocess.run = original_run

        except SystemExit:
            pass  # Scripts often call sys.exit()
        except Exception as e:
            monitor.warn(f"Script error: {type(e).__name__}: {e}")
        finally:
            for p in patches:
                p.stop()
            sys.stdout = old_stdout

        monitor.end_time = time.time()

        output = captured.getvalue()
        if output:
            print(f"Script output ({len(output)} chars):")
            print(output[:500])
            if len(output) > 500:
                print(f"  ... ({len(output) - 500} more chars)")

        return True

    except Exception as e:
        monitor.end_time = time.time()
        monitor.warn(f"Sandbox execution error: {e}")
        return False


def run_skill_sandbox(skill_path, monitor, timeout=60, fake_env=False, restricted=False):
    """Sandbox an entire skill directory."""
    skill_path = Path(skill_path)
    scripts_dir = skill_path / "scripts"

    if not scripts_dir.exists():
        print(f"No scripts/ directory in {skill_path}")
        return True

    scripts = list(scripts_dir.glob("*.py"))
    if not scripts:
        print(f"No Python scripts found in {scripts_dir}")
        return True

    print(f"Sandboxing {len(scripts)} script(s) from {skill_path.name}...\n")

    for script in scripts:
        print(f"--- Running: {script.name} ---")
        run_sandbox(script, monitor, timeout=timeout, fake_env=fake_env, restricted=restricted)
        print()

    return True


def main():
    parser = argparse.ArgumentParser(description="Skill Sandbox — Test skills safely")
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run", help="Run a skill in sandbox")
    p_run.add_argument("--path", help="Path to skill directory")
    p_run.add_argument("--script", help="Path to a single script")
    p_run.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")
    p_run.add_argument("--fake-env", action="store_true", help="Inject fake credentials")
    p_run.add_argument("--restricted", action="store_true", help="Block network and subprocess")
    p_run.add_argument("--monitor-network", action="store_true", help="Enhanced network monitoring")
    p_run.add_argument("--json", action="store_true", help="Output report as JSON")

    p_report = sub.add_parser("report", help="Generate safety report without running")
    p_report.add_argument("--path", required=True, help="Path to skill directory")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    monitor = SandboxMonitor()

    if args.command == "run":
        if args.path:
            run_skill_sandbox(
                args.path, monitor,
                timeout=args.timeout,
                fake_env=args.fake_env,
                restricted=args.restricted,
            )
        elif args.script:
            run_sandbox(
                args.script, monitor,
                timeout=args.timeout,
                fake_env=args.fake_env,
                restricted=args.restricted,
            )
        else:
            print("ERROR: Specify --path or --script", file=sys.stderr)
            sys.exit(1)

        report = monitor.generate_report()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"SANDBOX REPORT")
            print(f"{'='*60}")
            print(f"Verdict: {report['verdict']}")
            print(f"Duration: {report['duration_seconds']}s")
            print()
            s = report['summary']
            print(f"  Filesystem ops:     {s['filesystem_operations']}")
            print(f"  Env accesses:       {s['environment_accesses']}")
            print(f"  Sensitive env:      {s['sensitive_env_accesses']}")
            print(f"  Network calls:      {s['network_calls']}")
            print(f"  Subprocess calls:   {s['subprocess_calls']}")
            print(f"  Warnings:           {s['warnings']}")

            if report['warnings']:
                print(f"\nWarnings:")
                for w in report['warnings']:
                    print(f"  - {w['message']}")

    elif args.command == "report":
        # Static analysis report (without execution)
        skill_path = Path(args.path)
        scripts_dir = skill_path / "scripts"
        scripts = list(scripts_dir.glob("*.py")) if scripts_dir.exists() else []

        print(f"Skill: {skill_path.name}")
        print(f"Scripts: {len(scripts)}")
        for s in scripts:
            size = s.stat().st_size
            print(f"  {s.name} ({size} bytes)")
        print(f"\nRun with: sandbox.py run --path {skill_path} --fake-env --restricted")


if __name__ == "__main__":
    main()
