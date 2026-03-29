"""Load prompt.txt next to a node package."""

from pathlib import Path


def load_prompt(node_dir: Path, filename: str = "prompt.txt") -> str:
    path = node_dir / filename
    return path.read_text(encoding="utf-8")
