# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-23
**Commit:** HEAD
**Branch:** master

## OVERVIEW
URL Content Reader with Obsidian Sync - fetches web content and saves to Obsidian vault. Python 3.11+, CLI + FastAPI server.

## STRUCTURE
```
.
├── src/metis/          # Main source (8 modules)
│   ├── api/            # FastAPI server + web UI
│   ├── cli/            # Typer CLI commands
│   ├── fetchers/       # Content fetching (Firecrawl, Jina, Playwright)
│   ├── processors/     # Content processing, translation, summarization
│   ├── storage/        # Obsidian vault sync
│   ├── llm/           # LLM providers (OpenAI, Anthropic, Ollama)
│   ├── config/        # Settings management
│   └── workflow/       # Orchestration
├── tests/              # pytest
├── scripts/            # Utility scripts (issue polling)
├── pyproject.toml      # Project config (ruff, mypy)
├── config.yaml         # LLM and translation config
├── SKILL.md           # AI assistant integration
└── AGENTS.md          # This file
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add new platform | `src/metis/fetchers/platform.py` | Add URL patterns to PLATFORMS dict |
| Add CLI command | `src/metis/cli/__init__.py` | Typer app definition |
| Modify storage | `src/metis/storage/__init__.py` | Frontmatter, file ops |
| Add API endpoint | `src/metis/api/__init__.py` | FastAPI routes |
| Modify translation | `src/metis/processors/translation.py` | Uses deep-translator with chunking |
| Modify summarization | `src/metis/processors/__init__.py` | Uses LLM |
| LLM providers | `src/metis/llm/providers.py` | OpenAI, Anthropic, Ollama |

## CODE MAP
| Symbol | Type | Location |
|--------|------|----------|
| ContentFetcher | class | fetchers/__init__.py |
| process_content | func | processors/__init__.py |
| summarize_with_llm | func | processors/__init__.py |
| translate_to_chinese | func | processors/translation.py |
| save_to_obsidian | func | storage/__init__.py |
| detect_platform | func | fetchers/platform.py |
| url_db | singleton | storage/database.py |
| LLMProvider | class | llm/providers.py |

## CONVENTIONS
- **Imports**: Absolute imports from `metis.*`
- **Line length**: 100 max (ruff)
- **Async**: Use `async/await` for I/O operations
- **Dataclasses**: Use `@dataclass` for data structures
- **Config**: Hybrid (config.yaml + .env)

## ANTI-PATTERNS (THIS PROJECT)
- NEVER use `as any` or `@ts-ignore` for type safety
- NEVER commit `.env` files
- NEVER skip error handling in fetchers
- NEVER use empty catch blocks `except: pass`

## UNIQUE STYLES
- Frontmatter format: YAML with title, url, platform, status, tags, summary
- Translation: Chunk-based for texts >4500 chars
- LLM: Supports OpenAI, Anthropic, Ollama
- Filename sanitization: strip author prefix, replace spaces with dashes
- Platform detection via URL pattern matching

## CONFIGURATION
Metis uses `config.yaml` for primary config and `.env` for sensitive data:

```yaml
# config.yaml
llm:
  provider: "openai"
  model: "gpt-4o-mini"

translation:
  enabled: true
  target_lang: "zh"
```

```bash
# .env
OBSIDIAN_VAULT_PATH=/path/to/vault
FIRECRAWL_API_KEY=sk-...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## COMMANDS
```bash
# Install
pip install -e .

# CLI
metis fetch <url>
metis sync
metis schedule --interval=30
metis summarize <file.md>
metis config-llm

# API Server
uvicorn metis.api:app --reload

# Tests
pytest tests/ -v

# Lint
ruff check src/
mypy src/
```

## NOTES
- Translation uses `deep-translator` with chunking (4500 char limit)
- Summarization uses LLM (OpenAI/Anthropic/Ollama)
- Some platforms (Zhihu, WeChat) may require login or have rate limits
- GitHub issue polling: `python scripts/poll_issues.py`
