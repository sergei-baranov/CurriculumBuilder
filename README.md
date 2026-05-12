# Curriculum Builder

CLI-приложение на **CrewAI**: по введённой теме выполняется веб-исследование (Google через [Serper](https://serper.dev)), строится **траектория самообучения** с практическими шагами на ветках и сохраняется **Markdown** с чекбоксами `- [ ]` / `- [x]`.

## Требования

- Python **3.11+** (стек CrewAI / `onnxruntime` из транзитивных зависимостей не публикует колёса для 3.10 в актуальных версиях).
- Файл [`.python-version`](.python-version) подсказывает `uv`, какой интерпретатор взять для venv (сейчас **3.12**; при необходимости замените на свою установленную **3.11+** или выполните `uv python pin 3.11`).
- [uv](https://docs.astral.sh/uv/) (для `uv sync` и `uv.lock`) **или** только `pip` + `venv`.

## Быстрый запуск (uv)

```bash
cd CurriculumBuilder
uv venv
uv sync
cp .env.example .env
# Отредактируйте .env: OPENAI_API_KEY, SERPER_API_KEY
uv run curriculum-builder
```

Интерактивно вводятся: **тема**, **аудитория** (child / teen / adult / mixed), **регион** (ISO alpha-2, например `RU`, или Enter для `UNSPEC`).

## Запуск без uv (pip)

Интерпретатор должен быть **Python 3.11+**.

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
cp .env.example .env
curriculum-builder --topic "Ваша тема" --audience adult --region UNSPEC
```

## CLI и переменные окружения

| Аргумент / переменная | Назначение |
|----------------------|------------|
| `--topic` / `LEARNING_TOPIC` | Тема обучения (приоритет: CLI → env → интерактивный ввод). |
| `--audience` / `LEARNING_AUDIENCE` | `child`, `teen`, `adult`, `mixed`. |
| `--region` / `LEARNING_REGION` | Две латинские буквы (`RU`) или `UNSPEC`. |
| `OPENAI_API_KEY` | LLM для агентов и инструмента `study_assistant`. |
| `OPENAI_MODEL_NAME` | Модель для агентов (LiteLLM) и `study_assistant` (OpenAI SDK). По умолчанию `gpt-4o-mini`. Для ProxyAPI + OpenRouter через LiteLLM см. раздел ProxyAPI (`openai/openrouter/...` или автоподстановка). |
| `OPENAI_API_BASE` или `OPENAI_BASE_URL` | Необязательно: базовый URL OpenAI-совместимого API (прокси, локальный сервер). |
| `SERPER_API_KEY` | Поиск Google через SerperDevTool. |
| `TOPIC_MAX_LEN`, `SLUG_MAX_LENGTH`, `SERPER_N_RESULTS` | Лимиты темы, slug и число результатов Serper (см. [settings.py](src/curriculum_builder/settings.py)). |
| `LEARNING_OUTPUT_PREFIX` | Префикс имени файла в `output/` (по умолчанию `learning_trajectory`). |
| `CREW_VERBOSE`, `CREW_MEMORY` | Подробный лог экипа и память CrewAI (`true`/`false`). |
| `LITELLM_LOG`, `LEARNING_LITELLM_DEBUG`, `LITELLM_LOG_RAW` | Подробные логи HTTP к LLM (раздел «Отладка LLM» ниже). |
| `STUDY_ASSISTANT_*` | Лимиты и тексты инструмента `study_assistant` (см. ниже). |

Неинтерактивный режим (без TTY): задайте `--topic` или `LEARNING_TOPIC`; для аудитории/региона при отсутствии TTY используются значения по умолчанию **adult** и **UNSPEC**, либо переменные `LEARNING_*`.

### Кастомизация промптов и строк интерфейса

Тексты по умолчанию лежат в [src/curriculum_builder/prompts.py](src/curriculum_builder/prompts.py) (роли агентов, описания задач, подсказки CLI, фрагмент политики безопасности, шаблон метаданных Markdown, системный промпт инструмента `study_assistant`). Переопределить их без правки кода можно переменными окружения: полный перечень имён — в [.env.example](.env.example) (блок «Тексты и промпты»). В шаблонах с фигурными скобками используйте те же плейсхолдеры, что в значениях по умолчанию в `prompts.py` (например `{topic}`, `{audience}`, `{region}` в целях агентов).

Если импортировать `curriculum_builder.tools` до вызова `load_dotenv()`, переопределения из `.env` для описания инструмента и системного промпта могут не подхватиться; штатный запуск через `curriculum-builder` сначала загружает `.env`.

### Отладка LLM (LiteLLM)

CrewAI вызывает модели через **LiteLLM**. Чтобы в консоли видеть **приближённый к `curl` запрос** к провайдеру (URL, заголовки с маскировкой ключа, тело JSON), задайте в `.env` одно из:

- `LITELLM_LOG=DEBUG` — уровень логгера LiteLLM;
- или `LEARNING_LITELLM_DEBUG=true` — то же и принудительное включение DEBUG на логгерах LiteLLM (удобно, если одного `LITELLM_LOG` мало для вывода «POST Request Sent from LiteLLM»).

Дополнительно `LITELLM_LOG_RAW=true` включает `litellm.log_raw_request_response` (ещё более подробное тело запроса в метаданных лога). **Не включайте** это в общих логах в проде: в запросе могут быть большие промпты.

**Полный текст ответа** при ошибке зависит от провайдера: при HTTP 404 тело часто уже вложено в `litellm.NotFoundError` . Если нужен полный сырой HTTP-трафик, используйте внешний перехват (**mitmproxy**, логирующий прокси) или сниффер только в изолированной среде.

Ошибка `NotFound` / `Received Model Group=…` у OpenRouter через ProxyAPI чаще всего либо **неверный идентификатор** в каталоге ProxyAPI, либо **разбор LiteLLM**: строка `openrouter/…` без префикса `openai/` превращается в «родной» провайдер OpenRouter и укороченное имя модели (см. раздел ProxyAPI ниже).

## Результат

Файл в каталоге `output/`:

`{LEARNING_OUTPUT_PREFIX}_{slug}_{audience}_{region}_YYYYMMDD_HHMMSS.md` (префикс по умолчанию — `learning_trajectory`)

- `slug` — транслитерация темы (`python-slugify`).
- В начале файла — **метаданные** и **дисклеймер**; далее — дерево чекбоксов из последней задачи экипа.

## Безопасность данных и ключей

- Храните ключи **только** в `.env`. Файл `.env` в **`.gitignore`** и **`.cursorignore`** — не коммитьте и не вставляйте ключи в поле «тема».
- Текст темы, аудитория и код региона отправляются провайдерам (**OpenAI**, **Serper**). Не указывайте в теме пароли, токены, персональные данные третьих лиц.
- При утечке ключа — отзовите его в кабинете провайдера и обновите `.env`.
- Ознакомьтесь с политиками: [OpenAI](https://openai.com/policies), [Serper](https://serper.dev) — проект не даёт юридических консультаций по GDPR и аналогам.

## Безопасность вывода ИИ

Траектория и ссылки сгенерированы моделью и могут быть **неточными**. Это не медицинская, юридическая или психологическая консультация. Для аудиторий **child** и **teen** предусмотрено сопровождение взрослым; инструкции в промптах **снижают**, но **не гарантируют** приемлемость контента — просматривайте результат.

## CrewAI: служебные файлы в проекте

Приложение задаёт:

- `XDG_DATA_HOME=<корень_проекта>/.local/share` — SQLite и данные CrewAI внутри репозитория;
- `CREWAI_STORAGE_DIR=curriculum-builder-app` — имя подкаталога для appdirs;
- `CREWAI_TESTING=true` — отключает сценарий «первый запуск» tracing, который иначе обращается к `~/.local/share/crewai` (удобно в CI и ограниченных окружениях).

Каталог `.local/` добавлен в `.gitignore`. Чтобы включить облачный tracing CrewAI, снимите `CREWAI_TESTING` в своём окружении и следуйте документации CrewAI (возможны записи в домашний каталог).

## Смена LLM-провайдера

По умолчанию запросы идут на официальный **OpenAI** (см. [документацию CrewAI](https://docs.crewai.com) и стек **LiteLLM**). Агенты CrewAI подхватывают те же переменные, что и многие OpenAI-совместимые клиенты: `OPENAI_API_KEY`, при необходимости **`OPENAI_API_BASE`** или **`OPENAI_BASE_URL`** (оба имени поддерживаются в LiteLLM).

Инструмент **`study_assistant`** в [src/curriculum_builder/tools.py](src/curriculum_builder/tools.py) использует официальный **OpenAI Python SDK**; в репозитории он уже читает `OPENAI_API_BASE` / `OPENAI_BASE_URL` так же, как ниже в примере с явным `base_url`. Системный промпт и описание инструмента для агента задаются через [prompts.py](src/curriculum_builder/prompts.py) и переменные `STUDY_ASSISTANT_SYSTEM_PROMPT`, `STUDY_ASSISTANT_TOOL_DESCRIPTION` (см. `.env.example`).

### Пример: ProxyAPI и модель OpenRouter (DeepSeek) через `.env`

Сервис [ProxyAPI](https://proxyapi.ru) даёт [OpenAI-совместимый API](https://proxyapi.ru/docs/openai-compatible-api): те же пути `/v1/chat/completions`, другой хост и маршрутизация по полю `model` (строка вида `openrouter/<провайдер>/<модель>` должна уйти в JSON **целиком**).

**LiteLLM** (под капотом CrewAI) по первому сегменту до `/` выбирает «родного» провайдера: значение `openrouter/deepseek/deepseek-chat-v3.1` он разбирает на провайдер `openrouter` и модель `deepseek/deepseek-chat-v3.1`, из‑за чего ProxyAPI может ответить 404. Нужен транспорт **OpenAI** с полным идентификатором в поле `model`:

- либо в `.env` укажите **`OPENAI_MODEL_NAME=openai/openrouter/deepseek/deepseek-chat-v3.1`** (префикс `openai/` — это выбор транспорта LiteLLM, в теле запроса к прокси уйдёт `model=openrouter/deepseek/deepseek-chat-v3.1`);
- либо оставьте `openrouter/deepseek/...` без префикса: при `OPENAI_API_BASE` / `OPENAI_BASE_URL` с хостом **proxyapi.ru** приложение **само** добавит `openai/` при старте ([`normalize_openai_model_name_for_openai_compatible_proxy`](src/curriculum_builder/settings.py)). Для других прокси задайте полное имя вручную или включите `LEARNING_OPENAI_MODEL_OPENAI_TRANSPORT=true`.

Чтобы **и агенты CrewAI**, и **`study_assistant`** ходили в ProxyAPI **без правки кода**, в `.env` достаточно:

```env
OPENAI_API_KEY=<ваш_ключ_от_proxyapi.ru>
OPENAI_API_BASE=https://openai.api.proxyapi.ru/v1
OPENAI_MODEL_NAME=openai/openrouter/deepseek/deepseek-chat-v3.1
```

Убедитесь, что в кабинете ProxyAPI доступна выбранная модель; список идентификаторов см. в их документации по разделам **Модели** и формату `openrouter/<провайдер>/<модель>`.

Отключить автоподстановку `openai/` для ProxyAPI: `LEARNING_SKIP_OPENAI_MODEL_PREFIX=true` (см. [.env.example](.env.example)).

Официальный пример клиента у ProxyAPI (Python, [источник](https://proxyapi.ru/docs/openai-compatible-api)):

```python
from openai import OpenAI

client = OpenAI(
    api_key="<КЛЮЧ>",
    base_url="https://openai.api.proxyapi.ru/v1",
)

chat_completion = client.chat.completions.create(
    model="anthropic/claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Привет!"}],
)
```

В нашем проекте тот же смысл переносится в переменные: ключ в `OPENAI_API_KEY`, URL в `OPENAI_API_BASE`, имя модели — в `OPENAI_MODEL_NAME`.

### Пример: вручную изменить `tools.py` (другой прокси или жёстко зашитый URL)

Если вы предпочитаете не использовать переменные окружения для `base_url` или подключаете провайдера, для которого удобнее правка кода, откройте [src/curriculum_builder/tools.py](src/curriculum_builder/tools.py), найдите создание клиента и замените блок на явный вызов (значения подставьте свои):

```python
    model = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini")
    # Для вызова через OpenAI SDK к ProxyAPI в поле model нужна строка каталога без префикса openai/
    # (префикс openai/ в .env оставляют только ради LiteLLM в CrewAI — см. get_openai_sdk_model_name в settings.py).
    client = OpenAI(
        api_key=key,
        base_url="https://openai.api.proxyapi.ru/v1",
    )
    # В проекте текст system и лимиты берутся из prompts.py / .env (STUDY_ASSISTANT_*).
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "<ваш system prompt>"},
            {"role": "user", "content": question.strip()[:8000]},
        ],
        max_tokens=900,
        temperature=0.3,
    )
