import random

import requests
from bs4 import BeautifulSoup
import re
import feedparser
from feedparser import FeedParserDict


class Scraper:
    def __init__(self, url, character_limit=2000):
        self.url: str = url
        self.character_limit = character_limit

    def fetch_content(self):
        try:
            # 1) Optimistically parse as feed
            feed = feedparser.parse(self.url)
            if not feed.bozo and feed.entries:
                return self.rss_parse(feed)

            # 2) Fallback: treat as HTML page
            resp = requests.get(self.url, timeout=10)
            resp.raise_for_status()
            return self.parse(resp.text)

        except Exception as e:
            print(f"Error fetching content from {self.url}: {e}")
            return None

    def parse(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        # Removing undesired elements like navigation bars and headers
        # This is a generic example; adjust according to the specific website
        for element in soup.find_all(["nav", "header"]):  # You can also look for elements by their class or ID
            element.decompose()

        # Removing script and style elements to avoid non-visible text
        for script in soup(["script", "style"]):
            script.extract()

        # Extract text using the get_text() method
        all_text = soup.get_text()

        # Split the lines, remove leading and trailing whitespace
        lines = (line.strip() for line in all_text.splitlines())

        # Remove empty lines, and multi-space and join
        all_text_clean = re.sub(r'\s+', ' ', (' '.join(line for line in lines if line)))

        return all_text_clean[0:self.character_limit]

    def rss_parse(self, feed: FeedParserDict) -> str | None:
        if not feed.entries:
            return None     # Empty feed

        entry = random.choice(feed.entries)

        # prefer summary, fall back to content or title
        raw = (
                getattr(entry, "summary", None)
                or getattr(entry, "description", None)
                or (entry.content[0].value if getattr(entry, "content", None) else None)
                or entry.title
        )
        if raw is None:
            return None

        text = BeautifulSoup(raw, "html.parser").get_text(" ", strip=True)
        return text[: self.character_limit]
