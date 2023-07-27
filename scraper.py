import requests
from bs4 import BeautifulSoup
import re


class Scraper:
    def __init__(self, url, character_limit=2000):
        self.url = url
        self.character_limit = character_limit

    def fetch_content(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            return self.parse(response.text)
        return None

    def parse(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        for element in soup.find_all(["href"]):
            element.decompose()

        for script in soup(["script", "style"]):
            script.extract()

        all_text = soup.get_text()

        lines = (line.strip() for line in all_text.splitlines())

        all_text_clean = re.sub(r'\s+', ' ', (' '.join(line for line in lines if line)))
        all_text_clean = all_text_clean.replace("  ", " ").replace('\\n', '')
        return all_text_clean
