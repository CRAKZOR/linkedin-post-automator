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


def ask_chatgpt(messages, token_limit=150, model="gpt-3.5-turbo", temp=1, retry_count=5):
    """
    Queries the GPT model for a response based on input messages.

    :param messages     : Input messages formatted as a list of dictionaries.
                            Example: [{"role": "user", "content": "I am Peter"}]
    :param token_limit  : Maximum length of the GPT response.
    :param model        : Name of the GPT model/engine to be used.
    :param retry_delay  : Duration (in seconds) to wait before retrying after an error.
    :param temp         : Specifies the randomness of the model's output. Higher values (close to 1) make
                            the output more random, while lower values make it more deterministic.

    :return: GPT response as a string.
    """

    while retry_count >= 0:
        retry_count -= 1

        try:
            response = openai.ChatCompletion.create(
                model       = model,
                messages    = messages,
                max_tokens  = token_limit,
                temperature = temp

            )
            custom_print(response["usage"])

            if response.choices[0].finish_reason != "stop":
                # message was cut off
                sleep(5)
                continue

            return response.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            custom_print("Rate limit exceeded. Retrying in 60 seconds...")
            sleep(60)
        except openai.error.ServiceUnavailableError:
            custom_print("The server is overloaded or not ready yet.  Retrying in 60 seconds...")
            sleep(60)

    return None



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
    if not gpt_res:
        return custom_print("Error: gpt response empty")

    custom_print("Post: " + sub(r'\n+', ' ', gpt_res))

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
    config              = get_file_data("config.json")

    hour_interval       = int(config["hour_interval"])          or 0
    rand_hour_offset    = int(config["random_hour_offset"])     or 0
    rand_min_offset     = int(config["random_min_offset"])      or 0

    # Calculate the total interval in minutes, including the random offsets
    total_minutes_interval = (hour_interval * 60) + random.randint(0, rand_hour_offset * 60) + random.randint(0,
                                                                                                              rand_min_offset)
    # Compute the exact datetime for the next task
    next_run_time = datetime.now() + timedelta(minutes=total_minutes_interval)
    formatted_next_run_time = next_run_time.strftime('%Y-%m-%d %H:%M:%S')

    custom_print(f"Scheduled to run on {formatted_next_run_time}")

    schedule.every(total_minutes_interval).minutes.do(main_task)


if __name__ == "__main__":
    # Run main() once initially
    main()

    # Start the process by scheduling the first task
    schedule_next_task()

    while True:
        schedule.run_pending()
        sleep(1)
