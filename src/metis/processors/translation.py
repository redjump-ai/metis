"""Translation module using deep-translator (online)."""
import re
from pathlib import Path

from metis.config import settings


def is_english_text(text: str) -> bool:
    english_chars = len(re.findall(r"[a-zA-Z]", text))
    total_chars = len(re.findall(r"[a-zA-Z\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", text))

    if total_chars == 0:
        return False

    ratio = english_chars / total_chars
    return ratio > 0.8


async def translate_to_chinese(text: str) -> str:
    try:
        from deep_translator import GoogleTranslator

        translated = GoogleTranslator(source="en", target="zh-CN").translate(text)
        return translated or text
    except Exception:
        return text


def extract_frontmatter(content: str) -> tuple[str, str]:
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[1], parts[2]
    return "", content


def add_translation_to_markdown(
    original_markdown: str,
    translated_markdown: str,
    file_path: Path,
) -> None:
    combined = f"""{original_markdown}

---

## Translation

{translated_markdown}
"""
    file_path.write_text(combined, encoding="utf-8")


async def process_with_translation(
    content: str,
    file_path: Path,
    target_lang: str = "zh",
) -> bool:
    if not is_english_text(content):
        return False

    if target_lang == "zh":
        frontmatter, body = extract_frontmatter(content)
        translated = await translate_to_chinese(body)
        add_translation_to_markdown(content, translated, file_path)
        return True

    return False
