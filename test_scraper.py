#!/usr/bin/env python3
"""Tests for YouTube Channel Scraper.

Unit tests for pure functions + E2E test against live Bright Data API.

Usage:
    python test_scraper.py              # run all tests
    python test_scraper.py TestUnit     # unit tests only
    python test_scraper.py TestE2E      # E2E test only (requires API key)
    pytest -m "not e2e" -v              # pytest: unit tests only
    pytest -v                           # pytest: all tests
"""

import csv
import os
import sys
import tempfile
import unittest

# Set dummy API key BEFORE importing scraper (it does sys.exit(1) at module level if not set)
os.environ.setdefault("BRIGHT_DATA_API_KEY", "test-placeholder-key")

sys.path.insert(0, os.path.dirname(__file__))
import youtube_channel_scraper as scraper


class TestUnit(unittest.TestCase):
    """Unit tests for pure utility functions (no API calls)."""

    # -- extract_emails --------------------------------------------------

    def test_extract_emails_basic(self):
        emails = scraper.extract_emails("contact me at hello@example.org")
        self.assertIn("hello@example.org", emails)

    def test_extract_emails_multiple(self):
        text = "reach out to a@b.com or c@d.co.uk for info"
        emails = scraper.extract_emails(text)
        self.assertGreaterEqual(len(emails), 2)

    def test_extract_emails_empty(self):
        self.assertEqual(scraper.extract_emails(""), [])
        self.assertEqual(scraper.extract_emails(None), [])

    def test_extract_emails_deduplicates(self):
        text = "email me at test@example.com or test@example.com again"
        emails = scraper.extract_emails(text)
        # Should deduplicate
        self.assertEqual(len(emails), 1)
        self.assertIn("test@example.com", emails)

    def test_extract_emails_complex_formats(self):
        text = "contact: john.doe+tag@company.co.uk or support@sub.domain.org"
        emails = scraper.extract_emails(text)
        self.assertGreaterEqual(len(emails), 2)

    # -- read_keywords_csv -----------------------------------------------

    def test_read_keywords_csv_with_header(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write("keyword,num_of_posts\n")
            f.write("ai tools,60\n")
            f.write("cursor vs copilot,30\n")
            path = f.name
        try:
            keywords = scraper.read_keywords_csv(path)
            self.assertEqual(len(keywords), 2)
            self.assertEqual(keywords[0], ("ai tools", 60))
            self.assertEqual(keywords[1], ("cursor vs copilot", 30))
        finally:
            os.unlink(path)

    def test_read_keywords_csv_no_header(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write("raw query,50\n")
            f.write("another query\n")
            path = f.name
        try:
            keywords = scraper.read_keywords_csv(path)
            self.assertEqual(len(keywords), 2)
            self.assertEqual(keywords[0], ("raw query", 50))
            self.assertEqual(keywords[1], ("another query", 60))  # default num_of_posts
        finally:
            os.unlink(path)

    def test_read_keywords_csv_skips_empty_lines(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write("keyword,num_of_posts\n")
            f.write("test query,60\n")
            f.write("\n")
            f.write("another query,45\n")
            f.write("\n")
            path = f.name
        try:
            keywords = scraper.read_keywords_csv(path)
            self.assertEqual(len(keywords), 2)
            self.assertEqual(keywords[0], ("test query", 60))
            self.assertEqual(keywords[1], ("another query", 45))
        finally:
            os.unlink(path)

    def test_read_keywords_csv_default_num_of_posts(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write("keyword\n")
            f.write("just a keyword\n")
            path = f.name
        try:
            keywords = scraper.read_keywords_csv(path)
            self.assertEqual(len(keywords), 1)
            self.assertEqual(keywords[0], ("just a keyword", 60))  # default
        finally:
            os.unlink(path)

    def test_read_keywords_csv_strips_whitespace(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, newline=""
        ) as f:
            f.write("keyword,num_of_posts\n")
            f.write("  spaced keyword  ,  75  \n")
            path = f.name
        try:
            keywords = scraper.read_keywords_csv(path)
            self.assertEqual(len(keywords), 1)
            self.assertEqual(keywords[0], ("spaced keyword", 75))
        finally:
            os.unlink(path)


class TestE2E(unittest.TestCase):
    """End-to-end test against live Bright Data API.

    Requires BRIGHT_DATA_API_KEY environment variable (real key, not placeholder).
    Uses 1 keyword to keep costs low.
    """

    def setUp(self):
        # Skip if API key is not set or is the placeholder
        api_key = os.environ.get("BRIGHT_DATA_API_KEY", "")
        if not api_key or api_key == "test-placeholder-key":
            self.skipTest("BRIGHT_DATA_API_KEY not set (or is placeholder)")
        self.output_csv = tempfile.mktemp(suffix=".csv")
        self.input_csv = tempfile.mktemp(suffix=".csv")
        with open(self.input_csv, "w", newline="") as f:
            f.write("keyword,num_of_posts\n")
            f.write("bright data web scraping,10\n")

    def tearDown(self):
        for path in (self.output_csv, self.input_csv):
            if os.path.exists(path):
                os.unlink(path)

    def test_full_pipeline(self):
        """Run the full scraper pipeline with minimal input."""
        original_argv = sys.argv
        sys.argv = ["youtube_channel_scraper.py", self.input_csv, self.output_csv]
        try:
            scraper.main()
        finally:
            sys.argv = original_argv

        self.assertTrue(
            os.path.exists(self.output_csv),
            f"Output CSV was not created at {self.output_csv}",
        )

        with open(self.output_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        expected_cols = {
            "keyword",
            "channel_url",
            "channel_name",
            "subscribers",
            "description",
            "email",
            "links",
        }
        if rows:
            actual_cols = set(rows[0].keys())
            self.assertEqual(
                actual_cols,
                expected_cols,
                f"CSV columns mismatch.\nExpected: {expected_cols}\nGot: {actual_cols}",
            )

        self.assertGreater(
            len(rows),
            0,
            "No channels found. The API may have returned no results.",
        )

        # Verify data quality
        for row in rows[:5]:
            if row["channel_url"]:
                self.assertIn(
                    "youtube.com",
                    row["channel_url"],
                    f"Channel URL should contain youtube.com: {row['channel_url']}",
                )

        channels_with_emails = sum(1 for r in rows if r["email"])
        print(f"\n  E2E Result: {len(rows)} channels found")
        print(f"  With emails: {channels_with_emails}")
        print(
            f"  Sample: {rows[0]['channel_name']} - {rows[0]['channel_url'][:60] if rows else 'none'}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
