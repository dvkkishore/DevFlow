from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_SKILL_NAME_LENGTH = 64
MAX_SKILL_DESCRIPTION_LENGTH = 1024


class SkillValidationError(ValueError):
    """Raised when SKILL.md metadata is missing or invalid."""


@dataclass(frozen=True)
class ParsedSkillMetadata:
    name: str
    description: str


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_frontmatter_lines(lines: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    multiline_key: str | None = None
    multiline_style = "|"

    for raw_line in lines:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        if raw_line[0].isspace():
            if multiline_key is not None:
                separator = "\n" if multiline_style == "|" else " "
                current = values.get(multiline_key, "")
                addition = raw_line.strip()
                values[multiline_key] = (
                    f"{current}{separator}{addition}" if current else addition
                )
            continue

        multiline_key = None
        if ":" not in raw_line:
            raise SkillValidationError(
                f"Invalid YAML frontmatter line: {raw_line.strip()}"
            )

        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key:
            raise SkillValidationError("YAML frontmatter contains an empty key.")
        if key in values:
            raise SkillValidationError(f"Duplicate YAML frontmatter key: {key}")

        if value in {"|", ">"}:
            values[key] = ""
            multiline_key = key
            multiline_style = value
        else:
            values[key] = _unquote(value)

    return values


def parse_skill_metadata(skill_file: Path) -> ParsedSkillMetadata:
    try:
        with skill_file.open("r", encoding="utf-8-sig") as handle:
            first_line = handle.readline()
            if first_line.rstrip("\r\n") != "---":
                raise SkillValidationError("SKILL.md must begin with YAML frontmatter.")

            frontmatter_lines: list[str] = []
            for line in handle:
                if line.rstrip("\r\n") == "---":
                    break
                frontmatter_lines.append(line.rstrip("\r\n"))
            else:
                raise SkillValidationError("SKILL.md frontmatter is not closed with ---.")
    except OSError as exc:
        raise SkillValidationError(f"Could not read SKILL.md: {exc}") from exc

    values = _parse_frontmatter_lines(frontmatter_lines)
    name = values.get("name", "").strip()
    description = values.get("description", "").strip()
    if not name:
        raise SkillValidationError("SKILL.md frontmatter requires a non-empty name.")
    if not description:
        raise SkillValidationError(
            "SKILL.md frontmatter requires a non-empty description."
        )
    if len(name) > MAX_SKILL_NAME_LENGTH:
        raise SkillValidationError(
            f"Skill name must be at most {MAX_SKILL_NAME_LENGTH} characters."
        )
    if len(description) > MAX_SKILL_DESCRIPTION_LENGTH:
        raise SkillValidationError(
            "Skill description must be at most "
            f"{MAX_SKILL_DESCRIPTION_LENGTH} characters."
        )
    if not SKILL_NAME_PATTERN.fullmatch(name):
        raise SkillValidationError(
            "Skill name must contain only lowercase letters, digits, and hyphens."
        )
    return ParsedSkillMetadata(name=name, description=description)
