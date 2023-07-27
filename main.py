import configparser
from datetime import timedelta, datetime
import json
import random
import requests
import schedule
import openai
from time import sleep
import logging

from scraper import Scraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("in.log"),
        logging.StreamHandler()
    ]
)


def ask_chatgpt(messages, token_limit=150, model="gpt-3.5-turbo"):

    request_wait_time_seconds = 1
    response_text = ''
    # reason_mapping = {
    #     "stop": "Reached max_tokens",
    #     "length": "Response length exceeded max_tokens",
    #     "function_call": "Function call encountered",
    #     "content_filter": "Content filter triggered",
    #     "max_tokens": "Max tokens exceeded",
    # }
    while True:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=token_limit,
                stop=["xx"],
            )

            logging.info(f'Usage: {response["usage"]}')

            # if response.choices[0].finish_reason in reason_mapping.keys():
            #     reason_name = reason_mapping[response.choices[0].finish_reason]
            #     raise Exception(f"Reason: {reason_name}")

            response_text = response.choices[0].message['content'].strip()
            logging.info(f"Text from GPT: {response_text}")
            return response_text

        except openai.error.RateLimitError:
            logging.error(f"Rate limit exceeded. Retrying in {request_wait_time_seconds} seconds...")
        except openai.error.ServiceUnavailableError:
            logging.error("The server is overloaded or not ready yet.  Retrying in 60 seconds...")
        except Exception as e:
            logging.error(f"Error: {e}")
        finally:
            with open("out.log", "a") as f:
                f.write(f"{datetime.now()}: {response_text}\n")
            request_wait_time_seconds **= 2
            logging.info(f"Request wait time: {request_wait_time_seconds}")
            sleep(request_wait_time_seconds)


def get_session():
    if "linkedin_session" not in globals():
        session = requests.Session()
        globals()["linkedin_session"] = session
    return globals()["linkedin_session"]


def post_linkedin(payload, cookies):
    session = get_session()
    cookie_value = "li_at=%s; JSESSIONID=\"%s\"" % (cookies["li_at"], cookies["JSESSIONID"])
    headers = {
        "accept": "application/vnd.linkedin.normalized+json+2.1",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json; charset=UTF-8",
        "csrf-token": cookies["JSESSIONID"],
        "referrer-policy": "strict-origin-when-cross-origin, strict-origin-when-cross-origin",
        "origin": "https://www.linkedin.com",
        "Referrer": "https://www.linkedin.com/feed/",
        "Referrer-Policy": "strict-origin-when-cross-origin, strict-origin-when-cross-origin",
        "cookie": cookie_value
    }

    post_endpoint = "https://www.linkedin.com/voyager/api/contentcreation/normShares"

    try:
        response = session.post(post_endpoint, headers=headers, data=payload)
        response.raise_for_status()

        if response.json().get('someKey', None) == 'expectedValue':
            pass

    except requests.exceptions.RequestException as e:
        logging.error(f"Error posting to LinkedIn: {e}")


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    settings = config['settings']
    bio = settings['bio']
    preamble = settings['gpt_preamble']
    gpt_token_limit = int(settings['gpt_token_limit'])
    scrape_char_limit = int(settings['scrape_char_limit'])
    openai.api_key = settings['open_ai_api_key']

    cookies_conf = config['cookies']
    cookies = {
        'JSESSIONID': cookies_conf['JSESSIONID'],
        'li_at': cookies_conf['li_at']
    }

    urls = config['websites']['websites'].split()

    content = []
    for url in urls:
        data = Scraper(url, scrape_char_limit).fetch_content()
        if data:
            content.append(data)
    random.shuffle(content)

    system_messages = [
        {"role": "system", "content": preamble},
        {"role": "system", "content": bio},
    ]

    user_messages = [
        {"role": "user", "content": item} for item in content
    ]

    gpt_messages = system_messages + user_messages
    gpt_res = ask_chatgpt(gpt_messages, gpt_token_limit)

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

    post_linkedin(json.dumps(payload), cookies )


def main_task():
    main()
    schedule_next_task()
    logging.info("Task completed")


def schedule_next_task():
    minutes_for_next_task = random.randint(30, 90)
    logging.info(f"Next task scheduled in {minutes_for_next_task} minutes")
    schedule.every(minutes_for_next_task).minutes.do(main_task)


if __name__ == "__main__":
    schedule_next_task()

    while True:
        schedule.run_pending()
        sleep(1)
