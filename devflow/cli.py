from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from dotenv import load_dotenv

from devflow.agent.prompts import build_system_prompt
from devflow.agent.runtime import AgentRuntime
from devflow.gemini import GeminiSession
from devflow.skills import SkillCatalog
from devflow.tools.registry import create_default_registry
from devflow.tools.workspace import Workspace, WorkspaceError


DEFAULT_MODEL = "gemini-3.5-flash-lite"
DEFAULT_SKILLS_DIR = Path(__file__).resolve().parents[1] / ".github" / "skills"


def configure_output_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="devflow",
        description="Run the DevFlow engineering agent against a workspace.",
    )
    parser.add_argument(
        "--workspace",
        required=True,
        help="Path to the repository DevFlow may inspect and modify.",
    )
    parser.add_argument(
        "--skills-dir",
        help=(
            "Read-only Agent Skills directory. Defaults to DevFlow's "
            ".github/skills directory."
        ),
    )
    parser.add_argument("--verbose", action="store_true", help="Show tool activity.")
    parser.add_argument("prompt", help="Engineering task for DevFlow.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv()

    try:
        workspace = Workspace.from_path(args.workspace)
    except WorkspaceError as exc:
        print(f"Workspace error: {exc}", file=sys.stderr)
        return 2

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Configuration error: GEMINI_API_KEY is not set.", file=sys.stderr)
        return 2

    skills_directory = Path(args.skills_dir) if args.skills_dir else DEFAULT_SKILLS_DIR
    skill_catalog = SkillCatalog.discover(skills_directory)
    if args.verbose:
        for issue in skill_catalog.issues:
            print(
                f"Skipped invalid skill '{issue.directory_name}': {issue.error}",
                file=sys.stderr,
            )

    registry = create_default_registry(workspace, skill_catalog)
    session = GeminiSession(
        api_key=api_key,
        model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
        system_prompt=build_system_prompt(skill_catalog.prompt_catalog()),
        tools=registry.definitions,
    )
    result = AgentRuntime(
        session=session,
        registry=registry,
        verbose=args.verbose,
    ).run(args.prompt)

    if result.success:
        print(result.output)
        return 0

    print(f"DevFlow error: {result.error}", file=sys.stderr)
    return 1


def entrypoint() -> None:
    configure_output_streams()
    raise SystemExit(main())
