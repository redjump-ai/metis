<div align="center">

# Metis

> URL Content Reader with Obsidian Sync

[![PyPI Version](https://img.shields.io/pypi/v/metis.svg)](https://pypi.org/project/metis/)
[![Python Version](https://img.shields.io/pypi/pyversions/metis)](https://pypi.org/project/metis/)
[![License](https://img.shields.io/pypi/l/metis)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/redjump-ai/metis)](https://github.com/redjump-ai/metis/stargazers)

A powerful tool for fetching web content and automatically syncing to Obsidian. Supports multiple platforms including WeChat, Xiaohongshu, Zhihu, Twitter/X, and more.

</div>

## Features

- 🔍 **Multi-strategy Content Fetching**: Firecrawl (AI-powered) → Jina (free) → Playwright (browser automation)
- 🌍 **Platform Support**: WeChat, Xiaohongshu, Zhihu, Douyin, Bilibili, Twitter/X, and more
- 📷 **Image Download**: Downloads all images locally with proper Referer headers
- 📝 **Obsidian Sync**: Saves as individual Markdown files with YAML frontmatter
- 🌐 **Translation**: Auto-translates English content to Chinese with long-text chunking support
- 📊 **AI Summarization**: Uses LLM to generate article summaries (OpenAI, Anthropic, Oll 📥ama)
- **Inbox-based Workflow**: Add URLs to a markdown file, run `sync` to process them all

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
- **Optional**: Firecrawl API key for premium scraping

```bash
# Install Playwright
playwright install chromium
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

### 2. Configure LLM (Optional)

Create `config.yaml` for AI summarization:

```yaml
llm:
  provider: "openai"  # openai, anthropic, ollama
  model: "gpt-4o-mini"
  # model: "claude-sonnet-4-20250514"
  # model: "llama3"

# Or use environment variables
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Add URLs

Create `URL_INBOX.md` in your vault:

```markdown
https://x.com/someuser/status/1234567890
https://www.zhihu.com/question/1234567890
https://mp.weixin.qq.com/s/xxxxx
```

### 4. Sync

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
| `summarize <file>` | Summarize markdown using LLM |
| `config-llm` | Show LLM configuration |
| `schedule` | Run scheduled sync |
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
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |
| `OLLAMA_BASE_URL` | Ollama base URL | `http://localhost:11434` |
| `TRANSLATION_TARGET_LANG` | Target language | `zh` |

## Configuration

Metis uses a hybrid configuration system:

1. **`config.yaml`** - Primary config (LLM, translation, etc.)
2. **`.env`** - Sensitive data (API keys)

### config.yaml Example

```yaml
llm:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.7

translation:
  enabled: true
  target_lang: "zh"

fetch:
  timeout: 30
  user_agent: "Mozilla/5.0..."
```

## Architecture

```
metis/
├── src/metis/
│   ├── api/           # FastAPI server + web UI
│   ├── cli/           # Typer CLI commands
│   ├── fetchers/      # Content fetching (Firecrawl, Jina, Playwright)
│   ├── processors/   # Content processing, translation, summarization
│   ├── storage/       # Obsidian vault sync
│   ├── llm/           # LLM providers (OpenAI, Anthropic, Ollama)
│   └── config/        # Settings management
├── tests/
└── docs/
```

## FastAPI Server

```bash
uvicorn metis.api:app --reload
```

## AI Assistant Integration

Metis can be used as a skill in AI assistants. See [SKILL.md](SKILL.md) for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Firecrawl](https://www.firecrawl.dev/) - AI-powered web scraping
- [Jina AI](https://jina.ai/) - Free reader API
- [Playwright](https://playwright.dev/) - Browser automation