```

- В **`OPENAI_API_KEY`** в `.env` укажите ключ, выданный **ProxyAPI** (не ключ OpenAI.com), если работаете через их шлюз.
- В **`OPENAI_MODEL_NAME`** для официального SDK укажите строку из каталога ProxyAPI, например **`openrouter/deepseek/deepseek-chat-v3.1`** (как в [документации ProxyAPI](https://proxyapi.ru/docs/openai-compatible-api)). В штатном `tools.py` для SDK используется [`get_openai_sdk_model_name()`](src/curriculum_builder/settings.py): префикс `openai/`, если он появился ради LiteLLM, перед запросом снимается.

Агенты экипа по-прежнему настраиваются **только переменными окружения** (CrewAI / LiteLLM); для них задайте те же `OPENAI_API_KEY`, `OPENAI_API_BASE` и `OPENAI_MODEL_NAME`, иначе экип и инструмент будут смотреть на разные конечные точки.

## Поддержка и обновление зависимостей

```bash
uv lock --upgrade
uv sync
```

Либо `pip install -U crewai crewai-tools` в активированном venv (версии зафиксированы в [pyproject.toml](pyproject.toml) и [uv.lock](uv.lock)).

Типичные ошибки: отсутствует `OPENAI_API_KEY`; нет квоты API; не задан `SERPER_API_KEY` (поиск недоступен, агенты работают без Google).

## Структура репозитория

- [src/curriculum_builder/](src/curriculum_builder/) — код: `main.py`, `crew_app.py`, `cli.py`, `tools.py`, `prompts.py`, `settings.py`, `constants.py`, `paths.py`, `slug_util.py`.
- [output/](output/) — сгенерированные `.md` (в `.gitignore`).
- [.env.example](.env.example) — шаблон переменных (без секретов).
