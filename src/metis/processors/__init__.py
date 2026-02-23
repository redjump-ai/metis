"""Content processing - image download and markdown formatting."""
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx

from metis.config import settings
from metis.fetchers.platform import detect_platform
from metis.llm import llm_client


@dataclass
class ProcessedContent:
    title: str
    markdown: str
    images: list[str]
    url: str
    platform_name: str
    summary: str = ""


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = name[:100]
    return name or "untitled"


def extract_image_urls(markdown: str) -> list[str]:
    urls = []

    markdown_urls = re.findall(r"!\[.*?\]\((.*?)\)", markdown)
    urls.extend(markdown_urls)

    html_img_urls = re.findall(r'<img[^>]+src="([^"]+)"', markdown)
    urls.extend(html_img_urls)

    xiaohongshu_urls = re.findall(r"https://[^'\"\s]+\.xiaohongshu\.com[^\s'\"<>]+", markdown)
    urls.extend(xiaohongshu_urls)

    feishu_urls = re.findall(r"https://[^'\"\s]+\.feishu\.cn[^\s'\"<>]+", markdown)
    urls.extend(feishu_urls)

    return list(set(urls))


async def download_image(url: str, media_folder: Path, platform_name: str) -> Path | None:
    platform = detect_platform(url)
    headers = {"User-Agent": settings.user_agent}

    if platform.referer:
        headers["Referer"] = platform.referer

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return None

            content = response.content
            ext = _guess_extension(url, content)

            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            filename = f"img_{url_hash}{ext}"
            filepath = media_folder / filename

            filepath.write_bytes(content)
            return filepath
    except Exception:
        return None


def _guess_extension(url: str, content: bytes) -> str:
    if content[:4] == b"\xff\xd8\xff":
        return ".jpg"
    if content[:4] == b"\x89PNG":
        return ".png"
    if content[:8] == b"GIF89a" or content[:8] == b"GIF87a":
        return ".gif"
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return ".webp"

    url_lower = url.lower()
    if ".jpg" in url_lower or ".jpeg" in url_lower:
        return ".jpg"
    if ".png" in url_lower:
        return ".png"
    if ".gif" in url_lower:
        return ".gif"
    if ".webp" in url_lower:
        return ".webp"

    return ".jpg"


async def process_content(
    url: str,
    raw_markdown: str,
    title: str,
) -> ProcessedContent:
    platform = detect_platform(url)
    image_urls = extract_image_urls(raw_markdown)

    downloaded_images: dict[str, str] = {}
    media_folder = settings.media_folder

    for img_url in image_urls:
        if img_url.startswith("http"):
            local_path = await download_image(img_url, media_folder, platform.name)
            if local_path:
                relative_path = local_path.relative_to(settings.media_folder)
                downloaded_images[img_url] = str(relative_path)

    markdown = raw_markdown
    for original_url, local_path in downloaded_images.items():
        markdown = markdown.replace(original_url, local_path)

    markdown = _clean_metadata(markdown)

    return ProcessedContent(
        title=title,
        markdown=markdown,
        images=list(downloaded_images.values()),
        url=url,
        platform_name=platform.name,
    )


def _clean_metadata(markdown: str) -> str:
    lines = markdown.split("\n")
    cleaned_lines = []

    skip_patterns = [
        r"^来源：",
        r"^作者：",
        r"^发布时间：",
        r"^阅读：",
        r"^点赞：",
        r"^收藏：",
        r"^分享：",
    ]

    for line in lines:
        should_skip = False
        for pattern in skip_patterns:
            if re.match(pattern, line.strip()):
                should_skip = True
                break
        if not should_skip:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def summarize_text(markdown: str, max_length: int = 200) -> str:
    """Generate a summary from markdown content using extractive method.
    
    Args:
        markdown: The markdown content to summarize
        max_length: Maximum length of summary in characters
    
    Returns:
        A concise summary of the content
    """
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', markdown)
    # Remove inline code
    text = re.sub(r'`[^`]+`', '', text)
    # Remove image references
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Remove headers markers
    text = re.sub(r'^#+ ', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)

    # Split into paragraphs
    paragraphs = text.split('\n\n')

    # Filter out short paragraphs and noise
    meaningful_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        # Skip very short paragraphs
        if len(p) < 20:
            continue
        # Skip paragraphs that are mostly special characters
        if len(re.sub(r'[\w\u4e00-\u9fff]', '', p)) > len(p) * 0.5:
            continue
        meaningful_paragraphs.append(p)

    if not meaningful_paragraphs:
        return ""

    # Take first 2-3 meaningful paragraphs
    summary_parts = []
    total_length = 0

    for para in meaningful_paragraphs[:3]:
        if total_length + len(para) <= max_length:
            summary_parts.append(para)
            total_length += len(para)
        elif not summary_parts:
            # If first paragraph is too long, truncate it
            summary_parts.append(para[:max_length] + "...")
            break
        else:
            break

    summary = ' '.join(summary_parts)

    # Clean up extra whitespace
    summary = re.sub(r'\s+', ' ', summary).strip()

    # Truncate if still too long
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(' ', 1)[0] + "..."

    return summary



async def summarize_with_llm(
    markdown: str,
    prompt: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> str:
    """Generate a summary using LLM.
    
    Args:
        markdown: The markdown content to summarize
        prompt: Custom prompt template (uses {{content}} placeholder)
        provider: Override LLM provider (openai, anthropic, ollama)
        model: Override model name
    
    Returns:
        LLM-generated summary
    """
    client = llm_client
    if provider or model:
        client = llm_client.__class__(provider=provider, model=model)

    response = await client.summarize(markdown, prompt)
    return response.content
