#!/usr/bin/env python3
"""
Unit tests for crawler.py

Tests the basic paginated crawler functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, mock_open
import json
import csv
from io import StringIO

from app.core.crawler import CrawlerConfig, PaginatedCrawler


class TestCrawlerConfig:
    """Test CrawlerConfig dataclass"""

    def test_crawler_config_creation(self):
        """Test creating a CrawlerConfig with all parameters"""
        selectors = {'items': '.item', 'title': '.title'}
        
        config = CrawlerConfig(
            base_url="https://test.com",
            selectors=selectors,
            pagination_selector='.next',
            max_pages=10,
            delay_ms=2000,
            headless=True,
            output_format="csv",
            output_file="test_data"
        )
        
        assert config.base_url == "https://test.com"
        assert config.selectors == selectors
        assert config.pagination_selector == '.next'
        assert config.max_pages == 10
        assert config.delay_ms == 2000
        assert config.headless is True
        assert config.output_format == "csv"
        assert config.output_file == "test_data"

    def test_crawler_config_defaults(self):
        """Test CrawlerConfig with default values"""
        config = CrawlerConfig(
            base_url="https://test.com",
            selectors={'items': '.item'}
        )
        
        assert config.pagination_selector is None
        assert config.max_pages is None
        assert config.delay_ms == 1000
        assert config.headless is False
        assert config.output_format == "json"
        assert config.output_file == "crawled_data"


@pytest.mark.asyncio
class TestPaginatedCrawler:
    """Test PaginatedCrawler functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = CrawlerConfig(
            base_url="https://test.com",
            selectors={
                'items': '.quote',
                'text': '.text',
                'author': '.author'
            },
            pagination_selector='.next',
            max_pages=2,
            delay_ms=100
        )

    async def test_crawler_initialization(self):
        """Test crawler initialization"""
        crawler = PaginatedCrawler(self.config)
        
        assert crawler.config == self.config
        assert crawler.data == []
        assert crawler.current_page == 1
        assert crawler.browser is None
        assert crawler.page is None

    @patch('app.crawler.async_playwright')
    async def test_context_manager_entry(self, mock_playwright):
        """Test async context manager entry"""
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        
        crawler = PaginatedCrawler(self.config)
        
        async with crawler:
            assert crawler.browser == mock_browser
            assert crawler.page == mock_page

    async def test_extract_data_from_page_no_items_selector(self):
        """Test extract_data_from_page with missing items selector"""
        config = CrawlerConfig(
            base_url="https://test.com",
            selectors={'text': '.text'}  # Missing 'items' selector
        )
        
        crawler = PaginatedCrawler(config)
        
        # Mock page
        mock_page = AsyncMock()
        crawler.page = mock_page
        
        result = await crawler.extract_data_from_page()
        assert result == []

    async def test_extract_data_from_page_success(self):
        """Test successful data extraction from page"""
        crawler = PaginatedCrawler(self.config)
        
        # Mock page and elements
        mock_page = AsyncMock()
        mock_item1 = AsyncMock()
        mock_item2 = AsyncMock()
        
        # Mock text extraction
        mock_text1 = AsyncMock()
        mock_text1.text_content = AsyncMock(return_value="Test quote 1")
        mock_author1 = AsyncMock()
        mock_author1.text_content = AsyncMock(return_value="Author 1")
        
        mock_text2 = AsyncMock()
        mock_text2.text_content = AsyncMock(return_value="Test quote 2")
        mock_author2 = AsyncMock()
        mock_author2.text_content = AsyncMock(return_value="Author 2")
        
        mock_item1.query_selector = AsyncMock(side_effect=lambda sel: {
            '.text': mock_text1,
            '.author': mock_author1
        }.get(sel))
        
        mock_item2.query_selector = AsyncMock(side_effect=lambda sel: {
            '.text': mock_text2,
            '.author': mock_author2
        }.get(sel))
        
        mock_page.query_selector_all = AsyncMock(return_value=[mock_item1, mock_item2])
        crawler.page = mock_page
        
        result = await crawler.extract_data_from_page()
        
        assert len(result) == 2
        assert result[0] == {'text': 'Test quote 1', 'author': 'Author 1'}
        assert result[1] == {'text': 'Test quote 2', 'author': 'Author 2'}

    async def test_extract_data_from_page_with_missing_elements(self):
        """Test data extraction when some elements are missing"""
        crawler = PaginatedCrawler(self.config)
        
        # Mock page and elements
        mock_page = AsyncMock()
        mock_item = AsyncMock()
        
        # Mock text element exists but author doesn't
        mock_text = AsyncMock()
        mock_text.text_content = AsyncMock(return_value="Test quote")
        
        mock_item.query_selector = AsyncMock(side_effect=lambda sel: {
            '.text': mock_text,
            '.author': None  # Missing author element
        }.get(sel))
        
        mock_page.query_selector_all = AsyncMock(return_value=[mock_item])
        crawler.page = mock_page
        
        result = await crawler.extract_data_from_page()
        
        assert len(result) == 1
        assert result[0] == {'text': 'Test quote', 'author': None}

    async def test_is_element_clickable_disabled_attribute(self):
        """Test element clickability check with disabled attribute"""
        crawler = PaginatedCrawler(self.config)
        
        mock_element = AsyncMock()
        mock_element.get_attribute = AsyncMock(side_effect=lambda attr: {
            'disabled': 'true'  # Element is disabled
        }.get(attr))
        
        result = await crawler._is_element_clickable(mock_element)
        assert result is False

    async def test_is_element_clickable_aria_disabled(self):
        """Test element clickability check with aria-disabled"""
        crawler = PaginatedCrawler(self.config)
        
        mock_element = AsyncMock()
        mock_element.get_attribute = AsyncMock(side_effect=lambda attr: {
            'disabled': None,
            'aria-disabled': 'true'
        }.get(attr))
        
        result = await crawler._is_element_clickable(mock_element)
        assert result is False

    async def test_is_element_clickable_disabled_class(self):
        """Test element clickability check with disabled class"""
        crawler = PaginatedCrawler(self.config)
        
        mock_element = AsyncMock()
        mock_element.get_attribute = AsyncMock(side_effect=lambda attr: {
            'disabled': None,
            'aria-disabled': None,
            'class': 'btn btn-disabled'
        }.get(attr))
        
        result = await crawler._is_element_clickable(mock_element)
        assert result is False

    async def test_is_element_clickable_not_visible(self):
        """Test element clickability check with invisible element"""
        crawler = PaginatedCrawler(self.config)
        
        mock_element = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value=None)
        mock_element.is_visible = AsyncMock(return_value=False)
        
        result = await crawler._is_element_clickable(mock_element)
        assert result is False

    async def test_is_element_clickable_pointer_events_none(self):
        """Test element clickability check with pointer-events: none"""
        crawler = PaginatedCrawler(self.config)
        
        mock_element = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value=None)
        mock_element.is_visible = AsyncMock(return_value=True)
        mock_element.evaluate = AsyncMock(side_effect=lambda script: {
            "el => getComputedStyle(el).pointerEvents": "none",
            "el => getComputedStyle(el).opacity": "1"
        }.get(script))
        
        result = await crawler._is_element_clickable(mock_element)
        assert result is False

    async def test_is_element_clickable_low_opacity(self):
        """Test element clickability check with very low opacity"""
        crawler = PaginatedCrawler(self.config)
        
        mock_element = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value=None)
        mock_element.is_visible = AsyncMock(return_value=True)
        mock_element.evaluate = AsyncMock(side_effect=lambda script: {
            "el => getComputedStyle(el).pointerEvents": "auto",
            "el => getComputedStyle(el).opacity": "0.05"
        }.get(script))
        
        result = await crawler._is_element_clickable(mock_element)
        assert result is False

    async def test_is_element_clickable_success(self):
        """Test element clickability check with clickable element"""
        crawler = PaginatedCrawler(self.config)
        
        mock_element = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value=None)
        mock_element.is_visible = AsyncMock(return_value=True)
        mock_element.evaluate = AsyncMock(side_effect=lambda script: {
            "el => getComputedStyle(el).pointerEvents": "auto",
            "el => getComputedStyle(el).opacity": "1"
        }.get(script))
        
        result = await crawler._is_element_clickable(mock_element)
        assert result is True

    async def test_navigate_to_next_page_no_pagination_selector(self):
        """Test navigation when no pagination selector is configured"""
        config = CrawlerConfig(
            base_url="https://test.com",
            selectors={'items': '.item'},
            pagination_selector=None
        )
        crawler = PaginatedCrawler(config)
        
        result = await crawler.navigate_to_next_page()
        assert result is False

    async def test_navigate_to_next_page_no_elements_found(self):
        """Test navigation when pagination elements are not found"""
        crawler = PaginatedCrawler(self.config)
        
        mock_page = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        crawler.page = mock_page
        
        result = await crawler.navigate_to_next_page()
        assert result is False

    @patch('asyncio.sleep', new_callable=AsyncMock)
    async def test_navigate_to_next_page_success(self, mock_sleep):
        """Test successful navigation to next page"""
        crawler = PaginatedCrawler(self.config)
        
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="Next")
        mock_element.get_attribute = AsyncMock(return_value=None)
        mock_element.is_visible = AsyncMock(return_value=True)
        mock_element.evaluate = AsyncMock(side_effect=lambda script: {
            "el => getComputedStyle(el).pointerEvents": "auto",
            "el => getComputedStyle(el).opacity": "1"
        }.get(script))
        
        mock_page.query_selector_all = AsyncMock(return_value=[mock_element])
        mock_page.wait_for_load_state = AsyncMock()
        
        crawler.page = mock_page
        crawler.current_page = 1
        
        result = await crawler.navigate_to_next_page()
        
        assert result is True
        assert crawler.current_page == 2
        mock_element.click.assert_called_once()
        mock_page.wait_for_load_state.assert_called_once_with('networkidle')
        mock_sleep.assert_called_once()

    def test_save_data_no_data(self):
        """Test save_data when no data exists"""
        crawler = PaginatedCrawler(self.config)
        crawler.data = []
        
        # Should not raise an exception
        crawler.save_data()

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_data_json_format(self, mock_json_dump, mock_file):
        """Test saving data in JSON format"""
        crawler = PaginatedCrawler(self.config)
        crawler.data = [{'text': 'quote1', 'author': 'author1'}]
        
        crawler.save_data("test_output.json")
        
        mock_file.assert_called_once_with("test_output.json", 'w', encoding='utf-8')
        mock_json_dump.assert_called_once_with(
            crawler.data, 
            mock_file.return_value.__enter__.return_value,
            indent=2, 
            ensure_ascii=False
        )

    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.DictWriter')
    def test_save_data_csv_format(self, mock_dict_writer, mock_file):
        """Test saving data in CSV format"""
        config = CrawlerConfig(
            base_url="https://test.com",
            selectors={'items': '.item'},
            output_format="csv"
        )
        crawler = PaginatedCrawler(config)
        crawler.data = [
            {'text': 'quote1', 'author': 'author1'},
            {'text': 'quote2', 'author': 'author2'}
        ]
        
        mock_writer = Mock()
        mock_dict_writer.return_value = mock_writer
        
        crawler.save_data("test_output.csv")
        
        mock_file.assert_called_once_with("test_output.csv", 'w', newline='', encoding='utf-8')
        mock_dict_writer.assert_called_once_with(
            mock_file.return_value.__enter__.return_value,
            fieldnames=['text', 'author']
        )
        mock_writer.writeheader.assert_called_once()
        mock_writer.writerows.assert_called_once_with(crawler.data)

    def test_get_data(self):
        """Test get_data method"""
        crawler = PaginatedCrawler(self.config)
        test_data = [{'text': 'quote1', 'author': 'author1'}]
        crawler.data = test_data
        
        result = crawler.get_data()
        assert result == test_data

    @patch('app.crawler.async_playwright')
    async def test_crawl_with_max_pages_limit(self, mock_playwright):
        """Test crawling with max pages limit"""
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        
        crawler = PaginatedCrawler(self.config)
        
        # Mock methods
        crawler.extract_data_from_page = AsyncMock(return_value=[{'text': 'quote', 'author': 'author'}])
        crawler.navigate_to_next_page = AsyncMock(return_value=True)
        
        async with crawler:
            mock_page.goto = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            
            result = await crawler.crawl()
            
            # Should stop at max_pages (2)
            assert len(result) == 2  # 2 pages * 1 item per page
            assert crawler.extract_data_from_page.call_count == 2
            assert crawler.navigate_to_next_page.call_count == 1  # Called once, then stopped by max_pages

    @patch('app.crawler.async_playwright')
    async def test_crawl_no_more_pages(self, mock_playwright):
        """Test crawling when no more pages are available"""
        config = CrawlerConfig(
            base_url="https://test.com",
            selectors={'items': '.item'},
            max_pages=None  # No page limit
        )
        crawler = PaginatedCrawler(config)
        
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        
        # Mock methods
        crawler.extract_data_from_page = AsyncMock(return_value=[{'text': 'quote'}])
        crawler.navigate_to_next_page = AsyncMock(side_effect=[True, False])  # Second call returns False
        
        async with crawler:
            mock_page.goto = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            
            result = await crawler.crawl()
            
            # Should crawl 2 pages (first page + one successful navigation)
            assert len(result) == 2
            assert crawler.extract_data_from_page.call_count == 2
            assert crawler.navigate_to_next_page.call_count == 2

    @patch('app.crawler.async_playwright')
    async def test_crawl_with_custom_extractor(self, mock_playwright):
        """Test crawling with custom extractor function"""
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        
        crawler = PaginatedCrawler(self.config)
        
        # Custom extractor function
        async def custom_extractor(page):
            return [{'custom': 'data'}]
        
        # Mock methods
        crawler.navigate_to_next_page = AsyncMock(return_value=False)  # Only one page
        
        async with crawler:
            mock_page.goto = AsyncMock()
            mock_page.wait_for_load_state = AsyncMock()
            
            result = await crawler.crawl(custom_extractor)
            
            assert len(result) == 1
            assert result[0] == {'custom': 'data'}
            # extract_data_from_page should not be called when custom extractor is used
