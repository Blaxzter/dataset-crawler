"""
Interactive Web Crawler System

A comprehensive web crawling framework with both traditional programmatic
crawling and interactive visual element selection capabilities.

## Package Structure

- `core`: Basic crawling functionality and configurations
- `advanced`: Sophisticated workflow-based crawling
- `interactive`: Visual element selection and configuration tools
- `examples`: Usage examples and demonstrations
- `utils`: Utility scripts and helper tools
- `tests`: Comprehensive test suite

## Quick Imports

```python
# Core functionality
from app.core import PaginatedCrawler, CrawlerConfig, PresetConfigs

# Advanced features
from app.advanced import AdvancedCrawler, WorkflowBuilder

# Interactive tools
from app.interactive import InteractiveSelector, WorkflowConfigurator

# Example templates
from app.examples import WorkflowExamples
```
"""

# Convenience imports for easy access to main classes
from .core import PaginatedCrawler, CrawlerConfig, PresetConfigs
from .advanced import AdvancedCrawler, WorkflowBuilder
from .interactive import InteractiveSelector, WorkflowConfigurator
from .models import ElementSelection, WorkflowStep, CrawlerConfiguration

__version__ = "0.1.0"
__author__ = "Interactive Crawler Team"

__all__ = [
    # Core
    "PaginatedCrawler",
    "CrawlerConfig",
    "PresetConfigs",
    # Advanced
    "AdvancedCrawler",
    "WorkflowBuilder",
    # Interactive
    "InteractiveSelector",
    "WorkflowConfigurator",
    "ElementSelection",
    "WorkflowStep",
    "CrawlerConfiguration",
]
