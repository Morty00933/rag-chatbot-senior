from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, List
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Читаем конфиг из ENV (можно позже заменить на core.config)
PROMPT_DIR = os.getenv("PROMPT_DIR", "prompts")
PROMPT_LANG = os.getenv("PROMPT_LANG", "ru")
PROMPT_VARIANT = os.getenv("PROMPT_VARIANT", "v1")
PROMPT_STRICT = os.getenv("PROMPT_STRICT", "true").lower() in {"1", "true", "yes", "y"}
PROMPT_CITE = os.getenv("PROMPT_CITE", "true").lower() in {"1", "true", "yes", "y"}

def _prompt_dir() -> Path:
    return Path(PROMPT_DIR).resolve()

@lru_cache(maxsize=1)
def _jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(_prompt_dir())),
        autoescape=select_autoescape(enabled_extensions=(), default_for_string=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env

def _template_name(lang: str, variant: str) -> str:
    return f"system_{lang}_{variant}.j2"

@lru_cache(maxsize=128)
def get_system_instruction(
    lang: str | None = None,
    variant: str | None = None,
    cite: bool | None = None,
    strict: bool | None = None,
    extra_vars: Dict[str, Any] | None = None,
) -> str:
    lang = lang or PROMPT_LANG
    variant = variant or PROMPT_VARIANT
    cite = PROMPT_CITE if cite is None else cite
    strict = PROMPT_STRICT if strict is None else strict

    env = _jinja_env()
    tpl_name = _template_name(lang, variant)
    try:
        tpl = env.get_template(tpl_name)
    except Exception:
        tpl = env.get_template(f"system_{lang}.j2")

    vars: Dict[str, Any] = {"cite": cite, "strict": strict, "language": lang}
    if extra_vars:
        vars.update(extra_vars)
    return tpl.render(**vars).strip()

def build_user_prompt(question: str, contexts: List[str], system_instruction: str) -> str:
    ctx = "\n---\n".join(contexts)
    return (
        f"{system_instruction}\n\n"
        f"Вопрос: {question}\n\n"
        f"Контекстные фрагменты:\n{ctx}\n\n"
        f"Ответ:"
    )
