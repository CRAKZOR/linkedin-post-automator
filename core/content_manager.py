from core.linkedin import LinkedIn
from core.chatgpt import ChatGpt
from core.scraper import Scraper

import random
from re import sub

from utils import get_file_data, custom_print


class ContentManager:
    @staticmethod
    def load_config(fpath):
        return get_file_data(fpath)

    def __init__(self, config_path):

        self.config = self.load_config(config_path)

        # Initialize all config options as instance variables
        self.cookies            = self.config.get("cookies")
        self.chatgpt            = ChatGpt( self.config.get("open_ai_api_key") )
        self.urls               = self.config.get("websites")
        self.preamble           = self.config.get("gpt_preamble")
        self.bio                = self.config.get("bio")
        self.gpt_token_limit    = self.config.get("gpt_token_limit")
        self.scrape_char_limit  = self.config.get("scrape_char_limit")
        self.num_recent_posts   = self.config.get("num_recent_posts")

    def fetch_website_content(self):
        content = []
        for url in self.urls:
            data = Scraper(url, self.scrape_char_limit).fetch_content()
            if data:
                content.append(data)
        random.shuffle(content)

        return content

    def process_gpt_response(self, scraped_content=None, recent_posts=None):
        # Combine preamble, bio, and website content into the correctly formatted messages
        gpt_messages = [
            {"role": "system", "content": self.preamble},
            {"role": "user",   "content": self.bio},
        ]

        if scraped_content:
            gpt_messages.extend([
                {"role": "user", "content": content} for content in scraped_content
            ])

        # if recent_posts:
        #     gpt_messages.extend([
        #         {"role": "user", "content": "Recent post #" + str(idx+1) + ": " + post}
        #         for idx, post in enumerate(recent_posts)
        #     ])

        gpt_res = self.chatgpt.ask(gpt_messages, self.gpt_token_limit)

        if not gpt_res:
            return None

        return gpt_res

    def post_content(self):

        content         = self.fetch_website_content()

        # Remove first pair-of double quotes if there are any in the beginning.
        gpt_response    = sub(r'^"([^"]*)"', r'\1', self.process_gpt_response(content) )

        if not gpt_response:
            custom_print("Error: gpt response empty")
            return

        custom_print("Post: " + sub(r'\n+', ' ', gpt_response))

        linkedin        = LinkedIn(self.cookies)

        # linkedin.post_file(gpt_response, ["media", "burndown.png"])
        linkedin.post(gpt_response)
