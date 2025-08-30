"""
Core crawling functionality

This package contains the fundamental crawling components:
- Configuration classes and presets
- Basic paginated crawler implementation
- Core data structures and utilities
"""

from .config import SiteConfig, PresetConfigs
from .crawler import CrawlerConfig, PaginatedCrawler

__all__ = [
    'SiteConfig',
    'PresetConfigs', 
    'CrawlerConfig',
    'PaginatedCrawler'
]
