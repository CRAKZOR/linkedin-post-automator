import requests
from bs4 import BeautifulSoup
import re


class Scraper:
    def __init__(self, url, character_limit=2000):
        self.url = url
        self.character_limit = character_limit

    def fetch_content(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return self.parse(response.text)
        except Exception as e:
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
        all_text_clean = re.sub( r'\s+', ' ', ( ' '.join( line for line in lines if line ) ) )

        return all_text_clean[0:self.character_limit]
