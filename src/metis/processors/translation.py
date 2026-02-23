"""Translation module using deep-translator (online)."""
import re
from pathlib import Path


def is_english_text(text: str) -> bool:
    english_chars = len(re.findall(r"[a-zA-Z]", text))
    total_chars = len(re.findall(r"[a-zA-Z\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", text))

    if total_chars == 0:
        return False

    ratio = english_chars / total_chars
    return ratio > 0.8


async def translate_to_chinese(text: str) -> str:
    """Translate text to Chinese, handling long texts by chunking."""
    try:
        from deep_translator import GoogleTranslator

        # GoogleTranslator has a ~5000 char limit
        MAX_CHUNK_SIZE = 4500

        if len(text) <= MAX_CHUNK_SIZE:
            return GoogleTranslator(source="en", target="zh-CN").translate(text) or text

        # Split into chunks at paragraph boundaries
        chunks = _split_text_into_chunks(text, MAX_CHUNK_SIZE)
        translated_chunks = []

        for chunk in chunks:
            if chunk.strip():
                translated = GoogleTranslator(source="en", target="zh-CN").translate(chunk)
                translated_chunks.append(translated or chunk)
            else:
                translated_chunks.append(chunk)

        return "\n\n".join(translated_chunks)
    except Exception:
        return text


def _split_text_into_chunks(text: str, max_size: int) -> list[str]:
    """Split text into chunks at paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # If single paragraph is too long, split at sentence boundaries
        if len(para) > max_size:
            # First add any accumulated content
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            # Split long paragraph at sentence boundaries
            sentences = _split_into_sentences(para)
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 2 <= max_size:
                    current_chunk += (" " if current_chunk else "") + sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
        elif len(current_chunk) + len(para) + 2 <= max_size:
            current_chunk += ("\n\n" if current_chunk else "") + para
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences, preserving punctuation."""
    # Split at sentence-ending punctuation followed by space
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s for s in sentences if s.strip()]


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
