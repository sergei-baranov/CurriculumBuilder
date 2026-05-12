"""Каталог output и безопасный путь к файлу результата."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from curriculum_builder import prompts
from curriculum_builder.settings import get_output_filename_prefix


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def output_directory() -> Path:
    d = project_root() / "output"
    d.mkdir(parents=True, exist_ok=True)
    return d.resolve()


def local_timestamp_filename() -> str:
    return datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")


def validate_region_token(region: str) -> str:
    r = region.strip().upper()
    if r == "UNSPEC":
        return "UNSPEC"
    if re.fullmatch(r"[A-Z]{2}", r):
        return r
    raise ValueError(prompts.region_validation_error_message())


def safe_result_path(slug: str, audience: str, region: str) -> Path:
    if ".." in slug or "/" in slug or "\\" in slug:
        raise ValueError("Некорректный slug")
    for part in (audience, region):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", part):
            raise ValueError("Некорректные токены audience/region для имени файла")
    ts = local_timestamp_filename()
    prefix = get_output_filename_prefix()
    name = f"{prefix}_{slug}_{audience}_{region}_{ts}.md"
    out_dir = output_directory()
    path = (out_dir / name).resolve()
    if not path.is_relative_to(out_dir):
        raise ValueError("Путь выходит за пределы каталога output")
    return path
