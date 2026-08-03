# YouTube Channel Email Scraper

Find YouTube creator emails at scale. Give it keywords, get back a CSV of channels with their contact emails.

**Powered by [Bright Data](https://get.brightdata.com/1tndi4600b25) YouTube datasets.**

## What It Does

```
Your Keywords --> Search YouTube Videos --> Find Unique Channels --> Scrape Channel Pages --> Extract Emails --> CSV File
```

1. You provide search keywords (like "ai tools", "fitness tips", etc.)
2. The script searches YouTube for videos matching those keywords
3. It collects all unique channels from the video results
4. It scrapes each channel's About page for contact info
5. It extracts email addresses using pattern matching
6. Everything gets saved to a clean CSV file

## Example Results

Running with keywords `claude code`, `ai coding assistant`, `cursor vs copilot`:

| Channel            | Subscribers | Email                           | Keyword             |
| ------------------ | ----------- | ------------------------------- | ------------------- |
| Leon van Zyl       | 90,200      | sponsors@leonvanzyl.com         | claude code         |
| Zinho Automates    | 44,300      | business@zinhomedia.com         | claude code         |
| Robin Ebers        | 42,800      | team@robinebers.com             | claude code         |
| Software Scope     | 21,400      | howtotutorialspremium@gmail.com | cursor vs copilot   |
| The West Reviews   | 1,610       | thunderclapmedialab@gmail.com   | cursor vs copilot   |
| Tutorials By David | -           | davidmcnutt04@gmail.com         | ai coding assistant |
| Tobi Teaches       | -           | tobiteaches@gmail.com           | ai coding assistant |
| Nathan Covey       | -           | nathancovey23@gmail.com         | ai coding assistant |

**From 3 keywords: 180 videos found, 131 unique channels, 9 emails extracted.**

## Requirements

- **Python 3.9 or higher** (comes pre-installed on most Macs; [download for Windows](https://www.python.org/downloads/))
- **Bright Data account** with API access ([sign up here](https://get.brightdata.com/1tndi4600b25) - you'll get extra credits when signing up through this link)
- No extra libraries needed - uses only Python built-in modules

## Setup (5 minutes)

### Step 1: Get Your Bright Data API Key

1. Log into [Bright Data](https://get.brightdata.com/1tndi4600b25)
2. Go to **Settings > Account settings**
3. Copy your **API token**

### Step 2: Set Your API Key

**On Windows** (Command Prompt):

```
set BRIGHT_DATA_API_KEY=your-api-key-here
```

**On Windows** (PowerShell):

```
$env:BRIGHT_DATA_API_KEY = "your-api-key-here"
```

**On Mac/Linux** (Terminal):

```
export BRIGHT_DATA_API_KEY=your-api-key-here
```

### Step 3: Prepare Your Keywords

Edit `keywords.csv` with any text editor (Notepad, TextEdit, etc.):

```
keyword,num_of_posts
fitness tips,60
home workout,60
yoga for beginners,30
```

- **keyword**: What to search on YouTube
- **num_of_posts**: How many videos to search per keyword (default: 60)

## How to Run

Open your terminal/command prompt, navigate to this folder, and run:

```
python youtube_channel_scraper.py keywords.csv output_channels.csv
```

Or simply:

```
python youtube_channel_scraper.py
```

This uses the built-in default keywords and saves to `output_channels.csv`.

### What You'll See

```
[1/9] Reading keywords from keywords.csv
  Keywords: ['claude code', 'ai coding assistant', 'cursor vs copilot']

[2/9] Triggering Bright Data Videos collection...
  Triggering collection with 3 input(s)...
  Snapshot ID: sd_mm0pqs8c1d7gb52nb7

[3/9] Waiting for video collection to complete (this may take 2-5 minutes)...
  Status: running (0s elapsed)
  Status: ready (97s elapsed)

[4/9] Downloading video results...
  Got 180 video records

[5/9] Deduplicating channels...
  180 valid video records
  Found 131 unique channels

[6/9] Triggering Bright Data Channels collection...
  Triggering collection with 131 input(s)...

[7/9] Waiting for channel collection to complete (this may take 2-5 minutes)...
  Status: running (0s elapsed)
  Status: ready (142s elapsed)
  Got 131 channel results

[8/9] Extracting emails from channel descriptions...
  Found 9 email(s) across 131 channels

[9/9] Writing output to output_channels.csv...

Done! 131 channels written to output_channels.csv
  Channels with emails: 9
  Total unique emails: 9
```

## Output CSV Format

The output file has these columns:

| Column         | Description                                |
| -------------- | ------------------------------------------ |
| `keyword`      | Which search keyword found this channel    |
| `channel_url`  | Link to the YouTube channel                |
| `channel_name` | Channel display name                       |
| `subscribers`  | Subscriber count                           |
| `description`  | Channel description (first 500 characters) |
| `email`        | Extracted email address(es), if found      |
| `links`        | Links from the channel's About page        |

## How Email Extraction Works

The script scans each channel's **description** and **links** for email patterns using regex:

```
anything@something.domain
```

This catches formats like:

- `business@example.com`
- `contact.us@company.co.uk`
- `name+tag@domain.org`

Not every channel lists an email publicly. Typical results: **5-10% of channels** will have an email in their description.

## Tips

- **More keywords = more channels**: Each keyword searches up to 60 videos, yielding 30-50 unique channels
- **Be specific**: "react tutorial 2024" finds more relevant creators than just "react"
- **Niche keywords work best**: Smaller niches have higher email-in-bio rates
- **Runs take 5-10 minutes**: Most of the time is Bright Data scraping YouTube pages
- **No rate limits to worry about**: Bright Data handles all the scraping infrastructure

## Troubleshooting

| Problem                               | Solution                                                             |
| ------------------------------------- | -------------------------------------------------------------------- |
| `ERROR: Set your Bright Data API key` | You forgot to set the environment variable (see Setup Step 2)        |
| `HTTP 401`                            | Your API key is wrong or expired                                     |
| `HTTP 400`                            | Check that your Bright Data account has the YouTube datasets enabled |
| `Collection timed out`                | Try with fewer keywords or lower `num_of_posts`                      |
| Script hangs at "Triggering..."       | The API call can take 30-60 seconds, this is normal                  |
| `0 channels found`                    | Your keywords might be too niche. Try broader terms                  |

## Cost

This uses Bright Data's **Web Scraper API** with two YouTube datasets:

- **YouTube Videos** dataset: discovers videos by keyword
- **YouTube Channels** dataset: scrapes channel details

Pricing depends on your Bright Data plan. A typical run with 3 keywords costs roughly a few cents.

## Need a custom scraper?

If you need different YouTube channel fields or a discovery flow this tool does not cover, you can build your own with [Bright Data's Scraper Studio](https://brightdata.com/products/scraper-studio). Describe the YouTube data you need in plain English, and Scraper Studio generates a production-ready scraper with your exact output schema. It includes self-healing, so when YouTube changes its channel pages, you describe the fix and ship a patch in minutes instead of rewriting parsers.

## Free tier

Every Bright Data account comes with 5,000 free credits per month (roughly $7.50 in value). Credits reset on the first of each month, and no credit card is required to start. That is enough to search a few keywords, scrape the resulting channels, and evaluate whether this pipeline fits your creator outreach process.

## Disclaimer

Some links in this README are affiliate links. If you sign up for Bright Data through them, you may get extra credits on your account, and I may receive a small commission. This doesn't cost you anything extra - it helps support the project.

## License

MIT
