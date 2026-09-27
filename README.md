# YouTube Channel Research and Contact Lookup

Starting with search topics, this Python script finds matching YouTube videos, collects the unique channels represented in those results, fetches channel details, and writes one CSV row per channel. It can surface public channel descriptions, links, subscriber figures, and email-like strings for a marketer's manual research. It is useful for turning a topic-based discovery pass into a channel shortlist, but it does not assess sponsorship fit, verify contact details, or predict a creator's response.

## The useful outcome

Use it to build an initial set of channels around a specific topic, then review their videos and channel pages yourself before deciding whether to approach any creator.

Illustrative input and possible output (synthetic values):

```csv
keyword,num_of_posts
sample project management tutorial,25
sample project management review,25
```

The tool searches videos for each keyword, deduplicates their channel URLs, fetches channel data, then matches email-like strings in returned descriptions and links. The result lets a marketer filter the channel list by topic association and manually inspect a possible contact path. Being returned for a search term does not establish audience fit, sponsorship interest, or permission to email.

## What it does and does not do

- Takes search keywords and an optional number of videos per keyword.
- Uses Bright Data's YouTube Videos dataset, then its YouTube Channels dataset for channel details.
- Deduplicates by channel URL and retains the keyword(s) that surfaced each channel.
- Extracts email-like strings from the returned channel description and links.
- Does not analyze video content, qualify creators, verify email addresses, estimate reply rates, or send outreach.

## Start here

Requirements: Python 3.9+, internet access, and a Bright Data API token/account enabled for both YouTube Videos and YouTube Channels datasets. Python's standard library is sufficient. The script reads `BRIGHT_DATA_API_KEY` from the process environment; it does not load `.env` files.

Linux/macOS:

```bash
export BRIGHT_DATA_API_KEY="your-key"
python3 youtube_channel_scraper.py keywords.csv output_channels.csv
```

PowerShell:

```powershell
$env:BRIGHT_DATA_API_KEY = "your-key"
python youtube_channel_scraper.py keywords.csv output_channels.csv
```

Example CSV:

```csv
keyword,num_of_posts
sample project management tutorial,25
sample project management review,25
```

`num_of_posts` controls the video search request for that keyword; if omitted or not a number, the script uses 60. With no input path, it uses its built-in example keywords and writes `output_channels.csv`. Use an existing CSV for your own search.

## Output

The CSV columns are `keyword`, `channel_url`, `channel_name`, `subscribers`, `description` (up to 500 characters), `email`, and `links` (up to 500 characters). The `keyword` field can contain multiple semicolon-separated terms. Fields depend on the dataset response and may be blank. Email strings are pattern matches, not verified mailboxes.

## Cost and responsible use

One run makes a live collection for the video searches and another for the channels found. Bright Data pricing, credits, dataset access, and returned records depend on your account and current service terms. Review [current Web Scraper pricing](https://brightdata.com/pricing/web-scraper) and billing before running; no fixed run cost or number of channels is guaranteed. Use public data responsibly, follow platform terms and applicable privacy/marketing laws, and respect contact preferences and retention requirements.

## Optional email sending

The optional `apps_script.gs` file is a separate Google Sheets/Gmail workflow. The scraper does not automatically send anything. The sheet tab defaults to `Sheet1`; expected columns A-F are `channel_name`, `email`, `subscribers`, `subject`, `body`, and `status`. Review and personalize every message, verify the contact route, and send a test email to yourself before using any send action. Built-in pauses and batch controls do not guarantee compliance or inbox placement.

## Tests

Install pytest and run the local tests:

```bash
python3 -m pip install pytest
python3 test_scraper.py TestUnit
```

The full suite includes live tests and requires Bright Data access; running it may incur usage charges:

```bash
export BRIGHT_DATA_API_KEY="your-key"
python3 test_scraper.py TestE2E
```

## FAQ

**Does this search videos or channels directly?** It searches videos by keyword first, then fetches channel data for the unique channels found in those video results.

**Does a channel returned for a keyword mean it's relevant?** Only that it appeared in the returned search results. Review the channel and its content against your brief.

**Are emails verified?** No. The script looks for email patterns in returned channel text and links.

**Can it find every channel in a niche?** No completeness guarantee is made. Search results and dataset availability can vary.

**Does it send emails?** No. Sending is a separate, optional Apps Script that must be configured and run by you.

## License

MIT
