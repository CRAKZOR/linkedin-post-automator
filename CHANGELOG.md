# Changelog

## [1.1.0] – 04-13-2025
### Added
- **Updated RSS handling**  
  - First try to parse any URL with *feedparser*; fall back to HTML scraping only if it isn’t a feed.
  - `timeout` on `requests.get` to avoid hangs.
- Guards for malformed or empty feeds (`bozo`, empty `entries`).

### Changed
- `rss_parse()` now
  - chooses an entry with `random.choice()`,  
  - falls back to `description`, `content:encoded`, or `title` when `summary` is missing,  
  - strips HTML with *BeautifulSoup*
- Updated `example_config.json` with larger `scrape_char_limit` value.
- Clean up

### Fixed
- Crash when a feed had zero entries.  
- Crash when `summary` field was absent.

## [1.0.0] – 04-13-2025
### Added
- Inject current datetime into the pre‑amble of every ChatGPT request.
- Added CHANGELOG.md

### Changed
- Default model switched from **`gpt‑4`** to **`gpt‑4o‑mini`**.
- Added `.idea/` to `.gitignore`.

### Compatibility
- Codebase migrated to **openai‑python 1.73.0** (SDK ≥ 1.0).
