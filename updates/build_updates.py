#!/usr/bin/env python3
"""
Build /updates: the weekly WIEMIP update emails as one page, newest first.

    uv run --with markdown python updates/build_updates.py

Same shape as the docs (docs/build_docs.py): markdown in, static HTML out, both
committed. Edit `updates/updates.md`, re-run this, commit both. Every `## ` heading
is one email and gets a link in the sidebar, so a new week is a new `## <date>` block
pasted at the top of the file.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import markdown
except ModuleNotFoundError:
    sys.exit(
        "This script needs python-markdown. Run it as:\n"
        "    uv run --with markdown python updates/build_updates.py"
    )

# --- edit me ---------------------------------------------------------------
UPDATES_DIR = Path(__file__).resolve().parent
SOURCE = UPDATES_DIR / "updates.md"
OUT = UPDATES_DIR / "index.html"

# Links pinned to the bottom of the sidebar.
SIDEBAR_LINKS = [
    ("Simulation progress", "/progress-tracker/"),
    ("WIEMIP validation site", "https://d31938ghkxwp9r.cloudfront.net/"),
    ("Discussions/FAQ", "https://github.com/orgs/WIEMIP/discussions"),
]
# h2 only: the sidebar is one link per email, not per section of each email.
EXTENSIONS = ["extra", "toc", "sane_lists", "meta"]
EXTENSION_CONFIGS = {"toc": {"permalink": "#", "toc_depth": "2-2"}}
# ---------------------------------------------------------------------------

# The docs shell (assets/styles.css, .docs-* / .doc), minus search.
TEMPLATE = """<!doctype html>
<!-- GENERATED from updates/updates.md by updates/build_updates.py — edit the markdown, not this file. -->
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
  <link rel="stylesheet" href="/assets/styles.css">
</head>
<body class="docs-body">
  <input type="checkbox" id="docs-nav-toggle" class="docs-nav-toggle" hidden>
  <div class="docs-shell">
    <aside class="docs-sidebar">
      <a class="docs-brand" href="/">
        <span class="docs-brand-mark">W</span>
        <span>
          <strong>WIEMIP updates</strong>
          <small>Weekly emails, newest first</small>
        </span>
      </a>
      <label class="docs-nav-close" for="docs-nav-toggle" aria-label="Close navigation">✕</label>
      <nav class="docs-nav" aria-label="Updates">
        <ul class="docs-nav-pages">
{nav}
        </ul>
      </nav>
      <div class="docs-sidebar-links">
{sidebar_links}
      </div>
    </aside>

    <div class="docs-main">
      <div class="docs-topbar">
        <label class="docs-burger" for="docs-nav-toggle" aria-label="Open navigation">☰</label>
        <nav class="docs-crumbs" aria-label="Breadcrumb">
          <a href="/">WIEMIP</a> <span>›</span> Updates
        </nav>
      </div>

      <article class="doc">
{body}
      </article>

      <footer class="docs-foot">
        WIEMIP · <a href="https://github.com/WIEMIP">github.com/WIEMIP</a>
      </footer>
    </div>
  </div>
  <label class="docs-scrim" for="docs-nav-toggle" aria-hidden="true"></label>
</body>
</html>
"""


def _first(meta: dict, key: str) -> str:
    """python-markdown's `meta` gives {key: [line, ...]}; we want one line."""
    return " ".join(meta.get(key) or []).strip()


if __name__ == "__main__":
    md = markdown.Markdown(extensions=EXTENSIONS, extension_configs=EXTENSION_CONFIGS)
    body = md.convert(SOURCE.read_text())
    meta = getattr(md, "Meta", {})

    nav = "\n".join(
        f'          <li><a href="#{t["id"]}">{t["name"]}</a></li>' for t in md.toc_tokens
    )
    sidebar_links = "\n".join(
        f'        <a href="{href}">{label}</a>' for label, href in SIDEBAR_LINKS
    )
    OUT.write_text(TEMPLATE.format(
        title=_first(meta, "title") or "WIEMIP · Updates",
        description=_first(meta, "description"),
        nav=nav,
        sidebar_links=sidebar_links,
        body=body,  # flush left: indenting would shift every <pre> line
    ))
    print(f"{SOURCE.name} -> {OUT.relative_to(UPDATES_DIR.parent)}: {len(md.toc_tokens)} updates")
