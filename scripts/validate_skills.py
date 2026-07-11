#!/usr/bin/env python3
"""Validate the AtomFlow owner/package Agent Skills catalog."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing opening YAML delimiter")
    try:
        block = text.split("---\n", 2)[1]
    except IndexError as exc:
        raise ValueError("missing closing YAML delimiter") from exc

    values: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def main() -> int:
    errors: list[str] = []
    names: dict[str, Path] = {}
    files = sorted(SKILLS.rglob("SKILL.md"))

    if not files:
        errors.append("no skills found under skills/<owner>/[<package>/]<skill>/SKILL.md")

    for path in files:
        relative_parts = path.relative_to(SKILLS).parts
        if len(relative_parts) not in (3, 4):
            errors.append(
                f"{path.relative_to(ROOT)}: skills must use "
                "skills/<owner>/[<package>/]<skill>/SKILL.md"
            )
            continue

        owner = relative_parts[0]
        folder_name = path.parent.name
        rel = path.relative_to(ROOT)

        if owner != "shared" and not OWNER_RE.fullmatch(owner):
            errors.append(f"{rel}: invalid GitHub username directory {owner!r}")

        if len(relative_parts) == 4:
            package = relative_parts[1]
            if not NAME_RE.fullmatch(package):
                errors.append(f"{rel}: invalid lowercase hyphenated package name {package!r}")

        try:
            meta = frontmatter(path)
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{rel}: {exc}")
            continue

        name = meta.get("name", "")
        description = meta.get("description", "")
        if not NAME_RE.fullmatch(name):
            errors.append(f"{rel}: invalid or missing lowercase hyphenated name")
        if name != folder_name:
            errors.append(f"{rel}: frontmatter name must equal folder {folder_name!r}")
        if len(description) < 24:
            errors.append(f"{rel}: description is missing or too short")
        if name in names:
            errors.append(f"duplicate skill name {name!r}: {names[name]} and {rel}")
        else:
            names[name] = rel

    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} skill(s): {', '.join(sorted(names))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

