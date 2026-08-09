from __future__ import annotations

from pathlib import Path

from devflow.tools.registry import ToolResult
from devflow.tools.workspace import Workspace, WorkspaceError


MAX_READ_CHARACTERS = 20_000
MAX_LIST_ENTRIES = 500
MAX_SEARCH_MATCHES = 100
IGNORED_DIRECTORIES = {
    ".git",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "env",
    "node_modules",
    "venv",
}


def _ignored(workspace: Workspace, path: Path) -> bool:
    relative_parts = path.relative_to(workspace.root).parts
    return any(part in IGNORED_DIRECTORIES for part in relative_parts)


def list_files(
    workspace: Workspace,
    directory: str = ".",
    recursive: bool = False,
) -> ToolResult:
    try:
        target = workspace.resolve(directory)
        if not target.is_dir():
            return ToolResult.failure(f"Directory does not exist: {directory}")

        iterator = target.rglob("*") if recursive else target.iterdir()
        entries: list[str] = []
        for path in sorted(iterator, key=lambda item: str(item).lower()):
            if _ignored(workspace, path) or workspace.is_sensitive(path):
                continue
            relative = workspace.relative(path)
            if path.is_dir():
                entries.append(f"- {relative}/ (directory)")
            else:
                entries.append(f"- {relative} ({path.stat().st_size} bytes)")
            if len(entries) >= MAX_LIST_ENTRIES:
                entries.append(f"[Truncated after {MAX_LIST_ENTRIES} entries]")
                break

        return ToolResult.ok("\n".join(entries) if entries else "Directory is empty.")
    except (OSError, WorkspaceError) as exc:
        return ToolResult.failure(str(exc))


def read_file(workspace: Workspace, file_path: str) -> ToolResult:
    try:
        target = workspace.resolve(file_path)
        if workspace.is_sensitive(target):
            return ToolResult.failure(f"Reading sensitive file is not allowed: {file_path}")
        if not target.is_file():
            return ToolResult.failure(f"File does not exist: {file_path}")

        with target.open("r", encoding="utf-8", errors="replace") as handle:
            content = handle.read(MAX_READ_CHARACTERS + 1)
        if len(content) > MAX_READ_CHARACTERS:
            content = content[:MAX_READ_CHARACTERS]
            content += "\n\n[Content truncated due to size limit.]"
        return ToolResult.ok(content)
    except (OSError, WorkspaceError) as exc:
        return ToolResult.failure(str(exc))


def search_files(
    workspace: Workspace,
    query: str,
    directory: str = ".",
    file_pattern: str = "*",
) -> ToolResult:
    if not query:
        return ToolResult.failure("Search query must not be empty.")

    try:
        target = workspace.resolve(directory)
        if not target.is_dir():
            return ToolResult.failure(f"Directory does not exist: {directory}")

        matches: list[str] = []
        lowered_query = query.casefold()
        for path in target.rglob(file_pattern):
            if not path.is_file() or _ignored(workspace, path) or workspace.is_sensitive(path):
                continue
            try:
                with path.open("r", encoding="utf-8", errors="replace") as handle:
                    for line_number, line in enumerate(handle, start=1):
                        if lowered_query in line.casefold():
                            matches.append(
                                f"{workspace.relative(path)}:{line_number}: {line.rstrip()}"
                            )
                            if len(matches) >= MAX_SEARCH_MATCHES:
                                matches.append(
                                    f"[Truncated after {MAX_SEARCH_MATCHES} matches]"
                                )
                                return ToolResult.ok("\n".join(matches))
            except OSError:
                continue

        return ToolResult.ok("\n".join(matches) if matches else "No matches found.")
    except (OSError, ValueError, WorkspaceError) as exc:
        return ToolResult.failure(str(exc))


def write_file(workspace: Workspace, file_path: str, content: str) -> ToolResult:
    try:
        target = workspace.resolve(file_path)
        if workspace.is_sensitive(target):
            return ToolResult.failure(f"Writing sensitive file is not allowed: {file_path}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return ToolResult.ok(
            f"Wrote {len(content)} characters to {workspace.relative(target)}."
        )
    except (OSError, WorkspaceError) as exc:
        return ToolResult.failure(str(exc))
