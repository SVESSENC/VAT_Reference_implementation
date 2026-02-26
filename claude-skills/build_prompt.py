#!/usr/bin/env python3
"""
Build a Claude-ready prompt from project baseline rules and selected skills.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = REPO_ROOT / "claude-skills" / "skill-map.json"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def list_references(skill_dir: Path) -> list[Path]:
    ref_dir = skill_dir / "references"
    if not ref_dir.exists():
        return []
    return sorted([p for p in ref_dir.rglob("*.md") if p.is_file()])


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Claude prompt from one or more vendored skills.")
    parser.add_argument(
        "--skills",
        required=True,
        help="Comma-separated skill names from claude-skills/skill-map.json",
    )
    parser.add_argument(
        "--include-references",
        action="store_true",
        help="Include markdown files from each selected skill's references/ folder.",
    )
    parser.add_argument(
        "--output",
        help="Optional output markdown file path. If omitted, prints to stdout.",
    )
    args = parser.parse_args()

    skill_map = json.loads(read_text(MAP_PATH))
    selected = [s.strip() for s in args.skills.split(",") if s.strip()]
    if not selected:
        raise SystemExit("No skills selected.")

    missing = [s for s in selected if s not in skill_map]
    if missing:
        raise SystemExit(f"Unknown skill(s): {', '.join(missing)}")

    parts: list[str] = []
    parts.append("# Claude Session Context")
    parts.append("")
    parts.append("## Project Rules")
    parts.append(read_text(REPO_ROOT / "CLAUDE.md"))

    for skill in selected:
        rel_skill_path = Path(skill_map[skill])
        skill_path = (REPO_ROOT / rel_skill_path).resolve()
        parts.append("")
        parts.append(f"## Skill: {skill}")
        parts.append(read_text(skill_path))

        if args.include_references:
            for ref in list_references(skill_path.parent):
                rel_ref = ref.relative_to(REPO_ROOT)
                parts.append("")
                parts.append(f"### Reference: {rel_ref}")
                parts.append(read_text(ref))

    output = "\n\n".join(parts).strip() + "\n"
    if args.output:
        out_path = (REPO_ROOT / args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Wrote {out_path}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
