"""Идентификаторы аудитории и региона (используются в CLI и в имени файла)."""

from __future__ import annotations

# Аудитория траектории (для кого план), не «возраст пользователя».
AUDIENCE_CHILD = "child"
AUDIENCE_TEEN = "teen"
AUDIENCE_ADULT = "adult"
AUDIENCE_MIXED = "mixed"

AUDIENCE_CHOICES: tuple[str, ...] = (
    AUDIENCE_CHILD,
    AUDIENCE_TEEN,
    AUDIENCE_ADULT,
    AUDIENCE_MIXED,
)

REGION_UNSPEC = "UNSPEC"
