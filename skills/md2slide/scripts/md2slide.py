#!/usr/bin/env python3
"""
md2slide v2 — Markdown → HTML Slides with a full design system.
Style: Clean white presentation inspired by Claude Code Best Practice deck.

CLI:
    python md2slide.py input.md [options]

Slide directives (HTML comment at top of each slide):
    <!-- type: title|section|content|center -->
    <!-- bg: #hex | css-color-name -->
    <!-- class: extra-css-classes -->
"""

import sys
import re
import argparse
import json
import markdown
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
#  THEMES
# ---------------------------------------------------------------------------
THEMES = {
    "light": {
        "bg": "#fff",
        "fg": "#1a1a1a",
        "fg2": "#444",
        "fg3": "#666",
        "accent": "#1a1a1a",
        "code_bg": "#1a1a1a",
        "code_fg": "#e5e5e5",
        "border": "#e5e5e5",
        "muted": "#888",
        "progress": "#1a1a1a",
    },
    "dark": {
        "bg": "#0d1117",
        "fg": "#e6edf3",
        "fg2": "#b0b8c4",
        "fg3": "#8b949e",
        "accent": "#58a6ff",
        "code_bg": "#161b22",
        "code_fg": "#c9d1d9",
        "border": "#30363d",
        "muted": "#6e7681",
        "progress": "#58a6ff",
    },
    "minimal": {
        "bg": "#fafafa",
        "fg": "#111",
        "fg2": "#444",
        "fg3": "#666",
        "accent": "#111",
        "code_bg": "#111",
        "code_fg": "#f5f5f5",
        "border": "#ddd",
        "muted": "#999",
        "progress": "#111",
    },
    "accent": {
        "bg": "#fff",
        "fg": "#1a1a2e",
        "fg2": "#4a4a6a",
        "fg3": "#6a6a8a",
        "accent": "#e94560",
        "code_bg": "#1a1a2e",
        "code_fg": "#eee",
        "border": "#e0e0e8",
        "muted": "#999",
        "progress": "#e94560",
    },
}

