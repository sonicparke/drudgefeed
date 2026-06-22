import unittest
import xml.etree.ElementTree as ET

from drudgefeed.feed import build_rss
from drudgefeed.parser import FeedLink


class FeedTests(unittest.TestCase):
    def test_build_rss_returns_parseable_feed_with_items(self) -> None:
        xml = build_rss(
            [
                FeedLink("FIRST STORY", "https://example.com/story-one"),
                FeedLink("Relative Story", "https://www.drudgereport.com/relative-story"),
            ],
            title="Drudge Report",
            source_url="https://www.drudgereport.com/",
            feed_url="https://feeds.example.com/drudge.xml",
            description="Generated feed.",
        )

        root = ET.fromstring(xml)
        channel = root.find("channel")

        self.assertEqual(root.tag, "rss")
        self.assertEqual(root.attrib["version"], "2.0")
        self.assertIsNotNone(channel)
        self.assertEqual(channel.findtext("title"), "Drudge Report")
        self.assertEqual(channel.findtext("link"), "https://www.drudgereport.com/")
        self.assertEqual(len(channel.findall("item")), 2)
        self.assertEqual(channel.find("item/guid").attrib["isPermaLink"], "true")
        self.assertEqual(channel.findtext("item/guid"), "https://example.com/story-one")
        atom_link = channel.find("{http://www.w3.org/2005/Atom}link")
        self.assertIsNotNone(atom_link)
        self.assertEqual(atom_link.attrib["href"], "https://feeds.example.com/drudge.xml")


if __name__ == "__main__":
    unittest.main()
