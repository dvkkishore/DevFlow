from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from devflow.agent.prompts import build_system_prompt
from devflow.agent.runtime import AgentRuntime
from devflow.gemini import GeminiToolCall, GeminiTurn
from devflow.skills import SkillCatalog
from devflow.tools.registry import create_default_registry
from devflow.tools.workspace import Workspace


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "skill_workspace"
FIXTURE_SKILLS_DIR = FIXTURE_ROOT / ".github" / "skills"


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


class SkillCatalogTests(unittest.TestCase):
    def test_valid_skill_discovery_loads_metadata_only(self) -> None:
        catalog = SkillCatalog.discover(FIXTURE_SKILLS_DIR)

        self.assertEqual(len(catalog.metadata), 1)
        self.assertEqual(catalog.metadata[0].name, "sample-guidance")
        self.assertIn("progressive Agent Skill loading", catalog.metadata[0].description)
        self.assertFalse(hasattr(catalog.metadata[0], "content"))
        self.assertEqual(catalog.issues, ())

    def test_invalid_or_missing_frontmatter_and_missing_file_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            skills_root = root / ".github" / "skills"
            invalid = skills_root / "invalid-skill"
            invalid.mkdir(parents=True)
            (invalid / "SKILL.md").write_text("# Missing frontmatter\n", encoding="utf-8")
            missing_description = skills_root / "missing-description"
            missing_description.mkdir()
            (missing_description / "SKILL.md").write_text(
                "---\nname: missing-description\n---\nBody\n",
                encoding="utf-8",
            )
            (skills_root / "missing-file").mkdir()

            catalog = SkillCatalog.discover(skills_root)

        self.assertEqual(catalog.metadata, ())
        errors = {issue.directory_name: issue.error for issue in catalog.issues}
        self.assertIn("must begin with YAML frontmatter", errors["invalid-skill"])
        self.assertIn("requires a non-empty description", errors["missing-description"])
        self.assertIn("must contain SKILL.md", errors["missing-file"])
        invalid_result = catalog.load_skill("invalid-skill")
        self.assertFalse(invalid_result.success)
        self.assertIn("is invalid", invalid_result.error or "")

    def test_name_must_match_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            skill_directory = root / ".github" / "skills" / "expected-name"
            skill_directory.mkdir(parents=True)
            (skill_directory / "SKILL.md").write_text(
                "---\nname: different-name\ndescription: Test mismatch.\n---\nBody\n",
                encoding="utf-8",
            )

            catalog = SkillCatalog.discover(root / ".github" / "skills")

        self.assertEqual(catalog.metadata, ())
        self.assertIn("does not match directory", catalog.issues[0].error)

    def test_startup_context_contains_catalog_but_not_skill_body(self) -> None:
        catalog = SkillCatalog.discover(FIXTURE_SKILLS_DIR)
        prompt = build_system_prompt(catalog.prompt_catalog())

        self.assertIn("sample-guidance", prompt)
        self.assertIn("progressive Agent Skill loading", prompt)
        self.assertNotIn("UNIQUE_SKILL_BODY_MARKER", prompt)
        self.assertNotIn("Inspect the relevant input", prompt)

    def test_load_skill_returns_full_selected_skill(self) -> None:
        catalog = SkillCatalog.discover(FIXTURE_SKILLS_DIR)
        result = catalog.load_skill("sample-guidance")

        self.assertTrue(result.success)
        self.assertIn("name: sample-guidance", result.output)
        self.assertIn("UNIQUE_SKILL_BODY_MARKER", result.output)

    def test_unknown_skill_returns_clean_error(self) -> None:
        catalog = SkillCatalog.discover(FIXTURE_SKILLS_DIR)
        result = catalog.load_skill("not-present")

        self.assertFalse(result.success)
        self.assertEqual(result.error, "Unknown skill: not-present")

    def test_runtime_loads_skill_and_continues_agent_loop(self) -> None:
        with tempfile.TemporaryDirectory() as target_directory:
            workspace = Workspace.from_path(target_directory)
            catalog = SkillCatalog.discover(FIXTURE_SKILLS_DIR)
            registry = create_default_registry(workspace, catalog)
            session = FakeSession(
                [
                    GeminiTurn(
                        text="",
                        tool_calls=(
                            GeminiToolCall("load_skill", {"name": "sample-guidance"}),
                        ),
                    ),
                    GeminiTurn(text="Skill instructions applied.", tool_calls=()),
                ]
            )

            result = AgentRuntime(session, registry, max_iterations=3).run("Use the skill")

        self.assertTrue(result.success)
        self.assertEqual(result.output, "Skill instructions applied.")
        self.assertEqual(len(session.tool_results), 1)
        loaded = session.tool_results[0][1]
        self.assertTrue(loaded.success)
        self.assertIn("UNIQUE_SKILL_BODY_MARKER", loaded.output)

    def test_skills_directory_is_independent_and_not_a_write_workspace(self) -> None:
        skill_file = FIXTURE_SKILLS_DIR / "sample-guidance" / "SKILL.md"
        original_content = skill_file.read_text(encoding="utf-8")

        with tempfile.TemporaryDirectory() as target_directory:
            workspace = Workspace.from_path(target_directory)
            catalog = SkillCatalog.discover(FIXTURE_SKILLS_DIR)
            registry = create_default_registry(workspace, catalog)

            loaded = registry.execute("load_skill", {"name": "sample-guidance"})
            attempted_write = registry.execute(
                "write_file",
                {"file_path": str(skill_file.resolve()), "content": "changed"},
            )

        self.assertTrue(loaded.success)
        self.assertIn("UNIQUE_SKILL_BODY_MARKER", loaded.output)
        self.assertFalse(attempted_write.success)
        self.assertIn("relative to the workspace", attempted_write.error or "")
        self.assertEqual(skill_file.read_text(encoding="utf-8"), original_content)

    def test_name_longer_than_64_characters_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skills_root = Path(temporary_directory)
            long_name = "a" * 65
            skill_directory = skills_root / long_name
            skill_directory.mkdir()
            (skill_directory / "SKILL.md").write_text(
                f"---\nname: {long_name}\ndescription: Too long name.\n---\nBody\n",
                encoding="utf-8",
            )

            catalog = SkillCatalog.discover(skills_root)

        self.assertEqual(catalog.metadata, ())
        self.assertIn("at most 64 characters", catalog.issues[0].error)

    def test_description_longer_than_1024_characters_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skills_root = Path(temporary_directory)
            skill_directory = skills_root / "long-description"
            skill_directory.mkdir()
            description = "d" * 1025
            (skill_directory / "SKILL.md").write_text(
                "---\n"
                "name: long-description\n"
                f"description: {description}\n"
                "---\nBody\n",
                encoding="utf-8",
            )

            catalog = SkillCatalog.discover(skills_root)

        self.assertEqual(catalog.metadata, ())
        self.assertIn("at most 1024 characters", catalog.issues[0].error)


if __name__ == "__main__":
    unittest.main()
