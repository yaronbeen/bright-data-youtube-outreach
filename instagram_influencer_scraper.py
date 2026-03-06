#!/usr/bin/env python3
"""Instagram Influencer Contact Scraper via Bright Data.

Workflow: Hashtags CSV -> BD Instagram Posts Dataset -> Extract creator profile URLs
-> BD Instagram Profiles Dataset -> Extract emails -> Output CSV

Usage:
    python instagram_influencer_scraper.py hashtags.csv output_influencers.csv

Requires:
    - Python 3.9+
    - Bright Data API key (set BRIGHT_DATA_API_KEY environment variable)
    - Active Bright Data subscription with Instagram datasets enabled
    - Dataset IDs set through env vars:
        * BD_INSTAGRAM_POSTS_DATASET_ID
        * BD_INSTAGRAM_PROFILES_DATASET_ID
"""

import csv
import json
import os
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_KEY = os.environ.get("BRIGHT_DATA_API_KEY", "")
POSTS_DATASET_ID = os.environ.get("BD_INSTAGRAM_POSTS_DATASET_ID", "")
PROFILES_DATASET_ID = os.environ.get("BD_INSTAGRAM_PROFILES_DATASET_ID", "")

if not API_KEY:
    print("ERROR: Set your Bright Data API key:")
    print("  Windows:  set BRIGHT_DATA_API_KEY=your-api-key-here")
    print("  Mac/Linux: export BRIGHT_DATA_API_KEY=your-api-key-here")
    sys.exit(1)

if not POSTS_DATASET_ID or not PROFILES_DATASET_ID:
    print("ERROR: Set your Bright Data Instagram dataset IDs:")
    print("  export BD_INSTAGRAM_POSTS_DATASET_ID=your-instagram-posts-dataset-id")
    print("  export BD_INSTAGRAM_PROFILES_DATASET_ID=your-instagram-profiles-dataset-id")
    sys.exit(1)

BASE_URL = "https://api.brightdata.com/datasets/v3"
POLL_INTERVAL = 15
POLL_TIMEOUT = 1800

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.IGNORECASE)

DEFAULT_HASHTAGS = [
    ("ai", 60),
    ("fitness", 60),
    ("fashion", 60),
]


def api_request(method, url, data=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data is not None else None
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=180) as resp:
            raw = resp.read().decode()
            if not raw.strip():
                return None
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw.strip()
    except HTTPError as e:
        body_text = e.read().decode() if e.fp else ""
        print(f"  HTTP {e.code}: {body_text[:500]}")
        raise
    except URLError as e:
        print(f"  Network error: {e.reason}")
        raise


def normalize_hashtag(value):
    tag = str(value).strip()
    if not tag:
        return ""
    return tag[1:] if tag.startswith("#") else tag


def read_hashtags_csv(path):
    """Read hashtag rows from CSV.

    Expected format:
        hashtag,num_of_posts
        fitness,60
        #fashion,30
    """
    hashtags = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header and header[0].lower().strip() not in ("hashtag", "tag", "keyword"):
            num = int(header[1]) if len(header) > 1 and header[1].strip().isdigit() else 60
            tag = normalize_hashtag(header[0])
            if tag:
                hashtags.append((tag, num))
        for row in reader:
            if not row or not row[0].strip():
                continue
            tag = normalize_hashtag(row[0])
            if not tag:
                continue
            num = int(row[1]) if len(row) > 1 and row[1].strip().isdigit() else 60
            hashtags.append((tag, num))
    return hashtags


def trigger_collection(dataset_id, inputs, discover_by=None):
    url = f"{BASE_URL}/trigger?dataset_id={dataset_id}&notify=false&include_errors=true"
    if discover_by:
        url += f"&type=discover_new&discover_by={discover_by}"
    payload = {"input": inputs}
    print(f"  Triggering collection with {len(inputs)} input(s)...")
    resp = api_request("POST", url, payload)
    if isinstance(resp, dict) and "snapshot_id" in resp:
        return resp["snapshot_id"]
    if isinstance(resp, str):
        return resp
    raise RuntimeError(f"Unexpected trigger response: {resp}")


def poll_until_ready(snapshot_id):
    url = f"{BASE_URL}/progress/{snapshot_id}"
    start = time.time()
    last_status = None
    while time.time() - start < POLL_TIMEOUT:
        try:
            resp = api_request("GET", url)
        except HTTPError:
            time.sleep(POLL_INTERVAL)
            continue

        status = resp.get("status") if isinstance(resp, dict) else str(resp)
        if status != last_status:
            elapsed = int(time.time() - start)
            print(f"  Status: {status} ({elapsed}s elapsed)")
            last_status = status

        if status == "ready":
            time.sleep(5)
            return
        if status in ("failed", "error", "cancelled"):
            raise RuntimeError(f"Collection failed with status: {status}. Details: {resp}")

        time.sleep(POLL_INTERVAL)

    raise TimeoutError(f"Collection timed out after {POLL_TIMEOUT}s")


def download_snapshot(snapshot_id, retries=3):
    url = f"{BASE_URL}/snapshot/{snapshot_id}?format=json"
    for attempt in range(retries):
        print(f"  Downloading snapshot {snapshot_id} (attempt {attempt + 1}/{retries})...")
        try:
            result = api_request("GET", url)
        except Exception as e:
            print(f"  Download error: {e}")
            if attempt < retries - 1:
                time.sleep(10)
                continue
            raise

        if isinstance(result, dict) and "snapshot_id" in result:
            print("  Data not ready yet, retrying...")
            if attempt < retries - 1:
                time.sleep(15)
                continue
            raise RuntimeError(f"Snapshot data not available after {retries} attempts")

        if isinstance(result, list):
            return result

        print(f"  Unexpected response type: {type(result).__name__}, retrying...")
        if attempt < retries - 1:
            time.sleep(10)
            continue
        return result

    return None


