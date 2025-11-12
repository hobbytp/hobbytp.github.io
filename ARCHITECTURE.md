# Hugo Blog Architecture Guide

**Last Updated:** 2025-11-12
**Version:** 2.2
**Status:** ✅ STABLE & SYNCHRONIZED

**Recent Changes (v2.2):**

- ✅ Added left fixed sidebar + right sticky TOC on article pages
- ✅ Implemented scroll-based heading highlight (ScrollSpy)
- ✅ Removed Tailwind CDN from all templates; unified Hugo CSS pipeline
- ✅ Fixed duplicate `<aside>` wrapper that collapsed main content width
- ✅ Kept list pages with consistent sidebar + card layout

---

## 🚨 CRITICAL: Architecture Decisions

### ✅ PaperMod Standard Architecture (CURRENT STATE)

This project uses **PaperMod standard multi-page architecture**. All templates are currently compliant with PaperMod standards.

#### ✅ Current Template Status

- `layouts/_default/baseof.html` - ✅ **PAPERMOD STANDARD** (verified, adds `has-sidebar` class)
- `layouts/_default/list.html` - ✅ **CUSTOM WITH SIDEBAR LAYOUT** (uses Hugo standard features)
- `layouts/_default/single.html` - ✅ **PAPERMOD COMPATIBLE** (verified)
- `layouts/partials/sidebar.html` - ✅ **CUSTOM SIDEBAR COMPONENT** (new in v2.1)

#### ❌ FORBIDDEN (with current compliance status)

- ❌ Using `scripts/toggle-spa-mode.sh` (✅ DISABLED: `scripts/disable-spa-mode.sh.backup`)
- ❌ Replacing core templates with SPA variants (✅ NOT PRESENT)
- ❌ Adding Tailwind CDN alongside PaperMod CSS (✅ NOT PRESENT)
- ❌ Complex JavaScript routing systems (✅ NOT PRESENT)

### 🏗️ CSS Architecture

#### ✅ Current CSS Status

- `assets/css/custom.css` - ✅ ~**745 lines** (≤ 1000-line limit)
- ✅ **No `:contains()` selectors** (compliant)
- ✅ **No Tailwind CDN** (compliant)

#### ✅ Approved CSS Pipeline

```hugo
{{- $cssBundle := slice -}}
{{- $cssBundle = $cssBundle | append (resources.Get "css/main.css") -}}
{{- range resources.Match "css/extended/*.css" -}}
  {{- $cssBundle = $cssBundle | append . -}}
{{- end -}}
{{- $cssBundle = $cssBundle | append (resources.Get "css/custom.css") -}}
{{- $style := $cssBundle | resources.Concat "css/bundle.css" | resources.Minify | resources.Fingerprint -}}
```

#### ✅ CSS Customization Guidelines

- **Use PaperMod Variables:** Override CSS custom properties defined in PaperMod
- **Keep it Focused:** Only customize what's necessary for your brand
- **Responsive First:** Use mobile-first responsive design patterns
- **Performance First:** Avoid unnecessary CSS that increases bundle size
- **Modularize When Feasible:** Prefer splitting `custom.css` into layout/components/utilities over time

#### ❌ FORBIDDEN (CSS Level)

- ❌ `<script src="https://cdn.tailwindcss.com"></script>`
- ❌ `assets/css/custom.css` > 1000 lines (current ~745 lines ✅)
- ❌ CSS `:contains()` selectors (unsupported in CSS)
- ❌ Direct PaperMod core CSS modification

### 🧭 Navigation System

#### ✅ Approved Navigation

- Hugo menu system via `config.toml`
- Simple JavaScript enhancement only
- Standard Hugo routing

#### ❌ FORBIDDEN

- ❌ Hard-coded URL mapping in JavaScript
- ❌ AJAX page loading with `innerHTML`
- ❌ Complex SPA routers

### 🔧 SPA Resources Handling Strategy

#### ✅ Current SPA Resources Status

- `layouts/_default/baseof-spa.html` - 🔄 **PRESERVED FOR REFERENCE (Do Not Activate)**
- `layouts/_default/list-spa.html` - 🔄 **PRESERVED FOR REFERENCE (Do Not Activate)**
- `layouts/_default/single-spa.html` - 🔄 **PRESERVED FOR REFERENCE (Do Not Activate)**
- `scripts/disable-spa-mode.sh.backup` - 🔄 **DISABLED VERSION PRESERVED**

#### ✅ SPA Policy

- **KEEP FOR REFERENCE:** SPA templates are preserved but should not be used
- **NO ACTIVATION:** Never enable SPA mode on production
- **LEARNING PURPOSE:** Templates show what was tried and what caused issues
- **CLEANUP READY:** Can be safely removed when confident

> Note: A modern SPA-like experience should be added via progressive enhancement only, without breaking Hugo/PaperMod template inheritance.

