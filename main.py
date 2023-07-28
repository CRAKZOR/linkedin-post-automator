import configparser
from datetime import timedelta, datetime
import json
import random
import requests
import schedule
import openai
from time import sleep
import logging

from scraper import RssScrap

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("in.log"),
        logging.StreamHandler()
    ]
)


def ask_chatgpt(config, content, token_limit=150):
    preamble = config["preamble"]
    bio = config["bio"]

    system_messages = [
        {"role": "system", "content": preamble},
        {"role": "system", "content": bio},
    ]

    user_messages = [
        {"role": "user", "content": item} for item in content
    ]

    gpt_messages = system_messages + user_messages

    request_wait_time_seconds = 1
    response_text = ''
    while True:
        try:
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=gpt_messages,
                max_tokens=token_limit,
                stop=["xx"],
            )
            logging.info(f'Usage: {response["usage"]}')
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
            request_wait_time_seconds *= 2
            logging.info(f"Request wait time: {request_wait_time_seconds}")
            sleep(request_wait_time_seconds)


def get_session():
    if "linkedin_session" not in globals():
        session = requests.Session()
        globals()["linkedin_session"] = session
    return globals()["linkedin_session"]


def post_linkedin(payload_text, cookies_conf):
    payload = {
        "visibleToConnectionsOnly": False,
        "externalAudienceProviders": [],
        "commentaryV2": {
            "text": payload_text,
            "attributes": []
        },
        "origin": "FEED",
        "allowedCommentersScope": "ALL",
        "postState": "PUBLISHED",
        "media": []
    }
    session = get_session()
    cookie_value = "li_at=%s; JSESSIONID=\"%s\"" % (cookies_conf["li_at"], cookies_conf["JSESSIONID"])
    headers = {
        "accept": "application/vnd.linkedin.normalized+json+2.1",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json; charset=UTF-8",
        "csrf-token": cookies_conf["JSESSIONID"],
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


def main(config_path='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_path)

    settings = config['settings']
    gpt_token_limit = int(settings['gpt_token_limit'])
    scrape_char_limit = int(settings['scrape_char_limit'])
    openai.api_key = settings['open_ai_api_key']

    cookies_conf = config['cookies']

    urls = config['websites']['websites'].split()

    content = []
    for url in urls:
        data = RssScrap(url, scrape_char_limit).fetch_content()
        if data:
            content.append(data)
    random.shuffle(content)

    gpt_res = ask_chatgpt(settings, content, token_limit=gpt_token_limit)
    post_linkedin(gpt_res, cookies_conf)


def main_task(**kwargs):
    main(**kwargs)
    schedule_next_task()
    logging.info("Task completed")


def schedule_next_task(**kwargs):
    minutes_for_next_task = random.randint(30, 90)
    time_to_execute = datetime.now() + timedelta(minutes=minutes_for_next_task)
    logging.info(f"Next task scheduled in {minutes_for_next_task} minutes. Time to execute: {time_to_execute}")
    schedule.every(minutes_for_next_task).minutes.do(main_task, **kwargs)


if __name__ == "__main__":
    import sys

    main()

    config_file_path = None
    if len(sys.argv) > 1:
        config_file_path = sys.argv[1]
        schedule_next_task(config_path=config_file_path)
    else:
        schedule_next_task()

    while True:
        schedule.run_pending()
        sleep(1)
