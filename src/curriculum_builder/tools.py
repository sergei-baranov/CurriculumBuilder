"""Инструменты: Serper (Google) и отдельный вызов LLM для уточнений."""

from __future__ import annotations

import os

from crewai.tools import tool

from curriculum_builder import prompts
from curriculum_builder.settings import (
    get_openai_sdk_model_name,
    get_study_assistant_max_question_chars,
    get_study_assistant_max_tokens,
    get_study_assistant_temperature,
)


def _study_assistant_run(question: str) -> str:
    if not question or not question.strip():
        return prompts.study_assistant_empty_question_reply()
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return prompts.study_assistant_missing_key_reply()
    try:
        from openai import OpenAI
    except ImportError:
        return prompts.study_assistant_import_error_reply()

    model = get_openai_sdk_model_name()
    base = (
        os.environ.get("OPENAI_API_BASE", "").strip()
        or os.environ.get("OPENAI_BASE_URL", "").strip()
    )
    client_kw: dict = {"api_key": key}
    if base:
        client_kw["base_url"] = base
    client = OpenAI(**client_kw)
    max_q = get_study_assistant_max_question_chars()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompts.study_assistant_system_prompt()},
            {"role": "user", "content": question.strip()[:max_q]},
        ],
        max_tokens=get_study_assistant_max_tokens(),
        temperature=get_study_assistant_temperature(),
    )
    msg = resp.choices[0].message
    text = (msg.content or "").strip()
    return text if text else prompts.study_assistant_empty_model_reply()


_study_assistant_run.__doc__ = prompts.study_assistant_tool_description()
study_assistant = tool("study_assistant")(_study_assistant_run)
