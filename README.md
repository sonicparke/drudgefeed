# drudgefeed

A small RSS generator for [drudgereport.com](https://www.drudgereport.com/).

Drudge Report does not expose an RSS feed or per-story metadata. This tool reads
the visible links on the page and emits a valid RSS 2.0 feed with stable GUIDs
based on each story URL.

## Use

Self-host or point here:

```text
https://sonicparke.github.io/drudgefeed/feed.xml
```

Generate a feed once:

```bash
uv run drudgefeed --output feed.xml
```

Run a local feed server:

```bash
uv run drudgefeed-server --host 127.0.0.1 --port 8080
```

Then subscribe your RSS reader to:

```text
http://127.0.0.1:8080/feed.xml
```

## Deploy

This repository includes a GitHub Pages workflow that publishes a static RSS
feed every 10 minutes. Enable GitHub Pages for the repository and set the Pages
source to GitHub Actions, then run the "Publish feed" workflow once from the
Actions tab.

The workflow:

- runs on `main` pushes, manual dispatch, and a `3/10 * * * *` schedule
- runs the unit tests before publishing
- writes the generated RSS to `feed.xml`
- deploys only after a successful fetch and feed generation

If a scheduled fetch fails, the workflow fails before deployment, so the
previous successful `feed.xml` remains live.

## Options

```bash
uv run drudgefeed --help
uv run drudgefeed-server --help
```

Common options:

- `--url`: source page to fetch, defaults to `https://www.drudgereport.com/`
- `--limit`: maximum number of links to include
- `--feed-url`: public URL for this RSS feed, useful when deploying
- `--output`: output path for one-shot generation, or `-` for stdout

## Validate

```bash
uv run python -m unittest discover -s tests
uv run drudgefeed --url tests/fixtures/drudge_sample.html | python -c 'import sys, xml.etree.ElementTree as ET; ET.fromstring(sys.stdin.read())'
```
