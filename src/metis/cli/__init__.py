"""Metis CLI interface."""
import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from metis.config import settings
from metis.fetchers import ContentFetcher
from metis.processors import process_content, summarize_with_llm
from metis.processors.translation import is_english_text, process_with_translation
from metis.storage import read_url_inbox, save_to_obsidian
from metis.storage.database import ensure_base_file, url_db

app = typer.Typer(help="Metis - URL Content Reader with Obsidian Sync")
console = Console()


@app.command()
def fetch(url: str, save: bool = True, use_inbox: bool = True):
    """Fetch content from a URL and save to Obsidian."""
    asyncio.run(_fetch(url, save, use_inbox))


async def _fetch(url: str, save: bool, use_inbox: bool):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Fetching {url}...", total=None)

        # Add URL to database first
        url_db.add_url(url, "", "unknown")

        fetcher = ContentFetcher()
        content = await fetcher.fetch(url)

        if not content:
            url_db.update_status(url, "failed")
            console.print(f"[red]Failed to fetch content from {url}[/red]")
            raise typer.Exit(1)

        # Update URL with title and platform
        url_db.add_url(url, content.title, content.platform.name)

        progress.update(task, description="Processing content...")

        processed = await process_content(
            url=content.url,
            raw_markdown=content.markdown,
            title=content.title,
        )

        if save:
            # Generate summary using LLM
            progress.update(task, description="Generating summary...")
            try:
                processed.summary = await summarize_with_llm(processed.markdown)
            except Exception:
                # Fall back to empty summary if LLM fails
                processed.summary = ""

            progress.update(task, description="Saving to Obsidian...")
            # Save with status="extracted" directly to inbox file frontmatter
            path = save_to_obsidian(processed, status="extracted", use_inbox=use_inbox)

            saved_content_path = path  # Already a file, not a folder
            if is_english_text(processed.markdown):
                console.print("[yellow]English content detected, translating...[/yellow]")
                url_db.mark_english(url)
                await process_with_translation(
                    saved_content_path.read_text(encoding="utf-8"),
                    saved_content_path,
                    settings.translation_target_lang,
                )
                url_db.mark_translated(url)

            console.print(f"[green]Saved to: {path}[/green]")
        else:
            console.print(processed.markdown)

        progress.update(task, description="Done!", completed=True)


