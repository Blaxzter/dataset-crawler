"""
Advanced crawling functionality

This package contains sophisticated crawling capabilities:
- Advanced crawler with workflow support
- Workflow builder for programmatic workflow creation
- Complex navigation and data extraction patterns
- Multi-tab and sub-page handling
"""

from .advanced_crawler import AdvancedCrawler, ExtractionResult, NavigationState
from .workflow_builder import WorkflowBuilder

__all__ = [
    'AdvancedCrawler',
    'ExtractionResult', 
    'NavigationState',
    'WorkflowBuilder'
]
