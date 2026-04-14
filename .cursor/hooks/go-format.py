#!/usr/bin/env python3

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCK_FILE = REPO_ROOT / ".cursor" / "hooks" / ".go-format.lock"
USAGE = "usage: go-format.py [after-file-edit|post-tool-use]"
GO_FILE_PATTERN = re.compile(r"(^|/)[^/\s]+\.go$")
GO_PATH_CANDIDATE_PATTERN = re.compile(r"(?P<path>(?:/|\.{1,2}/)?[^\s\"'`]+\.go)")


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


def resolve_repo_file(candidate: str) -> Path | None:
    normalized = candidate.replace("\\", "/").strip().strip("\"'`")
    if not normalized or not GO_FILE_PATTERN.search(normalized):
        return None

    path = Path(normalized)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    else:
        path = path.resolve()

    try:
        path.relative_to(REPO_ROOT)
    except ValueError:
        return None

    if not path.is_file():
        return None

    return path


def collect_target_files(payload: Any) -> list[Path]:
    seen: set[Path] = set()
    targets: list[Path] = []

    for text in iter_strings(payload):
        direct = resolve_repo_file(text)
        if direct is not None and direct not in seen:
            seen.add(direct)
            targets.append(direct)
            continue

        for match in GO_PATH_CANDIDATE_PATTERN.finditer(text.replace("\\", "/")):
            candidate = resolve_repo_file(match.group("path"))
            if candidate is None or candidate in seen:
                continue
            seen.add(candidate)
            targets.append(candidate)

    return targets


def emit_json(payload: dict[str, str]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def get_goimports_path() -> str | None:
    goimports_path = shutil.which("goimports")
    if goimports_path is not None:
        return goimports_path

    for env_name in ("GOBIN", "GOPATH"):
        env_value = subprocess.run(
            ["go", "env", env_name],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if not env_value:
            continue

        candidate = Path(env_value) / "goimports" if env_name == "GOBIN" else Path(env_value) / "bin" / "goimports"
        if candidate.is_file():
            return str(candidate)

    return None


def run_formatter(files: list[Path]) -> tuple[bool, str, str]:
    formatter_path = get_goimports_path()
    formatter_name = "goimports"
    command = ["-w", *[str(path) for path in files]]

    if formatter_path is None:
        formatter_path = shutil.which("gofmt")
        formatter_name = "gofmt"
        if formatter_path is None:
            return False, "goimports and gofmt were not found in PATH", "formatter"

    result = subprocess.run(
        [formatter_path, *command],
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
    return result.returncode == 0, combined_output, formatter_name


def handle_after_file_edit(files: list[Path]) -> int:
    ok, output, formatter_name = run_formatter(files)
    if ok:
        print(
            f"[go-format-hook] {formatter_name}: OK "
            + ", ".join(str(path.relative_to(REPO_ROOT)) for path in files),
            file=sys.stderr,
        )
        return 0

    print(f"[go-format-hook] {formatter_name}: NG", file=sys.stderr)
    if output:
        print(output, file=sys.stderr)
    return 0


def handle_post_tool_use(files: list[Path]) -> int:
    ok, output, formatter_name = run_formatter(files)
    if ok:
        emit_json({})
        return 0

    emit_json(
        {
            "additional_context": (
                "Go ファイルの整形に失敗しました。"
                f" `{formatter_name} -w` が通るように修正してください。\n"
                f"formatter output:\n{output or '(no output)'}"
            )
        }
    )
    return 0


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"after-file-edit", "post-tool-use"}:
        print(f"[go-format-hook] {USAGE}", file=sys.stderr)
        return 0

    mode = sys.argv[1]
    raw_input = sys.stdin.read()
    if not raw_input.strip():
        return 0

    try:
        payload = json.loads(raw_input)
    except json.JSONDecodeError:
        print("[go-format-hook] invalid hook payload; skipped", file=sys.stderr)
        return 0

    target_files = collect_target_files(payload)
    if not target_files:
        if mode == "post-tool-use":
            emit_json({})
        return 0

    try:
        lock_fd = LOCK_FILE.open("x")
    except FileExistsError:
        print("[go-format-hook] formatter already running; skipped", file=sys.stderr)
        if mode == "post-tool-use":
            emit_json({})
        return 0

    try:
        if mode == "after-file-edit":
            return handle_after_file_edit(target_files)
        return handle_post_tool_use(target_files)
    finally:
        lock_fd.close()
        LOCK_FILE.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
