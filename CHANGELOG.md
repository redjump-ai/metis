# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
