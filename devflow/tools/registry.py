from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Mapping

from devflow.tools.workspace import Workspace

if TYPE_CHECKING:
    from devflow.skills.manager import SkillCatalog


@dataclass(frozen=True)
class ToolResult:
    success: bool
    output: str = ""
    error: str | None = None
    exit_code: int | None = None

    @classmethod
    def ok(cls, output: str = "", exit_code: int | None = None) -> "ToolResult":
        return cls(success=True, output=output, exit_code=exit_code)

    @classmethod
    def failure(
        cls,
        error: str,
        output: str = "",
        exit_code: int | None = None,
    ) -> "ToolResult":
        return cls(success=False, output=output, error=error, exit_code=exit_code)

    def as_function_response(self) -> dict[str, Any]:
        response: dict[str, Any] = {"success": self.success}
        if self.output:
            response["output"] = self.output
        if self.error:
            response["error"] = self.error
        if self.exit_code is not None:
            response["exit_code"] = self.exit_code
        return response


ToolHandler = Callable[..., ToolResult]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        if definition.name in self._tools:
            raise ValueError(f"Tool is already registered: {definition.name}")
        self._tools[definition.name] = definition

    @property
    def definitions(self) -> tuple[ToolDefinition, ...]:
        return tuple(self._tools.values())

    def execute(self, name: str, arguments: Mapping[str, Any] | None) -> ToolResult:
        definition = self._tools.get(name)
        if definition is None:
            return ToolResult.failure(f"Unknown tool: {name}")

        try:
            result = definition.handler(**dict(arguments or {}))
        except TypeError as exc:
            return ToolResult.failure(f"Invalid arguments for tool '{name}': {exc}")
        except Exception as exc:
            return ToolResult.failure(f"Tool '{name}' failed unexpectedly: {exc}")

        if not isinstance(result, ToolResult):
            return ToolResult.failure(f"Tool '{name}' returned an invalid result.")
        return result


def create_default_registry(
    workspace: Workspace,
    skill_catalog: "SkillCatalog | None" = None,
) -> ToolRegistry:
    from devflow.tools.execution import run_command
    from devflow.tools.filesystem import list_files, read_file, search_files, write_file

    registry = ToolRegistry()
    if skill_catalog is not None:
        registry.register(
            ToolDefinition(
                name="load_skill",
                description=(
                    "Load the full SKILL.md instructions for one discovered Agent Skill. "
                    "When a request matches an available skill description, use this "
                    "read-only tool before other tools. It does not execute scripts or "
                    "resources."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Exact skill name from the available skill catalog.",
                        }
                    },
                    "required": ["name"],
                },
                handler=skill_catalog.load_skill,
            )
        )
    registry.register(
        ToolDefinition(
            name="list_files",
            description="List files and directories inside the workspace.",
            parameters={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Workspace-relative directory to list.",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to list descendants recursively.",
                    },
                },
            },
            handler=partial(list_files, workspace),
        )
    )
    registry.register(
        ToolDefinition(
            name="read_file",
            description="Read a UTF-8 text file inside the workspace.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Workspace-relative path of the file to read.",
                    }
                },
                "required": ["file_path"],
            },
            handler=partial(read_file, workspace),
        )
    )
    registry.register(
        ToolDefinition(
            name="search_files",
            description="Search text files recursively inside the workspace.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text to find."},
                    "directory": {
                        "type": "string",
                        "description": "Workspace-relative directory to search.",
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Optional glob such as *.py.",
                    },
                },
                "required": ["query"],
            },
            handler=partial(search_files, workspace),
        )
    )
    registry.register(
        ToolDefinition(
            name="write_file",
            description="Create or overwrite a UTF-8 text file inside the workspace.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Workspace-relative destination path.",
                    },
                    "content": {"type": "string", "description": "Complete file content."},
                },
                "required": ["file_path", "content"],
            },
            handler=partial(write_file, workspace),
        )
    )
    registry.register(
        ToolDefinition(
            name="run_command",
            description=(
                "Run an allowed development command in the workspace without a shell and "
                "return stdout, stderr, and exit status. Commands use the workspace as "
                "their current directory, but do not run in an OS-level sandbox."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Executable and arguments as separate strings.",
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Timeout from 1 to 120 seconds.",
                    },
                },
                "required": ["command"],
            },
            handler=partial(run_command, workspace),
        )
    )
    return registry
