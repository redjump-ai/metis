# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-23
**Commit:** 4523072
**Branch:** master

## OVERVIEW
URL Content Reader with Obsidian Sync - fetches web content and saves to Obsidian vault. Python 3.11+, CLI + FastAPI server.

## STRUCTURE
```
.
├── src/metis/          # Main source (6 modules)
│   ├── api/            # FastAPI server + web UI
│   ├── cli/            # Typer CLI commands
│   ├── fetchers/       # Content fetching (Firecrawl, Playwright)
│   ├── processors/     # Content processing, image download
│   ├── storage/        # Obsidian vault sync
│   └── workflow/       # Orchestration
├── tests/              # pytest (20 tests)
├── scripts/            # Utility scripts
├── pyproject.toml      # Project config (ruff, mypy)
└── SKILL.md           # AI assistant integration
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add new platform | `src/metis/fetchers/platform.py` | Add URL patterns to PLATFORMS dict |
| Add CLI command | `src/metis/cli/__main__.py` | Typer app definition |
| Modify storage | `src/metis/storage/__init__.py` | Frontmatter, file ops |
| Add API endpoint | `src/metis/api/__init__.py` | FastAPI routes |

## CODE MAP
| Symbol | Type | Location |
|--------|------|----------|
| ContentFetcher | class | fetchers/__init__.py |
| process_content | func | processors/__init__.py |
| save_to_obsidian | func | storage/__init__.py |
| detect_platform | func | fetchers/platform.py |
| url_db | singleton | storage/database.py |

## CONVENTIONS
- **Imports**: Absolute imports from `metis.*`
- **Line length**: 100 max (ruff)
- **Async**: Use `async/await` for I/O operations
- **Dataclasses**: Use `@dataclass` for data structures

## ANTI-PATTERNS (THIS PROJECT)
- NEVER use `as any` or `@ts-ignore` for type safety
- NEVER commit `.env` files
- NEVER skip error handling in fetchers

## UNIQUE STYLES
- Frontmatter format: YAML with title, url, platform, status, tags, summary
- Filename sanitization: strip author prefix, replace spaces with dashes
- Platform detection via URL pattern matching

## COMMANDS
```bash
# Install
pip install -e .

# CLI
metis fetch <url>
metis sync
metis schedule --interval=30

# API Server
metis serve

# Tests
pytest tests/ -v

# Lint
ruff check src/
mypy src/
```

## NOTES
- Requires OBSIDIAN_VAULT_PATH env var
- Firecrawl API key optional (some platforms need it)
- Web UI available at FastAPI root `/`