@app.command()
def list_urls(status: str | None = None):
    """List all URLs in the database."""
    urls = url_db.get_all_urls(status)

    if not urls:
        console.print("[yellow]No URLs found[/yellow]")
        return

    table = Table(title="URLs")
    table.add_column("Title", style="cyan")
    table.add_column("Platform", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Created", style="blue")

    for u in urls:
        table.add_row(
            u.get("title", "-")[:50],
            u.get("platform", "-"),
            u.get("status", "-"),
            u.get("created", "-")[:19] if u.get("created") else "-",
        )

    console.print(table)


@app.command()
def mark_read(url: str):
    """Mark a URL as read."""
    url_db.update_status(url, "read")
    console.print(f"[green]Marked as read: {url}[/green]")


@app.command()
def mark_valuable(url: str):
    """Mark a URL as valuable (for creation/knowledge base)."""
    url_db.update_status(url, "valuable")
    console.print(f"[green]Marked as valuable: {url}[/green]")


@app.command()
def archive(url: str):
    """Archive a URL."""
    url_db.update_status(url, "archived")
    console.print(f"[green]Archived: {url}[/green]")


@app.command()
def status(url: str):
    """Show status of a specific URL."""
    url_info = url_db.get_url(url)
    if not url_info:
        console.print(f"[red]URL not found: {url}[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Title:[/cyan] {url_info.get('title', '-')}")
    console.print(f"[cyan]Platform:[/cyan] {url_info.get('platform', '-')}")
    console.print(f"[cyan]Status:[/cyan] {url_info.get('status', '-')}")
    console.print(f"[cyan]File:[/cyan] {url_info.get('file_path', '-')}")
    console.print(f"[cyan]Created:[/cyan] {url_info.get('created', '-')}")
    console.print(f"[cyan]Extracted:[/cyan] {url_info.get('extracted_at', '-')}")
    console.print(f"[cyan]Read:[/cyan] {url_info.get('read_at', '-')}")
    console.print(f"[cyan]English:[/cyan] {url_info.get('is_english', False)}")
    console.print(f"[cyan]Translated:[/cyan] {url_info.get('has_translation', False)}")


@app.command()
def init():
    """Initialize Metis configuration."""
    console.print("[blue]Metis Configuration[/blue]")
    console.print(f"Base Path: {settings.base_path}")
    console.print(f"Obsidian Vault: {settings.obsidian_vault_path}")
    console.print(f"URL Inbox (input): {settings.url_inbox_md}")
    console.print(f"Inbox Path (output): {settings.inbox_path}")
    console.print(f"Media Folder: {settings.media_folder}")
    console.print(f"Archive Folder: {settings.archive_folder}")
    console.print(f"Translation Target: {settings.translation_target_lang}")


@app.command()
def sync():
    """Sync URLs from inbox markdown file and process them."""
    asyncio.run(_sync())


async def _sync():
    urls = read_url_inbox()

    if not urls:
        console.print("[yellow]No URLs found in inbox file[/yellow]")
        return

    console.print(f"[blue]Found {len(urls)} URLs to process[/blue]")

    for url in urls:
        # Skip if already processed
        existing = url_db.get_url(url)
        if existing and existing.get("status") in ["extracted", "read", "valuable", "archived"]:
            console.print(f"[dim]Skipping (already processed): {url}[/dim]")
            continue

        console.print(f"[cyan]Processing: {url}[/cyan]")
        await _fetch(url, save=True, use_inbox=True)

    console.print("[green]Sync complete![/green]")


if __name__ == "__main__":
    app()


@app.command()
def wechat_setup(wait_seconds: int = 120):
    """Setup WeChat login for reading public account articles."""
    asyncio.run(_wechat_setup(wait_seconds))


async def _wechat_setup(wait_seconds: int):
    """Perform WeChat login setup."""
    import json

    from playwright.async_api import async_playwright

    console.print("[blue]WeChat Login Setup[/blue]")
    console.print("正在启动浏览器，请扫码登录微信...")

    # Ensure data directory exists
    settings.base_path.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Open WeChat MP login page
        await page.goto("https://mp.weixin.qq.com/")

        console.print("\n请在浏览器中完成以下操作：")
        console.print("1. 点击右上角「登录」")
        console.print("2. 使用微信扫码登录")
        console.print(f"3. 登录成功后会自动保存（等待 {wait_seconds} 秒）")
        console.print("\n等待登录中...")

        # Wait for login
        try:
            await page.wait_for_selector(".weui-desktop-account__nickname", timeout=wait_seconds * 1000)
            console.print("✓ 检测到登录成功！")
        except:
            console.print("等待超时，尝试保存当前状态...")

        # Save auth state
        storage = await context.storage_state()

        with open(settings.wechat_auth_path, 'w', encoding='utf-8') as f:
            json.dump(storage, f, ensure_ascii=False, indent=2)

        await browser.close()

    console.print(f"[green]✓ 认证状态已保存到: {settings.wechat_auth_path}[/green]")


@app.command()
def wechat_status():
    """Check WeChat login status."""
    if not settings.wechat_auth_path.exists():
        console.print("[yellow]✗ 未找到认证状态[/yellow]")
        console.print("运行: python -m metis.cli wechat-setup")
        return

    from datetime import datetime
    mtime = datetime.fromtimestamp(settings.wechat_auth_path.stat().st_mtime)
    age = datetime.now() - mtime

    console.print("[green]✓ 认证文件存在[/green]")
    console.print(f"  路径: {settings.wechat_auth_path}")
    console.print(f"  创建时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(f"  已过去: {age.days} 天 {age.seconds // 3600} 小时")

    if age.days > 7:
        console.print("\n[yellow]⚠ 认证可能已过期，建议重新登录[/yellow]")



@app.command()
def schedule(
    interval: int = typer.Option(60, help="Sync interval in minutes"),
    max_count: int = typer.Option(0, help="Max number of syncs (0 = infinite)"),
):
    """Run scheduled sync at regular intervals.
    
    Example:
        metis schedule --interval=30
        metis schedule --interval=60 --max-count=10
    """
    import time
    from datetime import datetime

    console.print(f"[blue]Starting scheduled sync (every {interval} minutes)[/blue]")
    console.print("Press Ctrl+C to stop\n")

    count = 0
    while True:
        count += 1
        console.print(f"\n[cyan]Sync #{count} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/cyan]")

        try:
            asyncio.run(_sync())
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

        if max_count > 0 and count >= max_count:
            console.print(f"\n[green]Completed {count} syncs, exiting[/green]")
            break

        console.print(f"\n[dim]Next sync in {interval} minutes...[/dim]")
        time.sleep(interval * 60)



@app.command()
def summarize(
    markdown_file: str = typer.Argument(..., help="Path to markdown file"),
    provider: str = typer.Option(None, help="LLM provider (openai, anthropic, ollama)"),
    model: str = typer.Option(None, help="Model name"),
    output: str = typer.Option(None, help="Output file path"),
):
    """Summarize markdown content using LLM.
    
    Example:
        metis summarize article.md
        metis summarize article.md --provider openai --model gpt-4
        metis summarize article.md --output summary.md
    """
    asyncio.run(_summarize(markdown_file, provider, model, output))


async def _summarize(markdown_file: str, provider: str | None, model: str | None, output: str | None):
    from metis.processors import summarize_with_llm

    file_path = Path(markdown_file)
    if not file_path.exists():
        console.print(f"[red]File not found: {markdown_file}[/red]")
        raise typer.Exit(1)

    markdown_content = file_path.read_text(encoding="utf-8")

    # Strip frontmatter if present
    if markdown_content.startswith("---"):
        parts = markdown_content.split("---", 2)
        if len(parts) >= 3:
            markdown_content = parts[2].strip()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating summary with LLM...", total=None)

        summary = await summarize_with_llm(
            markdown=markdown_content,
            provider=provider,
            model=model,
        )

        if output:
            output_path = Path(output)
            output_path.write_text(summary, encoding="utf-8")
            console.print(f"[green]Summary saved to: {output}[/green]")
        else:
            console.print("\n[cyan]Summary:[/cyan]")
            console.print(summary)

        progress.update(task, description="Done!", completed=True)


@app.command()
def config_llm():
    """Show LLM configuration."""
    console.print("[blue]LLM Configuration[/blue]")
    console.print(f"Provider: {settings.llm_provider}")
    console.print(f"Model: {settings.llm_model}")
    console.print(f"OpenAI API Key: {'*' * 20 if settings.openai_api_key else 'Not set'}")
    console.print(f"Anthropic API Key: {'*' * 20 if settings.anthropic_api_key else 'Not set'}")
    console.print(f"Ollama Base URL: {settings.ollama_base_url}")
    console.print("\n[blue]Summarization Prompt:[/blue]")
    console.print(settings.summarization_prompt[:200] + "...")
