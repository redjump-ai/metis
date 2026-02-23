---
name: metis
description: URL 内容抓取和 Obsidian 同步工具。支持多平台内容提取（WeChat、Xiaohongshu、Zhihu、Twitter/X 等）、自动翻译、LLM 摘要生成、图像下载。当用户需要抓取网页内容，保存到 Obsidian，管理 RSS/URL 工作流，生成文章摘要，翻译文章时使用。
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
  - "translate content"
  - "download article"
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
- **翻译**: 自动将英文内容翻译为中文（支持长文本分块，最大 4500 字符/块）
- **摘要**: 使用 LLM 生成文章摘要（OpenAI/Anthropic/Ollama/Zhipu）

### 3. Obsidian 同步

- 保存为 Markdown 文件，带 YAML frontmatter
- Frontmatter 字段：title, url, platform, status, tags, summary
- 工作流状态：pending → extracted → read → valuable → archive
- 支持 URL 状态跟踪数据库

### 4. API 服务

- 内置 FastAPI 服务器
- Web UI 界面
- RESTful API 端点

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
ZHIPU_API_KEY=your_zhipu_key
```

创建 `config.yaml` 配置 LLM：

```yaml
llm:
  provider: "openai"  # openai, anthropic, ollama, zhipu
  model: "gpt-4o-mini"

translation:
  enabled: true
  target_lang: "zh"

fetch:
  timeout: 30
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

# 仅获取内容不保存
python -m metis.cli fetch <url> --save=false
```

### 场景 3: 生成文章摘要

```bash
# 使用默认配置
python -m metis.cli summarize article.md

# 指定 provider 和 model
python -m metis.cli summarize article.md --provider openai --model gpt-4

# 输出到文件
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

### 场景 6: 启动 API 服务器

```bash
# 启动 FastAPI 服务器
uvicorn metis.api:app --reload --port 8000

# 访问 Web UI
# http://localhost:8000
```

## CLI 命令参考

| 命令 | 描述 |
|------|------|
| `sync` | 同步 inbox 中的所有 URL |
| `fetch <url>` | 抓取单个 URL |
| `list-urls [status]` | 列出所有 URL（可选：按状态过滤） |
| `mark-read <url>` | 标记为已读 |
| `mark-valuable <url>` | 标记为有价值 |
| `archive <url>` | 归档 URL |
| `status <url>` | 查看 URL 状态 |
| `summarize <file>` | 使用 LLM 摘要 |
| `config-llm` | 查看 LLM 配置 |
| `schedule` | 定时同步 |
| `init` | 查看配置 |
| `wechat-setup` | 设置微信登录 |
| `wechat-status` | 查看微信登录状态 |

## API 端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | Web UI 主页 |
| GET | `/health` | 健康检查 |
| POST | `/api/fetch` | 抓取 URL |
| POST | `/api/sync` | 批量同步 |
| GET | `/api/urls` | 列出所有 URL |
| POST | `/api/summarize` | 生成摘要 |

## 故障排除

### 抓取失败

1. **检查 URL 是否有效**
2. **平台是否需要登录**（WeChat、知乎可能需要）
3. **尝试使用 Playwright**（代码会自动回退）
4. **检查 Firecrawl API key**（如果使用 Firecrawl）

### 翻译失败

- 检查网络连接
- 长文本会自动分块处理（每块 4500 字符）
- 翻译失败时会返回原文

### 摘要生成失败

- 检查 LLM API key 配置
- 尝试不同的 provider 或 model
- 检查 config.yaml 配置

### 知乎抓取

- 知乎有严格的反爬机制，建议使用 Playwright MCP 或手动登录

## 架构

```
metis/
├── src/metis/
│   ├── api/           # FastAPI + Web UI
│   ├── cli/           # Typer CLI
│   ├── fetchers/      # 内容抓取 (Firecrawl, Jina, Playwright)
│   ├── processors/   # 处理、翻译、摘要
│   ├── storage/      # Obsidian 同步、数据库
│   ├── llm/          # LLM providers
│   └── config/       # 配置管理
```

## 环境变量

| 变量 | 描述 | 默认值 |
|------|------|---------|
| `OBSIDIAN_VAULT_PATH` | Obsidian vault 路径 | `./obsidian-vault` |
| `URL_INBOX_MD` | URL 输入文件 | `URL_INBOX.md` |
| `INBOX_PATH` | 输出文件夹 | `inbox` |
| `FIRECRAWL_API_KEY` | Firecrawl API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `ZHIPU_API_KEY` | Zhipu API key | - |
| `OLLAMA_BASE_URL` | Ollama 地址 | `http://localhost:11434` |
| `TRANSLATION_TARGET_LANG` | 翻译目标语言 | `zh` |
| `FETCH_TIMEOUT` | 抓取超时(秒) | 30 |
