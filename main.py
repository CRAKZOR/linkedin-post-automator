import os
from time import sleep
import openai
import json
import requests

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


def post_linkedin(payload, cookies):
    headers = {
        "accept":                   "application/vnd.linkedin.normalized+json+2.1",
        "accept-language":          "en-US,en;q=0.9",
        "content-type":             "application/json; charset=UTF-8",
        "csrf-token":               cookies["JSESSIONID"]["value"],
        "origin":                   "https://www.linkedin.com",
        "referrer":                 "https://www.linkedin.com/feed/",
        "referrer-policy": "strict-origin-when-cross-origin, strict-origin-when-cross-origin",
        "cookie": "JSESSIONID=\"" + cookies["JSESSIONID"]["value"] + "\";"
        # ... other headers ...
    }

    post_endpoint = "https://www.linkedin.com/voyager/api/contentcreation/normShares"

    try:
        response = requests.post(post_endpoint, headers=headers, json=payload)
        response.raise_for_status()

        # Check response content if needed
        if response.json().get('someKey', None) == 'expectedValue':
            # Handle response
            pass

    except requests.exceptions.RequestException as e:
        # Handle exception
        print(f"Error posting to LinkedIn: {e}")


def get_file_data (fname, protocol="r"):
    # Load websites from the JSON file
    with open(fname, protocol) as file:
        if "json" in str.lower(fname):
            # is .json
            return json.load(file)
        else:
            return file.read().strip()


def main():
    cookies  = get_file_data(os.path.join("context", "cookies.json"))
    urls     = get_file_data(os.path.join("context", "websites.json"))
    preamble = get_file_data(os.path.join("context", "gpt_preamble.txt"))
    bio      = get_file_data(os.path.join("context", "bio.txt"))

    content = []
    for url in urls:
        data = Scraper(url, 1000).fetch_content()
        if data:
            content.append(data)

    question = "\n\n".join({preamble, bio,"\n\n".join(content)})

    openai.api_key = os.getenv("OPENAI_API_KEY")

    # gpt_res = ask_chatgpt(question)
    gpt_res = "test"

    # format body
    payload = "{\"visibleToConnectionsOnly\":false,\"externalAudienceProviders\":[]," \
              "\"commentaryV2\":{\"text\":\"" + gpt_res + "\",\"attributes\":[]}," \
              "\"origin\":\"FEED\",\"allowedCommentersScope\":\"ALL\",\"postState\":\"PUBLISHED\",\"media\":[]}"

    print(payload)
    # post_linkedin( payload, cookies )



if __name__ == "__main__":
    main()
