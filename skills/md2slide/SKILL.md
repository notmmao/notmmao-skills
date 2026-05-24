---
name: md2slide
description: Convert delimiter-separated Markdown into a clean, minimal, design-system-powered HTML slide deck. Supports bilingual headings, semantic colored boxes, code blocks, pill badges, multi-column layouts, card grids, timelines, themes, transitions, aspect ratios, custom CSS injection, auto-TOC, and per-slide directives. Trigger when the user wants to turn a Markdown file into HTML slides, create a slideshow from markdown, generate an HTML presentation, convert markdown to a slide deck, or mentions making a PPT/Presentation from markdown. Also triggered by phrases like "md转幻灯片", "markdown生成PPT", "markdown转HTML演示", "幻灯片", "slide deck".
---

# md2slide — Markdown → HTML Slides

## What it does

Turns a Markdown file (split by `---` delimiters) into a self-contained, single-file HTML presentation with a full design system.

## CLI parameters

| Flag | Description | Default |
|------|-------------|---------|
| `input.md` | Source markdown file | **required** |
| `-o, --output` | Output HTML path | `input.html` |
| `-t, --title` | HTML `<title>` tag | filename stem |
| `-T, --theme` | Color preset: `light` `dark` `minimal` `accent` | `light` |
| `--transition` | Animation: `none` `fade` `slide` | `fade` |
| `-a, --aspect` | Ratio lock: `16:9` `4:3` `auto` | `auto` |
| `--toc` | Auto-generate TOC slide as slide 1 | off |
| `--footer` | Show source + timestamp footer | off |
| `--no-auto` | Disable automatic slide-type detection | off |
| `-c, --css` | Path to extra CSS file to inject | none |

**Script path**: `./scripts/md2slide.py`

## Markdown conventions

### Slide separator

Use `---` (three or more dashes on their own line) to separate slides.

### Slide directives (per-slide frontmatter)

Place an HTML comment block **at the very top** of a slide to control it:

```markdown
<!--
type: title
bg: #f8f9fa
class: special
-->

# Slide Title
Content here...
```

| Directive | Values | Effect |
|-----------|--------|--------|
| `type` | `title` `section` `content` `center` | Forces slide layout type |
| `bg` | `#hex` or `css-color` | Sets slide background color |
| `class` | any CSS classes | Adds extra CSS classes to the slide div |

**If `type` is omitted**, the script auto-detects:
- Short single-heading with no body → `section-slide` (chapter divider)
- Single-heading + short body → `title-slide` (centered hero)
- Rich content (h2+, code, table, image) → `content` (normal layout)

### Bilingual headings

Write `# English Title | 中文标题` — the script auto-splits into the dual-size bilingual format:

```html
<h1>English Title<br><span style="font-size:0.55em;color:#888">中文标题</span></h1>
```

Works for `h1`, `h2`, `h3`.

### Semantic boxes (blockquotes)

Start a blockquote with an emoji/keyword to color it:

| Prefix | Color | Use |
|--------|-------|-----|
| `> ℹ️ ...` or `> Info: ...` | 🔵 blue | General info |
| `> ⚠️ ...` or `> Warning: ...` | 🟠 orange | Warning / caution |
| `> ✅ ...` or `> Tip: ...` | 🟢 green | Best practice / tip |
| `> 🔮 ...` or `> Analogy: ...` | 🟣 purple | Analogy / metaphor |
| `> ❌ ...` or `> Danger: ...` | 🔴 red | Critical / danger |
| `> ...` (plain) | ⚪ gray | Neutral box |

### Layout hints (HTML comments)

Insert these **between** elements to wrap them into layouts.

**Important**: blocks are split by **blank lines** (double newline). Keep content
that belongs together as one column/card continuous — don't add blank lines
inside a logical group.

```markdown
## Two-Column

<!-- two-col -->

### Left Side
- item A
- item B

### Right Side
- item C
- item D
```

| Hint | Effect |
|------|--------|
| `<!-- two-col -->` | Wraps the **next 2 non-empty blocks** (separated by blank lines) into a 2-column grid |
| `<!-- three-col -->` | Wraps the **next 3 non-empty blocks** into a 3-column grid |
| `<!-- grid -->` | Wraps **all remaining blocks** into a responsive card grid |

**Note**: Each hint consumes the blocks that follow it. Content before the hint
is unaffected. If you need a heading + list as one column, keep them together
without a blank line between the heading and the list.

### Pill badges

Inline pill syntax for small colored labels:

```markdown
Status: [pill-green]Online[/pill]  [pill-red]Error[/pill]  [pill-blue]Beta[/pill]
```

Available colors: `green` `red` `blue` `amber` `purple` `gray`

### Timeline / steps

Use a numbered step pattern inside a blockquote or plain text. The script does **not** auto-generate timelines — write raw HTML if you need precise control, or use the `<!-- grid -->` hint for a card-based timeline.

### Images & tables

Standard Markdown. Images are auto-centered, rounded, shadowed, max-height 55vh. Tables get clean header styling.

### Code blocks

Fenced code blocks render with a dark background, monospace font, and rounded corners.

## Themes

| Theme | Vibe |
|-------|------|
| `light` | White bg, dark text, black accent — default |
| `dark` | GitHub-dark bg, light text, blue accent |
| `minimal` | Off-white bg, near-black accent, very clean |
| `accent` | White bg, coral-red accent, modern |

## Navigation & output

- **Keyboard**: `←` `→` `Space` to navigate; `Home` / `End` to jump to first/last; **`Esc` to open slide index overlay**
- **Touch**: Swipe left/right on mobile
- **Print**: `Ctrl+P` prints all slides; nav controls auto-hide
- **Single file**: Everything embedded — no external dependencies

### Slide Index Overlay (ESC)

Press `Esc` at any time to open a full-screen overlay listing all slides with their titles and numbers. Click any item to jump directly to that slide. Press `Esc` again or click the × button / backdrop to close the overlay.
- Works independently of the `--toc` option
- Responsive layout: two-column on desktop, single-column on mobile
- Auto-hides when printing

## Live Demos

| Theme | Preview |
|-------|---------|
| **light** | https://list.notmmao.com/demo/md2slide/v2/light.html |
| **dark** | https://list.notmmao.com/demo/md2slide/v2/dark.html |
| **accent** | https://list.notmmao.com/demo/md2slide/v2/accent.html |
| v1 (legacy) | https://list.notmmao.com/demo/md2slide/v1/index.html |
| **Demo Gallery** | https://list.notmmao.com/demo/ |

## Example workflow

```bash
# Basic conversion
python md2slide.py talk.md

# Dark theme, no animation, 16:9 ratio
python md2slide.py talk.md -T dark --transition none -a 16:9

# With TOC and footer
python md2slide.py talk.md --toc --footer -o talk.html

# Custom CSS override
python md2slide.py talk.md -c my-brand.css
```
