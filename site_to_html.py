#!/usr/bin/env python3
"""
site_to_html.py

Give it a URL. It fetches the page, pulls out the design/structure/elements
(HTML markup, linked + inline CSS, fonts, meta/favicon info), rebuilds it as
ONE self-contained, cleaned-up index.html file, saves it, and copies the
full code to your clipboard so you can paste it anywhere.

Usage:
    python site_to_html.py https://example.com
    python site_to_html.py https://example.com -o mypage.html
    python site_to_html.py https://example.com --no-clipboard

Install dependencies first:
    pip install requests beautifulsoup4 pyperclip --break-system-packages

Notes / limitations:
- This is a "clone the look and structure" tool, not a pixel-perfect mirror.
  It inlines external CSS files it can reach, absolutizes image/link URLs
  (so images still load from the original site), strips <script> tags by
  default (turn them back on with --keep-scripts) and tidies the markup.
- Some sites render most of their content with JavaScript. This script only
  sees what's in the initial HTML response (no headless browser), so
  heavily JS-driven pages (SPAs) may come back mostly empty.
"""

import argparse
import re
import sys
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError:
    sys.exit("Missing dependency 'requests'. Install with:\n"
              "  pip install requests beautifulsoup4 pyperclip --break-system-packages")

try:
    from bs4 import BeautifulSoup, Comment
except ImportError:
    sys.exit("Missing dependency 'beautifulsoup4'. Install with:\n"
              "  pip install requests beautifulsoup4 pyperclip --break-system-packages")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def fetch(url, timeout=15):
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def absolutize_urls(soup, base_url):
    """Turn every relative src/href/srcset/url(...) reference into an absolute URL."""
    attr_tags = {
        "img": ["src", "srcset"],
        "script": ["src"],
        "source": ["src", "srcset"],
        "video": ["src", "poster"],
        "audio": ["src"],
        "a": ["href"],
        "link": ["href"],
        "iframe": ["src"],
    }
    for tag_name, attrs in attr_tags.items():
        for tag in soup.find_all(tag_name):
            for attr in attrs:
                if not tag.has_attr(attr):
                    continue
                if attr == "srcset":
                    parts = []
                    for chunk in tag[attr].split(","):
                        chunk = chunk.strip()
                        if not chunk:
                            continue
                        bits = chunk.split()
                        bits[0] = urljoin(base_url, bits[0])
                        parts.append(" ".join(bits))
                    tag[attr] = ", ".join(parts)
                else:
                    val = tag[attr]
                    if val and not val.startswith(("data:", "mailto:", "tel:", "javascript:", "#")):
                        tag[attr] = urljoin(base_url, val)

    # url(...) references inside inline style attributes
    for tag in soup.find_all(style=True):
        tag["style"] = re.sub(
            r'url\((["\']?)(?!data:)([^"\')]+)\1\)',
            lambda m: f'url("{urljoin(base_url, m.group(2))}")',
            tag["style"],
        )
    return soup


def absolutize_css_urls(css_text, base_url):
    return re.sub(
        r'url\((["\']?)(?!data:)([^"\')]+)\1\)',
        lambda m: f'url("{urljoin(base_url, m.group(2))}")',
        css_text,
    )


def collect_css(soup, base_url, timeout=15):
    """Fetch every linked stylesheet it can reach and return combined CSS text."""
    css_chunks = []
    headers = {"User-Agent": USER_AGENT}

    for link in soup.find_all("link", rel=lambda v: v and "stylesheet" in v):
        href = link.get("href")
        if not href:
            continue
        full_url = urljoin(base_url, href)
        try:
            r = requests.get(full_url, headers=headers, timeout=timeout)
            r.raise_for_status()
            css = absolutize_css_urls(r.text, full_url)
            css_chunks.append(f"/* --- {full_url} --- */\n{css}")
        except requests.RequestException as e:
            css_chunks.append(f"/* Could not fetch {full_url}: {e} */")
        link.decompose()  # remove the <link> since we're inlining it

    for style_tag in soup.find_all("style"):
        css = absolutize_css_urls(style_tag.get_text(), base_url)
        css_chunks.append(f"/* --- inline <style> --- */\n{css}")
        style_tag.decompose()

    return "\n\n".join(css_chunks)


def collect_google_fonts(soup):
    """Keep Google Fonts <link> tags (fonts, not CSS files worth inlining)."""
    font_links = []
    for link in soup.find_all("link", href=True):
        if "fonts.googleapis.com" in link["href"] or "fonts.gstatic.com" in link["href"]:
            font_links.append(str(link))
    return "\n    ".join(font_links)


def strip_noise(soup, keep_scripts):
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
    if not keep_scripts:
        for tag in soup.find_all(["script", "noscript"]):
            tag.decompose()
    for selector in ["template"]:
        for tag in soup.find_all(selector):
            tag.decompose()


def get_meta_bits(soup, base_url):
    title = soup.title.get_text(strip=True) if soup.title else urlparse(base_url).netloc
    description = ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag and desc_tag.get("content"):
        description = desc_tag["content"]

    favicon = ""
    icon_tag = soup.find("link", rel=lambda v: v and "icon" in v.lower())
    if icon_tag and icon_tag.get("href"):
        favicon = urljoin(base_url, icon_tag["href"])

    return title, description, favicon


def build_html(url, keep_scripts=False, timeout=15):
    raw_html = fetch(url, timeout=timeout)
    soup = BeautifulSoup(raw_html, "html.parser")

    title, description, favicon = get_meta_bits(soup, url)
    google_fonts_html = collect_google_fonts(soup)
    css_text = collect_css(soup, url, timeout=timeout)

    absolutize_urls(soup, url)
    strip_noise(soup, keep_scripts)

    body = soup.body
    body_html = body.decode_contents() if body else soup.decode_contents()

    favicon_tag = f'<link rel="icon" href="{favicon}">' if favicon else ""
    desc_tag = f'<meta name="description" content="{description}">' if description else ""

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{desc_tag}
{favicon_tag}
{google_fonts_html}
<!--
  Rebuilt single-file copy of: {url}
  Structure and CSS pulled from the live page's source and inlined below.
-->
<style>
{css_text}
</style>
</head>
<body>
{body_html}
</body>
</html>
"""
    return page


def copy_to_clipboard(text):
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Clone a page's design/structure into one index.html file.")
    parser.add_argument("url", nargs="?", help="URL of the page to clone")
    parser.add_argument("-o", "--output", default="index.html", help="Output file path (default: index.html)")
    parser.add_argument("--keep-scripts", action="store_true", help="Keep <script> tags (off by default)")
    parser.add_argument("--no-clipboard", action="store_true", help="Skip copying result to clipboard")
    parser.add_argument("--timeout", type=int, default=15, help="Request timeout in seconds")
    args = parser.parse_args()

    url = args.url or input("URL to clone: ").strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"Fetching {url} ...")
    try:
        html_out = build_html(url, keep_scripts=args.keep_scripts, timeout=args.timeout)
    except requests.RequestException as e:
        sys.exit(f"Failed to fetch the page: {e}")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Saved: {args.output}  ({len(html_out):,} characters)")

    if not args.no_clipboard:
        if copy_to_clipboard(html_out):
            print("Copied full HTML to clipboard.")
        else:
            print("Could not copy to clipboard automatically.\n"
                  "Install pyperclip for that:  pip install pyperclip --break-system-packages\n"
                  f"For now, open {args.output} and copy its contents manually.")


if __name__ == "__main__":
    main()
