# Instagram Influencer Email Scraper

Find Instagram influencer contact emails at scale using hashtags. Give it hashtags, get back a CSV of profiles with their contact emails.

**Powered by Bright Data Instagram datasets.**

## What It Does

```
Your Hashtags --> Search Instagram Posts --> Find Unique Influencers --> Scrape Profiles --> Extract Emails --> CSV File
```

1. You provide hashtags (like `#fitness`, `#foodblogger`, `#techcreator`)
2. The script searches Instagram posts matching each hashtag
3. It collects unique influencer profile URLs from post owners
4. It scrapes each influencer profile for bio and links
5. It extracts email addresses from bio and external links
6. Everything gets saved to a clean CSV file

## Requirements

- **Python 3.9 or higher**
- **Bright Data account** with API access
- Environment variable: `BRIGHT_DATA_API_KEY`
- Environment variable: `BD_INSTAGRAM_POSTS_DATASET_ID`
- Environment variable: `BD_INSTAGRAM_PROFILES_DATASET_ID`
- No extra libraries needed (uses built-in modules only)

## Setup

### 1) Set API key

**Windows (Command Prompt):**

```bash
set BRIGHT_DATA_API_KEY=your-api-key-here
```

**Windows (PowerShell):**

```powershell
$env:BRIGHT_DATA_API_KEY = "your-api-key-here"
```

**Mac/Linux:**

```bash
export BRIGHT_DATA_API_KEY=your-api-key-here
```

### 2) Set Instagram dataset IDs

```bash
export BD_INSTAGRAM_POSTS_DATASET_ID=your-instagram-posts-dataset-id
export BD_INSTAGRAM_PROFILES_DATASET_ID=your-instagram-profiles-dataset-id
```

### 3) Add your hashtags

Edit `hashtags.csv`:

```csv
hashtag,num_of_posts
#fitness,60
#healthylifestyle,60
#homeworkout,40
```

- `hashtag`: with or without `#`
- `num_of_posts`: number of posts to discover per hashtag (default: 60)

## Run

```bash
python instagram_influencer_scraper.py hashtags.csv output_influencers.csv
```

Or run without args to use defaults:

```bash
python instagram_influencer_scraper.py
```

## Output CSV Columns

| Column           | Description                                 |
| ---------------- | ------------------------------------------- |
| `hashtag`        | Hashtag(s) that discovered the profile      |
| `profile_url`    | Instagram profile URL                       |
| `username`       | Instagram handle                            |
| `full_name`      | Profile name                                |
| `followers`      | Follower count if available                 |
| `bio`            | Profile bio text (trimmed)                  |
| `email`          | Extracted email(s), if found                |
| `external_links` | External links listed on profile (trimmed)  |

## Notes

- Email extraction is regex-based and checks bios + links.
- Not all influencers publish contact emails publicly.
- Results and available fields depend on your Bright Data dataset schema.

## Troubleshooting

| Problem | Solution |
| --- | --- |
| `ERROR: Set your Bright Data API key` | Set `BRIGHT_DATA_API_KEY` |
| `ERROR: Set your Bright Data Instagram dataset IDs` | Set both Instagram dataset env vars |
| `HTTP 401` | Invalid/expired API token |
| `No influencer profiles found` | Try broader hashtags or increase `num_of_posts` |

## License

MIT