#### ❌ FORBIDDEN SPA Actions

- ❌ Running `scripts/toggle-spa-mode.sh` (does not exist)
- ❌ Copying SPA templates over standard templates
- ❌ Any reference to SPA functionality in production code

### 💬 Comments System Requirements

#### ✅ Current Comments Status

- `layouts/partials/comments.html` - ✅ **SAFE PLACEHOLDER IMPLEMENTATION**
- `config.toml` - ✅ **COMMENTS DISABLED** (`[params.comments] enable = false`)
- ✅ **No Internal Template References** (avoids build errors)

#### ✅ Approved Comments Approach

1. **Current State:** Comments disabled, safe placeholder implementation
2. **Future Options:** When enabling comments, use:
   - Hugo's built-in comment partials
   - PaperMod-compatible comment systems
   - No `_internal/*` template references

#### ✅ Comments Implementation Guidelines

- **Safe Default:** Keep comments disabled until explicitly needed
- **Test First:** Always test comment system in development before production
- **PaperMod Compatible:** Use only PaperMod-supported comment integrations

#### ❌ FORBIDDEN Comments Patterns

- ❌ References to `_internal/utterances.html`, `_internal/giscus.html`, etc.
- ❌ Custom comment systems that override Hugo core templates
- ❌ Comment implementations that break Hugo builds

---

## 🔧 Development Rules

### ✅ DO

- ✅ Use Hugo v0.146.0+ (currently v0.149.x) with PaperMod theme
- ✅ Follow standard Hugo template hierarchy
- ✅ Use CSS custom properties for theming
- ✅ Test with `make build` before committing
- ✅ Keep `assets/css/custom.css` under 1000 lines (currently ~745 lines)

### ❌ DO NOT

- ❌ Run `scripts/toggle-spa-mode.sh` (it's disabled for a reason)
- ❌ Modify core PaperMod templates unnecessarily
- ❌ Add external CSS frameworks via CDN
- ❌ Create complex JavaScript routing systems
- ❌ Override Hugo's built-in optimization

## 🔍 Verification & Validation

### ✅ Automated Architecture Validation

```bash
# Run complete architecture check
make validate-architecture

# Check specific issues
make build          # Build validation
make dev             # Local development test
```

### ✅ Validation Script Coverage

The `scripts/validate-architecture.sh` automatically checks:

- ✅ SPA toggle script status (must be disabled)
- ✅ Core template architecture (PaperMod standard)
- ✅ CSS file size limits (≤1000 lines)
- ✅ Problematic CSS selectors (no `:contains()`)
- ✅ External CSS CDN dependencies (none allowed; Tailwind CDN removed)
- ✅ Hugo build success
- ✅ Template syntax validation

### ✅ Pre-commit Protection

- **Git Hooks:** Automatic validation on every commit
- **Build Integration:** Full builds include architecture validation
- **Early Detection:** Problems caught before deployment

### ✅ Common Build Errors & Solutions

| Error Pattern | Cause | Solution |
|--------------|-------|----------|
| `no such template "_internal/*.html"` | Comments template references internal Hugo templates | Use placeholder implementation or disable comments |
| `SPA Router` errors | SPA templates activated accidentally | Run `make validate-architecture` to detect |
| `CSS :contains()` errors | Unsupported CSS selectors | Remove `:contains()` from custom CSS |
| `Tailwind CDN` errors | External CSS conflicts | Remove CDN links, use Hugo CSS pipeline |
| Template syntax errors | Invalid Hugo template syntax | Run `make build` to see detailed errors |

### ✅ CI/CD Integration (Future)

When setting up CI/CD, add architecture validation:

```yaml
# Example GitHub Actions step
- name: Validate Architecture
  run: make validate-architecture

---

## 🚨 Emergency Recovery

If architecture gets broken:
```bash
# Restore core templates
git checkout HEAD~1 -- layouts/_default/baseof.html layouts/_default/list.html layouts/_default/single.html

# Restore clean CSS
cp assets/css/custom.css.backup assets/css/custom.css

# Rebuild
make clean && make build
```

---

## 📚 Documentation

- **Layout Overview:** `docs/layout-overview.md`
- **Full Architecture:** `docs/architecture.md`
- **BMAD Workflow:** `docs/bmm-workflow-status.yaml`
- **Project Guidelines:** `CLAUDE.md`

---

## 🎯 Architecture Philosophy

1. **Stability over Features:** PaperMod standard architecture is proven and stable
2. **Progressive Enhancement:** Add features without breaking core functionality
3. **Hugo-native Solutions:** Use Hugo's built-in features first
4. **Minimal Dependencies:** Avoid external CDN dependencies
5. **Test-driven Changes:** Verify every change works with `make build`

**THIS ARCHITECTURE IS PRODUCTION-READY AND STABLE. DO NOT MAKE CHANGES WITHOUT TESTING.**
