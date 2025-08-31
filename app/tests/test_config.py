#!/usr/bin/env python3
"""
Unit tests for config.py

Tests configuration classes and preset configurations.
"""

import pytest
from app.core.config import SiteConfig, PresetConfigs


class TestSiteConfig:
    """Test SiteConfig dataclass"""

    def test_site_config_creation(self):
        """Test creating a SiteConfig with all parameters"""
        selectors = {"items": ".item", "title": ".title", "link": ".link"}

        config = SiteConfig(
            name="Test Site",
            base_url="https://test.com",
            selectors=selectors,
            pagination_selector=".next",
            max_pages=5,
            delay_ms=2000,
        )

        assert config.name == "Test Site"
        assert config.base_url == "https://test.com"
        assert config.selectors == selectors
        assert config.pagination_selector == ".next"
        assert config.max_pages == 5
        assert config.delay_ms == 2000

    def test_site_config_defaults(self):
        """Test SiteConfig with default values"""
        selectors = {"items": ".item"}

        config = SiteConfig(
            name="Test Site", base_url="https://test.com", selectors=selectors
        )

        assert config.pagination_selector is None
        assert config.max_pages is None
        assert config.delay_ms == 1000

    def test_site_config_required_fields(self):
        """Test that required fields are enforced"""
        with pytest.raises(TypeError):
            SiteConfig()  # Missing required fields


class TestPresetConfigs:
    """Test preset configuration methods"""

    def test_hacker_news_jobs_config(self):
        """Test Hacker News Jobs preset configuration"""
        config = PresetConfigs.hacker_news_jobs()

        assert config.name == "Hacker News Jobs"
        assert config.base_url == "https://news.ycombinator.com/jobs"
        assert config.max_pages == 5
        assert config.delay_ms == 2000
        assert config.pagination_selector == 'a[rel="next"]'

        # Check required selectors
        assert "items" in config.selectors
        assert "title" in config.selectors
        assert "company" in config.selectors
        assert "link" in config.selectors

        assert config.selectors["items"] == ".athing"
        assert config.selectors["title"] == ".storylink"
        assert config.selectors["company"] == ".hnuser"
        assert config.selectors["link"] == ".storylink"

    def test_quotes_to_scrape_config(self):
        """Test Quotes to Scrape preset configuration"""
        config = PresetConfigs.quotes_to_scrape()

        assert config.name == "Quotes to Scrape"
        assert config.base_url == "http://quotes.toscrape.com/"
        assert config.max_pages == 10
        assert config.delay_ms == 1000
        assert config.pagination_selector == "li.next a"

        # Check required selectors
        assert "items" in config.selectors
        assert "text" in config.selectors
        assert "author" in config.selectors
        assert "tags" in config.selectors

        assert config.selectors["items"] == ".quote"
        assert config.selectors["text"] == ".text"
        assert config.selectors["author"] == ".author"
        assert config.selectors["tags"] == ".tags a"

    def test_reddit_subreddit_config(self):
        """Test Reddit subreddit preset configuration"""
        subreddit = "python"
        config = PresetConfigs.reddit_subreddit(subreddit)

        assert config.name == f"Reddit - {subreddit}"
        assert config.base_url == f"https://old.reddit.com/r/{subreddit}/"
        assert config.max_pages == 3
        assert config.delay_ms == 2000
        assert config.pagination_selector == ".next-button a"

        # Check required selectors
        expected_selectors = {
            "items": ".thing",
            "title": ".title a.title",
            "author": ".author",
            "score": ".score.unvoted",
            "comments": ".comments",
        }

        for key, value in expected_selectors.items():
            assert key in config.selectors
            assert config.selectors[key] == value

    def test_reddit_subreddit_custom_name(self):
        """Test Reddit configuration with different subreddit names"""
        test_subreddits = ["programming", "MachineLearning", "webdev"]

        for subreddit in test_subreddits:
            config = PresetConfigs.reddit_subreddit(subreddit)
            assert config.name == f"Reddit - {subreddit}"
            assert config.base_url == f"https://old.reddit.com/r/{subreddit}/"

    def test_all_presets_return_site_config(self):
        """Test that all preset methods return SiteConfig instances"""
        configs = [
            PresetConfigs.hacker_news_jobs(),
            PresetConfigs.quotes_to_scrape(),
            PresetConfigs.reddit_subreddit("test"),
        ]

        for config in configs:
            assert isinstance(config, SiteConfig)
            assert hasattr(config, "name")
            assert hasattr(config, "base_url")
            assert hasattr(config, "selectors")
            assert isinstance(config.selectors, dict)
