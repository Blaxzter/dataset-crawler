#!/usr/bin/env python3
"""
Browser Management Module for Interactive Selector

This module handles browser setup, context creation, and anti-detection measures
for the interactive web crawler element selector.
"""

import logging
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext


class BrowserManager:
    """Manages browser instances and contexts for web crawling"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()

    async def start(self):
        """Start the browser and create context"""
        self.playwright = await async_playwright().start()

        # Launch Firefox with anti-detection settings
        self.browser = await self.playwright.firefox.launch(
            headless=self.headless,
            firefox_user_prefs={
                "dom.webdriver.enabled": False,
                "useAutomationExtension": False,
                "general.platform.override": "Win32",
            },
        )

        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        # Create the page
        self.page = await self.context.new_page()

        # Apply anti-detection script
        await self._apply_anti_detection()

        self.logger.info("Browser manager started successfully")

    async def stop(self):
        """Stop the browser and clean up resources"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

        self.logger.info("Browser manager stopped")

    async def _apply_anti_detection(self):
        """Apply anti-detection measures to the page"""
        await self.page.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            """
        )

    def get_page(self) -> Page:
        """Get the current page instance"""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        return self.page

    async def navigate_to(self, url: str):
        """Navigate to a URL and wait for page to load"""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        await self.page.goto(url)
        await self.page.wait_for_load_state("networkidle")
        self.logger.info(f"Navigated to: {url}")
