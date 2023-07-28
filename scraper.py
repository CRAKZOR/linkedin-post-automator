import random
from configparser import ConfigParser

import requests
from bs4 import BeautifulSoup
import re
import logging


class Scraper:
    def __init__(self, url, character_limit=2000):
        self.url = url
        self.character_limit = character_limit

    def fetch_content(self):
        logging.info(f"Fetching content from {self.url}")
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


class RssScrap(Scraper):

    def parse(self, content):
        news = []
        try:
            soup = BeautifulSoup(content, 'xml')
            for item in soup.find_all('item'):
                news.append({
                    'title': item.find('title').text,
                    'link': item.find('link').text,
                    'description': item.find('description').text,
                    'thumbnail': item.find('media:thumbnail').get('url'),
                })
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            random.shuffle(news)
            chosen_rss = news[0]
            return chosen_rss


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    xss_urls = config.get('websites', 'websites').split(',')
    r = RssScrap('https://www.entrepreneur.com/latest.rss').fetch_content()
    print(r)
