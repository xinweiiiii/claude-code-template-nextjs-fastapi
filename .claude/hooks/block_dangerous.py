#!/usr/bin/env python3
"""
PreToolUse hook — block dangerous bash commands before they run.

Receives JSON on stdin:
  { "tool_name": "Bash", "tool_input": { "command": "..." }, ... }

Exits 1 (with a message) to abort the command.
Exits 0 to allow it through.
"""

import json
import re
import sys

BLOCKED_PATTERNS = [
    # Destructive filesystem — only block dangerous targets, not rm -rf node_modules etc.
    (
        r"\brm\s+(-[^\s]*\s+)*-[^\s]*r[^\s]*\s+/",
        "recursive delete from root (rm ... /)",
    ),
    (
        r"\brm\s+(-[^\s]*\s+)*-[^\s]*r[^\s]*\s+~",
        "recursive delete from home (rm ... ~)",
    ),
    (r"\brm\s+-[^\s]*r[^\s]*\s+-[^\s]*f[^\s]*\s+/", "rm -r -f from root (split flags)"),
    (r"\brm\s+-[^\s]*f[^\s]*\s+-[^\s]*r[^\s]*\s+/", "rm -f -r from root (split flags)"),
    (r"\bdd\b.*\bof\s*=\s*/dev/", "dd writing to device"),
    (r">\s*/dev/sd[a-z]", "redirect to block device"),
    # Git destructive
    (
        r"\bgit\s+push\s+.*--force(?!-with-lease)\b",
        "force push (use --force-with-lease instead)",
    ),
    (r"\bgit\s+push\s+[^-]*-f\b", "force push -f"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard"),
    (r"\bgit\s+clean\s+-[^\s]*f", "git clean -f"),
    (r"\bgit\s+checkout\s+--\s+\.", "git checkout -- ."),
    (r"\bgit\s+restore\s+(?!--staged)(\.|--source)", "git restore (destructive)"),
    (r"\bgit\s+branch\s+-D\b", "git branch -D"),
    # Database destructive
    (
        r"\bDROP\s+(TABLE|DATABASE|SCHEMA)\b",
        "DROP TABLE/DATABASE/SCHEMA",
        re.IGNORECASE,
    ),
    (r"\bTRUNCATE\s+TABLE\b", "TRUNCATE TABLE", re.IGNORECASE),
    (r"\bDELETE\s+FROM\b(?!.*\bWHERE\b)", "DELETE without WHERE", re.IGNORECASE),
    # Remote code execution
    (r"curl\s+.*\|\s*(bash|sh|zsh|python|ruby|perl)", "piping curl to shell"),
    (r"wget\s+.*\|\s*(bash|sh|zsh|python|ruby|perl)", "piping wget to shell"),
    (r"eval\s+\$\(curl", "eval curl output"),
    (
        r"base64\s+(-d|--decode).*\|\s*(bash|sh|zsh|python|ruby|perl)",
        "base64 decode piped to shell",
    ),
    # Credential / secret exposure
    (r"\benv\b\s*>\s*\S+", "redirecting env output to file"),
    (r"printenv\s*>\s*\S+", "redirecting printenv to file"),
    (r"\bcat\s+(\S+\s+)*\.env(\s|$)", "reading .env file"),
    # Process / system — require command position to avoid substring matches
    (r"(^|;|&&|\|\|)\s*shutdown\b", "shutdown command"),
    (r"(^|;|&&|\|\|)\s*reboot\b", "reboot command"),
    (r"\bkill\s+-9\s+1\b", "kill init (PID 1)"),
    (r"\bpkill\s+-[^\s]*9", "pkill -9"),
    # Privilege escalation
    (r"\bsudo\s+rm\b", "sudo rm"),
    (r"\bsudo\s+dd\b", "sudo dd"),
    (r"\bchmod\s+777\b", "chmod 777"),
    (r"\bchown\s+-R\s+.*\s+/\b", "chown -R on root"),
]


def is_blocked(command: str) -> tuple[bool, str]:
    for entry in BLOCKED_PATTERNS:
        pattern, reason = entry[0], entry[1]
        flags = entry[2] if len(entry) == 3 else 0
        if re.search(pattern, command, flags):
            return True, reason
    return False, ""


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    command: str = payload.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    blocked, reason = is_blocked(command)
    if blocked:
        print(f"[block_dangerous] Blocked: {reason}", file=sys.stderr)
        print(f"Command: {command[:200]}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
