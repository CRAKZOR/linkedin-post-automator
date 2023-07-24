import os
from time import sleep
import openai
import json
import requests

from scraper import Scraper


def ask_chatgpt(question, gpt_token_limit=150):
    while True:
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",          # The engine you want to use. "davinci" is the most advanced one.
                prompt=question,                    # Your question or prompt
                max_tokens=gpt_token_limit          # Maximum length of the response
            )
            return response.choices[0].text.strip()
        except openai.error.RateLimitError as e:
            print("Rate limit exceeded. Retrying in 60 seconds...")
            sleep(60)


def post_linkedin(payload, cookies ):
    cookie_value = "li_at=%s; JSESSIONID=\"%s\"" % (cookies["li_at"], cookies["JSESSIONID"])
    headers = {
        "accept":                   "application/vnd.linkedin.normalized+json+2.1",
        "accept-language":          "en-US,en;q=0.9",
        "content-type":             "application/json; charset=UTF-8",
        "csrf-token":               cookies["JSESSIONID"],
        "referrer-policy":          "strict-origin-when-cross-origin, strict-origin-when-cross-origin",
        "origin":                   "https://www.linkedin.com",
        "Referrer":                 "https://www.linkedin.com/feed/",
        "Referrer-Policy":          "strict-origin-when-cross-origin, strict-origin-when-cross-origin",
        "cookie":                   cookie_value
        # ... other headers ...
    }

    post_endpoint = "https://www.linkedin.com/voyager/api/contentcreation/normShares"

    try:
        response = requests.post(post_endpoint, headers=headers, data=payload)
        response.raise_for_status()

        # Check response content if needed
        if response.json().get('someKey', None) == 'expectedValue':
            # Handle response
            pass

    except requests.exceptions.RequestException as e:
        # Handle exception
        print(f"Error posting to LinkedIn: {e}")
        print(response.text)


def get_file_data (fname, protocol="r"):
    # Load websites from the JSON file
    with open(fname, protocol) as file:
        if "json" in str.lower(fname):
            # is .json
            return json.load(file)
        else:
            return file.read().strip()


def main():
    config      = get_file_data("config.json")

    cookies     = config["cookies"]
    api_key     = config["open_ai_api_key"]
    urls        = config["websites"]
    preamble    = config["gpt_preamble"]
    bio         = config["bio"]

    gpt_token_limit     = config["gpt_token_limit"]
    scrape_char_limit   = config["scrape_char_limit"]

    content = []
    for url in urls:
        data = Scraper(url, scrape_char_limit).fetch_content()
        if data:
            content.append(data)

    question = "\n".join([preamble, bio, "\n".join(content)])

    # print("question: ", question)

    openai.api_key = api_key

    gpt_res = ask_chatgpt(question, gpt_token_limit)
    print("Post: ", gpt_res)

    payload = {
        "visibleToConnectionsOnly": False,
        "externalAudienceProviders": [],
        "commentaryV2": {
            "text": gpt_res,
            "attributes": []
        },
        "origin": "FEED",
        "allowedCommentersScope": "ALL",
        "postState": "PUBLISHED",
        "media": []
    }

    post_linkedin( json.dumps(payload), cookies )


if __name__ == "__main__":
    main()
