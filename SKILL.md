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

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OBSIDIAN_VAULT_PATH` | Path to your Obsidian vault |
| `URL_INBOX_MD` | Input file with URLs to process |
| `INBOX_PATH` | Output folder for saved content |
| `FIRECRAWL_API_KEY` | Firecrawl API key (optional) |
