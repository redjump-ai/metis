---
name: metis
description: URL 内容抓取和 Obsidian 同步工具。支持多平台内容提取（WeChat、Xiaohongshu、Zhihu、Twitter/X 等）、自动翻译、LLM 摘要生成、图像下载。当用户需要抓取网页内容、保存到 Obsidian、管理 RSS/URL 工作流时使用。
triggers:
  - "抓取网页内容"
  - "保存到 Obsidian"
  - "同步 URL"
  - "提取微信文章"
  - "提取小红书"
  - "提取知乎文章"
  - "翻译文章"
  - "生成摘要"
  - "fetch url"
  - "save to obsidian"
  - "sync urls"
  - "extract wechat"
  - "summarize article"
---

# Metis

URL 内容抓取和 Obsidian 同步工具 - 帮助 AI agent 抓取网页内容并保存到 Obsidian vault。

## 核心功能

### 1. 内容抓取

支持多策略抓取（按优先级）：
- **Firecrawl** - AI 驱动的网页抓取（需要 API key）
- **Jina Reader** - 免费 API 抓取
- **Playwright** - 浏览器自动化（用于登录受限内容）

支持的平台：
- WeChat 公众号文章（需要登录）
- Xiaohongshu 小红书
- Zhihu 知乎
- Twitter/X
- Bilibili
- Douyin 抖音
- 通用网页

### 2. 内容处理

- **图像下载**: 自动下载所有图像到本地，带正确的 Referer 头
- **翻译**: 自动将英文内容翻译为中文（支持长文本分块）
- **摘要**: 使用 LLM 生成文章摘要（OpenAI/Anthropic/Ollama）

### 3. Obsidian 同步

- 保存为 Markdown 文件，带 YAML frontmatter
- Frontmatter 字段：title, url, platform, status, tags, summary
- 工作流状态：pending → extracted → read → valuable → archive

## 快速开始

### 安装

```bash
pip install metis
# 或从源码安装
git clone https://github.com/redjump-ai/metis.git
cd metis
pip install -e .
```

### 配置

创建 `.env` 文件：

```bash
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
URL_INBOX_MD=personal-os/captures/URL_INBOX.md
INBOX_PATH=personal-os/captures/inbox

# 可选：API Keys
FIRECRAWL_API_KEY=your_api_key
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

创建 `config.yaml` 配置 LLM：

```yaml
llm:
  provider: "openai"  # openai, anthropic, ollama
  model: "gpt-4o-mini"

translation:
  enabled: true
  target_lang: "zh"
```

## 使用场景

### 场景 1: 从 URL Inbox 同步

```bash
# 添加 URL 到 inbox 文件
# URL_INBOX.md 内容：
# https://x.com/user/status/123456
# https://mp.weixin.qq.com/s/xxxxx

# 运行同步
python -m metis.cli sync
```

### 场景 2: 抓取单个 URL

```bash
python -m metis.cli fetch <url>
```

### 场景 3: 生成文章摘要

```bash
python -m metis.cli summarize article.md
python -m metis.cli summarize article.md --provider openai --model gpt-4
python -m metis.cli summarize article.md --output summary.md
```

### 场景 4: 定时同步

```bash
# 每 30 分钟同步一次
python -m metis.cli schedule --interval=30

# 同步 10 次后退出
python -m metis.cli schedule --interval=60 --max-count=10
```

### 场景 5: 微信登录

```bash
# 首次设置：扫码登录
python -m metis.cli wechat-setup

# 查看登录状态
python -m metis.cli wechat-status
```

## CLI 命令参考

| 命令 | 描述 |
|------|------|
| `sync` | 同步 inbox 中的所有 URL |
| `fetch <url>` | 抓取单个 URL |
| `list-urls` | 列出所有 URL 及状态 |
| `mark-read <url>` | 标记为已读 |
| `mark-valuable <url>` | 标记为有价值 |
| `archive <url>` | 归档 URL |
| `status <url>` | 查看 URL 状态 |
| `summarize <file>` | 使用 LLM 摘要 |
| `config-llm` | 查看 LLM 配置 |
| `schedule` | 定时同步 |
| `init` | 查看配置 |

## 故障排除

### 抓取失败

1. **检查 URL 是否有效**
2. **平台是否需要登录**（WeChat、知乎可能需要）
3. **尝试使用 Playwright**（代码会自动回退）

### 翻译失败

- 检查网络连接
- 长文本会自动分块处理

### 摘要生成失败

- 检查 LLM API key 配置
- 尝试不同的 provider 或 model

## 架构

```
metis/
├── src/metis/
│   ├── cli/           # Typer CLI
│   ├── fetchers/      # 内容抓取
│   ├── processors/    # 处理、翻译、摘要
│   ├── storage/       # Obsidian 同步
│   ├── llm/           # LLM providers
│   └── config/        # 配置管理
```

## 环境变量

| 变量 | 描述 |
|------|------|
| `OBSIDIAN_VAULT_PATH` | Obsidian vault 路径 |
| `URL_INBOX_MD` | URL 输入文件 |
| `INBOX_PATH` | 输出文件夹 |
| `FIRECRAWL_API_KEY` | Firecrawl API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `OLLAMA_BASE_URL` | Ollama 地址 |
| `TRANSLATION_TARGET_LANG` | 翻译目标语言 |
