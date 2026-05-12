"""Точка входа: загрузка .env, опрос, запуск Crew, запись Markdown."""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from curriculum_builder import prompts
from curriculum_builder.cli import build_parser, resolve_audience, resolve_region, resolve_topic
from curriculum_builder.paths import project_root, safe_result_path
from curriculum_builder.settings import (
    configure_litellm_runtime_debug,
    normalize_openai_model_name_for_openai_compatible_proxy,
)
from curriculum_builder.slug_util import topic_slug


def _configure_crewai_runtime() -> None:
    """CrewAI 0.203: SQLite и «первый запуск» tracing трогают user_data_dir; без прав на домашний каталог — ошибка.

    - XDG_DATA_HOME внутри проекта — база для appdirs и SQLite kickoff storage.
    - CREWAI_TESTING — отключает авто-tracing первого запуска (иначе вызывается get_auth_token и mkdir в ~/.local/share/crewai).
    """
    share = project_root() / ".local" / "share"
    share.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("XDG_DATA_HOME", str(share))
    os.environ.setdefault("CREWAI_STORAGE_DIR", "curriculum-builder-app")
    os.environ.setdefault("CREWAI_TESTING", "true")
    os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")


def _extract_last_task_markdown(result) -> str:
    if hasattr(result, "tasks_output") and result.tasks_output:
        last = result.tasks_output[-1]
        raw = getattr(last, "raw", None)
        if raw is not None:
            return str(raw).strip()
    if hasattr(result, "raw"):
        return str(result.raw).strip()
    return str(result).strip()


def main() -> None:
    load_dotenv()
    normalize_openai_model_name_for_openai_compatible_proxy()
    _configure_crewai_runtime()
    args = build_parser().parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print(prompts.warn_missing_openai_key(), file=sys.stderr)

    if not os.environ.get("SERPER_API_KEY"):
        print(prompts.warn_missing_serper_key(), file=sys.stderr)

    topic = resolve_topic(args)
    audience = resolve_audience(args)
    region = resolve_region(args)

    slug = topic_slug(topic)
    out_path = safe_result_path(slug, audience, region)

    configure_litellm_runtime_debug()
    from curriculum_builder.crew_app import build_crew

    crew = build_crew(topic, audience, region)
    result = crew.kickoff()
    body = _extract_last_task_markdown(result)
    full_md = prompts.markdown_metadata_header(topic, audience, region) + "\n" + body + "\n"

    out_path.write_text(full_md, encoding="utf-8")
    print(str(out_path.resolve()))


if __name__ == "__main__":
    main()
