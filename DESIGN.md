# DESIGN.md — Peng Tan's AI Blog Design System

> **Theme Identity**: **E1 · Apple System Blue & Titanium Spatial Glass**
> **Architecture**: Hugo v0.152.2 (Extended) · PaperMod Standard + `220px` Frosted-Glass Left Sidebar

---

## 1. Visual Philosophy

This blog pairs **Apple Human Interface Guidelines (macOS Sequoia / iCloud / Apple Newsroom)** spatial glass craftsmanship with long-form architectural and AI technical writing.

- **Frosted Materiality**: Elevated navigation and content cards sit on translucent frosted glass (`backdrop-filter: blur(18px) saturate(160%)`) over a soft ambient radial titanium wash.
- **Specular Depth, Never Heavy Mud**: Depth comes from `1px` specular inner highlights (`inset 0 1px 0 rgba(255,255,255,0.92)` in light mode, `rgba(255,255,255,0.12)` in dark mode) and soft layered elevation shadows, not harsh drop shadows or thick borders.
- **Restraint Over Flash**: Color exists solely to signal interaction, hierarchy, and focus—never as decorative rainbow noise.

---

## 2. Anti-Slop Guardrails (Strict Rules)

1. **No AI Cliché Purple / Indigo**: Never use `#4F46E5`, `#6366F1`, `#8B5CF6`, `#A855F7`, or purple/violet gradients as primary UI, brand, or accent tokens.
2. **No Neon Gradients or Diagonal Stripes**: Never reintroduce saturated multi-stop gradients (`#f093fb -> #f5576c`, `#4facfe -> #00f2fe`) or animated diagonal stripe overlays on `.ai-generated-cover` or panels.
3. **No Emoji Clutter in Metadata**: Card dates, reading times, and word counts MUST use tabular monospace typography (`2026.11.14` · `12 MIN · 4,820 字`), never native color emojis (`📅`, `⏱️`, `📝`, `🤖`).
4. **No External CSS Frameworks via CDN**: Use Hugo's CSS pipeline (`assets/css/custom.css`, `assets/css/editorial-intelligence.css`, `layouts/partials/inline-css.html`). Keep `assets/css/custom.css` under **1,000 lines**.

---

## 3. Color Tokens

### Light Mode (`:root` / `html[data-theme="light"]`)
| Token | Value | Usage |
|---|---|---|
| `--color-bg` | `#f5f5f7` | Titanium Mist primary page canvas |
| `--color-bg-secondary` | `#ebebf0` | Secondary muted surface |
| `--glass-surface` | `rgba(255, 255, 255, 0.84)` | Card & frosted sidebar translucent fill |
| `--glass-border` | `rgba(0, 0, 0, 0.08)` | Hairline structural border |
| `--color-primary` | `#0071e3` | Apple System Blue (links, active nav, CTAs) |
| `--color-primary-light` | `#2997ff` | Hover highlight & secondary focus ring |
| `--color-primary-dark` | `#005bb5` | High-contrast pressed/hover text link |
| `--color-primary-50` | `rgba(0, 113, 227, 0.10)` | Pill & active menu soft tint |
| `--color-primary-100` | `rgba(0, 113, 227, 0.22)` | Subtle active outline & hairline |
| `--color-accent` | `#0284c7` | Glacier Ocean Blue secondary badge accent |
| `--color-heading-strong` | `#1d1d1f` | Primary display ink |
| `--color-text` | `#333336` | Body copy ink |
| `--color-secondary` | `#6e6e73` | Metadata, captions, secondary chrome |

### Dark Mode (`html[data-theme="dark"]`)
| Token | Value | Usage |
|---|---|---|
| `--color-bg` | `#121214` | Pro Space-Black Titanium canvas |
| `--color-bg-secondary` | `#1d1d1f` | Elevated secondary dark surface |
| `--glass-surface` | `rgba(29, 29, 31, 0.80)` | Translucent dark frosted glass fill |
| `--glass-border` | `rgba(255, 255, 255, 0.12)` | Specular dark hairline border |
| `--color-primary` | `#2997ff` | Luminous Apple Blue for dark backgrounds |
| `--color-primary-light` | `#64b5f6` | High-contrast text links & accents |
| `--color-primary-dark` | `#0071e3` | Hover state anchor |
| `--color-primary-50` | `rgba(41, 151, 255, 0.16)` | Pill & active nav translucent wash |
| `--color-primary-100` | `rgba(41, 151, 255, 0.30)` | Border glow accent |
| `--color-accent` | `#38bdf8` | Glacier Sky secondary status highlight |
| `--color-heading-strong` | `#f5f5f7` | Crisp alabaster display ink |
| `--color-text` | `#d1d1d6` | Balanced low-glare reading ink |
| `--color-secondary` | `#a1a1a6` | Titanium Silver muted metadata ink |

---

## 4. Typography & Hierarchy

- **Sans Stack (`--font-sans`)**: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", Inter, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif`
- **Monospace Stack (`--font-mono`)**: `"SF Mono", "JetBrains Mono", Menlo, Monaco, Consolas, monospace` with `font-variant-numeric: tabular-nums`
- **Headings**: Tight tracking (`letter-spacing: -0.02em` to `-0.04em`), crisp semibold/bold weights (`650–760`).
- **Metadata & Indices**: Uppercase kickers (`0.72rem–0.75rem`, `letter-spacing: 0.06em`) and dot-separated dates (`YYYY.MM.DD`).

---

## 5. Layout, Elevation & Components

- **Left Sidebar Layout (`220px`)**:
  - Fixed `220px` frosted-glass rail on desktop (`>= 769px`), sliding off-canvas on mobile (`<= 768px`).
  - Content offset: `.main-content-with-sidebar { padding-left: 220px; }` and aligned footer offset.
  - Navigation items use `10px` pill radius; active state uses soft blue tint (`--color-primary-50`) + `--color-primary` text rather than harsh solid blocks.
- **Article Cards (`.article-card`)**:
  - Radius: `16px` (`--radius-card: 16px`).
  - Glass border (`1px solid var(--glass-border)`) and ambient layered shadow (`0 10px 28px -10px rgba(0, 0, 0, 0.08)` light / `0 12px 32px -10px rgba(0, 0, 0, 0.6)` dark).
  - Hover: `translateY(-3px)` with soft Apple Blue hairline focus (`rgba(0, 113, 227, 0.32)` light / `rgba(41, 151, 255, 0.38)` dark).
- **Fallback Generated Covers (`.ai-generated-cover`)**:
  - Soft Apple Frosted Titanium-Blue surface (`#eef3f9 -> #e5ecf4 -> #eaecef` light; `#151820 -> #19202b -> #151619` dark) with subtle concentric SVG geometric rings (`.cover-apple-geometry`), frosted category pill (`.cover-category`), and crisp two-line clamp title.
- **Long-Form Reading Pages (`.editorial-article`)**:
  - Single-article pages (`assets/css/editorial-intelligence.css`) inherit matching `--ei-paper` (`#f5f5f7` / `#121214`) and `--ei-cobalt` (`#0071e3` / `#2997ff`) tokens for seamless list-to-article visual continuity.
