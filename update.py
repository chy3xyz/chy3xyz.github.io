#!/usr/bin/env python3
"""Regenerate index.html from the live GitHub API.

Requires `gh auth login`. Edit FEATURED to change which repos get a card.

    python3 update.py
"""

import datetime
import html
import json
import pathlib
import subprocess
import sys

OWNER = "chy3xyz"
FEATURED = ["ghw", "zdoc", "zigmodu", "zent", "zwechat", "zwasm", "zcordis", "zenaipa"]

HERE = pathlib.Path(__file__).parent


def fetch_repos():
    """Return [(name, description, stars, language, pushed_at, homepage), ...]."""
    out = subprocess.run(
        [
            "gh", "api",
            f"users/{OWNER}/repos?per_page=100&sort=updated&type=owner",
            "--paginate",
            "--jq",
            '.[] | select(.private==false) | '
            "[.name, (.description//\"\"), (.stargazers_count|tostring), "
            "(.language//\"\"), .pushed_at, (.homepage//\"\")] | @tsv",
        ],
        capture_output=True, text=True, check=True,
    ).stdout

    repos = []
    for line in out.splitlines():
        parts = (line.split("\t") + [""] * 6)[:6]
        repos.append(tuple(parts))
    return repos


def esc(value):
    return html.escape(value or "", quote=True)


def ago(iso):
    if not iso:
        return ""
    when = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    days = (datetime.datetime.now(datetime.timezone.utc) - when).days
    if days <= 0:
        return "today"
    if days == 1:
        return "1 day ago"
    if days < 30:
        return f"{days} days ago"
    if days < 365:
        return f"{days // 30} months ago"
    return f"{days // 365} years ago"


def build(repos, template):
    by_name = {r[0]: r for r in repos}

    cards = []
    for name in FEATURED:
        row = by_name.get(name)
        if not row:
            print(f"  ! skipped missing repo: {name}", file=sys.stderr)
            continue
        _, desc, stars, lang, _, home = row
        tags = [t for t in (lang, f"★ {stars}" if stars != "0" else None) if t]
        body = esc(desc) or '<span class="muted">No description yet.</span>'
        cards.append(
            f'      <a class="card" href="https://github.com/{OWNER}/{esc(name)}"'
            f' target="_blank" rel="noopener">\n'
            f"        <h3>{esc(name)}</h3>\n"
            f"        <p>{body}</p>\n"
            f"        <div class=\"meta\">{esc(' · '.join(tags))}</div>\n"
            f"      </a>"
        )

    rows_html = []
    for name, desc, stars, lang, pushed, home in sorted(repos, key=lambda r: r[4], reverse=True):
        body = esc(desc) or '<span class="muted">—</span>'
        site = (
            f'<a class="site" href="{esc(home)}" target="_blank" rel="noopener">site ↗</a>'
            if home else ""
        )
        rows_html.append(
            f"      <tr>\n"
            f'        <td><a href="https://github.com/{OWNER}/{esc(name)}"'
            f' target="_blank" rel="noopener">{esc(name)}</a></td>\n'
            f'        <td class="desc">{body}</td>\n'
            f'        <td class="lang">{esc(lang) or "—"}</td>\n'
            f'        <td class="num">{esc(stars)}</td>\n'
            f'        <td class="date">{esc(ago(pushed))}</td>\n'
            f"        <td>{site}</td>\n"
            f"      </tr>"
        )

    return (
        template
        .replace("__FEATURED__", "\n".join(cards))
        .replace("__ALL__", "\n".join(rows_html))
        .replace("__COUNT__", str(len(repos)))
    )


def main():
    template_path = HERE / "index.template.html"
    if not template_path.exists():
        sys.exit(f"missing template: {template_path}")

    repos = fetch_repos()
    out = build(repos, template_path.read_text(encoding="utf-8"))
    (HERE / "index.html").write_text(out, encoding="utf-8")

    print(f"wrote index.html — {len(repos)} repos, {len(FEATURED)} featured")


if __name__ == "__main__":
    main()