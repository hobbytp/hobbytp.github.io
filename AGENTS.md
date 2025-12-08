<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# Hugo Blog AI Assistant Instructions

## 🏗️ Project Overview

This is a Hugo-based static blog system using PaperMod theme, deployed on GitHub Pages. The system features multilingual support (Chinese/English), AI-powered content tools, and automated workflows.

### Core Architecture
- **Hugo Version**: 0.152.2 (extended)
- **Theme**: PaperMod (standard multi-page architecture)
- **Languages**: Chinese (default), English
- **Deployment**: GitHub Pages via GitHub Actions
- **Content Structure**: Multi-language content under `content/zh/` and `content/en/`

## 📁 Key Directory Structure

```
hobbytp.github.io/
├── config/_default/          # Hugo configuration files
├── content/                   # Multilingual content
│   ├── zh/                   # Chinese content
│   └── en/                   # English content
├── static/                    # Static assets (images, CSS, JS)
├── layouts/                   # Hugo template overrides
├── assets/                    # SCSS/CSS processing
├── tools/                     # Python tools for content management
│   ├── content-analysis/      # AI-powered content analysis
│   ├── image-optimization/    # Image optimization tools
│   ├── performance-monitor/   # Performance analysis
│   └── pdf-exporter/         # PDF export functionality
├── scripts/                   # Automation scripts
├── .github/workflows/         # CI/CD workflows
└── public/                    # Generated site (gitignored)
```

## 🛠️ Hugo Configuration

### Main Configuration (`config/_default/hugo.toml`)
- **BaseURL**: `https://hobbytp.github.io/`
- **Title**: "Peng Tan's AI Blog"
- **Theme**: PaperMod
- **Default Language**: Chinese (`zh`)
- **Build Settings**: Production-ready with optimizations enabled

### Key Features
- **Multilingual Support**: Separate content trees per language
- **Image Optimization**: WebP support, quality settings
- **Performance Caching**: Resource caching strategies
- **SEO**: Robots.txt enabled, Git info disabled

## 🚀 Development Workflow

### Local Development
```bash
# Start development server
make dev
# or
docker-compose up hugo
```

The development server runs on `http://localhost:1313` with:
- Live reload enabled
- Draft content visible
- Fast rendering disabled for better debugging

### Building for Production
```bash
# Production build
make build
# or
make full-build          # Includes optimization and analysis
make full-build-ai       # AI-enhanced build process
```

## 🧪 Testing & Validation

### Architecture Validation
```bash
# Run complete architecture validation
make validate-architecture
```

The validation script checks:
- Template architecture compliance (PaperMod standard)
- CSS file size limits (≤1000 lines)
- No problematic CSS selectors
- Hugo build success
- SPA mode disabled status

### Content Quality Analysis
```bash
# Basic content analysis
make analyze-content

# AI-enhanced content analysis
make analyze-content-ai

# Analyze specific file
make analyze-content FILE=./content/zh/some-article.md
```

### Performance Analysis
```bash
# Performance monitoring
make analyze-performance
make performance-report
```

## 📦 Deployment

### GitHub Actions CI/CD
- **Trigger**: Push to `main` or `gh-pages` branches
- **Process**: Build → Deploy to GitHub Pages
- **Environment**: Production Hugo build with minification
- **Dependencies**: Node.js for PostCSS processing

### Deployment Workflow (`.github/workflows/hugo.yml`)
1. Checkout repository with submodules
2. Setup Hugo v0.152.2 extended
3. Install Node.js dependencies (PostCSS, Autoprefixer)
4. Build site with `hugo --minify --configDir=config`
5. Deploy to GitHub Pages

## 🎨 Customization Guidelines

### CSS Architecture
- **Main File**: `assets/css/custom.css` (~745 lines)
- **Pipeline**: Hugo CSS bundling with minification and fingerprinting
- **Limits**: Keep under 1000 lines for performance
- **Approach**: Override PaperMod CSS variables, avoid CDN dependencies

### Template Customization
- **Location**: `layouts/` directory
- **Standard**: Follow Hugo template hierarchy
- **Compliance**: Must be PaperMod compatible
- **Forbidden**: No SPA templates or complex JavaScript routing

## 🤖 AI-Powered Tools

### Content Analysis (`tools/content-analysis/`)
- **Basic**: Word count, reading time, structure analysis
- **AI-Enhanced**: Content quality scoring, SEO recommendations
- **Dashboard**: JSON data generation for frontend analytics

### Image Management
```bash
# Optimize existing images
make optimize-images

# Generate AI cover images
make generate-ai-covers

# Generate covers for specific directory
make generate-covers-for-directory DIRECTORY=papers
```

### PDF Export
```bash
# Export all articles to PDF
make export-pdf

# Export specific article
make export-pdf FILE=./content/zh/article.md
```

## ⚙️ Makefile Commands

### Development
- `make dev` - Start development server
- `make fresh` - Clean and restart
- `make stop` - Stop services

### Build & Deploy
- `make build` - Production build
- `make full-build` - Complete build process
- `make clean` - Clean build artifacts

### Analysis & Optimization
- `make analyze-content` - Content quality analysis
- `make analyze-performance` - Performance monitoring
- `make optimize-images` - Image optimization

### AI Tools
- `make analyze-content-ai` - AI-enhanced analysis
- `make generate-ai-covers` - AI cover generation
- `make generate-json-data-ai` - AI analytics data

## 🚨 Architecture Constraints

### ✅ Allowed
- Standard Hugo template hierarchy
- PaperMod theme customization
- CSS custom properties for theming
- Hugo's built-in features and optimizations
- Progressive enhancement JavaScript

### ❌ Forbidden
- SPA mode activation (templates preserved but disabled)
- External CSS frameworks via CDN
- Complex JavaScript routing systems
- Modifying core PaperMod templates unnecessarily
- CSS `:contains()` selectors
- `assets/css/custom.css` > 1000 lines

## 🔧 Environment Setup

### Required Tools
- **Hugo**: v0.152.2+ extended
- **Docker**: For containerized development
- **Python**: For AI tools (conda `news_collector` environment)
- **Node.js**: For PostCSS processing

### Environment Variables
Key variables in `.env` file:
- `VOLCENGINE_ACCESS_KEY`, `VOLCENGINE_SECRET_KEY` - Default AI image generation
- `MODELSCOPE_API_KEY` - Alternative AI service
- `OPENAI_API_KEY` - OpenAI integration
- `TEXT2IMAGE_PROVIDER` - AI service selection

## 📋 Best Practices

### Before Committing
1. Run `make validate-architecture`
2. Test with `make build`
3. Check CSS file size limits
4. Verify template compliance

### Content Creation
1. Use proper front matter with language tags
2. Place content in correct language directory
3. Test with `make analyze-content`
4. Generate covers with AI tools when needed

### Performance Optimization
1. Optimize images before adding to content
2. Use Hugo's built-in image processing
3. Monitor with `make analyze-performance`
4. Keep CSS bundle size minimal

## 📚 Documentation

- **Architecture**: `ARCHITECTURE.md` - Detailed system architecture
- **Development**: `CLAUDE.md` - Development guidelines
- **Project**: `README.md` - General project information
- **Layouts**: `docs/layout-overview.md` - Template structure

---

**Current Architecture Status**: ✅ STABLE & PRODUCTION-READY
**Last Updated**: Based on analysis of Hugo v0.152.2, PaperMod theme, and current tooling
**Maintainer**: Follow the established patterns and validation procedures for any changes.
