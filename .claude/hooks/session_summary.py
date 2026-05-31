#!/usr/bin/env python3
"""
Stop hook — append a session entry to .claude/session-logs/.

The Claude Code Stop hook payload only provides:
  { "session_id": "...", "stop_hook_active": true }

No transcript is included. We log the session ID, timestamp, and any
extra fields present in the payload for visibility.
"""

import json
import os
import sys
from datetime import datetime


LOG_DIR = os.path.join(
    os.environ.get("PROJECT_ROOT", os.getcwd()), ".claude", "session-logs"
)

# Fields we handle explicitly — exclude from the "extra" dump
KNOWN_FIELDS = {"session_id", "stop_hook_active"}


def main() -> None:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {}

    session_id: str = payload.get("session_id", "unknown")
    extra = {k: v for k, v in payload.items() if k not in KNOWN_FIELDS}

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_slug = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"{date_slug}.log")

    with open(log_file, "a") as f:
        f.write(f"\n{'=' * 60}\n")
        f.write(f"Session : {session_id}\n")
        f.write(f"Ended   : {timestamp}\n")
        if extra:
            for key, value in extra.items():
                f.write(f"{key:<10}: {str(value)[:200]}\n")
        f.write(f"{'=' * 60}\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
