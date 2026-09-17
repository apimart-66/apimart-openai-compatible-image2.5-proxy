#!/usr/bin/env python3
"""Local-only scanner for OpenAI-compatible migration-sensitive code paths."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TEXT_SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".sh", ".md", ".json", ".yaml", ".yml", ".toml"}
IGNORED_DIRS = {".git", ".venv", "node_modules", "dist", "build", "__pycache__"}
PATTERNS = {
    "streaming_sse": re.compile(r"\bstream\s*[:=]\s*(?:True|true)|text/event-stream|chat\.completions.*stream", re.I | re.S),
    "tools_or_functions": re.compile(r"\btools\s*[:=]|\bfunctions\s*[:=]|tool_calls|function_call", re.I),
    "json_structured_output": re.compile(r"response_format|json_schema|json_object|structured output", re.I),
    "vision_image_input": re.compile(r"image_url|input_image|data:image/|vision", re.I),
    "responses_api": re.compile(r"responses\.create|/responses\b|response\.output", re.I),
    "custom_base_url": re.compile(r"base_url|OPENAI_BASE_URL|/v1/chat/completions", re.I),
}
POSSIBLE_KEY = re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{16,}")


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and not any(part in IGNORED_DIRS for part in path.parts):
            yield path


def scan(root: Path) -> dict:
    findings = {name: [] for name in PATTERNS}
    possible_keys = []
    files_scanned = 0
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        files_scanned += 1
        relative = str(path.relative_to(root)) if root.is_dir() else path.name
        for name, pattern in PATTERNS.items():
            if pattern.search(text):
                findings[name].append(relative)
        for line_number, line in enumerate(text.splitlines(), 1):
            if POSSIBLE_KEY.search(line):
                possible_keys.append({"file": relative, "line": line_number})
    return {
        "schema": "openai-compatible-migration-check-v1",
        "root": str(root.resolve()),
        "files_scanned": files_scanned,
        "risk_paths": findings,
        "possible_hardcoded_keys": possible_keys,
        "source_uploaded": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    if not args.path.exists():
        parser.error(f"path does not exist: {args.path}")
    report = scan(args.path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 2 if report["possible_hardcoded_keys"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
