#!/usr/bin/env python3
"""
Interactive Element Selector for Web Crawling

This module provides a visual interface for users to select elements on web pages
for data extraction and pagination. Users can click on elements to define:
- Data extraction fields
- Item containers
- Pagination controls
- Navigation elements for complex workflows

This is the main entry point that uses the modular components:
- browser_manager: Handles browser setup and management
- ui_injector: Manages UI injection and page interaction
- config_manager: Handles configuration saving/loading
- selector_core: Main orchestrator class
- demo: CLI interface and demonstration functionality
"""

import asyncio

# Import shared models to avoid circular dependencies
from models import ElementSelection, WorkflowStep, CrawlerConfiguration

# Import the modular components
from .selector_core import InteractiveSelector
from .demo import (
    interactive_selection_demo,
    run_interactive_demo_with_url,
    validate_existing_config,
)

# Re-export the main classes for backward compatibility
__all__ = [
    "InteractiveSelector",
    "interactive_selection_demo",
    "run_interactive_demo_with_url",
    "validate_existing_config",
    "ElementSelection",
    "WorkflowStep",
    "CrawlerConfiguration",
]

# Main demo function - keeping for backward compatibility
if __name__ == "__main__":
    asyncio.run(interactive_selection_demo())
