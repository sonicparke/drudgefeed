from pathlib import Path
import unittest

from drudgefeed.parser import parse_links


FIXTURE = Path(__file__).parent / "fixtures" / "drudge_sample.html"


class ParserTests(unittest.TestCase):
    def test_parse_links_keeps_visible_story_links_only(self) -> None:
        links = parse_links(FIXTURE.read_text(encoding="utf-8"), base_url="https://www.drudgereport.com/")

        self.assertEqual(
            [(link.title, link.url) for link in links],
            [
                ("FIRST STORY", "https://example.com/story-one"),
                ("Relative Story", "https://www.drudgereport.com/relative-story"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
