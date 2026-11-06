"""PreToolUse guard: no shell command may read, print or copy what is under .secrets/.

The user keeps keys and tokens there and asked that Claude never read them (6 Kasım). The Read deny
rule in settings.json covers the file tools; this covers the shell, where a command that names
.secrets together with a reading verb is refused. Commands that only hand the path to another tool
(colab upload, a script given the folder) still run. It is a guard against a slip, not a wall: a
script can still open the files, and Claude does not write one that prints them.
"""
import json
import re
import sys

READERS = re.compile(
    r"(?i)(?<![\w-])(cat|type|get-content|gc|head|tail|less|more|select-string|sls|grep|rg|findstr|"
    r"sed|awk|format-hex|xxd|od|strings|base64|certutil|copy-item|cp|copy|notepad|code)(?![\w-])"
)

command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
if ".secrets" in command and READERS.search(command):
    print("Blocked: .secrets/ holds the user's keys and is never read, printed or copied "
          "(.claude/hooks/guard_secrets.py).", file=sys.stderr)
    sys.exit(2)
