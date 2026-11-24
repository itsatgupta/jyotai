#!/usr/bin/python3
"""PreToolUse guard for the jyotish-prereview sub-agent (NEXT-PREREVIEW-01).

The pre-review agent prepares decisions for a human reviewer and must not touch code,
admitted knowledge or admission records. This hook enforces its file scope:

- tools: Read, Grep, Glob, Write only (anything else is blocked);
- Write: only under research/prereview/;
- Read / Grep / Glob: only inside the allowlist below; Grep and Glob must name a path;
- always blocked: apps/, knowledge/, admissions, protected files (see docs/HANDOVER.md).

Exit code 2 blocks the call; the stderr message is shown to the agent.
Standard library only; runs under the system /usr/bin/python3 (3.9+).
"""

import json
import os
import sys

ALLOWED_TOOLS = {"Read", "Grep", "Glob", "Write"}
WRITE_ROOTS = ("research/prereview",)
READ_ROOTS = (
    "research/prereview",
    "research/next_dasha_01_review",
    "docs/HANDOVER.md",
    "docs/ASTROLOGY_METHOD.md",
    "docs/DIGNITY_SOURCE_ADMISSION.md",
    "पराशरहोराशास्त्र Brihat Parashar Hora Shastra _text.pdf",
)
# Substrings that are blocked anywhere in a resolved path or pattern, whatever the root.
BLOCKED_PARTS = (
    "apps/",
    "knowledge/",
    "docs/admissions",
    "jyotai-marriage-pack-research",
    "google-adk",
    "next_08d",
    ".env",
)


def block(message: str) -> None:
    sys.stderr.write(f"jyotish-prereview guard: {message}\n")
    sys.exit(2)


def under(rel: str, roots: tuple[str, ...]) -> bool:
    return any(rel == root or rel.startswith(root.rstrip("/") + "/") for root in roots)


def relative(project: str, raw: str, cwd: str) -> str:
    path = raw if os.path.isabs(raw) else os.path.join(cwd, raw)
    resolved = os.path.realpath(path)
    rel = os.path.relpath(resolved, project)
    if rel.startswith(".."):
        block(f"path outside the project is not allowed: {raw}")
    return rel


def check_blocked(text: str) -> None:
    lowered = text.lower()
    for part in BLOCKED_PARTS:
        if part in lowered:
            block(f"access to '{part}' is not allowed: {text}")


def main() -> None:
    payload = json.load(sys.stdin)
    tool = payload.get("tool_name", "")
    args = payload.get("tool_input", {}) or {}
    project = os.path.realpath(
        os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    )
    cwd = payload.get("cwd") or project

    if tool not in ALLOWED_TOOLS:
        block(f"tool '{tool}' is not allowed for this agent")

    if tool in ("Read", "Write"):
        raw = args.get("file_path")
        if not raw:
            block(f"{tool} needs a file_path")
        rel = relative(project, raw, cwd)
        check_blocked(rel)
        roots = WRITE_ROOTS if tool == "Write" else READ_ROOTS
        if not under(rel, roots):
            block(f"{tool} outside {', '.join(roots)} is not allowed: {rel}")
        return

    # Grep / Glob: an explicit, allowlisted path is required (the default would be the
    # project root, which contains code and protected files).
    raw = args.get("path")
    if not raw:
        block(f"{tool} must name a path inside: {', '.join(READ_ROOTS)}")
    rel = relative(project, raw, cwd)
    check_blocked(rel)
    if not under(rel, READ_ROOTS):
        block(f"{tool} outside {', '.join(READ_ROOTS)} is not allowed: {rel}")
    for key in ("pattern", "glob") if tool == "Glob" else ("glob",):
        value = args.get(key) or ""
        if ".." in value or value.startswith("/"):
            block(f"{tool} {key} may not leave its path: {value}")
        check_blocked(value)


if __name__ == "__main__":
    main()
