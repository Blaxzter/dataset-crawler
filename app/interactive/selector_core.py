#!/usr/bin/env python3
"""
Core Interactive Selector Module

This module contains the main InteractiveSelector class that orchestrates
the browser management, UI injection, and configuration management.
"""

import asyncio
import logging
from typing import List, Optional

# Import shared models to avoid circular dependencies
from models import ElementSelection, WorkflowStep, CrawlerConfiguration

# Import the modular components
from .browser_manager import BrowserManager
from .ui_injector import UIInjector
from .config_manager import ConfigManager


class InteractiveSelector:
    """Main class that orchestrates the interactive element selection process"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser_manager = None
        self.ui_injector = None
        self.config_manager = None
        self.selections: List[ElementSelection] = []
        self.workflows: List[WorkflowStep] = []
        self.current_mode = "selection"  # 'selection', 'workflow'

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        """Async context manager entry"""
        self.browser_manager = BrowserManager(self.headless)
        await self.browser_manager.start()

        # Initialize UI injector and config manager with the page
        page = self.browser_manager.get_page()
        self.ui_injector = UIInjector(page)
        self.config_manager = ConfigManager(page)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser_manager:
            await self.browser_manager.stop()

    async def start_selection_session(self, url: str) -> None:
        """Start an interactive selection session on the given URL"""
        self.logger.info(f"Starting element selection session for: {url}")

        # Navigate to the page first
        await self.browser_manager.navigate_to(url)

        # Wait a bit for page to fully render
        await asyncio.sleep(2)

        # Now inject the UI after page is fully loaded
        await self.ui_injector.inject_modern_ui()

        # Add page navigation detection to auto re-inject UI
        await self.ui_injector.setup_navigation_detection()

        # Wait a moment for UI to render
        await asyncio.sleep(1)

        print(f"\n🎯 Interactive Element Selection Started!")
        print(f"🌐 Navigate to: {url}")
        print("\n📋 Instructions:")
        print("1. Use the selector panel in the top-right corner")
        print("2. Choose mode: Data Field, Items Container, Pagination, or Navigation")
        print("3. Enter a field name (optional)")
        print("4. Click on elements to select them")
        print("5. Selected elements will turn green")
        print("6. In Navigation mode, click links to follow them automatically")
        print("7. Use the Back button (←) to return to previous pages")
        print("8. Click 'Finish & Save' when done")
        print("\n⌨️  Press Enter in terminal when finished selecting...")

        # Wait for user input
        await self._wait_for_user_completion()

    async def _wait_for_user_completion(self):
        """Wait for user to complete element selection"""
        loop = asyncio.get_event_loop()

        def wait_for_input():
            input()
            return True

        await loop.run_in_executor(None, wait_for_input)

    async def get_configuration(self) -> Optional[CrawlerConfiguration]:
        """Extract the configuration created by user selections"""
        return await self.config_manager.extract_configuration()

    async def save_configuration(self, config: CrawlerConfiguration, filename: str):
        """Save configuration to JSON file"""
        await self.config_manager.save_configuration(config, filename)

    async def load_configuration(self, filename: str) -> Optional[CrawlerConfiguration]:
        """Load configuration from JSON file"""
        return await self.config_manager.load_configuration(filename)

    def preview_configuration(self, config: CrawlerConfiguration):
        """Print a human-readable preview of the configuration"""
        self.config_manager.preview_configuration(config)

    def get_configuration_summary(self, config: CrawlerConfiguration) -> dict:
        """Get a summary of the configuration for programmatic use"""
        return self.config_manager.get_configuration_summary(config)

    def validate_configuration(
        self, config: CrawlerConfiguration
    ) -> tuple[bool, List[str]]:
        """Validate configuration and return validation status and issues"""
        return self.config_manager.validate_configuration(config)

    # Legacy methods for backward compatibility
    async def _inject_selector_ui(self):
        """Legacy method - use inject_modern_ui instead"""
        await self.ui_injector.inject_legacy_ui()

    async def _inject_ui_after_load(self):
        """Legacy method - use inject_modern_ui instead"""
        await self.ui_injector.inject_modern_ui()

    async def _setup_navigation_detection(self):
        """Legacy method - now handled by ui_injector"""
        await self.ui_injector.setup_navigation_detection()
