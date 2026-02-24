#!/usr/bin/env python3
"""Run email-resend skill tests."""
import sys
from pathlib import Path

# Add skills to path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "email-resend" / "tests"))

exec(open(Path(__file__).parent.parent / "skills" / "email-resend" / "tests" / "test_inbound.py").read().replace("if __name__ == \"__main__\":", "if False:"))
