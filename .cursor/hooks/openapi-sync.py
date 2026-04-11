#!/usr/bin/env python3

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


TARGET_PATH_PATTERN = re.compile(
    r"(^|/)(docs/api/openapi\.yaml|docs/api/components/|docs/api/paths/)"
)

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCK_FILE = REPO_ROOT / ".cursor" / "hooks" / ".openapi-sync.lock"
USAGE = "usage: openapi-sync.py [after-file-edit|post-tool-use]"


def iter_strings(value: Any):
    if isinstance(value, str):
        yield value
        return

    if isinstance(value, dict):
        for key, nested_value in value.items():
            yield from iter_strings(key)
            yield from iter_strings(nested_value)
        return

    if isinstance(value, list):
        for item in value:
            yield from iter_strings(item)


def is_target_edit(payload: Any) -> bool:
    for text in iter_strings(payload):
        normalized = text.replace("\\", "/")
        if TARGET_PATH_PATTERN.search(normalized):
            return True
    return False


def run(command: list[str], label: str) -> tuple[bool, str]:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    output_parts: list[str] = []
    if result.stdout:
        output_parts.append(result.stdout.rstrip())
    if result.stderr:
        output_parts.append(result.stderr.rstrip())
    combined_output = "\n".join(part for part in output_parts if part).strip()

    if result.returncode == 0:
        print(f"[openapi-hook] {label}: OK", file=sys.stderr)
        return True, combined_output

    print(f"[openapi-hook] {label}: NG", file=sys.stderr)
    if combined_output:
        print(combined_output, file=sys.stderr)
    return False, combined_output


def emit_additional_context(message: str) -> None:
    print(
        json.dumps(
            {
                "additional_context": message,
            },
            ensure_ascii=False,
        )
    )


def bundle_openapi() -> bool:
    ok, _ = run(
        ["npx", "@redocly/cli", "bundle", "docs/api/openapi.yaml", "--output", "docs/api/api_schema.yaml"],
        "bundle",
    )
    return ok


def handle_after_file_edit() -> int:
    ok, _ = run(
        ["npx", "@redocly/cli", "lint", "--config", "redocly.yaml", "docs/api/openapi.yaml"],
        "lint",
    )
    if not ok:
        return 0

    bundle_openapi()
    return 0


def handle_post_tool_use() -> int:
    ok, lint_output = run(
        ["npx", "@redocly/cli", "lint", "--config", "redocly.yaml", "docs/api/openapi.yaml"],
        "lint",
    )
    if not ok:
        message = (
            "OpenAPI の lint に失敗しました。今回の編集が原因の可能性が高いので修正してください。\n"
            "対象: docs/api/openapi.yaml, docs/api/components/**, docs/api/paths/**\n"
            f"lint 出力:\n{lint_output or '(no output)'}"
        )
        emit_additional_context(message)
        return 0

    if not bundle_openapi():
        emit_additional_context(
            "OpenAPI の lint は成功しましたが、docs/api/api_schema.yaml の bundle 更新に失敗しました。"
            " bundle エラーを確認して修正してください。"
        )
        return 0

    print("{}")
    return 0


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"after-file-edit", "post-tool-use"}:
        print(f"[openapi-hook] {USAGE}", file=sys.stderr)
        return 0

    mode = sys.argv[1]
    raw_input = sys.stdin.read()
    if not raw_input.strip():
        return 0

    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError:
        print("[openapi-hook] invalid hook payload; skipped", file=sys.stderr)
        return 0

    if not is_target_edit(payload):
        return 0

    try:
        lock_fd = LOCK_FILE.open("x")
    except FileExistsError:
        print("[openapi-hook] sync already running; skipped", file=sys.stderr)
        if mode == "post-tool-use":
            print("{}")
        return 0

    try:
        if mode == "after-file-edit":
            return handle_after_file_edit()
        return handle_post_tool_use()
    finally:
        lock_fd.close()
        LOCK_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
