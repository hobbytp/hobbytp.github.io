# AI Tech Blog - Unified Architecture Document

**Document Version:** 2.0 (Merged)
**Date:** 2025-11-12
**Project:** AI Tech Blog (Peng Tan's AI Blog)
**BMAD Phase:** 3 - Architecture
**PRD Reference:** `docs/prd.md`

> This file merges previous `architecture.md` and `architecture-fixes.md` into one authoritative source. All prior fix summaries are integrated; the separate fixes file is removed for simplicity.

---

## 1. Executive Summary

This document defines the corrected and optimized architecture for the AI Tech Blog. The architecture addresses critical structural issues found in the current Hugo PaperMod implementation and provides a scalable foundation for implementing the requirements defined in the PRD.

## 2. Current Architecture Analysis & Issues

### 2.1 🔴 Historical Critical Issues (Resolved)

#### 2.1.1 Missing Core Hugo Templates

**Issue:** Essential Hugo templates were deleted, breaking the template inheritance chain

- `layouts/_default/baseof.html` - Missing (CRITICAL)
- `layouts/_default/list.html` - Missing (CRITICAL)
- Impact: Site build failures, broken layout inheritance

**Status:** ✅ Restored

#### 2.1.2 Template Hierarchy Conflicts

**Issue:** Custom SPA templates conflict with PaperMod theme templates

- Custom `baseof-spa.html` vs. missing `baseof.html`
- Custom `list-spa.html` vs. missing `list.html`
- Impact: Inconsistent rendering, theme features breaking

**Status:** ✅ Standard PaperMod templates reinstated; SPA templates archived only

#### 2.1.3 CSS and Asset Management Issues

**Issue:** Multiple CSS bundling approaches causing conflicts

- Tailwind CSS loaded via CDN in custom templates
- PaperMod's SCSS-based styling system
- Custom glassmorphism CSS conflicts

**Status:** ✅ Unified Hugo pipeline; Tailwind CDN removed; excessive overrides reduced

### 2.2 Current Working Components

✅ Hugo (v0.149.x)  
✅ PaperMod theme  
✅ Multi-language (zh/en)  
✅ Automated content & news scripts  
✅ CI/CD via GitHub Actions  
✅ Left sidebar + right sticky TOC + ScrollSpy  
✅ Architecture validation script (pre-commit)

## 3. Corrected Architecture Design

### 3.1 Template Hierarchy Architecture

```text
layouts/
├── _default/
│   ├── baseof.html              # ✅ RESTORED - Hugo base template
│   ├── list.html                # ✅ RESTORED - List page template
│   ├── single.html              # Custom article layout
│   ├── search.html              # Custom search functionality
│   ├── baseof-spa.html          # (Archived) SPA base – DO NOT ACTIVATE
│   └── list-spa.html            # (Archived) SPA list – DO NOT ACTIVATE
├── partials/
│   ├── head.html                # HTML head section
│   ├── header.html              # ✅ Custom glassmorphism header
│   ├── footer.html              # Footer section
│   ├── seo.html                 # SEO meta tags
│   └── search.html              # Search functionality partial
├── _custom/                     # Custom layout extensions
└── shortcodes/                  # Hugo shortcodes
```

### 3.2 CSS and Asset Architecture

#### 3.2.1 Stacked CSS Strategy
```text
assets/css/
├── main.css                     # PaperMod core styles (inherited)
├── extended/                    # Custom style extensions
│   ├── typography.css          # Typography enhancements
│   ├── components.css          # Component-specific styles
│   └── responsive.css          # Responsive design rules
├── glassmorphism.css           # (Optional) Glassmorphism UI components
├── custom.css                   # Site-specific customizations
└── spa.css                      # (Archived) SPA-specific styles (unused)
```

#### 3.2.2 CSS Bundling Pipeline
```hugo
{{/* CSS Bundle Configuration */}}
{{- $styles := slice (resources.Get "css/main.css") -}}
{{- range resources.Match "css/extended/*.css" -}}
  {{- $styles = $styles | append . -}}
{{- end -}}
{{- $styles = $styles | append (resources.Get "css/glassmorphism.css") -}}
{{- $styles = $styles | append (resources.Get "css/custom.css") -}}
{{- $bundle := $styles | resources.Concat "css/site.bundle.css" | resources.Minify -}}
```

#### 3.2.3 Current Constraints & Guidelines

| Rule | Status |
|------|--------|
| `custom.css` ≤ 1000 lines | ✅ (~745 lines) |
| No Tailwind CDN | ✅ Removed |
| No unsupported selectors like `:contains()` | ✅ Compliant |
| Prefer modular split (layout/components/utilities) | 🚧 Planned |

> Tailwind can be reconsidered only via local build tooling; CDN injection remains prohibited.

### 3.3 Content Management Architecture

#### 3.3.1 Content Structure
```text
content/
├── zh/                          # Chinese content (primary)
│   ├── papers/                 # Academic paper reviews
│   ├── technologies/           # Technical deep-dives
│   ├── projects/               # Project showcases
│   ├── daily_ai/               # Automated daily news
│   ├── celebrity_insights/     # Industry insights
│   ├── big_companies/          # Tech company analysis
│   └── training/               # Training guides
├── en/                         # English content (secondary)
└── draft/                      # Work in progress
```

#### 3.3.2 Content Processing Pipeline
```text
Content Creation → Quality Analysis → SEO Optimization → Build → Deploy
     ↓                ↓                   ↓           ↓        ↓
Hugo Front Matter   AI Analysis        Auto Tags   Hugo     GitHub
    ↓                ↓                   ↓        Build    Pages
Markdown Files   Content Score     Meta Tags    Minify   CDN
```

### 3.4 Automation Architecture

#### 3.4.1 Content Collection System
```text
Daily AI News Pipeline:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Data Sources   │───▶│  Collection API  │───▶│  Quality Filter │
│  • Gemini API   │    │  • Python V2     │    │  • Deduplication│
│  • Perplexity   │    │  • Multi-source  │    │  • Scoring      │
│  • RSS Feeds    │    │  • Scheduling    │    │  • Categorize   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  Hugo Content   │
                                                │  • Auto-gen MD   │
                                                │  • Front Matter  │
                                                │  • Image Gen     │
                                                └─────────────────┘
```

#### 3.4.2 Content Analysis System
```text
Content Analysis Pipeline:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Input Content  │───▶│  Analysis Engine │───▶│  Output Reports │
│  • Markdown     │    │  • Readability   │    │  • Quality Score │
│  • Front Matter │    │  • SEO Analysis  │    │  • Suggestions   │
│  • Images       │    │  • Keywords      │    │  • Analytics     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 3.5 Performance Architecture

#### 3.5.1 Optimization Layers
```text
Performance Optimization Stack:
┌─────────────────────────────────────────────────────────────┐
│                     CDN Layer                               │
│  • GitHub Pages CDN                                         │
│  • Static Asset Caching                                     │
│  • Geographic Distribution                                 │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Hugo Build Layer                          │
│  • Asset Minification (JS/CSS)                              │
│  • Image Optimization (WebP, Responsive)                    │
│  • HTML Minification                                        │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Content Layer                             │
│  • Lazy Loading Images                                      │
│  • Efficient HTML Structure                                 │
│  • Optimized Markdown Processing                            │
└─────────────────────────────────────────────────────────────┘
```

#### 3.5.2 Image Processing Architecture
```text
Image Processing Pipeline:
Original Images → Hugo Processing → Multiple Formats → CDN Delivery
       │               │                │                │
   Upload         Resize          Responsive           Cache
   Scripts        Compression     Generation           Distribution
   │               │                │                │
   ▼               ▼                ▼                ▼
 Raw Files    Optimized       WebP/AVIF           Fast Loading
```

### 3.6 Multi-language Architecture

#### 3.6.1 Language Management
```text
Multi-language Structure:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Chinese (zh)   │    │  English (en)    │    │  Language Data  │
│  • Primary Lang │    │  • Selected Art  │    │  • i18n Files   │
│  • All Content  │    │  • Translations  │    │  • UI Strings   │
│  • SEO Focus    │    │  • SEO Support   │    │  • Language Nav │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 4. Technology Stack

### 4.1 Core Technologies
- **Static Site Generator:** Hugo v0.146.0+
- **Theme:** PaperMod (v6+)
- **Host:** GitHub Pages
- **Domain:** hobbytp.github.io
- **SSL:** GitHub Pages automatic
- **CI/CD:** GitHub Actions

### 4.2 Development Tools
- **Content Management:** Hugo CLI, Makefile
- **Image Processing:** Hugo imaging, Custom Python scripts
- **Automation:** Python 3.11+, Conda environment
- **Analytics:** Google Analytics, Search Console
- **SEO:** Hugo built-in SEO, Schema.org

### 4.3 External Integrations
- **AI APIs:** Google Gemini, Perplexity
- **News Sources:** Multiple RSS feeds, AI news APIs
- **Image Generation:** AI image generation APIs
- **Analytics:** Google Analytics 4
- **Search:** Hugo built-in search + JavaScript enhancement

## 5. Data Architecture

### 5.1 Content Data Flow
```text
Content Creation → Hugo Processing → Static Files → CDN → Users
      │                │                │           │        │
  Markdown          Build           Optimized     Cache    Browser
  Files            Process         HTML/CSS/JS    Dist      Render
  Front Matter     Template         Generation    Update    Display
```

### 5.2 Metadata Architecture
```yaml
# Content Metadata Schema
---
title: "Article Title"
date: 2024-01-15T10:00:00+08:00
draft: false
tags: ["AI", "LLM", "技术"]
categories: ["ai_tools"]
description: "Article summary"
keywords: ["SEO", "keywords"]
author: "Peng Tan"
images: ["/images/article-cover.jpg"]
series: ["AI Series"]
weight: 100
---
```

### 5.3 Analytics Data
```text
Analytics Collection:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  User Actions   │───▶│  GA4 Tracking    │───▶│  Analytics UI   │
│  • Page Views   │    │  • Events        │    │  • Dashboard    │
│  • Search       │    │  • Conversions   │    │  • Reports      │
│  • Engagement   │    │  • Custom Events │    │  • Insights     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 6. Security Architecture

### 6.1 Security Layers
```
Security Implementation:
┌─────────────────────────────────────────────────────────────┐
│                   Application Security                      │
│  • Input Sanitization                                       │
│  • XSS Prevention                                           │
│  • Secure Headers                                           │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Security                   │
│  • HTTPS Enforcement                                        │
│  • GitHub Security                                          │
│  • Dependency Updates                                       │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                       Data Security                         │
│  • GDPR Compliance                                          │
│  • Minimal Data Collection                                 │
│  • Cookie Management                                        │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Content Security Policy (CSP)

```text
Content-Security-Policy:
default-src 'self';
script-src 'self' 'unsafe-inline' https://www.googletagmanager.com;
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
font-src 'self' https://fonts.gstatic.com;
img-src 'self' data: https:;
connect-src 'self' https://www.google-analytics.com;
```

> Tailwind CDN removed; CSP tightened accordingly.

## 7. Deployment Architecture

### 7.1 Build Process
```text
Build Pipeline:
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Source Code    │───▶│  Hugo Build      │───▶│  GitHub Pages   │
│  • Content      │    │  • Asset Minify  │    │  • Deployment   │
│  • Templates    │    │  • Image Opt     │    │  • SSL Cert     │
│  • Config       │    │  • HTML Gen      │    │  • CDN          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 7.2 CI/CD Architecture
```yaml
# GitHub Actions Workflow
name: Build and Deploy
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Hugo
      - name: Build Site
      - name: Deploy to GitHub Pages
```

## 8. Scalability Architecture

### 8.1 Content Scalability
- **Content Volume:** Support 10,000+ articles
- **Media Storage:** Optimized image handling with CDN
- **Search Performance:** Fast search with indexing
- **Build Time:** Incremental builds for large sites

### 8.2 Traffic Scalability
- **Concurrent Users:** 1000+ simultaneous visitors
- **Geographic Distribution:** CDN-based content delivery
- **Load Handling:** Static site architecture scales naturally
- **Peak Performance:** Core Web Vitals maintenance

## 9. Implementation Plan

### 9.1 Phase 1: Critical Fixes (Week 1)
1. **Template Architecture Restoration**
   - ✅ Restore `layouts/_default/baseof.html`
   - ✅ Restore `layouts/_default/list.html`
   - Validate template hierarchy
   - Test all page types

2. **CSS Architecture Cleanup**
   - Consolidate CSS bundling strategy
   - Resolve PaperMod vs custom styles conflicts
   - Implement responsive design correctly
   - Optimize loading performance

3. **Build System Validation**
   - Verify Hugo build process
   - Test all content types
   - Validate multi-language support
   - Check CI/CD pipeline

### 9.2 Phase 2: Performance Optimization (Weeks 2-4)
1. **Asset Optimization**
   - Implement advanced image processing
   - CSS/JS minification and bundling
   - Lazy loading implementation
   - CDN optimization

2. **Core Web Vitals**
   - Performance monitoring setup
   - Optimization implementation
   - Continuous monitoring
   - Performance reporting

### 9.3 Phase 3: Feature Implementation (Weeks 5-12)
Based on PRD requirements, implement features in priority order:
1. Enhanced content analysis system
2. Advanced search functionality
3. Personalized recommendations
4. Interactive content features
5. Community features

## 10. Monitoring & Maintenance

### 10.1 Performance Monitoring

Key Metrics:

- Page Load Time: < 2 seconds
- Core Web Vitals: All "Good"
- Mobile Performance: 90+ PageSpeed
- Site Uptime: 99.5%+

Monitoring Tools:

- Google PageSpeed Insights
- Google Search Console
- Google Analytics
- Custom performance scripts

### 10.2 Architecture Health Checks
```yaml
Regular Checks:
  Weekly: Build performance verification
  Monthly: Template hierarchy validation
  Quarterly: Security audit
  Annually: Architecture review and optimization
```

## 11. Risk Mitigation

### 11.1 Technical Risks
- **Template Conflicts:** Proper override hierarchy
- **Performance Degradation:** Continuous monitoring
- **Build Failures:** Automated testing
- **Dependency Issues:** Regular updates

### 11.2 Mitigation Strategies
- **Backup Templates:** Maintain template backups
- **Staging Environment:** Test changes before deployment
- **Rollback Strategy:** Quick rollback procedures
- **Documentation:** Comprehensive architecture docs

---

**Document Status:** Complete
**Architecture Fixes:** Critical issues resolved
**Next Phase:** Sprint Planning and Implementation
**Estimated Implementation:** 12 weeks across 3 phases

## Appendix: Layout Enhancements Summary (Merged from Fixes)

| Feature | Previous State | Current State | Status |
|---------|----------------|---------------|--------|
| Sidebar | None / fragile | Fixed left sidebar | ✅ |
| TOC | Absent | Sticky + ScrollSpy | ✅ |
| Template Mode | SPA overwrite risk | Stable multi-page | ✅ |
| CSS Size | 2000+ lines (legacy) | ~745 lines focused | ✅ |
| External CSS | Tailwind CDN injected | Removed / pipeline only | ✅ |
| Navigation | Hard-coded SPA map | Hugo menu taxonomy | ✅ |
| Validation | Manual checking | Automated pre-commit script | ✅ |

### A.1 ScrollSpy Overview

Lightweight native JS observes heading intersection; updates TOC link `.active` and sets `aria-current="true"` for accessibility.

### A.2 Future Enhancements

- Mobile sidebar collapse / drawer
- TOC collapsible on narrow screens
- Modular CSS refactor
- Automated accessibility audit

## 12. Critical Architecture Fixes Completed

✅ **Fixed Issues:**
1. **Restored `layouts/_default/baseof.html`** - Hugo base template
2. **Restored `layouts/_default/list.html`** - List page template
3. **Validated template hierarchy** - Proper inheritance chain
4. **CSS architecture cleanup plan** - Resolved conflicts
5. **Build system validation** - Hugo build process verified

🎯 **Ready for PRD Implementation:**
- Architecture foundation is solid
- Template hierarchy properly established
- Performance optimizations planned
- Scalability considerations addressed
- Security measures implemented