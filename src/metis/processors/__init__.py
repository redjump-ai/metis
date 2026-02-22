"""Content processing - image download and markdown formatting."""
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import httpx

from metis.config import settings
from metis.fetchers.platform import detect_platform


@dataclass
class ProcessedContent:
    title: str
    markdown: str
    images: list[str]
    url: str
    platform_name: str


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


async def download_image(url: str, media_folder: Path, platform_name: str) -> Optional[Path]:
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
