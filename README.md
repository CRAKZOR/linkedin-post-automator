# 🤖 LinkedIn Post Automator

**LinkedIn Post Automator** is a versatile tool designed to generate content using OpenAI's GPT. It crafts compelling LinkedIn post content in response to user prompts and can optionally incorporate scraped data from designated websites. This tool ensures that fresh and captivating content is produced regularly without manual intervention.

## 📁 Project Structure

### 🚀 Main Component:
- **main.py**: This file is the central hub of the project. It seamlessly integrates web scraping, ChatGPT processing, and LinkedIn content generation. Once initiated, it operates in a continuous loop, relying on an internal scheduler to roll out content at user-defined intervals.

### 🛠 Configuration:
User-specific settings are housed in the `config.json` file:

- **bio**: Your professional biography.
- **gpt_preamble**: Initial instructions for the ChatGPT model.
- **gpt_token_limit**: The response token limit for GPT.
- **open_ai_api_key**: Your personal API key to access OpenAI's services.
  - To obtain this:
    - Visit [OpenAI's Platform](https://platform.openai.com/signup).
    - Sign up for an account.
    - Once you are registered and logged in, navigate to the API section to get your API key.

- **cookies**: LinkedIn cookies for authentication.
  - To get your logged-in cookies from the browser:
    - Login to LinkedIn.
    - Right-click on the page and select "Inspect" (or Ctrl+Shift+I).
    - Navigate to the "Application" tab.
    - In the left sidebar, find and expand the "Cookies" section.
    - Copy the relevant cookie values.

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
