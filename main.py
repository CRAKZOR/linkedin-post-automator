import os
from time import sleep
import openai
import json

from scraper import Scraper


def ask_chatgpt(question):
    while True:
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",  # The engine you want to use. "davinci" is the most advanced one.
                prompt=question,            # Your question or prompt
                max_tokens=150              # Maximum length of the response
            )
            return response.choices[0].text.strip()
        except openai.error.RateLimitError as e:
            print("Rate limit exceeded. Retrying in 60 seconds...")
            sleep(60)

def get_file_data (fname, protocol="r"):
    # Load websites from the JSON file
    with open(fname, protocol) as file:
        if "json" in str.lower(fname):
            # is .json
            return json.load(file)
        else:
            return file.read().strip()

def main():
    urls     = get_file_data( os.path.join("context", "websites.json") )
    preamble = get_file_data( os.path.join("context", "gpt_preamble.txt") )
    bio      = get_file_data( os.path.join("context", "bio.txt") )

    content = []
    for url in urls:
        data = Scraper(url, 1000).fetch_content()
        if data:
            content.append(data)

    question = preamble + "\n\n" + bio + "\n\n" + "\n\n".join(content)
    print(question)

    openai.api_key = os.getenv("OPENAI_API_KEY")

    # print(ask_chatgpt("how are you?"))


if __name__ == "__main__":
    main()
