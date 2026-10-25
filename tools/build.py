#!/usr/bin/env python3
"""Renders src/*.html into _site/ with values from site.config.json.

Templating is deliberately tiny: `{{key}}` is replaced by the config value, `{{include:name}}`
pulls in src/_partials/name.html, and blocks wrapped in `<!-- if:key -->…<!-- endif -->` are kept
only when the key has a non-empty value (`<!-- ifnot:key -->` is the inverse). Pages end up as
`_site/<name>/index.html` so URLs have no extension; `index.html` stays at the root.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
OUT = ROOT / "_site"
CONFIG = json.loads((ROOT / "site.config.json").read_text())

# innermost blocks only (no nested `<!-- if` inside), applied repeatedly so nesting works
COND_RE = re.compile(r"<!-- (if|ifnot):(\w+) -->((?:(?!<!-- if).)*?)<!-- endif -->", re.S)
INCLUDE_RE = re.compile(r"\{\{include:(\w+)\}\}")
VAR_RE = re.compile(r"\{\{(\w+)\}\}")


def render(text: str, extra: dict[str, str]) -> str:
    values = {**CONFIG, **extra}

    def cond(m: re.Match) -> str:
        kind, key, body = m.group(1), m.group(2), m.group(3)
        truthy = bool(str(values.get(key, "")).strip())
        return body if (truthy if kind == "if" else not truthy) else ""

    # resolve includes first (they may contain conditionals), then conditionals, then variables
    for _ in range(3):
        text = INCLUDE_RE.sub(lambda m: (SRC / "_partials" / f"{m.group(1)}.html").read_text(), text)
    while COND_RE.search(text):
        text = COND_RE.sub(cond, text)
    text = VAR_RE.sub(lambda m: str(values.get(m.group(1), m.group(0))), text)
    return text


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC / "assets", OUT / "assets")
    pages = sorted(p for p in SRC.glob("*.html"))
    unresolved: list[str] = []
    for page in pages:
        name = page.stem
        extra = {"page": name, "canonical": CONFIG["site_url"] + ("" if name == "index" else f"/{name}")}
        html = render(page.read_text(), extra)
        leftover = VAR_RE.findall(html)
        if leftover:
            unresolved.extend(f"{page.name}: {{{{{k}}}}}" for k in leftover)
        dest = OUT / "index.html" if name == "index" else OUT / name / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html)
    (OUT / ".nojekyll").write_text("")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {CONFIG['site_url']}/sitemap.xml\n")
    urls = "".join(
        f"  <url><loc>{CONFIG['site_url']}{'' if p.stem == 'index' else '/' + p.stem}</loc></url>\n"
        for p in pages
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n"
    )
    if unresolved:
        print("unresolved placeholders:\n  " + "\n  ".join(unresolved), file=sys.stderr)
        return 1
    print(f"built {len(pages)} pages into {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
