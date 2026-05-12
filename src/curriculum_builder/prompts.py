"""Тексты промптов, UI и шаблонов.

Значения по умолчанию задаются в этом модуле; переопределение — переменными окружения
(см. .env.example и README). Многострочные значения в .env удобно задавать в кавычках.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone


def _str_env(name: str, default: str) -> str:
    v = os.environ.get(name)
    if v is None:
        return default
    s = v.strip()
    return s if s else default


# --- Политика безопасности (добавляется в backstory агентов)

SAFETY_POLICY_SNIPPET_DEFAULT = """
Обязательные ограничения (дополнительно к политикам провайдера API):
- Не генерировать сексуализированный контент с несовершеннолетними, насилие, экстремизм, инструкции по причинению вреда себе или другим, взлом, обход закона.
- Образовательный нейтральный тон; не собирать и не запрашивать персональные данные в тексте траектории.
- Для аудитории child/teen: только безопасные практики, проверяемые взрослым; избегать опасных экспериментов; осторожность со ссылками в интернет.
- Медицина/психология/юриспруденция: не выдавать персональные диагнозы и не заменять специалиста; отсылать к официальным источникам и квалифицированным специалистам.
- Регион {region}: учитывать типичные ожидания к обучению в этом регионе без утверждений о «силе закона» или юридических нормах.
""".strip()


def safety_policy_snippet(region: str) -> str:
    raw = _str_env("SAFETY_POLICY_SNIPPET", SAFETY_POLICY_SNIPPET_DEFAULT)
    if "{region}" in raw:
        return raw.format(region=region)
    return f"{raw}\n\n(Регион-ориентир: {region})"


# --- CLI / argparse

def argparse_description() -> str:
    return _str_env("CLI_ARGPARSE_DESCRIPTION", "Исследование темы и генерация траектории самообучения (CrewAI).")


def argparse_help_topic() -> str:
    return _str_env("CLI_HELP_TOPIC", "Тема обучения (иначе ввод или переменная LEARNING_TOPIC).")


def argparse_help_audience() -> str:
    return _str_env(
        "CLI_HELP_AUDIENCE",
        "Аудитория траектории: child | teen | adult | mixed (или LEARNING_AUDIENCE).",
    )


def argparse_help_region() -> str:
    return _str_env(
        "CLI_HELP_REGION",
        "ISO 3166-1 alpha-2 (например RU) или UNSPEC; пусто = UNSPEC (или LEARNING_REGION).",
    )


def cli_prompt_topic() -> str:
    return _str_env("CLI_PROMPT_TOPIC", "Тема обучения: ")


def cli_error_topic_noninteractive() -> str:
    return _str_env(
        "CLI_ERROR_TOPIC_NONINTERACTIVE",
        "Неинтерактивный режим: задайте тему через --topic или переменную окружения LEARNING_TOPIC.",
    )


def cli_error_topic_too_long(max_len: int) -> str:
    tpl = _str_env("CLI_ERROR_TOPIC_TOO_LONG", "Тема длиннее {max_len} символов. Сократите формулировку.")
    return tpl.format(max_len=max_len)


def cli_prompt_empty_retry() -> str:
    return _str_env("CLI_PROMPT_EMPTY_RETRY", "Значение не должно быть пустым. Повторите ввод.")


def cli_audience_intro() -> str:
    return _str_env("CLI_AUDIENCE_INTRO", "\nДля кого строится траектория (тон и сложность материала)?")


def cli_audience_labels() -> dict[str, str]:
    """Подписи к пунктам меню; ключи фиксированы (child, teen, adult, mixed)."""
    import json

    raw = os.environ.get("CLI_AUDIENCE_LABELS_JSON", "").strip()
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
        except json.JSONDecodeError:
            pass
    return {
        "child": "дети (примерно до 12 лет)",
        "teen": "подростки (примерно 13–17 лет)",
        "adult": "взрослые (18+)",
        "mixed": "смешанная аудитория / семейное или групповое обучение",
    }


def cli_audience_prompt_choice() -> str:
    return _str_env("CLI_AUDIENCE_PROMPT_CHOICE", "Номер варианта [1–4]: ")


def cli_audience_invalid() -> str:
    return _str_env(
        "CLI_AUDIENCE_INVALID",
        "Введите число от 1 до 4 или один из кодов: child, teen, adult, mixed.",
    )


def cli_region_intro() -> str:
    return _str_env(
        "CLI_REGION_INTRO",
        "\nРегион (ориентир для тона и типовых ожиданий к обучению). "
        "Введите ISO 3166-1 alpha-2 (например RU, DE, KZ) или пусто, если не указываете.",
    )


def cli_region_prompt() -> str:
    return _str_env("CLI_REGION_PROMPT", "Код региона [Enter = не указываю]: ")


def region_validation_error_message() -> str:
    return _str_env(
        "REGION_VALIDATION_ERROR",
        "Код региона должен быть ISO 3166-1 alpha-2 (две латинские буквы) или UNSPEC.",
    )


# --- Инструмент study_assistant

STUDY_ASSISTANT_SYSTEM_DEFAULT = (
    "Ты помощник по обучению. Отвечай кратко, по делу, без воды, на русском если вопрос на русском."
)


def study_assistant_system_prompt() -> str:
    return _str_env("STUDY_ASSISTANT_SYSTEM_PROMPT", STUDY_ASSISTANT_SYSTEM_DEFAULT)


STUDY_ASSISTANT_TOOL_DOC_DEFAULT = (
    "Коротко уточняет или критикует формулировки траектории, связность шагов, упрощение под аудиторию. "
    "Передавайте один чёткий вопрос."
)


def study_assistant_tool_description() -> str:
    return _str_env("STUDY_ASSISTANT_TOOL_DESCRIPTION", STUDY_ASSISTANT_TOOL_DOC_DEFAULT)


def study_assistant_empty_question_reply() -> str:
    return _str_env("STUDY_ASSISTANT_EMPTY_QUESTION", "Пустой вопрос.")


def study_assistant_missing_key_reply() -> str:
    return _str_env(
        "STUDY_ASSISTANT_MISSING_KEY",
        "Переменная OPENAI_API_KEY не задана; инструмент недоступен.",
    )


def study_assistant_import_error_reply() -> str:
    return _str_env(
        "STUDY_ASSISTANT_IMPORT_ERROR",
        "Пакет openai недоступен; установите зависимости проекта.",
    )


def study_assistant_empty_model_reply() -> str:
    return _str_env("STUDY_ASSISTANT_EMPTY_REPLY", "(пустой ответ модели)")


# --- Markdown: метаданные в начале файла

MARKDOWN_METADATA_TEMPLATE_DEFAULT = """# Метаданные траектории