def extract_emails(text):
    if not text:
        return []
    return sorted(set(EMAIL_REGEX.findall(str(text))))


def main():
    input_csv = sys.argv[1] if len(sys.argv) > 1 else None
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "output_influencers.csv"

    if input_csv and os.path.exists(input_csv):
        print(f"[1/9] Reading hashtags from {input_csv}")
        hashtags = read_hashtags_csv(input_csv)
    else:
        print("[1/9] Using default hashtags (no CSV provided)")
        hashtags = DEFAULT_HASHTAGS

    if not hashtags:
        print("No hashtags found. Exiting.")
        return

    print(f"  Hashtags: {[h for h, _ in hashtags]}")

    print("\n[2/9] Triggering Bright Data Instagram posts collection...")
    post_inputs = [{"keyword": f"#{tag}", "num_of_posts": str(num)} for tag, num in hashtags]
    posts_snapshot_id = trigger_collection(POSTS_DATASET_ID, post_inputs, discover_by="keyword")
    print(f"  Snapshot ID: {posts_snapshot_id}")

    print("\n[3/9] Waiting for posts collection to complete (this may take 2-5 minutes)...")
    poll_until_ready(posts_snapshot_id)

    print("\n[4/9] Downloading posts results...")
    posts = download_snapshot(posts_snapshot_id)
    if not posts:
        print("  No posts returned. Exiting.")
        return
    posts = [p for p in posts if isinstance(p, dict)]
    print(f"  Got {len(posts)} post records")

    print("\n[5/9] Deduplicating influencer profiles...")
    influencer_map = {}
    for p in posts:
        profile_url = (
            p.get("owner_profile_link")
            or p.get("owner_profile_url")
            or p.get("profile_url")
            or p.get("user_url")
            or ""
        )
        if not profile_url:
            continue

        hashtag = ""
        if isinstance(p.get("discovery_input"), dict):
            hashtag = normalize_hashtag(p["discovery_input"].get("keyword", ""))
        if not hashtag and isinstance(p.get("input"), dict):
            hashtag = normalize_hashtag(p["input"].get("keyword", ""))

        if profile_url not in influencer_map:
            influencer_map[profile_url] = {
                "username": p.get("owner_username") or p.get("username") or "",
                "followers": p.get("owner_followers") or p.get("followers") or "",
                "hashtags": set(),
            }
        if hashtag:
            influencer_map[profile_url]["hashtags"].add(hashtag)

    print(f"  Found {len(influencer_map)} unique influencer profiles")
    if not influencer_map:
        print("  No influencer profiles found. Exiting.")
        return

    print("\n[6/9] Triggering Bright Data Instagram profiles collection...")
    profile_inputs = [{"url": url} for url in influencer_map.keys()]
    profiles_snapshot_id = trigger_collection(PROFILES_DATASET_ID, profile_inputs)
    print(f"  Snapshot ID: {profiles_snapshot_id}")

    print("\n[7/9] Waiting for profiles collection to complete (this may take 2-5 minutes)...")
    poll_until_ready(profiles_snapshot_id)

    print("  Downloading profile results...")
    profile_results = download_snapshot(profiles_snapshot_id)
    if not profile_results:
        print("  No profile data returned.")
        profile_results = []
    profile_results = [r for r in profile_results if isinstance(r, dict)]
    print(f"  Got {len(profile_results)} profile results")

    profile_data_map = {}
    for profile in profile_results:
        url = profile.get("url", "")
        if url:
            profile_data_map[url.rstrip("/")] = profile
            profile_data_map[url] = profile

    print("\n[8/9] Extracting contact emails from bios and external links...")
    rows = []
    email_count = 0

    for profile_url, info in influencer_map.items():
        normalized = profile_url.rstrip("/")
        profile = profile_data_map.get(normalized, profile_data_map.get(profile_url, {}))

        username = profile.get("username") or profile.get("handle") or info.get("username", "")
        followers = profile.get("followers") or profile.get("followers_count") or info.get("followers", "")
        full_name = profile.get("full_name") or profile.get("name") or ""
        bio = profile.get("bio") or profile.get("biography") or ""

        external_links = profile.get("external_url") or profile.get("external_urls") or profile.get("links") or ""
        if isinstance(external_links, list):
            external_links_str = "; ".join(str(link) for link in external_links)
        else:
            external_links_str = str(external_links)

        all_text = f"{bio} {external_links_str}"
        emails = extract_emails(all_text)
        email_str = "; ".join(emails)
        if emails:
            email_count += len(emails)

        rows.append(
            {
                "hashtag": "; ".join(sorted(info["hashtags"])),
                "profile_url": profile_url,
                "username": username,
                "full_name": full_name,
                "followers": followers,
                "bio": str(bio)[:500],
                "email": email_str,
                "external_links": external_links_str[:500],
            }
        )

    print(f"  Found {email_count} email(s) across {len(rows)} profiles")

    print(f"\n[9/9] Writing output to {output_csv}...")
    fieldnames = [
        "hashtag",
        "profile_url",
        "username",
        "full_name",
        "followers",
        "bio",
        "email",
        "external_links",
    ]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone! {len(rows)} influencers written to {output_csv}")
    print(f"  Profiles with emails: {sum(1 for row in rows if row['email'])}")
    print(f"  Total emails found: {email_count}")


if __name__ == "__main__":
    main()
