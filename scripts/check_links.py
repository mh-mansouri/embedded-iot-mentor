"""Verify every outbound link in the READMEs, the landing page, and CONTRIBUTING.md
still resolves.

These are the links a reader actually clicks — badges, the release download, the
Marketplace listing, the one-click Render deploy, the registry submission pages.
A renamed listing or a moved release asset fails silently otherwise; nobody
notices until someone reports a dead "Install" button.

Some hosts (Claude.ai, the VS Code Marketplace) return 403 to a plain scripted
request from a datacenter IP range -- confirmed manually to work fine from a
real browser -- even though the page itself is live. Those are treated as
unverifiable rather than failures. Everything else must return a successful or
redirect status.

GET only, no HEAD: the Marketplace answers HEAD with 404 regardless of whether
the listing exists, which would make every extension page look broken.
"""
from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent

FILES = [
    ROOT / "README.md",
    ROOT / "README.sv.md",
    ROOT / "README.fa.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "docs" / "index.html",
    ROOT / ".github" / "DISTRIBUTION.md",
]

# Markdown `[text](url)` and HTML `href="url"` / `src="url"`, in one pass —
# docs/index.html carries its badges and links as literal HTML, not Markdown.
# The href/src alternative excludes quotes and whitespace from the URL itself,
# not just as the closing delimiter: docs/index.html builds several links by
# JS string concatenation (`href="https://.../repo=' + REPO + '"`), and a
# looser class would swallow the `' + REPO + '` fragment into the "URL" and
# hand urlopen something with a space in it instead of skipping the line.
LINK_RE = re.compile(r"\]\((https?://[^)\s]+)\)|(?:href|src)=\"(https?://[^\"\s']+)\"")

BOT_PROTECTED_DOMAINS = ("marketplace.visualstudio.com", "claude.ai")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
}


def collect_urls() -> list[tuple[str, str]]:
    """(source file, url) pairs, in file order, de-duplicated by url."""
    seen: set[str] = set()
    urls: list[tuple[str, str]] = []
    for path in FILES:
        if not path.is_file():
            continue
        for match in LINK_RE.finditer(path.read_text(encoding="utf-8")):
            url = (match.group(1) or match.group(2)).rstrip(".,")
            if url in seen:
                continue
            seen.add(url)
            urls.append((path.name, url))
    return urls


def check(url: str) -> str | None:
    request = urllib.request.Request(url, headers=HEADERS, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            if 200 <= response.status < 400:
                return None
            return f"unexpected status {response.status}"
    except urllib.error.HTTPError as exc:
        # Python's redirect handler doesn't chase 308s, but the resource is live.
        if 300 <= exc.code < 400:
            return None
        if exc.code == 403 and any(domain in url for domain in BOT_PROTECTED_DOMAINS):
            return None
        return f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return str(exc.reason)


def main() -> int:
    failures = []
    for source, url in collect_urls():
        error = check(url)
        if error is None:
            print(f"OK   {url}")
        else:
            print(f"FAIL {url} ({source}): {error}")
            failures.append((source, url, error))

    if failures:
        print(f"\n{len(failures)} broken link(s):")
        for source, url, error in failures:
            print(f"  {source}: {url} -> {error}")
        return 1

    print("\nAll links OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
