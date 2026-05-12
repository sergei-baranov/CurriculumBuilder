"""Числовые и короткие настройки из переменных окружения (после load_dotenv в main)."""

from __future__ import annotations

import os


def _int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    if raw in ("1", "true", "yes", "on"):
        return True
    if raw in ("0", "false", "no", "off"):
        return False
    return default


def get_topic_max_len() -> int:
    return _int("TOPIC_MAX_LEN", 500)


def get_slug_max_length() -> int:
    return _int("SLUG_MAX_LENGTH", 60)


def get_serper_n_results() -> int:
    return _int("SERPER_N_RESULTS", 8)


def get_study_assistant_max_tokens() -> int:
    return _int("STUDY_ASSISTANT_MAX_TOKENS", 900)


def get_study_assistant_temperature() -> float:
    return _float("STUDY_ASSISTANT_TEMPERATURE", 0.3)


def get_study_assistant_max_question_chars() -> int:
    return _int("STUDY_ASSISTANT_MAX_QUESTION_CHARS", 8000)


def get_output_filename_prefix() -> str:
    raw = os.environ.get("LEARNING_OUTPUT_PREFIX", "").strip()
    if not raw:
        return "learning_trajectory"
    safe = "".join(c for c in raw if c.isalnum() or c in ("-", "_")).strip("-_")
    return safe or "learning_trajectory"


def get_crew_verbose() -> bool:
    return _bool("CREW_VERBOSE", True)


def get_crew_memory() -> bool:
    return _bool("CREW_MEMORY", False)


def normalize_openai_model_name_for_openai_compatible_proxy() -> None:
    """Подправить OPENAI_MODEL_NAME для LiteLLM при OpenAI-совместимом прокси (ProxyAPI).

    LiteLLM по первому сегменту до «/» выбирает провайдера: строка вида
    ``openrouter/deepseek/deepseek-chat-v3.1`` превращается в провайдер ``openrouter`` и модель
    ``deepseek/deepseek-chat-v3.1``, тогда как ProxyAPI ожидает в JSON поле ``model`` **целиком**
    ``openrouter/deepseek/deepseek-chat-v3.1``.

    Префикс ``openai/`` переключает транспорт на OpenAI-совместимый, при этом в теле запроса
    остаётся ``model="openrouter/deepseek/deepseek-chat-v3.1"`` (см. ``litellm.get_llm_provider``).

    По умолчанию: если ``OPENAI_API_BASE`` / ``OPENAI_BASE_URL`` содержит ``proxyapi.ru``,
    в имени модели есть ``/`` и ещё нет префикса ``openai/``, добавляем ``openai/``.

    - ``LEARNING_SKIP_OPENAI_MODEL_PREFIX=true`` — не менять имя (ручной контроль).
    - ``LEARNING_OPENAI_MODEL_OPENAI_TRANSPORT=true`` — то же правило для **любого** непустого
      custom base (не только ProxyAPI).
    """
    if _bool("LEARNING_SKIP_OPENAI_MODEL_PREFIX", False):
        return
    base = (
        os.environ.get("OPENAI_API_BASE", "").strip()
        or os.environ.get("OPENAI_BASE_URL", "").strip()
    )
    model = os.environ.get("OPENAI_MODEL_NAME", "").strip()
    if not model or model.startswith("openai/"):
        return
    if "/" not in model:
        return
    proxyapi = "proxyapi.ru" in base.lower()
    force = _bool("LEARNING_OPENAI_MODEL_OPENAI_TRANSPORT", False)
    if not proxyapi and not force:
        return
    os.environ["OPENAI_MODEL_NAME"] = f"openai/{model}"


def get_openai_sdk_model_name() -> str:
    """Имя модели для официального OpenAI Python SDK (study_assistant, прокси).

    Если в ``OPENAI_MODEL_NAME`` задан префикс ``openai/`` только ради LiteLLM (см.
    :func:`normalize_openai_model_name_for_openai_compatible_proxy`), для SDK его
    нужно убрать: прокси в теле ``model`` ожидает строку без этого префикса.
    """
    raw = os.environ.get("OPENAI_MODEL_NAME", "").strip() or "gpt-4o-mini"
    return raw.removeprefix("openai/")


def configure_litellm_runtime_debug() -> None:
    """Включить подробный вывод LiteLLM (запрос как curl, тело JSON).

    Вызывать после load_dotenv(), до ``import curriculum_builder.crew_app``, чтобы флаги
    применились до первой загрузки litellm из CrewAI.

    Переменные:
    - LITELLM_LOG=DEBUG — уровень логгера LiteLLM (см. документацию LiteLLM).
    - LEARNING_LITELLM_DEBUG=true — выставить LITELLM_LOG в DEBUG и поднять уровень логгеров LiteLLM
      (иначе при LITELLM_LOG=DEBUG curl к провайдеру может не печататься: нужен DEBUG на logger).
    - LITELLM_LOG_RAW=true — litellm.log_raw_request_response (сырое тело запроса в метаданных лога;
      не включайте там, где логи утекают наружу).

    Полный текст ответа при ошибке HTTP частично зависит от провайдера; при 404 тело часто уже
    в сообщении исключения. Для ещё более низкого уровня используйте перехват httpx (mitmproxy) или
    прокси с логированием.
    """
    if _bool("LEARNING_LITELLM_DEBUG", False):
        os.environ.setdefault("LITELLM_LOG", "DEBUG")
    want_debug_loggers = (
        os.environ.get("LITELLM_LOG", "").strip().upper() == "DEBUG"
        or _bool("LEARNING_LITELLM_DEBUG", False)
    )
    want_raw = _bool("LITELLM_LOG_RAW", False)
    if not want_debug_loggers and not want_raw:
        return
    import litellm
    from litellm._logging import _turn_on_debug

    if want_debug_loggers:
        _turn_on_debug()
    if want_raw:
        litellm.log_raw_request_response = True
