# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Hugo-based AI tech blog (个人AI技术博客) focused on AI content including paper reviews, technical analysis, open source projects, industry news, and celebrity insights. The blog is bilingual (Chinese primary, English secondary) and uses the PaperMod theme.

## Key Development Commands

### Local Development

```bash
# Start development server (recommended)
make dev

# Fresh start (clean + dev)
make fresh

# Stop services
make stop
```

### Build & Deployment

```bash
# Production build
make build

# Full build pipeline (image optimization + analysis + build + performance)
make full-build

# AI-enhanced build pipeline
make full-build-ai

# Generate AI covers for articles
make generate-ai-covers

# Clean build artifacts
make clean
```

### AI Cover Generation

The blog features automated AI cover generation using ModelScope Qwen-image:

**🆕 Automatic Generation (Recommended):**
```bash
# Simply commit new articles, AI covers are generated automatically
git add content/zh/category/new-article.md
git commit -m "Add new article"
git push origin main
```

**Manual Generation:**
```bash
# Generate AI covers for articles without covers
make generate-ai-covers

# Limited batch generation (recommended for API limits)
conda run -n news_collector python scripts/ai_cover_generator.py --workflow-mode --limit=10

# Force regenerate existing covers
conda run -n news_collector python scripts/ai_cover_generator.py --workflow-mode --force
```

**GitHub Actions:**
- Automatic: Triggered on push to main branch
- Manual: Use "Generate Blog Images" workflow in Actions tab
- Supports: ModelScope (default), Gemini, or both services

### Content Management

```bash
# Create new content
hugo new content/zh/technologies/new-article.md
hugo new content/zh/papers/paper-review.md
hugo new content/zh/projects/project-intro.md

# Update word counts for all articles
python scripts/update_word_count.py

# Collect daily AI news (automated workflow)
python scripts/daily_ai_collector_v2.py
```

### Analysis & Optimization

```bash
# Analyze content quality
make analyze-content

# AI-enhanced content analysis
make analyze-content-ai

# Analyze specific file
make analyze-content FILE=./content/zh/google/a2a.md
make analyze-content-ai FILE=./content/zh/google/a2a.md

# Generate JSON data for frontend dashboard
make generate-json-data
make generate-json-data-ai

# Optimize images
make optimize-images

# Performance analysis
make analyze-performance
make performance-report
```

## Architecture & Structure

### Content Organization

```
content/
├── zh/                    # Chinese content (primary)
│   ├── papers/           # Paper reviews and analysis
│   ├── technologies/     # Technical deep dives
│   ├── projects/         # Open source project showcases
│   ├── celebrity_insights/  # Industry leader interviews
│   ├── my_insights/      # Personal analysis and thoughts
│   ├── daily_ai/         # Daily AI news collection
│   ├── big_companies/    # Big tech company analysis
│   ├── training/         # Training and fine-tuning guides
│   └── ...
├── en/                   # English content (select)
└── draft/               # Work in progress articles
```

### Key Configuration Files

- `config.toml` - Main Hugo configuration with Chinese localization
- `docker-compose.yml` - Development and build containers
- `Makefile` - Comprehensive build automation and tools
- `.github/workflows/` - CI/CD pipelines for automated deployment

### Automation & Scripts

- `scripts/daily_ai_collector_v2.py` - Automated AI news collection using multiple APIs
- `scripts/update_word_count.py` - Word count statistics for all articles
- `scripts/blog_analyzer.py` - Content analysis and reporting
- `tools/` - Image optimization, performance monitoring, and content analysis tools

### Theme & Customization

- Uses PaperMod theme with extensive customization
- Custom layouts in `layouts/` directory
- Enhanced link styling with visual indicators
- Dark mode support and responsive design
- Custom CSS for improved readability and visual hierarchy

## Development Workflow

### 🚨 CRITICAL: Architecture Rules
**THIS PROJECT USES PAPERMOD STANDARD ARCHITECTURE - DO NOT MODIFY!**

