from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from devflow.agent.runtime import AgentRuntime
from devflow.cli import build_parser
from devflow.gemini import GeminiToolCall, GeminiTurn
from devflow.tools.execution import run_command
from devflow.tools.registry import create_default_registry
from devflow.tools.workspace import Workspace, WorkspaceError


class WorkspaceAndToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        parent = Path(self.temporary_directory.name)
        self.root = parent / "project"
        self.root.mkdir()
        self.outside = parent / "project-other"
        self.outside.mkdir()
        self.workspace = Workspace.from_path(self.root)
        self.registry = create_default_registry(self.workspace)

    def test_workspace_accepts_internal_paths_and_rejects_escape(self) -> None:
        self.assertEqual(self.workspace.resolve("src/main.py"), self.root / "src" / "main.py")
        with self.assertRaises(WorkspaceError):
            self.workspace.resolve("../project-other/secret.txt")
        with self.assertRaises(WorkspaceError):
            self.workspace.resolve(self.outside / "secret.txt")

    def test_registry_provides_required_tools_and_normalized_results(self) -> None:
        (self.root / "src").mkdir()
        (self.root / "src" / "app.py").write_text(
            "def greet():\n    return 'hello'\n", encoding="utf-8"
        )

        names = {definition.name for definition in self.registry.definitions}
        self.assertEqual(
            names,
            {"list_files", "read_file", "search_files", "write_file", "run_command"},
        )

        listed = self.registry.execute("list_files", {"directory": "src"})
        self.assertTrue(listed.success)
        self.assertIn("src/app.py", listed.output)

        read = self.registry.execute("read_file", {"file_path": "src/app.py"})
        self.assertTrue(read.success)
        self.assertIn("def greet", read.output)

        searched = self.registry.execute("search_files", {"query": "greet"})
        self.assertTrue(searched.success)
        self.assertIn("src/app.py:1", searched.output)

        written = self.registry.execute(
            "write_file",
            {"file_path": "notes/result.txt", "content": "verified"},
        )
        self.assertTrue(written.success)
        self.assertEqual((self.root / "notes" / "result.txt").read_text(), "verified")

        missing = self.registry.execute("read_file", {"file_path": "missing.txt"})
        self.assertFalse(missing.success)
        self.assertIn("does not exist", missing.error or "")

    def test_unknown_tool_and_invalid_arguments_are_clean_failures(self) -> None:
        unknown = self.registry.execute("not_a_tool", {})
        self.assertFalse(unknown.success)
        self.assertEqual(unknown.error, "Unknown tool: not_a_tool")

        invalid = self.registry.execute("read_file", {})
        self.assertFalse(invalid.success)
        self.assertIn("Invalid arguments", invalid.error or "")

    def test_run_command_is_allowlisted_bounded_and_uses_no_shell(self) -> None:
        with patch.dict(
            os.environ,
            {
                "GEMINI_API_KEY": "devflow-secret",
                "GOOGLE_API_KEY": "alternate-secret",
                "DEVFLOW_TEST_VALUE": "preserved",
            },
        ):
            with patch("devflow.tools.execution.subprocess.run") as mocked_run:
                mocked_run.return_value = subprocess.CompletedProcess(
                    args=[sys.executable, "example.py"],
                    returncode=0,
                    stdout="ok\n",
                    stderr="",
                )
                result = run_command(self.workspace, ["python", "example.py"], 10)

        self.assertTrue(result.success)
        self.assertEqual(result.exit_code, 0)
        self.assertFalse(mocked_run.call_args.kwargs["shell"])
        self.assertEqual(mocked_run.call_args.kwargs["timeout"], 10)
        self.assertEqual(mocked_run.call_args.kwargs["cwd"], self.workspace.root)
        child_environment = mocked_run.call_args.kwargs["env"]
        self.assertNotIn("GEMINI_API_KEY", child_environment)
        self.assertNotIn("GOOGLE_API_KEY", child_environment)
        self.assertEqual(child_environment["DEVFLOW_TEST_VALUE"], "preserved")

        disallowed = run_command(self.workspace, ["powershell", "-Command", "Get-Date"])
        self.assertFalse(disallowed.success)
        self.assertIn("not allowed", disallowed.error or "")

        invalid_timeout = run_command(self.workspace, ["python", "example.py"], 121)
        self.assertFalse(invalid_timeout.success)
        self.assertIn("between 1 and 120", invalid_timeout.error or "")

        destructive_git = run_command(self.workspace, ["git", "reset", "--hard"])
        self.assertFalse(destructive_git.success)
        self.assertIn("Git subcommand 'reset' is not allowed", destructive_git.error or "")


class FakeSession:
    def __init__(self, turns: list[GeminiTurn]) -> None:
        self.turns = list(turns)
        self.prompts: list[str] = []
        self.tool_results = []

    def add_user_prompt(self, prompt: str) -> None:
        self.prompts.append(prompt)

    def generate(self) -> GeminiTurn:
        return self.turns.pop(0)

    def add_tool_result(self, call, result) -> None:
        self.tool_results.append((call, result))


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.workspace = Workspace.from_path(self.temporary_directory.name)
        self.registry = create_default_registry(self.workspace)

    def test_tool_failure_is_returned_to_model_and_agent_can_finish(self) -> None:
        session = FakeSession(
            [
                GeminiTurn(
                    text="",
                    tool_calls=(GeminiToolCall("unknown_tool", {}),),
                ),
                GeminiTurn(text="I could not use that tool.", tool_calls=()),
            ]
        )
        result = AgentRuntime(session, self.registry, max_iterations=3).run("Inspect")

        self.assertTrue(result.success)
        self.assertEqual(result.output, "I could not use that tool.")
        self.assertEqual(session.prompts, ["Inspect"])
        self.assertFalse(session.tool_results[0][1].success)

    def test_iteration_limit_returns_clean_failure(self) -> None:
        call = GeminiToolCall("list_files", {"directory": "."})
        session = FakeSession(
            [
                GeminiTurn(text="", tool_calls=(call,)),
                GeminiTurn(text="", tool_calls=(call,)),
            ]
        )
        result = AgentRuntime(session, self.registry, max_iterations=2).run("Keep looking")

        self.assertFalse(result.success)
        self.assertEqual(result.iterations, 2)
        self.assertIn("maximum iteration limit", result.error or "")

    def test_cli_requires_and_parses_workspace(self) -> None:
        args = build_parser().parse_args(
            [
                "--workspace",
                str(self.workspace.root),
                "--skills-dir",
                "skill-library",
                "Explain this repository",
            ]
        )
        self.assertEqual(args.workspace, str(self.workspace.root))
        self.assertEqual(args.skills_dir, "skill-library")
        self.assertEqual(args.prompt, "Explain this repository")


if __name__ == "__main__":
    unittest.main()