# ---------------------------------------------------------------------------
#  CSS  (injected into the template)
# ---------------------------------------------------------------------------
CSS_BASE = """
        /* ===== RESET ===== */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        html {{ scroll-behavior: smooth; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                         'Helvetica Neue', Arial, 'Noto Sans SC', 'PingFang SC',
                         'Microsoft YaHei', sans-serif;
            background: {bg};
            color: {fg};
            line-height: 1.6;
            overflow-x: hidden;
        }}

        /* ===== SLIDE SYSTEM ===== */
        .slide {{
            display: none;
            width: 100%;
            min-height: 100vh;
            padding: 60px 80px;
            max-width: 1200px;
            margin: 0 auto;
            position: relative;
        }}
        .slide.active {{ display: block; }}

        .slide.title-slide.active,
        .slide.center-slide.active {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 40px;
        }}
        .title-slide h1 {{
            font-size: 3.2rem;
            font-weight: 700;
            margin-bottom: 20px;
            border-bottom: none;
            padding-bottom: 0;
            letter-spacing: -0.02em;
            line-height: 1.15;
        }}
        .title-slide .subtitle {{
            font-size: 1.4rem;
            color: {muted};
            margin-bottom: 50px;
            font-weight: 400;
        }}

        .slide.section-slide.active {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 40px;
        }}
        .section-slide h1 {{
            font-size: 3rem;
            font-weight: 700;
            border-bottom: none;
            padding-bottom: 0;
            margin-bottom: 16px;
            line-height: 1.15;
        }}
        .section-slide .section-desc {{
            font-size: 1.2rem;
            color: {fg3};
            max-width: 600px;
        }}

        .center-slide h1 {{
            font-size: 2.8rem;
            font-weight: 700;
            border-bottom: none;
            padding-bottom: 0;
            margin-bottom: 16px;
            line-height: 1.15;
        }}
        .center-slide p {{
            font-size: 1.2rem;
            color: {fg2};
            max-width: 700px;
        }}

        /* ===== TYPOGRAPHY ===== */
        h1 {{
            font-size: 2.2rem;
            font-weight: 600;
            margin-bottom: 32px;
            color: {fg};
            border-bottom: 2px solid {border};
            padding-bottom: 16px;
            line-height: 1.3;
        }}
        h2 {{
            font-size: 1.6rem;
            font-weight: 600;
            margin: 28px 0 16px 0;
            color: {fg};
            line-height: 1.35;
        }}
        h3 {{
            font-size: 1.25rem;
            font-weight: 600;
            margin: 20px 0 10px 0;
            color: {fg};
            line-height: 1.4;
        }}
        p {{
            font-size: 1.05rem;
            margin-bottom: 14px;
            color: {fg2};
            line-height: 1.65;
        }}
        code {{
            background: rgba(128,128,128,0.12);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'SF Mono', Monaco, 'Courier New', 'Noto Sans Mono CJK SC', monospace;
            font-size: 0.92rem;
            color: {accent};
            font-weight: 600;
        }}
        a {{ color: {accent}; text-decoration: underline; }}
        a:hover {{ opacity: 0.8; }}
        strong {{ color: {fg}; font-weight: 700; }}
        em {{ font-style: italic; color: {fg3}; }}

        /* ===== CODE BLOCK ===== */
        .slide pre {{
            background: {code_bg};
            color: {code_fg};
            padding: 20px 24px;
            border-radius: 8px;
            font-family: 'SF Mono', Monaco, 'Courier New', 'Noto Sans Mono CJK SC', monospace;
            font-size: 0.88rem;
            overflow-x: auto;
            margin: 16px 0;
            line-height: 1.7;
        }}
        .slide pre code {{
            background: transparent;
            padding: 0;
            color: inherit;
            font-size: inherit;
            font-weight: inherit;
        }}

        /* ===== BLOCKQUOTE / BOXES ===== */
        .slide blockquote {{
            background: rgba(128,128,128,0.06);
            border-left: 4px solid {accent};
            padding: 16px 20px;
            margin: 16px 0;
            border-radius: 0 8px 8px 0;
        }}
        .slide blockquote p {{
            font-size: 1rem;
            color: {fg2};
            margin: 0 0 8px 0;
        }}
        .slide blockquote p:last-child {{ margin-bottom: 0; }}

        .slide blockquote.info-box {{
            background: rgba(33,150,243,0.08);
            border-left-color: #2196f3;
        }}
        .slide blockquote.info-box p {{ color: #0d47a1; }}
        .slide blockquote.warning-box {{
            background: rgba(255,152,0,0.08);
            border-left-color: #ff9800;
        }}
        .slide blockquote.warning-box p {{ color: #bf360c; }}
        .slide blockquote.analogy-box {{
            background: rgba(156,39,176,0.08);
            border-left-color: #9c27b0;
        }}
        .slide blockquote.analogy-box p {{ color: #4a148c; }}
        .slide blockquote.tip-box {{
            background: rgba(76,175,80,0.08);
            border-left-color: #4caf50;
        }}
        .slide blockquote.tip-box p {{ color: #1b5e20; }}
        .slide blockquote.danger-box {{
            background: rgba(244,67,54,0.08);
            border-left-color: #f44336;
        }}
        .slide blockquote.danger-box p {{ color: #c62828; }}
        .slide blockquote.neutral-box {{
            background: rgba(128,128,128,0.06);
            border-left-color: {muted};
        }}
        .slide blockquote.neutral-box p {{ color: {fg2}; }}

        /* ===== LISTS ===== */
        .slide ul, .slide ol {{
            margin: 16px 0;
            padding-left: 28px;
        }}
        .slide ul {{
            list-style: none;
            padding-left: 0;
        }}
        .slide ul li {{
            padding: 10px 0 10px 28px;
            border-bottom: 1px solid {border};
            font-size: 1.02rem;
            position: relative;
            color: {fg2};
            line-height: 1.55;
        }}
        .slide ul li:last-child {{ border-bottom: none; }}
        .slide ul li::before {{
            content: "•";
            position: absolute;
            left: 8px;
            color: {accent};
            font-weight: 700;
        }}
        .slide ol li {{
            padding: 8px 0;
            font-size: 1.02rem;
            color: {fg2};
            line-height: 1.6;
            margin-left: 4px;
        }}

        /* ===== TABLE ===== */
        .slide table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.95rem;
        }}
        .slide thead th {{
            background: rgba(128,128,128,0.06);
            padding: 12px 16px;
            text-align: left;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: {fg3};
            border-bottom: 2px solid {border};
            font-weight: 600;
        }}
        .slide td {{
            padding: 12px 16px;
            border-bottom: 1px solid {border};
            color: {fg2};
        }}
        .slide tr:last-child td {{ border-bottom: none; }}

        /* ===== IMAGE ===== */
        .slide img {{
            max-width: 100%;
            max-height: 55vh;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.12);
            display: block;
            margin: 16px auto;
        }}

        /* ===== HR ===== */
        .slide hr {{
            border: none;
            border-top: 2px solid {border};
            margin: 24px 0;
        }}

        /* ===== LAYOUT HELPERS ===== */
        .slide .two-col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin: 20px 0;
            align-items: start;
        }}
        .slide .three-col {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin: 20px 0;
            align-items: start;
        }}
        .slide .col-card {{
            background: rgba(128,128,128,0.04);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid {border};
        }}
        .slide .col-card h3,
        .slide .col-card h4 {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: {fg3};
            margin-bottom: 10px;
            font-weight: 600;
        }}
        .slide .col-card.good {{ border-left-color: #4caf50; }}
        .slide .col-card.bad {{ border-left-color: #f44336; }}
        .slide .col-card.info {{ border-left-color: #2196f3; }}
        .slide .col-card.warn {{ border-left-color: #ff9800; }}

        /* Pill badges */
        .slide .pill {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.3px;
            margin: 2px 4px 2px 0;
            white-space: nowrap;
        }}
        .slide .pill-green {{ background: rgba(76,175,80,0.12); color: #2e7d32; }}
        .slide .pill-red {{ background: rgba(244,67,54,0.12); color: #c62828; }}
        .slide .pill-blue {{ background: rgba(33,150,243,0.12); color: #1565c0; }}
        .slide .pill-amber {{ background: rgba(255,152,0,0.12); color: #e65100; }}
        .slide .pill-purple {{ background: rgba(156,39,176,0.12); color: #7b1fa2; }}
        .slide .pill-gray {{ background: rgba(128,128,128,0.12); color: #555; }}

        /* Timeline / steps */
        .slide .timeline {{
            display: flex;
            flex-direction: column;
            gap: 0;
            margin: 24px 0;
            padding-left: 0;
        }}
        .slide .timeline .step {{
            display: flex;
            align-items: flex-start;
            padding: 16px 20px;
            background: rgba(128,128,128,0.03);
            border-left: 4px solid {border};
            margin-bottom: 12px;
            border-radius: 0 8px 8px 0;
        }}
        .slide .timeline .step-num {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-right: 16px;
            min-width: 32px;
            color: {accent};
            line-height: 1;
        }}
        .slide .timeline .step-body {{
            flex: 1;
        }}
        .slide .timeline .step-body strong {{
            display: block;
            font-size: 1.05rem;
            margin-bottom: 4px;
        }}
        .slide .timeline .step-body span {{
            font-size: 0.95rem;
            color: {fg3};
        }}
        .slide .timeline .step.step-1 {{ border-left-color: #2196f3; }}
        .slide .timeline .step.step-2 {{ border-left-color: #ff9800; }}
        .slide .timeline .step.step-3 {{ border-left-color: #4caf50; }}

        /* Card grid */
        .slide .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }}
        .slide .card-grid .card {{
            background: rgba(128,128,128,0.04);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid {border};
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .slide .card-grid .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        }}
        .slide .card-grid .card-emoji {{
            font-size: 2rem;
            margin-bottom: 8px;
        }}
        .slide .card-grid .card-title {{
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 6px;
            color: {fg};
        }}
        .slide .card-grid .card-desc {{
            font-size: 0.9rem;
            color: {fg3};
            line-height: 1.5;
        }}

        /* Footer */
        .slide-footer {{
            position: absolute;
            bottom: 84px;
            left: 80px;
            right: 80px;
            font-size: 0.75rem;
            color: {muted};
            border-top: 1px solid {border};
            padding-top: 8px;
            display: flex;
            justify-content: space-between;
        }}
        .title-slide .slide-footer,
        .section-slide .slide-footer,
        .center-slide .slide-footer {{
            left: 40px;
            right: 40px;
        }}

        /* Custom bg per slide */
        .slide[style*="background"] {{ background-size: cover; }}
"""

