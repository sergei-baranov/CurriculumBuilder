"""Slug темы и безопасное имя файла."""

from __future__ import annotations

from slugify import slugify

from curriculum_builder.settings import get_slug_max_length, get_topic_max_len


def topic_slug(topic: str, max_length: int | None = None) -> str:
    lim = max_length if max_length is not None else get_slug_max_length()
    t = topic.strip()[: get_topic_max_len()]
    s = slugify(t, max_length=lim, word_boundary=True, allow_unicode=False)
    return s or "topic"
