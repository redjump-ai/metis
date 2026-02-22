"""FastAPI application for Metis."""
import asyncio
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from metis.config import settings
from metis.fetchers import ContentFetcher
from metis.processors import process_content
from metis.storage import save_to_obsidian, read_url_inbox
from metis.storage.database import url_db

app = FastAPI(title="Metis API", version="0.1.0")


class FetchRequest(BaseModel):
    url: str
    save: bool = True


class SyncRequest(BaseModel):
    urls: list[str]


class FetchResponse(BaseModel):
    success: bool
    message: str
    path: str | None = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web UI."""
    template_path = Path(__file__).parent / "templates" / "index.html"
    return template_path.read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/api/fetch", response_model=FetchResponse)
async def fetch_url(request: FetchRequest):
    """Fetch a single URL and optionally save to Obsidian."""
    try:
        # Add URL to database
        url_db.add_url(request.url, "", "unknown")

        # Fetch content
        fetcher = ContentFetcher()
        content = await fetcher.fetch(request.url)

        if not content:
            url_db.update_status(request.url, "failed")
            return FetchResponse(
                success=False,
                message=f"Failed to fetch content from {request.url}",
                path=None,
            )

        # Update URL with title and platform
        url_db.add_url(request.url, content.title, content.platform.name)

        if request.save:
            # Process content
            processed = await process_content(
                url=content.url,
                raw_markdown=content.markdown,
                title=content.title,
            )

            # Save to Obsidian
            path = save_to_obsidian(processed, status="extracted")

            return FetchResponse(
                success=True,
                message=f"Successfully fetched and saved to {path.name}",
                path=str(path),
            )

        return FetchResponse(
            success=True,
            message="Successfully fetched content",
            path=None,
        )

    except Exception as e:
        return FetchResponse(
            success=False,
            message=f"Error: {str(e)}",
            path=None,
        )


@app.post("/api/sync", response_model=FetchResponse)
async def sync_urls(request: SyncRequest):
    """Sync multiple URLs."""
    try:
        count = 0
        for url in request.urls:
            # Skip if already processed
            existing = url_db.get_url(url)
            if existing and existing.get("status") in ["extracted", "read", "valuable", "archived"]:
                continue

            # Fetch content
            url_db.add_url(url, "", "unknown")
            fetcher = ContentFetcher()
            content = await fetcher.fetch(url)

            if content:
                url_db.add_url(url, content.title, content.platform.name)

                # Process and save
                processed = await process_content(
                    url=content.url,
                    raw_markdown=content.markdown,
                    title=content.title,
                )
                save_to_obsidian(processed, status="extracted")
                count += 1

        return FetchResponse(
            success=True,
            message=f"Synced {count} URLs",
            path=None,
        )

    except Exception as e:
        return FetchResponse(
            success=False,
            message=f"Error: {str(e)}",
            path=None,
        )


@app.get("/api/urls")
async def list_urls():
    """List all URLs with their status."""
    try:
        urls = url_db.get_all_urls()
        return [
            {
                "url": u.get("url", ""),
                "title": u.get("title", ""),
                "platform": u.get("platform", "unknown"),
                "status": u.get("status", "pending"),
                "created": u.get("created", ""),
            }
            for u in urls
        ]
    except Exception:
        return []