| Поле | Значение |
|------|----------|
| Тема | {topic_esc} |
| Аудитория | {audience} |
| Регион (ориентир) | {region} |
| Сгенерировано (UTC) | {utc} |

## Дисклеймер

{disclaimer_body}

---

"""


def markdown_disclaimer_body() -> str:
    return _str_env(
        "MARKDOWN_DISCLAIMER_BODY",
        "Текст ниже сгенерирован нейросетью и может содержать **ошибки** и **неточности**. "
        "Это не медицинская, не юридическая и не психологическая консультация. Для аудиторий **child** и **teen** "
        "рекомендуется **сопровождение** родителя или педагога; будьте осторожны при переходе по ссылкам из интернета. "
        "Инструкции приложения снижают риски, но **не гарантируют** приемлемость всего содержимого — просмотрите материал перед использованием.",
    )


def markdown_metadata_header(topic: str, audience: str, region: str) -> str:
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    topic_esc = topic.replace("|", "\\|").replace("\n", " ")
    tpl = _str_env("MARKDOWN_METADATA_TEMPLATE", MARKDOWN_METADATA_TEMPLATE_DEFAULT)
    return tpl.format(
        topic_esc=topic_esc,
        audience=audience,
        region=region,
        utc=utc,
        disclaimer_body=markdown_disclaimer_body(),
    )


# --- Агент: исследователь

RESEARCHER_ROLE_DEFAULT = "Исследователь учебных материалов"


def researcher_role() -> str:
    return _str_env("AGENT_RESEARCHER_ROLE", RESEARCHER_ROLE_DEFAULT)


RESEARCHER_GOAL_DEFAULT = (
    "Собрать обзор по теме «{topic}» для аудитории {audience} "
    "(регион-ориентир: {region}): ключевые понятия, качественные источники, типичные ошибки новичков."
)


def researcher_goal(topic: str, audience: str, region: str) -> str:
    return _str_env("AGENT_RESEARCHER_GOAL", RESEARCHER_GOAL_DEFAULT).format(
        topic=topic, audience=audience, region=region
    )


RESEARCHER_BACKSTORY_PREFIX_DEFAULT = (
    "Ты опытный методист и исследователь. Используешь веб-поиск для фактов и ссылок. "
    "Пишешь структурировано, без лишней воды."
)


def researcher_backstory_prefix() -> str:
    return _str_env("AGENT_RESEARCHER_BACKSTORY_PREFIX", RESEARCHER_BACKSTORY_PREFIX_DEFAULT)


def researcher_backstory(safety: str) -> str:
    return f"{researcher_backstory_prefix()}\n\n{safety}"


# --- Агент: архитектор

ARCHITECT_ROLE_DEFAULT = "Архитектор траектории обучения"


def architect_role() -> str:
    return _str_env("AGENT_ARCHITECT_ROLE", ARCHITECT_ROLE_DEFAULT)


ARCHITECT_GOAL_DEFAULT = (
    "Построить иерархию этапов от основ к продвинутым темам с критериями «готово» "
    "и хотя бы одной практикой на каждой ветке (если тема допускает практику; иначе — осмысленная активная практика)."
)


def architect_goal() -> str:
    return _str_env("AGENT_ARCHITECT_GOAL", ARCHITECT_GOAL_DEFAULT)


ARCHITECT_BACKSTORY_TEMPLATE_DEFAULT = (
    "Ты проектируешь траекторию для темы «{topic}», аудитория {audience}, регион {region}. "
    "На каждой ветке — проверяемое практическое задание или безопасная альтернатива для теории. "
    "Для child/teen — только действия, безопасные и проверяемые взрослым."
)


def architect_backstory(topic: str, audience: str, region: str, safety: str) -> str:
    prefix = _str_env("AGENT_ARCHITECT_BACKSTORY_PREFIX", ARCHITECT_BACKSTORY_TEMPLATE_DEFAULT).format(
        topic=topic, audience=audience, region=region
    )
    return f"{prefix}\n\n{safety}"


# --- Агент: редактор

EDITOR_ROLE_DEFAULT = "Редактор Markdown"


def editor_role() -> str:
    return _str_env("AGENT_EDITOR_ROLE", EDITOR_ROLE_DEFAULT)


EDITOR_GOAL_DEFAULT = "Превратить согласованную иерархию в строгий Markdown: дерево чекбоксов."


def editor_goal() -> str:
    return _str_env("AGENT_EDITOR_GOAL", EDITOR_GOAL_DEFAULT)


EDITOR_BACKSTORY_PREFIX_DEFAULT = (
    "Ты редактор формата. Не придумываешь новую структуру с нуля — только разметка. "
    "Используй study_assistant только если нужно уточнить формулировку узла."
)


def editor_backstory(safety: str) -> str:
    prefix = _str_env("AGENT_EDITOR_BACKSTORY_PREFIX", EDITOR_BACKSTORY_PREFIX_DEFAULT)
    return f"{prefix}\n\n{safety}"


# --- Задачи

TASK_RESEARCH_DESCRIPTION_DEFAULT = (
    "Тема: «{topic}». Аудитория: {audience}. Регион (ориентир): {region}.\n\n"
    "Сделай исследование: ключевые подтемы, глоссарий, 5–12 надёжных направлений для изучения "
    "(курсы, документация, книги — с названиями и при возможности URL из поиска). "
    "Отметь типичные ловушки для новичков. Учитывай возрастную аудиторию и регион только как мягкий контекст."
)


def task_research_description(topic: str, audience: str, region: str) -> str:
    return _str_env("TASK_RESEARCH_DESCRIPTION", TASK_RESEARCH_DESCRIPTION_DEFAULT).format(
        topic=topic, audience=audience, region=region
    )


TASK_RESEARCH_EXPECTED_DEFAULT = (
    "Структурированный текст исследования (разделы с заголовками), без финального чеклиста."
)


def task_research_expected_output() -> str:
    return _str_env("TASK_RESEARCH_EXPECTED_OUTPUT", TASK_RESEARCH_EXPECTED_DEFAULT)


TASK_TRAJECTORY_DESCRIPTION_DEFAULT = (
    "На основе исследования построй траекторию для темы «{topic}», аудитория {audience}, регион {region}.\n\n"
    "Требования:\n"
    "- Дерево: корень → ветви → листья; явный рекомендуемый порядок.\n"
    "- На **каждой** ветке минимум один пункт практики (лабораторная, мини-проект, упражнение, кейс, "
    "настройка окружения и т.д.) если тема допускает; иначе — активная практика (резюме текста, чек-лист наблюдения, "
    "письменный разбор источника).\n"
    "- Краткие критерии «готово» у ключевых узлов.\n"
    "- Не включай Markdown чекбоксы на этом шаге — только текстовый план иерархии."
)


def task_trajectory_description(topic: str, audience: str, region: str) -> str:
    return _str_env("TASK_TRAJECTORY_DESCRIPTION", TASK_TRAJECTORY_DESCRIPTION_DEFAULT).format(
        topic=topic, audience=audience, region=region
    )


TASK_TRAJECTORY_EXPECTED_DEFAULT = "Текстовое дерево траектории с практиками по веткам (без - [ ])."


def task_trajectory_expected_output() -> str:
    return _str_env("TASK_TRAJECTORY_EXPECTED_OUTPUT", TASK_TRAJECTORY_EXPECTED_DEFAULT)


TASK_MARKDOWN_DESCRIPTION_DEFAULT = (
    "По утверждённой траектории для темы «{topic}» (аудитория {audience}, регион {region}) "
    "сформируй **только** раздел с деревом обучения в Markdown.\n\n"
    "Формат:\n"
    "- Один заголовок второго уровня: `## План по теме: …` (кратко вставь тему).\n"
    "- Далее **только** вложенные списки: каждая строка начинается с `- [ ] ` (пробел после скобок). "
    "Вложенность — два пробела на уровень.\n"
    "- Практические шаги — отдельные дочерние пункты, начинающиеся с `- [ ] Практика: `.\n"
    "- Без таблиц метаданных, без дисклеймеров в этом выводе, без JSON, без кода блоков, без пояснительных абзацев вне списков."
)


def task_markdown_description(topic: str, audience: str, region: str) -> str:
    return _str_env("TASK_MARKDOWN_DESCRIPTION", TASK_MARKDOWN_DESCRIPTION_DEFAULT).format(
        topic=topic, audience=audience, region=region
    )


TASK_MARKDOWN_EXPECTED_DEFAULT = "Markdown: заголовок ## и дерево - [ ] …"


def task_markdown_expected_output() -> str:
    return _str_env("TASK_MARKDOWN_EXPECTED_OUTPUT", TASK_MARKDOWN_EXPECTED_DEFAULT)


# --- Предупреждения main

def warn_missing_openai_key() -> str:
    return _str_env(
        "WARN_MISSING_OPENAI_KEY",
        "Предупреждение: не задан OPENAI_API_KEY — запросы к LLM завершатся ошибкой.",
    )


def warn_missing_serper_key() -> str:
    return _str_env(
        "WARN_MISSING_SERPER_KEY",
        "Предупреждение: не задан SERPER_API_KEY — агенты не смогут вызывать поиск Google через Serper.",
    )
