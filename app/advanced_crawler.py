#!/usr/bin/env python3
"""
Advanced Web Crawler with Workflow Support

This module extends the basic crawler to support complex extraction workflows
including sub-page navigation, multi-tab handling, and sophisticated data extraction patterns.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from interactive_selector import CrawlerConfiguration, ElementSelection, WorkflowStep

@dataclass 
class ExtractionResult:
    data: Dict[str, Any]
    source_url: str
    extraction_time: str
    workflow_path: List[str]

@dataclass
class NavigationState:
    current_url: str
    page_number: int
    workflow_step: int
    context: Dict[str, Any]

class AdvancedCrawler:
    def __init__(self, config: CrawlerConfiguration, headless: bool = True):
        self.config = config
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.main_page: Optional[Page] = None
        self.data: List[ExtractionResult] = []
        self.navigation_history: List[NavigationState] = []
        self.visited_urls: Set[str] = set()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.firefox.launch(
            headless=self.headless,
            firefox_user_prefs={
                "dom.webdriver.enabled": False,
                "useAutomationExtension": False
            }
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
        )
        self.main_page = await self.context.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def crawl_with_workflows(self) -> List[ExtractionResult]:
        """Main crawling method that handles workflows and pagination"""
        self.logger.info(f"Starting advanced crawl of {self.config.base_url}")
        
        await self.main_page.goto(self.config.base_url)
        await self.main_page.wait_for_load_state('networkidle')
        
        page_number = 1
        
        while True:
            self.logger.info(f"Processing page {page_number}")
            
            # Save current navigation state
            current_state = NavigationState(
                current_url=self.main_page.url,
                page_number=page_number,
                workflow_step=0,
                context={}
            )
            self.navigation_history.append(current_state)
            
            # Extract data from current page
            page_results = await self._extract_page_data()
            self.data.extend(page_results)
            
            self.logger.info(f"Extracted {len(page_results)} items from page {page_number}")
            
            # Check if we should continue pagination
            if self.config.max_pages and page_number >= self.config.max_pages:
                self.logger.info(f"Reached max pages limit: {self.config.max_pages}")
                break
                
            if not await self._navigate_to_next_page():
                self.logger.info("No more pages to crawl")
                break
                
            page_number += 1
            
        self.logger.info(f"Crawling completed. Total items: {len(self.data)}")
        return self.data

    async def _extract_page_data(self) -> List[ExtractionResult]:
        """Extract data from current page using configured selectors and workflows"""
        page_results = []
        
        # Find items container
        items_selector = self._get_items_selector()
        if not items_selector:
            self.logger.warning("No items selector configured")
            return page_results
        
        # Get initial count of items
        items = await self.main_page.query_selector_all(items_selector.selector)
        total_items = len(items)
        self.logger.info(f"Found {total_items} items to process")
        
        # Process each item by index to avoid stale element handles
        for i in range(total_items):
            self.logger.debug(f"Processing item {i + 1}/{total_items}")
            
            # Re-query items to get fresh element handles (important after navigation)
            current_items = await self.main_page.query_selector_all(items_selector.selector)
            
            # Check if we still have enough items (in case page changed)
            if i >= len(current_items):
                self.logger.warning(f"Item {i + 1} no longer exists, stopping")
                break
            
            item = current_items[i]
            
            # Extract basic data from item
            item_data = await self._extract_item_data(item)
            
            # Execute workflows if configured
            if self.config.workflows:
                workflow_data = await self._execute_workflows_by_index(i, item_data)
                if workflow_data:
                    item_data.update(workflow_data)
            
            result = ExtractionResult(
                data=item_data,
                source_url=self.main_page.url,
                extraction_time=self._get_timestamp(),
                workflow_path=[]
            )
            
            page_results.append(result)
            
        return page_results

    async def _extract_item_data(self, item_element) -> Dict[str, Any]:
        """Extract data from a single item using configured selectors"""
        item_data = {}
        current_url = self.main_page.url
        
        for selection in self.config.selections:
            if selection.element_type != 'data_field':
                continue
            
            # Skip fields that belong to other pages (workflow-only fields)
            # These will be extracted during workflow execution
            field_page_url = getattr(selection, 'page_url', None)
            if field_page_url:
                # Check if this field belongs to a different page path
                # We need to exclude fields that belong to detail pages when we're on listing pages
                belongs_to_current = self._is_field_for_current_page(field_page_url, current_url)
                if not belongs_to_current:
                    self.logger.debug(f"Skipping {selection.name} - belongs to different page: {field_page_url}")
                    continue
                
            try:
                element = await item_element.query_selector(selection.selector)
                if element:
                    value = await self._extract_element_value(element, selection)
                    item_data[selection.name] = value
                else:
                    item_data[selection.name] = None
                    
            except Exception as e:
                self.logger.warning(f"Error extracting {selection.name}: {e}")
                item_data[selection.name] = None
        
        return item_data

    async def _extract_element_value(self, element, selection: ElementSelection) -> Any:
        """Extract value from element based on extraction type"""
        if selection.extraction_type == 'text':
            return await element.text_content()
        elif selection.extraction_type == 'href':
            return await element.get_attribute('href')
        elif selection.extraction_type == 'src':
            return await element.get_attribute('src')
        elif selection.extraction_type == 'attribute' and selection.attribute_name:
            return await element.get_attribute(selection.attribute_name)
        else:
            return await element.text_content()

    async def _execute_workflows(self, item_element, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps for deeper data extraction"""
        workflow_data = {}
        
        for workflow in self.config.workflows:
            try:
                result = await self._execute_workflow_step(item_element, workflow, base_data)
                if result:
                    workflow_data.update(result)
            except Exception as e:
                self.logger.error(f"Error executing workflow {workflow.step_id}: {e}")
        
        return workflow_data

    async def _execute_workflows_by_index(self, item_index: int, base_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps using fresh element queries to avoid staleness"""
        workflow_data = {}
        
        # Get items selector for fresh queries
        items_selector = self._get_items_selector()
        if not items_selector:
            self.logger.warning("No items selector configured for workflow execution")
            return workflow_data
        
        for workflow in self.config.workflows:
            try:
                result = await self._execute_workflow_step_by_index(item_index, workflow, base_data)
                if result:
                    workflow_data.update(result)
            except Exception as e:
                self.logger.error(f"Error executing workflow {workflow.step_id}: {e}")
        
        return workflow_data

    async def _execute_workflow_step_by_index(self, item_index: int, workflow: WorkflowStep, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a single workflow step using index-based selectors to avoid staleness"""
        
        if workflow.action == 'click':
            return await self._handle_click_workflow_by_index(item_index, workflow, context)
        elif workflow.action == 'extract':
            return await self._handle_extract_workflow_by_index(item_index, workflow)
        elif workflow.action == 'open_new_tab':
            return await self._handle_new_tab_workflow_by_index(item_index, workflow, context)
        else:
            self.logger.warning(f"Unknown workflow action: {workflow.action}")
            return None

    async def _execute_workflow_step(self, item_element, workflow: WorkflowStep, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a single workflow step"""
        
        if workflow.action == 'click':
            return await self._handle_click_workflow(item_element, workflow, context)
        elif workflow.action == 'extract':
            return await self._handle_extract_workflow(item_element, workflow)
        elif workflow.action == 'open_new_tab':
            return await self._handle_new_tab_workflow(item_element, workflow, context)
        else:
            self.logger.warning(f"Unknown workflow action: {workflow.action}")
            return None

    async def _handle_click_workflow_by_index(self, item_index: int, workflow: WorkflowStep, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle click workflow using index-based selectors to avoid staleness"""
        
        # Get items selector to build nth-child selector
        items_selector = self._get_items_selector()
        if not items_selector:
            return None
        
        # Build selector that targets the nth item directly
        nth_item_selector = f"({items_selector.selector}):nth-of-type({item_index + 1})"
        full_clickable_selector = f"{nth_item_selector} {workflow.target_selector}"
        
        try:
            # Find the clickable element using the complete selector
            clickable = await self.main_page.query_selector(full_clickable_selector)
            if not clickable:
                self.logger.warning(f"Clickable element not found with selector: {full_clickable_selector}")
                return None
            
            # Check if the element is actually clickable
            if not await self._is_element_clickable(clickable):
                self.logger.warning(f"Element is not clickable: {full_clickable_selector}")
                return None
            
            # Store current URL for navigation back
            original_url = self.main_page.url
            
            try:
                # Click the element and wait for navigation
                self.logger.info(f"Clicking element for item {item_index + 1}")
                await clickable.click()
                
                if workflow.wait_condition == 'selector' and workflow.wait_selector:
                    await self.main_page.wait_for_selector(workflow.wait_selector, timeout=10000)
                else:
                    await self.main_page.wait_for_load_state(workflow.wait_condition, timeout=10000)
                
                # Add small delay to ensure page is fully loaded
                await asyncio.sleep(0.5)
                
                # Extract data from the new page if fields are specified
                extracted_data = {}
                if workflow.extract_fields:
                    for field_name in workflow.extract_fields:
                        try:
                            # Find corresponding selection config
                            selection = self._find_selection_by_name(field_name)
                            if selection:
                                # Use fresh query on the main page (not stale item_element)
                                element = await self.main_page.query_selector(selection.selector)
                                if element:
                                    value = await self._extract_element_value(element, selection)
                                    extracted_data[field_name] = value
                                    self.logger.debug(f"Successfully extracted {field_name}: {value}")
                                else:
                                    extracted_data[field_name] = None
                                    self.logger.debug(f"Element not found for {field_name}")
                            else:
                                self.logger.warning(f"Selection config not found for field: {field_name}")
                        except Exception as field_error:
                            self.logger.warning(f"Error extracting workflow field {field_name}: {field_error}")
                            extracted_data[field_name] = None
                
                # Navigate back to original page
                await self.main_page.goto(original_url)
                await self.main_page.wait_for_load_state('networkidle', timeout=10000)
                
                return extracted_data
                
            except Exception as e:
                self.logger.error(f"Error in click workflow navigation: {e}")
                # Try to navigate back even if extraction failed
                try:
                    await self.main_page.goto(original_url)
                    await self.main_page.wait_for_load_state('networkidle', timeout=10000)
                except Exception as nav_error:
                    self.logger.error(f"Failed to navigate back: {nav_error}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in click workflow setup: {e}")
            return None

    async def _handle_extract_workflow_by_index(self, item_index: int, workflow: WorkflowStep) -> Optional[Dict[str, Any]]:
        """Handle extract workflow using index-based selectors"""
        # Get items selector to build nth-child selector
        items_selector = self._get_items_selector()
        if not items_selector:
            return None
        
        # Build selector that targets the nth item directly
        nth_item_selector = f"({items_selector.selector}):nth-of-type({item_index + 1})"
        
        extracted_data = {}
        if workflow.extract_fields:
            for field_name in workflow.extract_fields:
                try:
                    selection = self._find_selection_by_name(field_name)
                    if selection:
                        # Build full selector for this field within the nth item
                        full_selector = f"{nth_item_selector} {selection.selector}"
                        element = await self.main_page.query_selector(full_selector)
                        if element:
                            value = await self._extract_element_value(element, selection)
                            extracted_data[field_name] = value
                        else:
                            extracted_data[field_name] = None
                except Exception as field_error:
                    self.logger.warning(f"Error extracting field {field_name}: {field_error}")
                    extracted_data[field_name] = None
        
        return extracted_data

    async def _handle_new_tab_workflow_by_index(self, item_index: int, workflow: WorkflowStep, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle new tab workflow using index-based selectors"""
        # Get items selector to build nth-child selector
        items_selector = self._get_items_selector()
        if not items_selector:
            return None
        
        # Build selector that targets the nth item's link directly
        nth_item_selector = f"({items_selector.selector}):nth-of-type({item_index + 1})"
        full_link_selector = f"{nth_item_selector} {workflow.target_selector}"
        
        try:
            # Find the link element
            link_element = await self.main_page.query_selector(full_link_selector)
            if not link_element:
                self.logger.warning(f"Link element not found: {full_link_selector}")
                return None
            
            # Get the URL to open
            href = await link_element.get_attribute('href')
            if not href:
                self.logger.warning(f"No href attribute found on link element")
                return None
            
            # Handle relative URLs
            if href.startswith('/'):
                base_url = self.main_page.url
                if base_url.endswith('/'):
                    href = base_url + href[1:]
                else:
                    href = base_url + href
            
            # Open new page in same context
            new_page = await self.context.new_page()
            
            try:
                await new_page.goto(href, timeout=10000)
                await new_page.wait_for_load_state('networkidle', timeout=10000)
                
                # Add small delay to ensure page is fully loaded
                await asyncio.sleep(0.5)
                
                # Extract data from new page
                extracted_data = {}
                if workflow.extract_fields:
                    for field_name in workflow.extract_fields:
                        try:
                            selection = self._find_selection_by_name(field_name)
                            if selection:
                                element = await new_page.query_selector(selection.selector)
                                if element:
                                    value = await self._extract_element_value(element, selection)
                                    extracted_data[field_name] = value
                                else:
                                    extracted_data[field_name] = None
                        except Exception as field_error:
                            self.logger.warning(f"Error extracting field {field_name} in new tab: {field_error}")
                            extracted_data[field_name] = None
                
                return extracted_data
                
            except Exception as e:
                self.logger.error(f"Error in new tab workflow: {e}")
                return None
            finally:
                await new_page.close()
                
        except Exception as e:
            self.logger.error(f"Error setting up new tab workflow: {e}")
            return None

    async def _handle_click_workflow(self, item_element, workflow: WorkflowStep, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle workflow that involves clicking and navigating to sub-pages"""
        try:
            # Find the clickable element within the item
            clickable = await item_element.query_selector(workflow.target_selector)
            if not clickable:
                self.logger.warning(f"Clickable element not found: {workflow.target_selector}")
                return None
            
            # Check if the element is actually clickable
            if not await self._is_element_clickable(clickable):
                self.logger.warning(f"Element is not clickable: {workflow.target_selector}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error finding clickable element {workflow.target_selector}: {e}")
            return None
        
        # Store current URL for navigation back
        original_url = self.main_page.url
        
        try:
            # Click the element and wait for navigation
            await clickable.click()
            
            if workflow.wait_condition == 'selector' and workflow.wait_selector:
                await self.main_page.wait_for_selector(workflow.wait_selector, timeout=10000)
            else:
                await self.main_page.wait_for_load_state(workflow.wait_condition, timeout=10000)
            
            # Add small delay to ensure page is fully loaded
            await asyncio.sleep(0.5)
            
            # Extract data from the new page if fields are specified
            extracted_data = {}
            if workflow.extract_fields:
                for field_name in workflow.extract_fields:
                    try:
                        # Find corresponding selection config
                        selection = self._find_selection_by_name(field_name)
                        if selection:
                            # Use fresh query on the main page (not stale item_element)
                            element = await self.main_page.query_selector(selection.selector)
                            if element:
                                value = await self._extract_element_value(element, selection)
                                extracted_data[field_name] = value
                                self.logger.debug(f"Successfully extracted {field_name}: {value}")
                            else:
                                extracted_data[field_name] = None
                                self.logger.debug(f"Element not found for {field_name}")
                        else:
                            self.logger.warning(f"Selection config not found for field: {field_name}")
                    except Exception as field_error:
                        self.logger.warning(f"Error extracting workflow field {field_name}: {field_error}")
                        extracted_data[field_name] = None
            
            # Navigate back to original page
            await self.main_page.goto(original_url)
            await self.main_page.wait_for_load_state('networkidle', timeout=10000)
            
            return extracted_data
            
        except Exception as e:
            self.logger.error(f"Error in click workflow: {e}")
            # Try to navigate back even if extraction failed
            try:
                await self.main_page.goto(original_url)
                await self.main_page.wait_for_load_state('networkidle', timeout=10000)
            except Exception as nav_error:
                self.logger.error(f"Failed to navigate back: {nav_error}")
            return None

    async def _handle_new_tab_workflow(self, item_element, workflow: WorkflowStep, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle workflow that opens links in new tabs"""
        try:
            # Find the link element
            link_element = await item_element.query_selector(workflow.target_selector)
            if not link_element:
                self.logger.warning(f"Link element not found: {workflow.target_selector}")
                return None
            
            # Get the URL to open
            href = await link_element.get_attribute('href')
            if not href:
                self.logger.warning(f"No href attribute found on link element")
                return None
            
            # Handle relative URLs
            if href.startswith('/'):
                base_url = self.main_page.url
                if base_url.endswith('/'):
                    href = base_url + href[1:]
                else:
                    href = base_url + href
            
            # Open new page in same context
            new_page = await self.context.new_page()
            
            try:
                await new_page.goto(href, timeout=10000)
                await new_page.wait_for_load_state('networkidle', timeout=10000)
                
                # Add small delay to ensure page is fully loaded
                await asyncio.sleep(0.5)
                
                # Extract data from new page
                extracted_data = {}
                if workflow.extract_fields:
                    for field_name in workflow.extract_fields:
                        try:
                            selection = self._find_selection_by_name(field_name)
                            if selection:
                                element = await new_page.query_selector(selection.selector)
                                if element:
                                    value = await self._extract_element_value(element, selection)
                                    extracted_data[field_name] = value
                                    self.logger.debug(f"Successfully extracted {field_name} from new tab: {value}")
                                else:
                                    extracted_data[field_name] = None
                                    self.logger.debug(f"Element not found for {field_name} in new tab")
                            else:
                                self.logger.warning(f"Selection config not found for field: {field_name}")
                        except Exception as field_error:
                            self.logger.warning(f"Error extracting field {field_name} in new tab: {field_error}")
                            extracted_data[field_name] = None
                
                return extracted_data
                
            except Exception as e:
                self.logger.error(f"Error in new tab workflow: {e}")
                return None
            finally:
                await new_page.close()
                
        except Exception as e:
            self.logger.error(f"Error setting up new tab workflow: {e}")
            return None

    async def _handle_extract_workflow(self, item_element, workflow: WorkflowStep) -> Optional[Dict[str, Any]]:
        """Handle workflow that only extracts data without navigation"""
        extracted_data = {}
        
        if workflow.extract_fields:
            for field_name in workflow.extract_fields:
                try:
                    selection = self._find_selection_by_name(field_name)
                    if selection:
                        element = await item_element.query_selector(selection.selector)
                        if element:
                            value = await self._extract_element_value(element, selection)
                            extracted_data[field_name] = value
                            self.logger.debug(f"Successfully extracted {field_name}: {value}")
                        else:
                            extracted_data[field_name] = None
                            self.logger.debug(f"Element not found for {field_name}")
                    else:
                        self.logger.warning(f"Selection config not found for field: {field_name}")
                except Exception as field_error:
                    self.logger.warning(f"Error extracting field {field_name}: {field_error}")
                    extracted_data[field_name] = None
        
        return extracted_data

    def _find_selection_by_name(self, name: str) -> Optional[ElementSelection]:
        """Find a selection configuration by name"""
        for selection in self.config.selections:
            if selection.name == name:
                return selection
        return None

    def _get_items_selector(self) -> Optional[ElementSelection]:
        """Get the items container selector"""
        for selection in self.config.selections:
            if selection.element_type == 'items_container':
                return selection
        return None

    async def _is_element_clickable(self, element) -> bool:
        """
        Comprehensive check to determine if an element is clickable.
        Checks for various disabled states and visibility issues.
        """
        try:
            # Check disabled attribute
            is_disabled = await element.get_attribute('disabled')
            if is_disabled is not None:
                self.logger.info(f"Element is disabled (disabled attribute)")
                return False
            
            # Check aria-disabled
            aria_disabled = await element.get_attribute('aria-disabled')
            if aria_disabled == 'true':
                self.logger.info(f"Element is disabled (aria-disabled)")
                return False
            
            # Check class name for disabled indicators
            class_name = await element.get_attribute('class') or ''
            disabled_classes = ['disabled', 'btn-disabled', 'inactive', 'not-clickable', 'btn-inactive']
            if any(disabled_class in class_name.lower() for disabled_class in disabled_classes):
                self.logger.info(f"Element has disabled class: {class_name}")
                return False
            
            # Check if element is visible and has dimensions
            is_visible = await element.is_visible()
            if not is_visible:
                self.logger.info(f"Element is not visible")
                return False
            
            # Check computed styles for pointer-events and opacity
            pointer_events = await element.evaluate("el => getComputedStyle(el).pointerEvents")
            opacity = await element.evaluate("el => getComputedStyle(el).opacity")
            
            if pointer_events == 'none':
                self.logger.info(f"Element has pointer-events: none")
                return False
                
            if float(opacity) < 0.1:
                self.logger.info(f"Element has very low opacity: {opacity}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error checking element clickability: {e}")
            return False

    async def _navigate_to_next_page(self) -> bool:
        """Navigate to the next page using pagination configuration"""
        if not self.config.pagination_config:
            return False
        
        try:
            # Find all elements matching the pagination selector
            pagination_elements = await self.main_page.query_selector_all(
                self.config.pagination_config.selector
            )
            
            if not pagination_elements:
                self.logger.info(f"Navigation element not found with selector: {self.config.pagination_config.selector}")
                return False
            
            selected_element = None
            
            # If we have original content, try to find element with matching content
            if hasattr(self.config.pagination_config, 'original_content') and self.config.pagination_config.original_content:
                original_content = self.config.pagination_config.original_content.strip().lower()
                self.logger.info(f"Looking for pagination element containing: '{original_content}'")
                
                for element in pagination_elements:
                    # Get element text content
                    element_text = await element.text_content()
                    if element_text:
                        element_text = element_text.strip().lower()
                        
                        # Check if element contains the original content (or vice versa for flexibility)
                        if (original_content in element_text or element_text in original_content or 
                            element_text == original_content):
                            selected_element = element
                            self.logger.info(f"Found matching pagination element with content: '{element_text}'")
                            break
                
                # If no content match found, stop crawling (likely reached last page)
                if not selected_element and pagination_elements:
                    self.logger.info(f"No pagination element found with content matching '{original_content}' - stopping crawl")
                    return False
            else:
                # No original content specified, use first element
                selected_element = pagination_elements[0]
            
            if not selected_element:
                return False
            
            # Comprehensive check if pagination element is clickable
            if not await self._is_element_clickable(selected_element):
                return False
            
            # Log what we're about to click
            element_text = await selected_element.text_content()
            self.logger.info(f"Clicking pagination element: '{element_text.strip()}'")
            
            # Click pagination element
            await selected_element.click()
            await self.main_page.wait_for_load_state('networkidle')
            await asyncio.sleep(self.config.delay_ms / 1000)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error navigating to next page: {e}")
            return False

    def _get_base_url(self, url: str) -> str:
        """Extract base URL from full URL for comparison"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _is_field_for_current_page(self, field_page_url: str, current_url: str) -> bool:
        """
        Determine if a field belongs to the current page.
        Returns True if the field should be extracted on the current page.
        """
        from urllib.parse import urlparse
        
        # Parse both URLs
        field_parsed = urlparse(field_page_url)
        current_parsed = urlparse(current_url)
        
        # If different domains, definitely different pages
        if field_parsed.netloc != current_parsed.netloc:
            return False
        
        # If the paths are significantly different, they're different pages
        field_path = field_parsed.path.rstrip('/')
        current_path = current_parsed.path.rstrip('/')
        
        # Exact match is always valid
        if field_path == current_path:
            return True
        
        # If field is for a more specific path (detail page) and we're on a broader path (listing),
        # then this field doesn't belong to current page
        if len(field_path.split('/')) > len(current_path.split('/')):
            # Field is for a more specific/deeper page
            return False
        
        # If current path starts with field path, field belongs to current page
        return current_path.startswith(field_path)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime
        return datetime.now().isoformat()

    async def crawl_with_visual_feedback(self) -> List[ExtractionResult]:
        """Crawl with visual feedback in non-headless mode"""
        if self.headless:
            self.logger.warning("Visual feedback requires headless=False")
        
        return await self.crawl_with_workflows()

    def save_results(self, filename: Optional[str] = None, format: str = 'json'):
        """Save extraction results to file"""
        if not self.data:
            self.logger.warning("No data to save")
            return
        
        filename = filename or f"advanced_crawl_results.{format}"
        
        if format.lower() == 'json':
            # Convert dataclasses to dicts for JSON serialization
            serializable_data = []
            for result in self.data:
                serializable_data.append({
                    'data': result.data,
                    'source_url': result.source_url,
                    'extraction_time': result.extraction_time,
                    'workflow_path': result.workflow_path
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {filename}")

    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the extraction"""
        return {
            'total_items': len(self.data),
            'unique_sources': len(set(result.source_url for result in self.data)),
            'workflow_usage': len([r for r in self.data if r.workflow_path]),
            'pages_visited': len(self.navigation_history)
        }

class WorkflowBuilder:
    """Helper class for building complex workflows programmatically"""
    
    def __init__(self):
        self.steps: List[WorkflowStep] = []
    
    def add_click_and_extract(self, 
                             step_id: str,
                             click_selector: str, 
                             extract_fields: List[str],
                             description: str = "") -> 'WorkflowBuilder':
        """Add a workflow step that clicks an element and extracts data from the resulting page"""
        step = WorkflowStep(
            step_id=step_id,
            action='click',
            target_selector=click_selector,
            description=description or f"Click {click_selector} and extract data",
            extract_fields=extract_fields,
            wait_condition='networkidle'
        )
        self.steps.append(step)
        return self
    
    def add_new_tab_extraction(self,
                              step_id: str,
                              link_selector: str,
                              extract_fields: List[str],
                              description: str = "") -> 'WorkflowBuilder':
        """Add a workflow step that opens a link in new tab and extracts data"""
        step = WorkflowStep(
            step_id=step_id,
            action='open_new_tab',
            target_selector=link_selector,
            description=description or f"Open {link_selector} in new tab and extract",
            extract_fields=extract_fields,
            wait_condition='networkidle'
        )
        self.steps.append(step)
        return self
    
    def add_extract_only(self,
                        step_id: str,
                        target_selector: str,
                        extract_fields: List[str],
                        description: str = "") -> 'WorkflowBuilder':
        """Add a workflow step that only extracts data without navigation"""
        step = WorkflowStep(
            step_id=step_id,
            action='extract',
            target_selector=target_selector,
            description=description or f"Extract from {target_selector}",
            extract_fields=extract_fields
        )
        self.steps.append(step)
        return self
    
    def build(self) -> List[WorkflowStep]:
        """Return the built workflow steps"""
        return self.steps.copy()

# Integration function to load configuration from interactive selector
def load_interactive_config(config_file: str) -> CrawlerConfiguration:
    """Load configuration created by interactive selector"""
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    
    selections = [ElementSelection(**sel) for sel in config_data['selections']]
    workflows = [WorkflowStep(**wf) for wf in config_data['workflows']]
    
    # Find pagination config
    pagination_config = None
    if config_data.get('pagination_config'):
        pagination_config = ElementSelection(**config_data['pagination_config'])
    
    return CrawlerConfiguration(
        name=config_data['name'],
        base_url=config_data['base_url'],
        selections=selections,
        workflows=workflows,
        pagination_config=pagination_config,
        max_pages=config_data.get('max_pages'),
        delay_ms=config_data.get('delay_ms', 1000)
    )

async def demo_advanced_crawling():
    """Demonstration of advanced crawling capabilities"""
    
    # Example: Build a workflow programmatically
    workflow_builder = WorkflowBuilder()
    workflow_builder.add_click_and_extract(
        step_id="get_details",
        click_selector="a.detail-link",
        extract_fields=["detail_text", "price", "description"],
        description="Click product link to get detailed information"
    ).add_new_tab_extraction(
        step_id="get_reviews", 
        link_selector="a.reviews-link",
        extract_fields=["rating", "review_count"],
        description="Open reviews in new tab"
    )
    
    # Create configuration (this would typically come from interactive selector)
    config = CrawlerConfiguration(
        name="Advanced Demo",
        base_url="https://example.com",
        selections=[
            ElementSelection("title", "h2", "data_field", "Product title"),
            ElementSelection("items", ".product", "items_container", "Product items"),
            ElementSelection("detail_text", ".description", "data_field", "Detailed description"),
            ElementSelection("next_page", ".pagination .next", "pagination", "Next page button")
        ],
        workflows=workflow_builder.build(),
        pagination_config=ElementSelection("next_page", ".pagination .next", "pagination", "Next page"),
        max_pages=5
    )
    
    async with AdvancedCrawler(config, headless=False) as crawler:
        results = await crawler.crawl_with_workflows()
        summary = crawler.get_extraction_summary()
        
        print(f"\n📊 Crawling Summary:")
        print(f"Total items: {summary['total_items']}")
        print(f"Unique sources: {summary['unique_sources']}")
        print(f"Workflow extractions: {summary['workflow_usage']}")
        
        crawler.save_results("advanced_crawl_results.json")

if __name__ == "__main__":
    asyncio.run(demo_advanced_crawling())
