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
            print(self.url)
            if self.url.endswith('rss') or self.url.endswith('xml') or self.url.endswith('feed'):
                print('RSS feed')
                return self.rss_parse(self.url)

            response = requests.get(self.url)
            response.raise_for_status()
            return self.parse(response.text)
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

    def rss_parse(self, url):
        feed: FeedParserDict = feedparser.parse(url)
        print("Feed Entries:", len(feed.entries))
        # for entry in feed.entries:
        #     print("Entry Title:", entry.title)
        #     print("Entry Link:", entry.link)
        #     print("Entry Published Date:", entry.published)
        #     print("Entry Summary:", entry.summary)
        #     print("\n")
        return feed.entries[random.randint(0, len(feed.entries) - 1)].summary
