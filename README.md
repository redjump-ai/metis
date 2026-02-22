<div align="center">

# Metis

> URL Content Reader with Obsidian Sync

[![PyPI Version](https://img.shields.io/pypi/v/metis.svg)](https://pypi.org/project/metis/)
[![Python Version](https://img.shields.io/pypi/pyversions/metis)](https://pypi.org/project/metis/)
[![License](https://img.shields.io/pypi/l/metis)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/your-username/metis)](https://github.com/your-username/metis/stargazers)

A powerful tool for fetching web content and automatically syncing to Obsidian. Supports multiple platforms including WeChat, Xiaohongshu, Zhihu, Twitter/X, and more.

</div>

## Features

- 🔍 **Multi-strategy Content Fetching**: Firecrawl (AI-powered) → Jina (free) → Playwright (browser automation)
- 🌍 **Platform Support**: WeChat, Xiaohongshu, Zhihu, Douyin, Bilibili, Twitter/X, and more
- 📷 **Image Download**: Downloads all images locally with proper Referer headers
- 📝 **Obsidian Sync**: Saves as individual Markdown files with YAML frontmatter
- 🌐 **Translation**: Auto-translates English content to Chinese (optional)
- 📊 **Workflow Tracking**: Content lifecycle from pending → extracted → read → valuable/archive
- 📥 **Inbox-based Workflow**: Add URLs to a markdown file, run `sync` to process them all

## Installation

```bash
pip install metis
```

Or install from source:

```bash
git clone https://github.com/redjump-ai/metis.git
cd metis
pip install -e .
```

### Dependencies

- **Required**: Python 3.11+, Playwright
- **Optional**: Firecrawl API key for premium scraping, Argos Translate for offline translation

```bash
# Install Playwright
playwright install chromium

# For translation support (optional)
pip install metis[translate]
```

## Quick Start

### 1. Configure

Copy `.env.example` to `.env` and configure:

```bash
# Path to your Obsidian vault
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault

# URL inbox file (input)
URL_INBOX_MD=personal-os/captures/URL_INBOX.md

# Output folder for saved content
INBOX_PATH=personal-os/captures/inbox

# Optional: Firecrawl API key
FIRECRAWL_API_KEY=your_api_key
```

### 2. Add URLs

Create `URL_INBOX.md` in your vault:

```markdown
https://x.com/someuser/status/1234567890
https://www.zhihu.com/question/1234567890
https://mp.weixin.qq.com/s/xxxxx
```

### 3. Sync

```bash
metis sync
# or
python -m metis.cli sync
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `sync` | Sync all URLs from inbox file |
| `list-urls` | List all URLs with status |
| `fetch <url>` | Fetch a single URL |
| `mark-read <url>` | Mark URL as read |
| `mark-valuable <url>` | Mark as valuable |
| `archive <url>` | Archive URL |
| `status <url>` | Show URL status |
| `wechat-setup` | Setup WeChat login |
| `init` | Show configuration |

## WeChat Support

For WeChat public account articles, you need to login first:

```bash
# Setup WeChat login (opens browser for QR code scan)
metis wechat-setup

# Check login status
metis wechat-status
```

## Content Workflow

```
URL Inbox → extracted → read → valuable → knowledge base
                     ↘ archive
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OBSIDIAN_VAULT_PATH` | Path to your Obsidian vault | Required |
| `URL_INBOX_MD` | Input file with URLs | `URL_INBOX.md` |
| `INBOX_PATH` | Output folder | `inbox` |
| `FIRECRAWL_API_KEY` | Firecrawl API key | Optional |
| `TRANSLATION_TARGET_LANG` | Target language | `zh` |

## Architecture

```
metis/
├── src/metis/
│   ├── cli/           # CLI interface
│   ├── fetchers/     # URL fetching (Firecrawl, Jina, Playwright)
│   ├── processors/    # Content processing
│   ├── storage/      # Obsidian sync
│   ├── config/       # Settings
│   └── workflow/     # State machine
├── tests/
└── docs/
```

## FastAPI Server

```bash
uvicorn metis.api:app --reload
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Firecrawl](https://www.firecrawl.dev/) - AI-powered web scraping
- [Jina AI](https://jina.ai/) - Free reader API
- [Playwright](https://playwright.dev/) - Browser automation
