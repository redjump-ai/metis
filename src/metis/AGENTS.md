# src/metis/

**Parent:** ./AGENTS.md

## OVERVIEW
Core modules package containing all business logic.

## STRUCTURE
```
src/metis/
├── api/          # FastAPI + web UI
├── cli/          # Typer CLI entry
├── fetchers/     # Content fetchers
├── processors/   # Content processing
├── storage/      # Obsidian sync
├── workflow/     # Task orchestration
├── config.py     # Settings singleton
├── __main__.py   # CLI entry point
└── __init__.py   # Package init
```

## WHERE TO LOOK
| Task | File | Notes |
|------|------|-------|
| Platform support | `fetchers/platform.py` | PLATFORMS dict |
| API routes | `api/__init__.py` | FastAPI app |
| CLI commands | `cli/__main__.py` | Typer commands |
| DB operations | `storage/database.py` | SQLite wrapper |
| Config | `config.py` | Settings class |

## CONVENTIONS (this dir)
- Follow parent conventions
- Each module has `__init__.py` exposing public API
- Async functions in fetchers/processors

## ANTI-PATTERNS
- Don't import directly from submodules; use parent package imports
