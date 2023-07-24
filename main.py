from datetime import timedelta, datetime
import json
import random
import requests
import schedule
import openai
from re import sub
from time import sleep

from scraper import Scraper


def custom_print(message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{current_time}] {message}")


def ask_chatgpt(messages, token_limit=150, model="gpt-3.5-turbo"):
    """
        see https://platform.openai.com/docs/models/gpt-4 for available engines
        :param messages:
        :param token_limit: limit the response length
        :param model:       gpt model/engine
        :return:

        messages must be in format ex: [ {"role": "user", "content": "I am Peter"} ... ]
    """

    while True:
        try:
            response = openai.ChatCompletion.create(
                model       = model,
                messages    = messages,
                max_tokens=token_limit
                # temperature = 0,

            )
            custom_print(response["usage"])
            custom_print(response.choices)
            return response.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            custom_print("Rate limit exceeded. Retrying in 60 seconds...")
            sleep(60)
        except openai.error.ServiceUnavailableError:
            custom_print("The server is overloaded or not ready yet.  Retrying in 60 seconds...")
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
        custom_print(f"Error posting to LinkedIn: {e}")
        custom_print(response.text)


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
    random.shuffle(content)

    # Combine preamble, bio, and website content into the correctly formatted messages
    gpt_messages = [
                       {"role": "system", "content": preamble},
                       {"role": "system", "content": bio},
                   ] + [
                       {"role": "user", "content": item} for item in content
                   ]

    openai.api_key = api_key

    # print(gpt_messages)
    gpt_res = ask_chatgpt(gpt_messages, gpt_token_limit)
    # custom_print("Post: " + sub( r'\n+', ' ', gpt_res))

    return
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


def main_task():
    main()
    # After the main task is done, schedule the next task
    schedule_next_task()


def schedule_next_task():
    random_hour     = random.randint(11, 16)           # Random hour between 11am and 4pm inclusive
    random_minute   = random.randint(0, 59)            # Random minute

    # Compute the next date when the task will run
    next_run_date = datetime.now() + timedelta(days=2)
    formatted_next_run_date = next_run_date.strftime('%m/%d/%Y')

    custom_print(f"Scheduled to run on {formatted_next_run_date} at {random_hour}:{random_minute}")

    # Clear all jobs before scheduling a new one
    schedule.clear()

    schedule.every(2).days.at(f"{random_hour:02d}:{random_minute:02d}").do(main_task)


if __name__ == "__main__":
    # Run main() once initially
    main()

    # Start the process by scheduling the first task
    schedule_next_task()

    while True:
        schedule.run_pending()
        sleep(1)
