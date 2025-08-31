import asyncio
import json
import csv
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, Browser
import logging


@dataclass
class CrawlerConfig:
    base_url: str
    selectors: Dict[str, str]
    pagination_selector: Optional[str] = None
    max_pages: Optional[int] = None
    delay_ms: int = 1000
    headless: bool = False
    output_format: str = "json"  # json, csv
    output_file: str = "crawled_data"


class PaginatedCrawler:
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.data: List[Dict[str, Any]] = []
        self.current_page = 1
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.headless
        )
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def extract_data_from_page(self) -> List[Dict[str, Any]]:
        page_data = []

        # Get the items selector (should be a string, not a list)
        item_selector = self.config.selectors.get("items")
        if not item_selector:
            self.logger.warning("No 'items' selector found in config")
            return page_data

        items = await self.page.query_selector_all(item_selector)

        for item in items:
            item_data = {}

            for field_name, field_selector in self.config.selectors.items():
                if field_name == "items":
                    continue

                try:
                    element = await item.query_selector(field_selector)
                    if element:
                        item_data[field_name] = await element.text_content()
                    else:
                        item_data[field_name] = None
                except Exception as e:
                    self.logger.warning(f"Error extracting {field_name}: {e}")
                    item_data[field_name] = None

            if item_data:
                page_data.append(item_data)

        return page_data

    async def _is_element_clickable(self, element) -> bool:
        """
        Comprehensive check to determine if an element is clickable.
        Checks for various disabled states and visibility issues.
        """
        try:
            # Check disabled attribute
            is_disabled = await element.get_attribute("disabled")
            if is_disabled is not None:
                self.logger.info(f"Element is disabled (disabled attribute)")
                return False

            # Check aria-disabled
            aria_disabled = await element.get_attribute("aria-disabled")
            if aria_disabled == "true":
                self.logger.info(f"Element is disabled (aria-disabled)")
                return False

            # Check class name for disabled indicators
            class_name = await element.get_attribute("class") or ""
            disabled_classes = [
                "disabled",
                "btn-disabled",
                "inactive",
                "not-clickable",
                "btn-inactive",
            ]
            if any(
                disabled_class in class_name.lower()
                for disabled_class in disabled_classes
            ):
                self.logger.info(f"Element has disabled class: {class_name}")
                return False

            # Check if element is visible and has dimensions
            is_visible = await element.is_visible()
            if not is_visible:
                self.logger.info(f"Element is not visible")
                return False

            # Check computed styles for pointer-events and opacity
            pointer_events = await element.evaluate(
                "el => getComputedStyle(el).pointerEvents"
            )
            opacity = await element.evaluate("el => getComputedStyle(el).opacity")

            if pointer_events == "none":
                self.logger.info(f"Element has pointer-events: none")
                return False

            if float(opacity) < 0.1:
                self.logger.info(f"Element has very low opacity: {opacity}")
                return False

            return True

        except Exception as e:
            self.logger.warning(f"Error checking element clickability: {e}")
            return False

    async def navigate_to_next_page(self) -> bool:
        if not self.config.pagination_selector:
            return False

        try:
            # Find all elements matching the pagination selector
            pagination_elements = await self.page.query_selector_all(
                self.config.pagination_selector
            )
            if not pagination_elements:
                return False

            selected_element = None

            # Check if config has original content for verification
            if (
                hasattr(self.config, "pagination_original_content")
                and self.config.pagination_original_content
            ):
                original_content = (
                    self.config.pagination_original_content.strip().lower()
                )
                self.logger.info(
                    f"Looking for pagination element containing: '{original_content}'"
                )

                for element in pagination_elements:
                    element_text = await element.text_content()
                    if element_text:
                        element_text = element_text.strip().lower()

                        # Check if element contains the original content
                        if (
                            original_content in element_text
                            or element_text in original_content
                            or element_text == original_content
                        ):
                            selected_element = element
                            self.logger.info(
                                f"Found matching pagination element with content: '{element_text}'"
                            )
                            break

                # If no content match found, use first element as fallback
                if not selected_element and pagination_elements:
                    self.logger.warning(
                        f"No pagination element found with content matching '{original_content}', using first available"
                    )
                    selected_element = pagination_elements[0]
            else:
                # No original content specified, use first element
                selected_element = pagination_elements[0]

            if not selected_element:
                return False

            # Comprehensive check if element is clickable
            if not await self._is_element_clickable(selected_element):
                return False

            # Log what we're about to click
            element_text = await selected_element.text_content()
            element_text_clean = element_text.strip() if element_text else ""
            self.logger.info(f"Clicking pagination element: '{element_text_clean}'")
            await selected_element.click()
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(self.config.delay_ms / 1000)

            self.current_page += 1
            return True

        except Exception as e:
            self.logger.error(f"Error navigating to next page: {e}")
            return False

    async def crawl(
        self, custom_extractor: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        self.logger.info(f"Starting crawl of {self.config.base_url}")

        await self.page.goto(self.config.base_url)
        await self.page.wait_for_load_state("networkidle")

        while True:
            self.logger.info(f"Crawling page {self.current_page}")

            if custom_extractor:
                page_data = await custom_extractor(self.page)
            else:
                page_data = await self.extract_data_from_page()

            self.data.extend(page_data)
            self.logger.info(
                f"Extracted {len(page_data)} items from page {self.current_page}"
            )

            if self.config.max_pages and self.current_page >= self.config.max_pages:
                self.logger.info(f"Reached max pages limit: {self.config.max_pages}")
                break

            if not await self.navigate_to_next_page():
                self.logger.info("No more pages to crawl")
                break

        self.logger.info(f"Crawling completed. Total items: {len(self.data)}")
        return self.data

    def save_data(self, filename: Optional[str] = None):
        if not self.data:
            self.logger.warning("No data to save")
            return

        filename = filename or f"{self.config.output_file}.{self.config.output_format}"

        if self.config.output_format.lower() == "json":
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        elif self.config.output_format.lower() == "csv":
            if self.data:
                fieldnames = list(self.data[0].keys())
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.data)

        self.logger.info(f"Data saved to {filename}")

    def get_data(self) -> List[Dict[str, Any]]:
        return self.data
