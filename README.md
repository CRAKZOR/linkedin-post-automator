# 🤖 LinkedIn Post Automator

Automatically curates and posts daily tech news to LinkedIn. This tool extracts top tech headlines from industry-related sites and then leverages ChatGPT to craft engaging LinkedIn posts.

## Features

- **Web Scraping**: Gathers top tech headlines from specified news sites.
- **Content Curation with ChatGPT**: Converts raw news headlines into LinkedIn-friendly posts tailored to the user's profile.

## Prerequisites

- Python 3.x
- Necessary API key for OpenAI

## Installation

1. Clone this repository:
    ```bash
    git clone [REPO_URL]
    cd [REPO_DIR]
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure your OpenAI API key in `config.py`.

## Usage

1. Modify the list of tech news URLs in the script according to your preference.
2. Execute the script:
    ```bash
    python automator.py
    ```

## Caution

Always ensure you have the appropriate permissions to scrape content from websites. If you integrate a method to post to LinkedIn, always adhere to LinkedIn's terms of service and respect `robots.txt` on all websites you target.

## Contribution

Contributions are welcome! Please read the contributing guidelines and ensure you follow the code of conduct.

## License

[MIT License](LICENSE.md)

