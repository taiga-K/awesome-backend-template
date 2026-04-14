#!/usr/bin/env python3

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


TARGET_PATH_PATTERN = re.compile(r"(^|/)[^/\s]+\.go$")
REPO_ROOT = Path(__file__).resolve().parents[2]
LOCK_FILE = REPO_ROOT / ".cursor" / "hooks" / ".gosec-auto-fix.lock"
GOSEC_TIMEOUT_SECONDS = 60
USAGE = "usage: gosec-auto-fix.py [after-file-edit|post-tool-use]"


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
        normalized = text.replace("\\", "/").strip()
        if TARGET_PATH_PATTERN.search(normalized):
            return True
    return False


def emit_json(payload: dict[str, str]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def run_gosec() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["gosec", "./..."],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=GOSEC_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return False, f"gosec timed out after {GOSEC_TIMEOUT_SECONDS} seconds"

    output_parts: list[str] = []
    if result.stdout:
        output_parts.append(result.stdout.rstrip())
    if result.stderr:
        output_parts.append(result.stderr.rstrip())
    combined_output = "\n".join(part for part in output_parts if part).strip()

    return result.returncode == 0, combined_output


def handle_after_file_edit() -> int:
    gosec_path = shutil.which("gosec")
    if gosec_path is None:
        print("[gosec-hook] gosec not found in PATH; skipped", file=sys.stderr)
        return 0

    ok, output = run_gosec()
    if ok:
        print(f"[gosec-hook] gosec: OK ({gosec_path})", file=sys.stderr)
        return 0

    print(f"[gosec-hook] gosec: NG ({gosec_path})", file=sys.stderr)
    if output:
        print(output, file=sys.stderr)
    return 0


def handle_post_tool_use() -> int:
    gosec_path = shutil.which("gosec")
    if gosec_path is None:
        emit_json(
            {
                "additional_context": (
                    "Go ファイルの編集を検知しましたが、`gosec` が PATH 上に見つかりません。"
                    " このリポジトリでは Go の変更後に `gosec ./...` を実行して"
                    " 問題がない状態にしてください。"
                )
            }
        )
        return 0

    ok, output = run_gosec()
    if ok:
        emit_json({})
        return 0

    message = (
        "Go ファイルの編集後に `gosec ./...` が失敗しました。"
        " この指摘を解消するようにコードを修正してください。\n"
        f"gosec binary: {gosec_path}\n"
        f"gosec output:\n{output or '(no output)'}"
    )
    emit_json({"additional_context": message})
    return 0


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"after-file-edit", "post-tool-use"}:
        print(f"[gosec-hook] {USAGE}", file=sys.stderr)
        return 0

    mode = sys.argv[1]
    raw_input = sys.stdin.read()
    if not raw_input.strip():
        return 0

    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError:
        print("[gosec-hook] invalid hook payload; skipped", file=sys.stderr)
        return 0

    if not is_target_edit(payload):
        return 0

    try:
        lock_fd = LOCK_FILE.open("x")
    except FileExistsError:
        print("[gosec-hook] gosec already running; skipped", file=sys.stderr)
        if mode == "post-tool-use":
            emit_json(
                {
                    "additional_context": (
                        "Go ファイルの編集を検知しましたが、別の `gosec ./...` 実行が進行中のため"
                        " 今回のチェックはスキップされました。必要なら再度 `gosec ./...` を実行して"
                        " 問題がないことを確認してください。"
                    )
                }
            )
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