CSS_TRANSITIONS = {
    "none": "",
    "fade": """
        .slide {{ opacity: 0; transition: opacity 0.4s ease; }}
        .slide.active {{ opacity: 1; }}
    """,
    "slide": """
        .slide {{ transform: translateX(30px); opacity: 0; transition: all 0.35s ease; }}
        .slide.active {{ transform: translateX(0); opacity: 1; }}
    """,
}

CSS_ASPECT = {
    "16:9": """.slide {{ min-height: auto; aspect-ratio: 16/9; padding: 48px 72px; }}""",
    "4:3": """.slide {{ min-height: auto; aspect-ratio: 4/3; padding: 48px 72px; }}""",
    "auto": "",
}

CSS_EXTRA = """
        /* ===== NAVIGATION ===== */
        .progress {{
            position: fixed;
            top: 0;
            left: 0;
            height: 4px;
            background: {progress};
            transition: width 0.3s;
            z-index: 100;
        }}
        .navigation {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            display: flex;
            gap: 12px;
            z-index: 100;
        }}
        .nav-btn {{
            width: 48px;
            height: 48px;
            border: 2px solid {accent};
            background: {bg};
            color: {accent};
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            user-select: none;
        }}
        .nav-btn:hover {{
            background: {accent};
            color: {bg};
        }}
        .nav-btn:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
        }}
        .slide-counter {{
            position: fixed;
            bottom: 40px;
            left: 40px;
            font-size: 0.9rem;
            color: {muted};
            z-index: 100;
        }}
        .keyboard-hint {{
            position: fixed;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.85rem;
            color: {muted};
            z-index: 100;
        }}
        .keyboard-hint kbd {{
            background: rgba(128,128,128,0.12);
            padding: 3px 7px;
            border-radius: 4px;
            border: 1px solid {border};
            font-family: inherit;
            font-size: 0.85em;
        }}

        /* ===== PRINT ===== */
        @media print {{
            .slide {{
                display: block !important;
                page-break-after: always;
                min-height: auto;
            }}
            .navigation, .progress, .slide-counter, .keyboard-hint {{
                display: none !important;
            }}
        }}

        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {{
            .slide {{ padding: 30px 24px; }}
            h1 {{ font-size: 1.6rem; }}
            h2 {{ font-size: 1.3rem; }}
            .title-slide h1, .section-slide h1, .center-slide h1 {{ font-size: 2rem; }}
            .slide .two-col, .slide .three-col {{ grid-template-columns: 1fr; }}
            .slide .card-grid {{ grid-template-columns: 1fr; }}
            .navigation {{ bottom: 16px; right: 16px; }}
            .slide-counter {{ bottom: 22px; left: 20px; }}
            .slide-footer {{ left: 24px; right: 24px; }}
        }}
"""

