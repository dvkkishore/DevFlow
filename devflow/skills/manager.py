from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from devflow.skills.parser import SkillValidationError, parse_skill_metadata
from devflow.tools.registry import ToolResult


@dataclass(frozen=True)
class SkillMetadata:
    name: str
    description: str
    skill_file: Path


@dataclass(frozen=True)
class SkillIssue:
    directory_name: str
    error: str


class SkillCatalog:
    def __init__(
        self,
        skills_root: Path,
        skills: tuple[SkillMetadata, ...] = (),
        issues: tuple[SkillIssue, ...] = (),
    ) -> None:
        self._skills_root = skills_root
        self._skills = {skill.name: skill for skill in skills}
        self._issues = issues
        self._invalid_by_directory = {
            issue.directory_name: issue.error for issue in issues
        }

    @classmethod
    def discover(cls, skills_directory: str | Path) -> "SkillCatalog":
        skills_root = Path(skills_directory).expanduser().resolve(strict=False)

        if not skills_root.exists():
            return cls(skills_root)
        if not skills_root.is_dir():
            return cls(
                skills_root,
                issues=(
                    SkillIssue(str(skills_root), "Skills path is not a directory."),
                )
            )

        skills: list[SkillMetadata] = []
        issues: list[SkillIssue] = []
        try:
            directories = sorted(
                (path for path in skills_root.iterdir() if path.is_dir()),
                key=lambda path: path.name,
            )
        except OSError as exc:
            return cls(
                skills_root,
                issues=(
                    SkillIssue(str(skills_root), f"Could not discover skills: {exc}"),
                ),
            )

        for directory in directories:
            directory_name = directory.name
            try:
                skill_file = (directory / "SKILL.md").resolve(strict=False)
                skill_file.relative_to(skills_root)
            except (OSError, ValueError) as exc:
                issues.append(
                    SkillIssue(
                        directory_name,
                        f"Skill path escapes the skills directory: {exc}",
                    )
                )
                continue

            if not skill_file.is_file():
                issues.append(
                    SkillIssue(directory_name, "Skill directory must contain SKILL.md.")
                )
                continue

            try:
                parsed = parse_skill_metadata(skill_file)
            except SkillValidationError as exc:
                issues.append(SkillIssue(directory_name, str(exc)))
                continue

            if parsed.name != directory_name:
                issues.append(
                    SkillIssue(
                        directory_name,
                        f"Skill name '{parsed.name}' does not match directory "
                        f"'{directory_name}'.",
                    )
                )
                continue

            skills.append(
                SkillMetadata(
                    name=parsed.name,
                    description=parsed.description,
                    skill_file=skill_file,
                )
            )

        return cls(skills_root, tuple(skills), tuple(issues))

    @property
    def metadata(self) -> tuple[SkillMetadata, ...]:
        return tuple(self._skills[name] for name in sorted(self._skills))

    @property
    def issues(self) -> tuple[SkillIssue, ...]:
        return self._issues

    def prompt_catalog(self) -> str:
        if not self._skills:
            return (
                "Available Agent Skills: none discovered.\n"
                "Use load_skill only for names listed in this catalog."
            )

        lines = [
            "Available Agent Skills (metadata only):",
            *(
                f"- {skill.name}: {skill.description}"
                for skill in self.metadata
            ),
            (
                "Before using another tool, compare the request with these descriptions. "
                "If a listed skill is relevant, you must call load_skill with its exact "
                "name and follow the loaded instructions."
            ),
        ]
        return "\n".join(lines)

    def load_skill(self, name: str) -> ToolResult:
        skill = self._skills.get(name)
        if skill is None:
            invalid_error = self._invalid_by_directory.get(name)
            if invalid_error:
                return ToolResult.failure(f"Skill '{name}' is invalid: {invalid_error}")
            return ToolResult.failure(f"Unknown skill: {name}")

        try:
            safe_file = skill.skill_file.resolve(strict=False)
            safe_file.relative_to(self._skills_root)
            content = safe_file.read_text(encoding="utf-8")
        except (OSError, ValueError) as exc:
            return ToolResult.failure(f"Could not load skill '{name}': {exc}")
        return ToolResult.ok(content)
