"""Аргументы CLI и интерактивный ввод темы, аудитории, региона."""

from __future__ import annotations

import argparse
import os
import sys

from curriculum_builder.constants import (
    AUDIENCE_ADULT,
    AUDIENCE_CHOICES,
    REGION_UNSPEC,
)
from curriculum_builder import prompts
from curriculum_builder.paths import validate_region_token
from curriculum_builder.settings import get_topic_max_len


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=prompts.argparse_description())
    p.add_argument("--topic", default=None, help=prompts.argparse_help_topic())
    p.add_argument(
        "--audience",
        choices=list(AUDIENCE_CHOICES),
        default=None,
        help=prompts.argparse_help_audience(),
    )
    p.add_argument(
        "--region",
        default=None,
        help=prompts.argparse_help_region(),
    )
    return p


def _prompt_nonempty(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print(prompts.cli_prompt_empty_retry())


def resolve_topic(args: argparse.Namespace) -> str:
    max_len = get_topic_max_len()
    if args.topic:
        t = args.topic.strip()
    elif os.environ.get("LEARNING_TOPIC"):
        t = os.environ["LEARNING_TOPIC"].strip()
    elif sys.stdin.isatty():
        t = _prompt_nonempty(prompts.cli_prompt_topic())
    else:
        raise SystemExit(prompts.cli_error_topic_noninteractive())
    if len(t) > max_len:
        raise SystemExit(prompts.cli_error_topic_too_long(max_len))
    return t


def _interactive_audience() -> str:
    print(prompts.cli_audience_intro())
    labels = prompts.cli_audience_labels()
    for i, key in enumerate(AUDIENCE_CHOICES, start=1):
        print(f"  {i}) {key} — {labels.get(key, key)}")
    while True:
        raw = input(prompts.cli_audience_prompt_choice()).strip()
        if raw in AUDIENCE_CHOICES:
            return raw
        if raw.isdigit() and 1 <= int(raw) <= len(AUDIENCE_CHOICES):
            return AUDIENCE_CHOICES[int(raw) - 1]
        print(prompts.cli_audience_invalid())


def resolve_audience(args: argparse.Namespace) -> str:
    if args.audience:
        return args.audience
    env = os.environ.get("LEARNING_AUDIENCE", "").strip().lower()
    if env in AUDIENCE_CHOICES:
        return env
    if sys.stdin.isatty():
        return _interactive_audience()
    return AUDIENCE_ADULT


def _interactive_region() -> str:
    print(prompts.cli_region_intro())
    raw = input(prompts.cli_region_prompt()).strip().upper()
    if not raw:
        return REGION_UNSPEC
    return validate_region_token(raw)


def resolve_region(args: argparse.Namespace) -> str:
    if args.region is not None:
        r = args.region.strip().upper()
        if not r:
            return REGION_UNSPEC
        return validate_region_token(r)
    env = os.environ.get("LEARNING_REGION", "").strip().upper()
    if env:
        return validate_region_token(env)
    if sys.stdin.isatty():
        return _interactive_region()
    return REGION_UNSPEC
