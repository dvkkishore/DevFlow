from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from devflow.skills import SkillCatalog
from devflow.tools.registry import create_default_registry
from devflow.tools.workspace import Workspace


PRODUCTION_SKILLS_DIR = Path(__file__).parents[1] / ".github" / "skills"
EXPECTED_SKILLS = {"repo-understanding", "debug-and-fix"}


class ProductionSkillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = SkillCatalog.discover(PRODUCTION_SKILLS_DIR)

    def test_both_production_skills_are_discovered(self) -> None:
        discovered = {skill.name for skill in self.catalog.metadata}

        self.assertEqual(discovered, EXPECTED_SKILLS)
        self.assertEqual(self.catalog.issues, ())

    def test_startup_catalog_contains_metadata_not_full_bodies(self) -> None:
        startup_context = self.catalog.prompt_catalog()

        for skill in self.catalog.metadata:
            self.assertIn(f"- {skill.name}: {skill.description}", startup_context)

        self.assertNotIn("# Repository Understanding", startup_context)
        self.assertNotIn("# Debug and Fix", startup_context)
        self.assertNotIn("## Maintain evidence discipline", startup_context)
        self.assertNotIn("## Verify and iterate", startup_context)

    def test_each_production_skill_loads_individually(self) -> None:
        with tempfile.TemporaryDirectory() as target_directory:
            workspace = Workspace.from_path(target_directory)
            registry = create_default_registry(workspace, self.catalog)

            repo_result = registry.execute(
                "load_skill", {"name": "repo-understanding"}
            )
            debug_result = registry.execute(
                "load_skill", {"name": "debug-and-fix"}
            )

        self.assertTrue(repo_result.success)
        self.assertIn("# Repository Understanding", repo_result.output)
        self.assertIn("## Maintain evidence discipline", repo_result.output)

        self.assertTrue(debug_result.success)
        self.assertIn("# Debug and Fix", debug_result.output)
        self.assertIn("## Verify and iterate", debug_result.output)


if __name__ == "__main__":
    unittest.main()
