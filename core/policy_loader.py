from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from core.s3_sync import get_effective_policies_dir


PROJECT_ROOT = Path(__file__).resolve().parent.parent
POLICIES_DIR = PROJECT_ROOT / "data" / "policies"


@dataclass
class PolicySection:
    source_file: str
    section_title: str
    section_level: int
    content: str

    def to_dict(self) -> dict:
        return {
            "source_file": self.source_file,
            "section_title": self.section_title,
            "section_level": self.section_level,
            "content": self.content,
        }


def get_policies_dir() -> Path:
    return get_effective_policies_dir()


def validate_policy_files() -> None:
    policies_dir = get_policies_dir()
    required_files = [
        "Política de devoluciones.md",
        "Política de garantía.md",
        "Políticas de envío.md",
    ]

    missing = [
        file_name
        for file_name in required_files
        if not (policies_dir / file_name).exists()
    ]

    if missing:
        missing_str = ", ".join(sorted(missing))
        raise FileNotFoundError(
            f"Faltan archivos .md en data/policies: {missing_str}"
        )


def _normalize_heading(raw_heading: str) -> str:
    text = raw_heading.strip()
    text = text.replace("*", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _split_markdown_into_sections(file_path: Path) -> list[PolicySection]:
    text = file_path.read_text(encoding="utf-8").strip()

    lines = text.splitlines()
    sections: list[PolicySection] = []

    current_title = "Documento completo"
    current_level = 1
    buffer: list[str] = []

    heading_pattern = re.compile(r"^(#{1,6})\s+(.*)$")

    for line in lines:
        match = heading_pattern.match(line.strip())

        if match:
            if buffer:
                content = "\n".join(buffer).strip()
                if content:
                    sections.append(
                        PolicySection(
                            source_file=file_path.name,
                            section_title=current_title,
                            section_level=current_level,
                            content=content,
                        )
                    )
                buffer = []

            hashes = match.group(1)
            heading_text = _normalize_heading(match.group(2))
            current_title = heading_text or "Sección sin título"
            current_level = len(hashes)
        else:
            buffer.append(line)

    if buffer:
        content = "\n".join(buffer).strip()
        if content:
            sections.append(
                PolicySection(
                    source_file=file_path.name,
                    section_title=current_title,
                    section_level=current_level,
                    content=content,
                )
            )

    return sections


@lru_cache(maxsize=1)
def load_policy_sections() -> list[PolicySection]:
    validate_policy_files()

    sections: list[PolicySection] = []

    for file_path in sorted(get_policies_dir().glob("*.md")):
        sections.extend(_split_markdown_into_sections(file_path))

    return sections
