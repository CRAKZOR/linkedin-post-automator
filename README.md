# 🤖 LinkedIn Post Automator

This project is designed to scrape the latest news from designated websites and, with the help of the OpenAI GPT model, generates LinkedIn post content. It's tailored for automation, ensuring that once set in motion, it continually crafts content daily without manual input.

## Project Structure

### Main Components:
- **main.py**: The core of the project. This script orchestrates the activities, coordinating the scraping, processing with ChatGPT, and content preparation for LinkedIn. When triggered, it will persistently loop and has an internal mechanism to generate content daily, at a randomized time slot between 11am-3pm.

### Context Folder:
Found within are pivotal text files critical for content tailoring:
- **bio.txt**: Houses the user's biography, assisting ChatGPT in creating content that resonates with the user's professional backdrop.
- **gpt_preamble.txt**: The initial interaction for ChatGPT, setting the stage and guiding the model before it delves into the bio and the freshly scraped data.
- **websites.json**: An array of web addresses. Each address points to a site which the script will explore for the freshest news.

## How to Run

1. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
2. Customize `bio.txt` to echo your profile, and tweak the roster of websites in `websites.json` as desired.
3. Launch the loop by running `python main.py`. Once up and running, the script will handle the task of daily content genesis on its own.

## Internal Scheduling

The script is powered by an inbuilt Python-based cron utility. This translates to an automated self-scheduling system where, once the script is set in motion, it commits to crafting content daily, choosing a random time between 11am-3pm. There's no need for an external cron setup.

## Contributing

Open arms for contributions! If you stumble upon areas ripe for enhancement or feel the urge to introduce new features, kindly fork the project and present your pull requests. Ensure that your documentation remains crystal clear and succinct for any modifications you introduce.

## License

[MIT License](LICENSE.md)

