from http import HTTPStatus
from pathlib import Path
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen
import xml.etree.ElementTree as ET

from drudgefeed.server import build_server


FIXTURE = Path(__file__).parent / "fixtures" / "drudge_sample.html"


class ServerTests(unittest.TestCase):
    def test_server_serves_feed_health_and_not_found(self) -> None:
        server = build_server("127.0.0.1", 0, source_url=str(FIXTURE), feed_url="http://127.0.0.1/feed.xml")
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            host, port = server.server_address
            base_url = f"http://{host}:{port}"

            with urlopen(f"{base_url}/healthz", timeout=2) as response:
                self.assertEqual(response.status, HTTPStatus.OK)
                self.assertEqual(response.read().decode("utf-8"), "ok\n")

            with urlopen(f"{base_url}/feed.xml", timeout=2) as response:
                self.assertEqual(response.status, HTTPStatus.OK)
                self.assertEqual(response.headers["Content-Type"], "application/rss+xml; charset=utf-8")
                root = ET.fromstring(response.read().decode("utf-8"))
                self.assertEqual(len(root.find("channel").findall("item")), 2)

            with self.assertRaises(HTTPError) as raised:
                urlopen(f"{base_url}/missing", timeout=2)
            self.assertEqual(raised.exception.code, HTTPStatus.NOT_FOUND)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

if __name__ == "__main__":
    unittest.main()
