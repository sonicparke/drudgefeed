from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .feed import build_rss
from .parser import DEFAULT_SOURCE_URL, parse_links, read_source, source_base_url


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve a generated Drudge Report RSS feed.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--url", default=DEFAULT_SOURCE_URL)
    parser.add_argument("--feed-url", default="")
    parser.add_argument("--limit", type=int, default=0)
    return parser


def build_server(
    host: str,
    port: int,
    *,
    source_url: str = DEFAULT_SOURCE_URL,
    feed_url: str = "",
    limit: int = 0,
) -> ThreadingHTTPServer:
    handler = type(
        "ConfiguredFeedHandler",
        (FeedHandler,),
        {"source_url": source_url, "feed_url": feed_url, "limit": limit},
    )
    return ThreadingHTTPServer((host, port), handler)


class FeedHandler(BaseHTTPRequestHandler):
    source_url = DEFAULT_SOURCE_URL
    feed_url = ""
    limit = 0

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/healthz":
            self._write_text(HTTPStatus.OK, "ok\n", "text/plain; charset=utf-8")
            return
        if path not in {"/", "/feed.xml"}:
            self._write_text(HTTPStatus.NOT_FOUND, "not found\n", "text/plain; charset=utf-8")
            return

        try:
            html = read_source(self.source_url)
            base_url = source_base_url(self.source_url)
            links = parse_links(html, base_url=base_url)
            if self.limit > 0:
                links = links[: self.limit]
            xml = build_rss(
                links,
                title="Drudge Report",
                source_url=base_url,
                description="Generated RSS feed for Drudge Report links.",
                feed_url=self.feed_url,
            )
        except Exception as exc:  # noqa: BLE001 - runtime fetch errors become HTTP 502.
            self._write_text(
                HTTPStatus.BAD_GATEWAY,
                f"failed to generate feed: {exc}\n",
                "text/plain; charset=utf-8",
            )
            return

        self._write_text(HTTPStatus.OK, xml + "\n", "application/rss+xml; charset=utf-8")

    def _write_text(self, status: HTTPStatus, body: str, content_type: str) -> None:
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    server = build_server(args.host, args.port, source_url=args.url, feed_url=args.feed_url, limit=args.limit)
    print(f"Serving Drudge RSS feed at http://{args.host}:{args.port}/feed.xml")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
