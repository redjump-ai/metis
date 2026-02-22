"""URL content fetching with three-tier fallback strategy."""
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import httpx

from metis.config import settings
from metis.fetchers.platform import detect_platform, PlatformInfo


@dataclass
class FetchedContent:
    url: str
    title: str
    markdown: str
    platform: PlatformInfo
    raw_html: Optional[str] = None
    metadata: Optional[dict] = None


class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> Optional[FetchedContent]:
        pass


class FirecrawlFetcher(BaseFetcher):
    async def fetch(self, url: str) -> Optional[FetchedContent]:
        if not settings.firecrawl_api_key:
            return None

        try:
            from firecrawl import FirecrawlApp

            app = FirecrawlApp(api_key=settings.firecrawl_api_key)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, lambda: app.scrape(url, formats=["markdown", "html"])
            )

            if result and getattr(result, "markdown", None):
                markdown = getattr(result, "markdown", "")
                # Check for WeChat verification page
                if "环境异常" in markdown or "完成验证" in markdown[:500]:
                    return None
                if len(markdown) > 100:
                    platform = detect_platform(url)
                    title = self._extract_title(markdown, result)
                    return FetchedContent(
                        url=url,
                        title=title,
                        markdown=markdown,
                        platform=platform,
                        raw_html=getattr(result, "html", None),
                        metadata=getattr(result, "metadata", None),
                    )
        except Exception:
            pass
        return None

    def _extract_title(self, markdown: str, result) -> str:
        if hasattr(result, "metadata") and result.metadata:
            if isinstance(result.metadata, dict):
                title = result.metadata.get("title", "")
                if title:
                    return title[:200]
        
        lines = markdown.split("\n")
        for line in lines[:30]:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()[:200]
        for line in lines[:30]:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("!") and not line.startswith("[") and len(line) > 10 and "http" not in line and not line.isupper():
                return line[:200]
        return "Untitled"


class JinaFetcher(BaseFetcher):
    async def fetch(self, url: str) -> Optional[FetchedContent]:
        try:
            jina_url = f"https://r.jina.ai/{url}"
            headers = {
                "Accept": "text/markdown",
            }

            async with httpx.AsyncClient(timeout=settings.fetch_timeout) as client:
                response = await client.get(jina_url, headers=headers)
                if response.status_code == 200 and len(response.text) > 100:
                    markdown = response.text
                    # Check for WeChat verification page
                    if "环境异常" in markdown or "完成验证" in markdown[:500]:
                        return None
                    platform = detect_platform(url)
                    title = self._extract_title(markdown)
                    return FetchedContent(
                        url=url,
                        title=title,
                        markdown=markdown,
                        platform=platform,
                    )
        except Exception:
            pass
        return None

    def _extract_title(self, markdown: str) -> str:
        lines = markdown.split("\n")
        for line in lines[:10]:
            line = line.strip()
            if line.startswith("Title: "):
                title = line[7:].strip()
                if title.endswith(" / X"):
                    title = title[:-5].strip()
                if title:
                    return title[:200]
        for line in lines[:10]:
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("[") and len(line) > 5 and "http" not in line:
                return line[:200]
        return "Untitled"