#### ✅ MANDATORY Requirements:
- **NEVER** run `scripts/toggle-spa-mode.sh` (DISABLED)
- **NEVER** modify core Hugo templates (`layouts/_default/baseof.html`, `list.html`)
- **NEVER** add Tailwind CDN alongside PaperMod CSS
- **ALWAYS** test with `make build` before committing
- **READ** `ARCHITECTURE.md` before any changes

#### ✅ Approved Templates:
- `layouts/_default/baseof.html` - PaperMod standard only
- `layouts/_default/list.html` - PaperMod standard only
- `layouts/_default/single.html` - PaperMod compatible
- `layouts/partials/header.html` - Clean navigation
- `layouts/partials/head.html` - Optimized CSS bundling

#### ❌ FORBIDDEN:
- SPA mode scripts and templates
- Tailwind CDN integration
- Complex JavaScript routing systems
- Hugo core template modification
- Large custom CSS files (>500 lines)

### Content Creation Process

1. Create new article using `hugo new content/zh/category/article-name.md`
2. Write content with proper front matter (title, date, tags, categories)
3. Use `make analyze-content-ai` to get AI-powered content suggestions
4. **CRITICAL:** Test with `make build` to ensure architecture stability
5. Test locally with `make dev`
6. Update word counts with `python scripts/update_word_count.py`

### Daily Content Automation

The blog features automated daily AI news collection:

- Uses multiple APIs (Google Gemini, Perplexity, custom news sources)
- Filters content from last 24 hours
- Removes duplicates and ranks by quality
- Auto-generates daily articles in `content/zh/daily_ai/`

### Deployment Pipeline

- Automatic deployment to GitHub Pages on push to main branch
- CI/CD includes submodules, dependencies, and optimization
- Production build with minification and performance optimization

## Content Guidelines

### Front Matter Structure

```yaml
---
title: "文章标题"
date: 2024-01-15T10:00:00+08:00
draft: false
tags: ["AI", "LLM", "技术"]
categories: ["ai_tools"]
description: "文章简介"
---
```

### Content Categories

- **papers**: Academic paper reviews and analysis
- **technologies**: Technical tutorials and deep dives
- **projects**: Open source project showcases
- **celebrity_insights**: Industry leader interviews and quotes
- **my_insights**: Personal analysis and thoughts
- **daily_ai**: Daily AI news and updates
- **big_companies**: Analysis of tech companies' AI strategies
- **training**: ML training and fine-tuning guides
- **context_engineering**: Context window optimization techniques
- **mas**: Multi-agent systems
- **ai_programming**: AI-assisted programming tools and techniques

## Special Features

### AI-Enhanced Content Analysis

The blog includes sophisticated AI-powered content analysis tools that can:

- Analyze content quality and readability
- Suggest improvements for structure and clarity
- Generate metadata and tags automatically
- Create performance reports and analytics

### Multi-Language Support

- Primary language: Chinese (Simplified)
- Secondary language: English (for important content)
- Configurable through Hugo's i18n system

### Performance Optimizations

- Image optimization pipeline with multiple format support
- CDN-ready asset management
- Performance monitoring and reporting
- Automatic minification and compression

## Environment Setup

### Requirements

- Hugo Extended v0.140.0+
- Docker & Docker Compose (for containerized development)
- Python 3.11+ (for scripts and automation)
- Node.js (optional, for theme development)
- Hugo theme "PaperMod" (for theme customization)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/hobbytp/hobbytp.github.io.git
cd hobbytp.github.io

# Initialize submodules
git submodule update --init --recursive

# Install Python dependencies for scripts
pip install -r scripts/requirements.txt

# Start development
make fresh
```

### Python Environment

The project uses a conda environment called `news_collector` for automation scripts. The Makefile automatically detects and uses this environment when available.

## Deployment

The blog is automatically deployed to GitHub Pages when pushing to the `main` branch. The deployment process includes:

- Building the site with Hugo
- Optimizing images and assets
- Running performance analysis
- Deploying to GitHub Pages with proper configuration

For manual deployment or testing, use `make build` to generate the `public/` directory.