# ---------------------------------------------------------------------------
#  HTML TEMPLATE
# ---------------------------------------------------------------------------
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css}
{custom_css}
    </style>
</head>
<body>
    <div class="progress" id="progress"></div>

{slides_html}

    <div class="slide-counter" id="slide-counter">1 / {total}</div>
    <div class="keyboard-hint"><kbd>←</kbd> <kbd>→</kbd> 翻页 · <kbd>Space</kbd></div>
    <div class="navigation">
        <button class="nav-btn" id="prev-btn" onclick="changeSlide(-1)">◀</button>
        <button class="nav-btn" id="next-btn" onclick="changeSlide(1)">▶</button>
    </div>

    <script>
        let currentSlide = 1;
        const totalSlides = {total};

        function updateSlide() {{
            document.querySelectorAll('.slide').forEach((slide, idx) => {{
                slide.classList.toggle('active', idx + 1 === currentSlide);
            }});
            document.getElementById('progress').style.width =
                (currentSlide / totalSlides * 100) + '%';
            document.getElementById('slide-counter').textContent =
                currentSlide + ' / ' + totalSlides;
            document.getElementById('prev-btn').disabled = currentSlide === 1;
            document.getElementById('next-btn').disabled = currentSlide === totalSlides;
            window.scrollTo(0, 0);
        }}

        function changeSlide(delta) {{
            const ns = currentSlide + delta;
            if (ns >= 1 && ns <= totalSlides) {{
                currentSlide = ns;
                updateSlide();
            }}
        }}

        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowLeft') changeSlide(-1);
            if (e.key === 'ArrowRight' || e.key === ' ') changeSlide(1);
            if (e.key === 'Home') {{ currentSlide = 1; updateSlide(); }}
            if (e.key === 'End') {{ currentSlide = totalSlides; updateSlide(); }}
        }});

        let touchStartX = 0;
        document.addEventListener('touchstart', e => {{
            touchStartX = e.changedTouches[0].screenX;
        }});
        document.addEventListener('touchend', e => {{
            const d = touchStartX - e.changedTouches[0].screenX;
            if (Math.abs(d) > 50) changeSlide(d > 0 ? 1 : -1);
        }});

        updateSlide();
    </script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
