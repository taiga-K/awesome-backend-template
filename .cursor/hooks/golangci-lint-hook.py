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
LOCK_FILE = REPO_ROOT / ".cursor" / "hooks" / ".golangci-lint-hook.lock"
GOLANGCI_TIMEOUT_SECONDS = 180
USAGE = "usage: golangci-lint-hook.py [after-file-edit|post-tool-use]"


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


def has_go_module() -> bool:
    return (REPO_ROOT / "go.mod").is_file()


def run_golangci_lint() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["golangci-lint", "run", "./..."],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=GOLANGCI_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return False, f"golangci-lint timed out after {GOLANGCI_TIMEOUT_SECONDS} seconds"

    output_parts: list[str] = []
    if result.stdout:
        output_parts.append(result.stdout.rstrip())
    if result.stderr:
        output_parts.append(result.stderr.rstrip())
    combined_output = "\n".join(part for part in output_parts if part).strip()

    return result.returncode == 0, combined_output


def handle_after_file_edit() -> int:
    golangci_path = shutil.which("golangci-lint")
    if golangci_path is None:
        print("[golangci-lint-hook] golangci-lint not found in PATH; skipped", file=sys.stderr)
        return 0

    if not has_go_module():
        print("[golangci-lint-hook] go.mod not found at repo root; skipped", file=sys.stderr)
        return 0

    ok, output = run_golangci_lint()
    if ok:
        print(f"[golangci-lint-hook] golangci-lint: OK ({golangci_path})", file=sys.stderr)
        return 0

    print(f"[golangci-lint-hook] golangci-lint: NG ({golangci_path})", file=sys.stderr)
    if output:
        print(output, file=sys.stderr)
    return 0


def handle_post_tool_use() -> int:
    golangci_path = shutil.which("golangci-lint")
    if golangci_path is None:
        emit_json(
            {
                "additional_context": (
                    "Go ファイルの編集を検知しましたが、`golangci-lint` が PATH 上に見つかりません。"
                    " このリポジトリでは Go の変更後に `golangci-lint run ./...` を実行して"
                    " 問題がない状態にしてください。"
                )
            }
        )
        return 0

    if not has_go_module():
        emit_json({})
        return 0

    ok, output = run_golangci_lint()
    if ok:
        emit_json({})
        return 0

    message = (
        "Go ファイルの編集後に `golangci-lint run ./...` が失敗しました。"
        " この指摘を解消するようにコードを修正してください。\n"
        f"golangci-lint binary: {golangci_path}\n"
        f"golangci-lint output:\n{output or '(no output)'}"
    )
    emit_json({"additional_context": message})
    return 0


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"after-file-edit", "post-tool-use"}:
        print(f"[golangci-lint-hook] {USAGE}", file=sys.stderr)
        return 0

    mode = sys.argv[1]
    raw_input = sys.stdin.read()
    if not raw_input.strip():
        return 0

    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError:
        print("[golangci-lint-hook] invalid hook payload; skipped", file=sys.stderr)
        return 0

    if not is_target_edit(payload):
        return 0

    try:
        lock_fd = LOCK_FILE.open("x")
    except FileExistsError:
        print("[golangci-lint-hook] golangci-lint already running; skipped", file=sys.stderr)
        if mode == "post-tool-use":
            emit_json(
                {
                    "additional_context": (
                        "Go ファイルの編集を検知しましたが、別の `golangci-lint run ./...` 実行が進行中のため"
                        " 今回のチェックはスキップされました。必要なら再度 `golangci-lint run ./...` を実行して"
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
