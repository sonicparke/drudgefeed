from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from .parser import FeedLink


def build_rss(
    links: list[FeedLink],
    *,
    title: str,
    source_url: str,
    description: str,
    feed_url: str = "",
) -> str:
    ET.register_namespace("atom", "http://www.w3.org/2005/Atom")

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = title
    ET.SubElement(channel, "link").text = source_url
    ET.SubElement(channel, "description").text = description
    ET.SubElement(channel, "language").text = "en-us"
    ET.SubElement(channel, "lastBuildDate").text = _rfc2822_now()
    ET.SubElement(channel, "generator").text = "drudgefeed"

    if feed_url:
        ET.SubElement(
            channel,
            "{http://www.w3.org/2005/Atom}link",
            {"href": feed_url, "rel": "self", "type": "application/rss+xml"},
        )

    for link in links:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = link.title
        ET.SubElement(item, "link").text = link.url
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = link.url
        ET.SubElement(item, "description").text = f"Linked from Drudge Report. Source: {_source_label(link.url)}"

    return ET.tostring(rss, encoding="unicode", xml_declaration=True)


def _rfc2822_now() -> str:
    return format_datetime(datetime.now(timezone.utc), usegmt=True)


def _source_label(url: str) -> str:
    host = urlparse(url).netloc
    return host.removeprefix("www.") or "external link"