#  FLAVOR PATTERNS (blockquote detection)
# ---------------------------------------------------------------------------
FLAVOR_PATTERNS = [
    (re.compile(r'^(ℹ️|💡|Info:|INFO:|info:).*'), 'info-box'),
    (re.compile(r'^(⚠️|🚨|Warning:|WARNING:|warning:).*'), 'warning-box'),
    (re.compile(r'^(🔮|🧠|Analogy:|ANALOGY:|analogy:).*'), 'analogy-box'),
    (re.compile(r'^(✅|💚|🎉|Tip:|TIP:|tip:).*'), 'tip-box'),
    (re.compile(r'^(❌|🚫|Danger:|DANGER:|danger:).*'), 'danger-box'),
]

# ---------------------------------------------------------------------------
#  PARSING HELPERS
# ---------------------------------------------------------------------------

SLIDE_DIRECTIVE_RE = re.compile(
    r'^<!--\s*\n?(.*?)\n?-->',
    re.DOTALL
)


def parse_slide_directives(text: str) -> tuple[dict, str]:
    """
    Extract HTML-comment frontmatter directives from top of a slide.
    Returns (directives_dict, remaining_markdown).
    """
    directives: dict = {}
    body = text
    m = SLIDE_DIRECTIVE_RE.match(text.strip())
    if m:
        raw = m.group(1)
        # simple key: value per line
        for line in raw.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                directives[k.strip().lower()] = v.strip()
        body = text.strip()[m.end():].strip()
    return directives, body


def split_slides(md_text: str) -> list[tuple[dict, str]]:
    """
    Split markdown by 3+ dashes. Return list of (directives, body).
    """
    pattern = r'(?:\r?\n|^)\s*-{3,}\s*(?:\r?\n|$)'
    parts = re.split(pattern, md_text)
    result = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        directives, body = parse_slide_directives(p)
        result.append((directives, body))
    return result


def _detect_bilingual(text: str) -> str:
    if '|' not in text or '<' in text:
        return text
    parts = text.split('|', 1)
    en = parts[0].strip()
    zh = parts[1].strip()
    return (
        f'{en}<br>'
        f'<span style="font-size: 0.55em; color: #888; font-weight: 400;">{zh}</span>'
    )


def _flavor_blockquote(html: str) -> str:
    """
    Detect flavor emoji/keyword inside <blockquote>.
    If a single blockquote contains multiple <p> tags with *different*
    flavors, split them into individual blockquotes.
    """
    def repl(m):
        inner = m.group(1)
        # Find all <p> tags inside this blockquote
        para_matches = list(re.finditer(r'<p>(.*?)</p>', inner, flags=re.DOTALL))

        # If only one paragraph or contains non-<p> block elements, handle as single
        has_non_p = bool(re.search(r'<(?:ul|ol|pre|table|h[1-6]|div|blockquote)[^>]*>', inner))
        if len(para_matches) <= 1 or has_non_p:
            plain = re.sub(r'<[^>]+>', '', inner).strip()
            flavor = ''
            for pat, cls in FLAVOR_PATTERNS:
                if pat.match(plain):
                    flavor = cls
                    break
            if flavor:
                return f'<blockquote class="{flavor}">{inner}</blockquote>'
            return f'<blockquote class="neutral-box">{inner}</blockquote>'

        # Multiple paragraphs: detect flavor for each
        flavors = []
        for pm in para_matches:
            para_text = re.sub(r'<[^>]+>', '', pm.group(1)).strip()
            flavor = ''
            for pat, cls in FLAVOR_PATTERNS:
                if pat.match(para_text):
                    flavor = cls
                    break
            flavors.append(flavor or 'neutral-box')

        # All same flavor -> keep as one blockquote
        if len(set(flavors)) == 1:
            return f'<blockquote class="{flavors[0]}">{inner}</blockquote>'

        # Mixed flavors -> split into individual blockquotes
        return '\n'.join(
            f'<blockquote class="{f}">{pm.group(0)}</blockquote>'
            for pm, f in zip(para_matches, flavors)
        )

    return re.sub(r'<blockquote>(.*?)</blockquote>', repl, html, flags=re.DOTALL)


