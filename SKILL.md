# Metis Skill

Metis can be used as a skill in AI assistants like OpenCode, Claude Code (Trae), OpenClaw, etc.

## Commands

### sync
Sync all URLs from inbox file and save content to Obsidian.

```bash
python -m metis.cli sync
```

### fetch
Fetch a single URL and save to Obsidian.

```bash
python -m metis.cli fetch <url>
```

### list-urls
List all URLs with their status.

```bash
python -m metis.cli list-urls
```

### schedule
Run scheduled sync at regular intervals.

```bash
python -m metis.cli schedule --interval=30
python -m metis.cli schedule --interval=60 --max-count=10
```

### wechat-setup
Setup WeChat login for reading public account articles.

```bash
python -m metis.cli wechat-setup
```

### wechat-status
Check WeChat login status.

```bash
python -m metis.cli wechat-status
```

### summarize
Summarize markdown content using LLM.

```bash
python -m metis.cli summarize <file.md>
python -m metis.cli summarize article.md --provider openai --model gpt-4
python -m metis.cli summarize article.md --output summary.md
```

### config-llm
Show LLM configuration.

```bash
python -m metis.cli config-llm
```

### init
Show current configuration.

```bash
python -m metis.cli init
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OBSIDIAN_VAULT_PATH` | Path to your Obsidian vault |
| `URL_INBOX_MD` | Input file with URLs to process |
| `INBOX_PATH` | Output folder for saved content |
| `FIRECRAWL_API_KEY` | Firecrawl API key (optional) |
| `OPENAI_API_KEY` | OpenAI API key (optional) |
| `ANTHROPIC_API_KEY` | Anthropic API key (optional) |
| `OLLAMA_BASE_URL` | Ollama base URL (optional) |

## Configuration

Create `config.yaml` for AI features:

```yaml
llm:
  provider: "openai"  # openai, anthropic, ollama
  model: "gpt-4o-mini"
  temperature: 0.7

translation:
  enabled: true
  target_lang: "zh"
```

## Features

- **Multi-platform**: WeChat, Xiaohongshu, Zhihu, Twitter/X, etc.
- **Translation**: Auto-translate English to Chinese with long-text support
- **Summarization**: Generate AI summaries using OpenAI, Anthropic, or Ollama
- **Workflow**: Track content from inbox → extracted → read → valuable
