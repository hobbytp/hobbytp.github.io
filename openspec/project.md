# Project Context: hobbytp.github.io

## Purpose
Personal AI knowledge base and daily AI news aggregation system. Combines:
- Hugo-based blog for AI research papers, DeepSeek analysis, and technical topics
- Automated daily AI news collection system (V2.0 Pro)
- Multi-source news aggregation with quality scoring and deduplication

## Tech Stack
- **Frontend**: Hugo (PaperMod theme), Markdown
- **Backend**: Python 3.12, Conda environment (`news_collector`)
- **AI/LLM**: Google Gemini API, Anthropic Claude, DeepSeek models
- **News APIs**: NewsAPI, Tavily, Google Search, Serper, Brave Search, Metasota, HackerNews, DuckDuckGo, RSS Feeds, ArXiv
- **Automation**: GitHub Actions (daily @ 08:00 Beijing time)
- **Data Processing**: PyYAML, requests, python-dateutil, Pillow
- **Libraries**: google-generativeai, openai, perplexityai (suspended), ai-news-collector-lib

## Project Conventions

### Code Style
- Python: PEP 8 with 4-space indentation
- Markdown: Standard with Hugo front matter (YAML)
- File naming: kebab-case for filenames, snake_case for variables
- Comments: English, concise and meaningful

### Architecture Patterns
- **Content**: Organized by topic (zh/ subdirectories: deepseek, papers, daily_ai, etc.)
- **Scripts**: Modular collectors with quality scoring, deduplication, and fallback strategies
- **Error Handling**: Graceful degradation with fallback data sources
- **Data Flow**: Collection → Quality Scoring → Deduplication → Markdown Generation → Hugo Build

### Testing Strategy
- Manual testing with local conda environment before deployment
- Python import validation and error logging
- GitHub Actions workflow validation
- Visual inspection of generated markdown content

### Git Workflow
- Main branch: `main` (production)
- Feature branches: `enh/feature-name` (enhancements), `fix/issue-name` (bug fixes)
- Commit messages: Emoji prefixes + descriptive message (e.g., "🔧 改进今日焦点提取逻辑")
- PR reviews required before merge to main

## Domain Context
- **Daily AI News Format**: Hierarchical structure (Focus → Models → Tools → Applications → Academic) with quality ratings
- **Time Windows**: 24-hour rolling window (previous day 08:00 to current day 08:00, Beijing time)
- **Quality Metrics**: Stars (GitHub), downloads (HuggingFace), author count (ArXiv), keyword count (multi-source)
- **User Base**: Technical professionals, researchers, AI enthusiasts
- **Content Freshness**: Critical - outdated content undermines credibility

## Important Constraints
- **API Rate Limits**: Multiple APIs must be managed for quota
- **Processing Time**: Must complete within GitHub Actions time limits
- **Context Windows**: Long documents require efficient token compression (see DeepSeek-OCR patterns)
- **Data Privacy**: No sensitive personal data; API keys managed via GitHub Secrets
- **Chinese Language Support**: Content primarily in Chinese Simplified

## External Dependencies
- **Google Gemini API** - Daily summary generation
- **GitHub API** - Trending project collection
- **HuggingFace API** - New model detection
- **NewsAPI, Tavily, Serper, Brave Search, Metasota** - News aggregation
- **ArXiv API** - Academic paper collection
- **RSS Feeds** - Content syndication
- **Hugo** - Static site generation
- **GitHub Actions** - Automation and deployment
