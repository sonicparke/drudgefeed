from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET

from drudgefeed.cli import main


FIXTURE = Path(__file__).parent / "fixtures" / "drudge_sample.html"


class CliTests(unittest.TestCase):
    def test_cli_writes_feed_from_local_html_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "feed.xml"

            exit_code = main(["--url", str(FIXTURE), "--output", str(output)])

            self.assertEqual(exit_code, 0)
            root = ET.fromstring(output.read_text(encoding="utf-8"))
            channel = root.find("channel")
            self.assertEqual(root.tag, "rss")
            self.assertEqual(len(channel.findall("item")), 2)
            self.assertEqual(
                channel.findall("item")[1].findtext("link"),
                "https://www.drudgereport.com/relative-story",
            )


if __name__ == "__main__":
    unittest.main()
