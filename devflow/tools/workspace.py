from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class WorkspaceError(ValueError):
    """Raised when a workspace or workspace-relative path is invalid."""


@dataclass(frozen=True)
class Workspace:
    root: Path

    @classmethod
    def from_path(cls, path: str | Path) -> "Workspace":
        root = Path(path).expanduser().resolve(strict=False)
        if not root.exists():
            raise WorkspaceError(f"Workspace does not exist: {root}")
        if not root.is_dir():
            raise WorkspaceError(f"Workspace is not a directory: {root}")
        return cls(root=root.resolve(strict=True))

    def resolve(self, relative_path: str | Path = ".") -> Path:
        requested = Path(relative_path)
        if requested.is_absolute():
            raise WorkspaceError("Tool paths must be relative to the workspace.")

        candidate = (self.root / requested).resolve(strict=False)
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise WorkspaceError(
                f"Path escapes the workspace: {relative_path}"
            ) from exc
        return candidate

    def relative(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix() or "."

    def is_sensitive(self, path: Path) -> bool:
        name = path.name.lower()
        return name == ".env" or (name.startswith(".env.") and name != ".env.example")
