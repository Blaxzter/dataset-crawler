from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class SiteConfig:
    name: str
    base_url: str
    selectors: Dict[str, str]
    pagination_selector: Optional[str] = None
    max_pages: Optional[int] = None
    delay_ms: int = 1000
    
class PresetConfigs:
    @staticmethod
    def hacker_news_jobs():
        return SiteConfig(
            name="Hacker News Jobs",
            base_url="https://news.ycombinator.com/jobs",
            selectors={
                'items': '.athing',
                'title': '.storylink',
                'company': '.hnuser',
                'link': '.storylink',
            },
            pagination_selector='a[rel="next"]',
            max_pages=5,
            delay_ms=2000
        )
    
    @staticmethod
    def quotes_to_scrape():
        return SiteConfig(
            name="Quotes to Scrape",
            base_url="http://quotes.toscrape.com/",
            selectors={
                'items': '.quote',
                'text': '.text',
                'author': '.author',
                'tags': '.tags a',
            },
            pagination_selector='li.next a',
            max_pages=10,
            delay_ms=1000
        )
    
    @staticmethod
    def reddit_subreddit(subreddit: str):
        return SiteConfig(
            name=f"Reddit - {subreddit}",
            base_url=f"https://old.reddit.com/r/{subreddit}/",
            selectors={
                'items': '.thing',
                'title': '.title a.title',
                'author': '.author',
                'score': '.score.unvoted',
                'comments': '.comments',
            },
            pagination_selector='.next-button a',
            max_pages=3,
            delay_ms=2000
        )