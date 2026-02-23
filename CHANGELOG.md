# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-02-23

### Added
- LLM summarization support (OpenAI, Anthropic, Ollama)
- Translation with long-text chunking (handles >5000 char articles)
- CLI summary generation command (`metis summarize`)
- CLI config-llm command to show LLM configuration
- Scheduled sync command (`metis schedule`)
- GitHub issue polling script
- Comprehensive unit tests (config, processors, LLM, platform, storage)

### Fixed
- Translation failure for long articles (chunked at 4500 char limit)
- Summary not generated in CLI mode
- Zhihu error response detection
- Title escaping and LLM context truncation
- Config loading for FastAPI server

### Changed
- Updated SKILL.md to skills.sh standard format
- Updated AGENTS.md with code structure
- Refactored config to use hybrid YAML + .env approach

### Removed
- Unused imports cleanup (partial)

## [0.1.0] - 2026-02-22

### Added
- Multi-strategy content fetching (Firecrawl → Jina → Playwright)
- Platform detection for WeChat, Xiaohongshu, Zhihu, Douyin, Bilibili, Twitter/X, etc.
- Image download with proper Referer headers
- Obsidian sync with YAML frontmatter
- Optional translation support (Argos Translate)
- Workflow tracking (pending → extracted → read → valuable/archive)
- Inbox-based workflow (add URLs to markdown, run sync)
- WeChat public account support with authentication
- CLI commands: fetch, sync, list-urls, mark-read, mark-valuable, archive, status
- FastAPI server support

### Changed
- Save as individual markdown files instead of folders
- URL status stored in file frontmatter
- Platform unification (x.com and twitter.com → twitter)
- Removed author prefix from filenames

### Fixed
- YAML frontmatter quote escaping
- Array parsing in frontmatter
- Content preservation when updating frontmatter
