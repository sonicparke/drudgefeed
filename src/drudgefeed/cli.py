from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .feed import build_rss
from .parser import DEFAULT_SOURCE_URL, parse_links, read_source, source_base_url


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an RSS feed from Drudge Report.")
    parser.add_argument(
        "--url",
        default=DEFAULT_SOURCE_URL,
        help="Source URL or local HTML file path.",
    )
    parser.add_argument("--feed-url", default="", help="Public URL for this RSS feed.")
    parser.add_argument("--title", default="Drudge Report", help="RSS channel title.")
    parser.add_argument(
        "--description",
        default="Generated RSS feed for Drudge Report links.",
        help="RSS channel description.",
    )
    parser.add_argument("--limit", type=int, default=0, help="Maximum items to include.")
    parser.add_argument("--output", default="-", help="Output path, or '-' for stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    html = read_source(args.url)
    base_url = source_base_url(args.url)
    links = parse_links(html, base_url=base_url)
    if args.limit > 0:
        links = links[: args.limit]

    xml = build_rss(
        links,
        title=args.title,
        source_url=base_url,
        description=args.description,
        feed_url=args.feed_url,
    )

    if args.output == "-":
        sys.stdout.write(xml)
        sys.stdout.write("\n")
    else:
        Path(args.output).write_text(xml + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