def _postprocess_slide(html: str, slide_type: str) -> str:
    # Bilingual headings
    for tag in ('h1', 'h2', 'h3'):
        def repl(m, t=tag):
            inner = m.group(1)
            if '<' not in inner:
                inner = _detect_bilingual(inner)
            return f'<{t}>{inner}</{t}>'
        html = re.sub(rf'<{tag}>(.*?)</{tag}>', repl, html, flags=re.DOTALL)

    # Flavor blockquotes
    html = _flavor_blockquote(html)

    # Process inline pill syntax: [pill-green]text[/pill]  or  ✅ text
    html = _process_pills(html)

    # Layout hints are processed at markdown level (see _process_layout_hints)

    return html


def _process_pills(html: str) -> str:
    """
    Convert inline pill syntax into styled spans.
    Supports:
        [pill-green]text[/pill]   → green pill
        [pill-red]text[/pill]     → red pill
        [pill-blue]text[/pill]    → blue pill
        [pill-amber]text[/pill]   → amber pill
        [pill-purple]text[/pill]  → purple pill
        [pill-gray]text[/pill]    → gray pill
    """
    def repl(m):
        color = m.group(1)
        text = m.group(2)
        valid = ('green', 'red', 'blue', 'amber', 'purple', 'gray')
        if color not in valid:
            return m.group(0)
        return f'<span class="pill pill-{color}">{text}</span>'
    return re.sub(
        r'\[pill-(green|red|blue|amber|purple|gray)\](.*?)\[/pill\]',
        repl, html
    )


def _split_markdown_blocks(text: str) -> list[str]:
    """Split markdown text into content blocks separated by blank lines.
    Skips leading/trailing blank lines and filters empty blocks."""
    lines = text.splitlines()
    blocks = []
    current = []
    for line in lines:
        stripped = line.strip()
        if stripped == '':
            if current:
                blocks.append('\n'.join(current))
                current = []
            # skip consecutive/leading blank lines
        else:
            current.append(line)
    if current:
        blocks.append('\n'.join(current))
    return [b for b in blocks if b.strip()]


def _process_layout_hints(md_body: str) -> str:
    """
    Process layout hints at markdown level before HTML conversion.
    Uses independent markdown converter to avoid state pollution.
    """
    import markdown as _md_mod
    _tmp_md = _md_mod.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])

    def _convert_block(block: str) -> str:
        _tmp_md.reset()
        return _tmp_md.convert(block.strip())

    # two-col
    pattern = r'<!--\s*two-col\s*-->'
    if re.search(pattern, md_body):
        parts = re.split(pattern, md_body, maxsplit=1)
        before = parts[0]
        after = parts[1] if len(parts) > 1 else ''
        blocks = _split_markdown_blocks(after)
        if len(blocks) >= 2:
            cols = [_convert_block(b) for b in blocks[:2]]
            grid = '<div class="two-col">\n' + '\n'.join(
                f'<div class="col-card">{c}</div>' for c in cols
            ) + '\n</div>'
            rest = '\n\n'.join(blocks[2:])
            md_body = before + grid + rest

    # three-col
    pattern = r'<!--\s*three-col\s*-->'
    if re.search(pattern, md_body):
        parts = re.split(pattern, md_body, maxsplit=1)
        before = parts[0]
        after = parts[1] if len(parts) > 1 else ''
        blocks = _split_markdown_blocks(after)
        if len(blocks) >= 3:
            cols = [_convert_block(b) for b in blocks[:3]]
            grid = '<div class="three-col">\n' + '\n'.join(
                f'<div class="col-card">{c}</div>' for c in cols
            ) + '\n</div>'
            rest = '\n\n'.join(blocks[3:])
            md_body = before + grid + rest

    # grid
    pattern = r'<!--\s*grid\s*-->'
    if re.search(pattern, md_body):
        parts = re.split(pattern, md_body, maxsplit=1)
        before = parts[0]
        after = parts[1] if len(parts) > 1 else ''
        blocks = _split_markdown_blocks(after)
        if blocks:
            cards = [_convert_block(b) for b in blocks]
            grid = '<div class="card-grid">\n' + '\n'.join(
                f'<div class="card">{c}</div>' for c in cards if c.strip()
            ) + '\n</div>'
            md_body = before + grid

    return md_body


