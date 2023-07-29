# 🤖 LinkedIn Post Automator

**LinkedIn Post Automator** is a versatile tool designed to either scrape the latest news from designated websites or generate content directly through OpenAI's GPT, crafting compelling LinkedIn post content. This tool ensures fresh and captivating content is produced at regular intervals without the need for manual intervention.

## 📁 Project Structure

### 🚀 Main Component:
- **main.py**: This file serves as the crux of the project. It provides a seamless integration between web scraping, ChatGPT processing, and LinkedIn content generation. Once initiated, it operates in a perpetual loop, relying on an internal scheduler to roll out content based on the user-defined interval.

### 🛠 Configuration:
User-specific settings are housed in the `config.json` file:

- **bio**: Your professional biography.
- **gpt_preamble**: Initial instructions for the ChatGPT model.
- **gpt_token_limit**: The response token limit for GPT.
- **open_ai_api_key**: Your OpenAI API key.
- **cookies**: LinkedIn cookies for authentication.
- **hour_interval**: Interval (in hours) between each post.
- **random_hour_offset**: Max random hour offset added to the interval.
- **random_min_offset**: Max random minute offset added to the interval.
- **scrape_char_limit**: Maximum character limit for web scraping (relevant if "websites" are provided).
- **websites**: An optional array of URLs for news scraping. If not provided, the tool will lean on ChatGPT, for example, to generate daily jokes or insights based on the preamble.

## 🚀 How to Run

1. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
2. Rename `example_config.json` to `config.json`.
3. Populate the `config.json` file with your details and preferences.
4. Start the automation with:
    ```bash
    python main.py
    ```

## ⏰ Internal Scheduling
Equipped with an internal Python scheduler, the tool ensures automated content generation at user-defined intervals, enhanced by random offsets for variability. No external cron configurations are required.

## 🤝 Contributing

Contributions are highly appreciated! If you see potential improvements or wish to introduce new functionalities, please fork the repository and submit your pull requests. Keep your documentation clear and concise.

## 📜 License

This project is under the [MIT License](LICENSE.md).
