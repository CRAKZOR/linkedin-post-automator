# 🤖 LinkedIn Post Automator

**LinkedIn Post Automator** is a powerful tool that scrapes the latest news from designated websites and utilizes the capabilities of the OpenAI GPT model to craft compelling LinkedIn post content. Designed with automation at its core, this tool ensures that fresh and engaging content is produced daily without the need for manual intervention.

## 📁 Project Structure

### 🚀 Main Component:
- **main.py**: This is the engine room of the project. It seamlessly integrates web scraping, ChatGPT processing, and content crafting for LinkedIn. Once initiated, it operates in a continuous loop, employing an internal mechanism to roll out content daily during a randomly chosen slot between 11am-3pm.

### 🛠 Configuration:
All settings and user-specific information are now housed in `config.json`. This file captures:

- **bio**: Your professional biography.
- **gpt_preamble**: Initial guidance for the ChatGPT model.
- **gpt_token_limit**: The token limit for the GPT response.
- **scrape_char_limit**: Character limit for web scraping.
- **open_ai_api_key**: Your OpenAI API key.
- **cookies**: Your LinkedIn cookies for authentication.
- **websites**: An array of URLs you want to target for scraping news.

## 🚀 How to Run

1. Install the necessary Python packages:
    ```bash
    pip install -r requirements.txt
    ```

2. Update the `config.json` file with your details and desired settings.

3. Kick off the automation with:
    ```bash
    python main.py
    ```
   Once launched, the script will independently handle the daily content generation task.

## ⏰ TODO: Internal Scheduling

The tool comes with an embedded Python cron utility, ensuring a self-regulated scheduling mechanism. Once set in motion, it's committed to churning out content every day, selecting a random window between 11am-3pm. External cron configurations are unnecessary.

## 🤝 Contributing

We welcome and appreciate contributions! If you identify potential improvements or wish to introduce new functionalities, kindly fork the repository and submit your pull requests. Ensure your documentation remains clear and concise for any changes you suggest.

## 📜 License

This project falls under the [MIT License](LICENSE.md).