def _process_layouts(html: str) -> str:
    """Deprecated: layout hints are now processed at markdown level."""
    return html


def _auto_detect_type(html: str) -> str:
    h1_count = html.count('<h1>')
    plain = re.sub(r'<[^>]+>', ' ', html).strip()
    text_len = len(plain)

    rich_tags = re.findall(r'<(h2|h3|pre|table|img)[ >]', html)
    if rich_tags or h1_count > 1 or text_len > 400:
        return 'content'

    body_tags = re.findall(r'<(p|ul|ol|blockquote)[ >]', html)
    if h1_count == 1 and text_len < 150 and not body_tags:
        return 'section-slide'

    if h1_count == 1 and text_len < 350:
        return 'title-slide'

    return 'content'


def _make_toc(slides: list[tuple[dict, str, str, str]], title: str, theme: dict) -> tuple[str, str]:
    """
    Generate a TOC slide from slide titles.
    """
    items = []
    for idx, (directives, body, _, _) in enumerate(slides, 1):
        # Extract first h1 or plain first line
        h1_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
        if h1_match:
            t = h1_match.group(1).strip()
        else:
            t = body.strip().split('\n')[0][:60]
        items.append(f'<div class="toc-item" onclick="jumpTo({idx})">\n'
                     f'  <span class="toc-number">{idx}</span>\n'
                     f'  <span class="toc-name">{t}</span>\n'
                     f'</div>')

    toc_css = """
        .toc-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-top: 32px; }
        .toc-item { display: flex; align-items: center; padding: 14px 18px; background: rgba(128,128,128,0.04); border-radius: 8px; cursor: pointer; transition: background 0.2s; border: 1px solid {border}; }
        .toc-item:hover { background: rgba(128,128,128,0.1); }
        .toc-number { width: 28px; height: 28px; background: {accent}; color: {bg}; border-radius: 50%; text-align: center; line-height: 28px; font-size: 0.8rem; margin-right: 12px; font-weight: 600; flex-shrink: 0; }
        .toc-name { font-size: 1rem; color: {fg}; }
    """
    toc_html = (
        f'    <div class="slide title-slide active" data-slide="0" id="toc-slide">\n'
        f'      <h1>{title}</h1>\n'
        f'      <p class="subtitle">目录 · Table of Contents</p>\n'
        f'      <div class="toc-grid">\n        ' +
        '\n        '.join(items) +
        f'\n      </div>\n'
        f'    </div>'
    )
    # Replace theme tokens manually to avoid CSS brace conflicts
    for k, v in theme.items():
        toc_css = toc_css.replace('{' + k + '}', str(v))
    return toc_css, toc_html


# ---------------------------------------------------------------------------
#  MAIN
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description='md2slide v2 — Markdown → HTML Slides with design system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Slide directives (HTML comment at top of each slide):
  <!-- type: title | section | content | center -->
  <!-- bg: #f5f5f5 -->
  <!-- class: dark-theme -->

Layout hints (inline HTML comments):
  <!-- two-col -->   → wrap next two blocks in 2-column grid
  <!-- three-col --> → wrap next three blocks in 3-column grid
  <!-- grid -->      → wrap remaining blocks in card grid

