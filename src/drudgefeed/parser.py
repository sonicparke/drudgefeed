from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


DEFAULT_SOURCE_URL = "https://www.drudgereport.com/"
USER_AGENT = "drudgefeed/0.1 (+https://www.drudgereport.com/)"


@dataclass(frozen=True)
class FeedLink:
    title: str
    url: str


class _LinkParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.links: list[FeedLink] = []
        self._href_stack: list[str | None] = []
        self._text_stack: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attr_map = {name.lower(): value for name, value in attrs}
        self._href_stack.append(attr_map.get("href"))
        self._text_stack.append([])

    def handle_data(self, data: str) -> None:
        if self._text_stack:
            self._text_stack[-1].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._href_stack:
            return

        href = self._href_stack.pop()
        text_parts = self._text_stack.pop()
        title = _normalize_text(" ".join(text_parts))
        url = _normalize_url(href, self.base_url)
        if title and url:
            self.links.append(FeedLink(title=title, url=url))


def parse_links(html: str, *, base_url: str = DEFAULT_SOURCE_URL) -> list[FeedLink]:
    parser = _LinkParser(base_url)
    parser.feed(html)

    seen: set[str] = set()
    links: list[FeedLink] = []
    for link in parser.links:
        if _is_homepage_link(link.url, base_url):
            continue
        if link.url in seen:
            continue
        seen.add(link.url)
        links.append(link)
    return links


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _normalize_url(href: str | None, base_url: str) -> str:
    if not href:
        return ""

    href = href.strip()
    parsed = urlparse(href)
    if parsed.scheme in {"javascript", "mailto", "tel"}:
        return ""
    if href.startswith("#"):
        return ""

    url = urljoin(base_url, href)
    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"}:
        return ""
    return url


def _is_homepage_link(url: str, base_url: str) -> bool:
    parsed_url = urlparse(url)
    parsed_base = urlparse(base_url)
    if parsed_url.netloc != parsed_base.netloc:
        return False
    return parsed_url.path.rstrip("/") == parsed_base.path.rstrip("/")


def fetch_html(url: str = DEFAULT_SOURCE_URL, *, timeout: float = 20.0) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def read_source(source: str) -> str:
    path = Path(source)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return fetch_html(source)


def source_base_url(source: str) -> str:
    if Path(source).exists():
        return DEFAULT_SOURCE_URL
    return source
