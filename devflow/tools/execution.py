from __future__ import annotations

import os
import subprocess
import sys

from devflow.tools.registry import ToolResult
from devflow.tools.workspace import Workspace


ALLOWED_EXECUTABLES = {
    "git",
    "mypy",
    "node",
    "npm",
    "npx",
    "py",
    "pytest",
    "python",
    "python3",
    "ruff",
    "uv",
}
DEFAULT_TIMEOUT_SECONDS = 30
MAX_TIMEOUT_SECONDS = 120
PROVIDER_CREDENTIAL_ENV_KEYS = {"GEMINI_API_KEY", "GOOGLE_API_KEY"}
SAFE_GIT_SUBCOMMANDS = {
    "blame",
    "cat-file",
    "diff",
    "grep",
    "log",
    "ls-files",
    "ls-tree",
    "rev-parse",
    "show",
    "status",
}


def _executable_name(command: str) -> str:
    name = os.path.basename(command).lower()
    for suffix in (".exe", ".cmd", ".bat"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def _format_output(stdout: str | None, stderr: str | None) -> str:
    sections: list[str] = []
    if stdout:
        sections.append(f"STDOUT:\n{stdout.rstrip()}")
    if stderr:
        sections.append(f"STDERR:\n{stderr.rstrip()}")
    return "\n".join(sections) or "Command produced no output."


def _subprocess_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for key in PROVIDER_CREDENTIAL_ENV_KEYS:
        environment.pop(key, None)
    return environment


def run_command(
    workspace: Workspace,
    command: list[str],
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> ToolResult:
    if not command or not all(isinstance(item, str) and item for item in command):
        return ToolResult.failure("Command must be a non-empty list of strings.")
    if not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= MAX_TIMEOUT_SECONDS:
        return ToolResult.failure(
            f"timeout_seconds must be between 1 and {MAX_TIMEOUT_SECONDS}."
        )

    executable = _executable_name(command[0])
    if executable not in ALLOWED_EXECUTABLES:
        allowed = ", ".join(sorted(ALLOWED_EXECUTABLES))
        return ToolResult.failure(
            f"Executable '{executable}' is not allowed. Allowed executables: {allowed}."
        )

    if executable == "git":
        subcommand = command[1].lower() if len(command) > 1 else ""
        if subcommand not in SAFE_GIT_SUBCOMMANDS:
            allowed = ", ".join(sorted(SAFE_GIT_SUBCOMMANDS))
            return ToolResult.failure(
                f"Git subcommand '{subcommand or '[missing]'}' is not allowed. "
                f"Allowed Git subcommands: {allowed}."
            )

    normalized_command = list(command)
    if executable in {"py", "python", "python3"}:
        normalized_command[0] = sys.executable

    try:
        completed = subprocess.run(
            normalized_command,
            cwd=workspace.root,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=_subprocess_environment(),
        )
    except subprocess.TimeoutExpired as exc:
        return ToolResult.failure(
            f"Command timed out after {timeout_seconds} seconds.",
            output=_format_output(exc.stdout, exc.stderr),
        )
    except OSError as exc:
        return ToolResult.failure(f"Could not execute command: {exc}")

    output = _format_output(completed.stdout, completed.stderr)
    if completed.returncode != 0:
        return ToolResult.failure(
            f"Command exited with status {completed.returncode}.",
            output=output,
            exit_code=completed.returncode,
        )
    return ToolResult.ok(output, exit_code=completed.returncode)