Pill badges (inline):
  [pill-green]文本[/pill]  [pill-red]...[/pill]  [pill-blue]...
  [pill-amber]...[/pill]   [pill-purple]...[/pill] [pill-gray]...
        """
    )
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('-o', '--output', help='Output HTML file (default: input.html)')
    parser.add_argument('-t', '--title', help='HTML <title> (default: filename stem)')
    parser.add_argument('-T', '--theme', choices=list(THEMES.keys()), default='light',
                        help='Color theme preset (default: light)')
    parser.add_argument('--transition', choices=list(CSS_TRANSITIONS.keys()), default='fade',
                        help='Slide transition animation (default: fade)')
    parser.add_argument('-a', '--aspect', choices=list(CSS_ASPECT.keys()), default='auto',
                        help='Slide aspect ratio (default: auto)')
    parser.add_argument('--footer', action='store_true',
                        help='Show source + timestamp footer on each slide')
    parser.add_argument('--toc', action='store_true',
                        help='Auto-generate a TOC slide as slide 1')
    parser.add_argument('--no-auto', action='store_true',
                        help='Disable automatic slide-type detection')
    parser.add_argument('-c', '--css', help='Path to extra CSS file to inject')
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f'Error: file not found: {in_path}', file=sys.stderr)
        return 1

    md_text = in_path.read_text(encoding='utf-8')
    slides_raw = split_slides(md_text)
    if not slides_raw:
        print('Error: no slides found. Use --- (3+ dashes) to separate slides.',
              file=sys.stderr)
        return 1

    # Theme
    theme = THEMES[args.theme]

    # Custom CSS file
    custom_css = ''
    if args.css:
        css_path = Path(args.css)
        if css_path.exists():
            custom_css = css_path.read_text(encoding='utf-8')
        else:
            print(f'Warning: CSS file not found: {css_path}', file=sys.stderr)

    # Build CSS
    css_parts = [CSS_BASE.format(**theme)]
    css_parts.append(CSS_TRANSITIONS[args.transition])
    css_parts.append(CSS_ASPECT[args.aspect])
    css_parts.append(CSS_EXTRA.format(**theme))
    css = '\n'.join(css_parts)

    md_converter = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])

    processed_slides: list[tuple[dict, str, str]] = []
    for directives, body in slides_raw:
        # Process layout hints at markdown level FIRST
        body = _process_layout_hints(body)

        md_converter.reset()
        raw_html = md_converter.convert(body)

        # Determine slide type
        if args.no_auto:
            stype = directives.get('type', 'content')
        else:
            stype = directives.get('type')
            if not stype:
                stype = _auto_detect_type(raw_html)

        # Normalize type to CSS class name
        TYPE_MAP = {
            'section': 'section-slide',
            'title': 'title-slide',
            'center': 'center-slide',
            'content': 'content',
        }
        stype = TYPE_MAP.get(stype, stype)

        # Post-process HTML
        proc = _postprocess_slide(raw_html, stype)

        processed_slides.append((directives, body, proc, stype))

    # Build slide divs
    slide_divs = []
    offset = 0

    # TOC slide
    if args.toc:
        toc_css_extra, toc_html = _make_toc(processed_slides, args.title or in_path.stem, theme)
        # Inject TOC CSS
        css += '\n' + toc_css_extra
        slide_divs.append(toc_html)
        offset = 1

    for idx, (directives, _, proc, stype) in enumerate(processed_slides):
        real_idx = idx + 1 + offset
        extra_classes = directives.get('class', '')
        bg = directives.get('bg', '')
        style_attr = f' style="background: {bg};"' if bg else ''

        css_cls = f'slide {stype}'
        if extra_classes:
            css_cls += ' ' + extra_classes

        # Footer
        footer_html = ''
        if args.footer:
            ts = datetime.now().strftime('%Y-%m-%d %H:%M')
            footer_html = (
                f'\n      <div class="slide-footer">'
                f'<span>{in_path.name}</span>'
                f'<span>{ts}</span>'
                f'</div>'
            )

        div = (
            f'    <div class="{css_cls}" data-slide="{real_idx}"{style_attr}>\n'
            f'{proc}'
            f'{footer_html}\n'
            f'    </div>'
        )
        slide_divs.append(div)

    title = args.title or in_path.stem
    out_path = Path(args.output) if args.output else in_path.with_suffix('.html')
    total_slides = len(slide_divs)

    # Final template interpolation
    final_html = HTML_TEMPLATE.format(
        title=title,
        css=css,
        custom_css=custom_css,
        slides_html='\n\n'.join(slide_divs),
        total=total_slides,
    )

    # Inject TOC jump function if TOC enabled
    if args.toc:
        toc_js = '\n        function jumpTo(n) { currentSlide = n + 1; updateSlide(); }'
        final_html = final_html.replace(
            '</script>',
            f'        {toc_js}\n    </script>'
        )

    out_path.write_text(final_html, encoding='utf-8')
    print(f'✅  {total_slides} slides → {out_path.resolve()}')
    print(f'   theme={args.theme}  transition={args.transition}  aspect={args.aspect}')
    if args.toc:
        print('   +TOC slide')
    if args.footer:
        print('   +footer')
    return 0


if __name__ == '__main__':
    sys.exit(main())