class PlaywrightFetcher(BaseFetcher):
    """Playwright-based fetcher with platform-specific extraction."""

    async def fetch(self, url: str) -> Optional[FetchedContent]:
        try:
            from playwright.async_api import async_playwright

            platform = detect_platform(url)
            user_agent = self._get_user_agent(platform.name)

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(user_agent=user_agent)

                # Load saved authentication state if available
                if settings.playwright_state_path.exists():
                    try:
                        await context.add_cookies(
                            eval(settings.playwright_state_path.read_text())
                        )
                    except Exception:
                        pass

                page = await context.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Check for verification page (WeChat)
                page_content = await page.content()
                if "环境异常" in page_content or "完成验证" in page_content:
                    # Try to click verification button
                    verify_btn = await page.query_selector("text=去验证")
                    if verify_btn:
                        await verify_btn.click()
                        await page.wait_for_load_state("networkidle", timeout=15000)
                        page_content = await page.content()
                    
                    # If still on verification page, fail
                    if "环境异常" in page_content or "完成验证" in page_content:
                        await browser.close()
                        return None

                # Platform-specific content extraction
                if platform.name == "wechat":
                    content = await self._extract_wechat_content(page)
                else:
                    content = await self._extract_generic_content(page)

                await browser.close()

                if content and len(content.get("content", "")) > 100:
                    markdown = self._format_markdown(content, platform.name)
                    return FetchedContent(
                        url=url,
                        title=content.get("title", "Untitled")[:200],
                        markdown=markdown,
                        platform=platform,
                        raw_html=content.get("html"),
                        metadata=content.get("metadata"),
                    )
        except Exception:
            pass
        return None

    def _get_user_agent(self, platform_name: str) -> str:
        """Get platform-specific user agent."""
        if platform_name == "wechat":
            # WeChat built-in browser user agent
            return "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38(0x18002629) NetType/WIFI Language/zh_CN"
        return settings.user_agent

    async def _extract_wechat_content(self, page) -> dict:
        """Extract content from WeChat public account article."""
        # Wait for article content to load
        try:
            await page.wait_for_selector("#js_content", timeout=10000)
        except Exception:
            pass

        result = await page.evaluate("""
            () => {
                const title = document.querySelector('#activity-name')?.innerText?.trim() || '';
                const author = document.querySelector('#js_name')?.innerText?.trim() || '';
                const content = document.querySelector('#js_content')?.innerText?.trim() || '';
                const publishTime = document.querySelector('#publish_time')?.innerText?.trim() || '';
                const html = document.querySelector('#js_content')?.innerHTML || '';
                
                // Extract images
                const images = [];
                document.querySelectorAll('#js_content img').forEach(img => {
                    const src = img.dataset.src || img.src;
                    if (src && !src.startsWith('data:')) {
                        images.push(src);
                    }
                });

                return {
                    title,
                    author,
                    content,
                    publishTime,
                    html,
                    metadata: {
                        author,
                        publishTime,
                        imageCount: images.length
                    }
                };
            }
        """)
        return result

    async def _extract_generic_content(self, page) -> dict:
        """Generic content extraction for other platforms."""
        return await page.evaluate("""() => {
            const title = document.title || '';
            const body = document.body || document.documentElement;
            return {
                title: title,
                content: body.innerText || '',
                html: body.innerHTML || ''
            };
        }""")

    def _format_markdown(self, content: dict, platform_name: str) -> str:
        """Format extracted content as markdown."""
        lines = []
        
        if platform_name == "wechat":
            metadata = content.get("metadata", {})
            if metadata.get("author"):
                lines.append(f"**作者**: {metadata['author']}")
            if metadata.get("publishTime"):
                lines.append(f"**发布时间**: {metadata['publishTime']}")
            if lines:
                lines.insert(0, "")
            lines.insert(0, f"# {content.get('title', '无标题')}")
            lines.append("")
            lines.append("---")
            lines.append("")
            lines.append(content.get("content", ""))
        else:
            lines.append(content.get("content", ""))
        
        return "\n".join(lines)


class ContentFetcher:
    def __init__(self):
        self.fetchers: list[BaseFetcher] = [
            FirecrawlFetcher(),
            JinaFetcher(),
            PlaywrightFetcher(),
        ]

    async def fetch(self, url: str) -> Optional[FetchedContent]:
        platform = detect_platform(url)
        
        # For platforms that require login (like WeChat), try Playwright first
        if platform.name == "wechat":
            # Try Playwright first for WeChat (better content extraction)
            playwright = PlaywrightFetcher()
            result = await playwright.fetch(url)
            if result:
                return result
            # Fall back to other fetchers if Playwright fails
        
        # Default order: Firecrawl -> Jina -> Playwright
        for fetcher in self.fetchers:
            result = await fetcher.fetch(url)
            if result:
                return result
        return None
