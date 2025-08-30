#!/usr/bin/env python3
"""
Unit tests for advanced_crawler.py

Tests the advanced crawler with workflow support.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.advanced.advanced_crawler import (
    AdvancedCrawler, ExtractionResult, NavigationState,
    load_interactive_config
)
from app.advanced.workflow_builder import WorkflowBuilder
from app.models import (
    CrawlerConfiguration, ElementSelection, WorkflowStep
)


class TestExtractionResult:
    """Test ExtractionResult dataclass"""

    def test_extraction_result_creation(self):
        """Test creating an ExtractionResult"""
        data = {'title': 'Test', 'price': '$10'}
        source_url = 'https://test.com/page1'
        extraction_time = '2024-01-01T10:00:00'
        workflow_path = ['step1', 'step2']
        
        result = ExtractionResult(
            data=data,
            source_url=source_url,
            extraction_time=extraction_time,
            workflow_path=workflow_path
        )
        
        assert result.data == data
        assert result.source_url == source_url
        assert result.extraction_time == extraction_time
        assert result.workflow_path == workflow_path


class TestNavigationState:
    """Test NavigationState dataclass"""

    def test_navigation_state_creation(self):
        """Test creating a NavigationState"""
        state = NavigationState(
            current_url='https://test.com/page1',
            page_number=2,
            workflow_step=1,
            context={'key': 'value'}
        )
        
        assert state.current_url == 'https://test.com/page1'
        assert state.page_number == 2
        assert state.workflow_step == 1
        assert state.context == {'key': 'value'}


class TestWorkflowBuilder:
    """Test WorkflowBuilder functionality"""

    def test_workflow_builder_initialization(self):
        """Test WorkflowBuilder initialization"""
        builder = WorkflowBuilder()
        assert builder.steps == []

    def test_add_click_and_extract(self):
        """Test adding click and extract workflow step"""
        builder = WorkflowBuilder()
        
        result = builder.add_click_and_extract(
            step_id="test_step",
            click_selector=".link",
            extract_fields=["title", "description"],
            description="Test click and extract"
        )
        
        # Should return self for chaining
        assert result is builder
        assert len(builder.steps) == 1
        
        step = builder.steps[0]
        assert step.step_id == "test_step"
        assert step.action == "click"
        assert step.target_selector == ".link"
        assert step.extract_fields == ["title", "description"]
        assert step.description == "Test click and extract"
        assert step.wait_condition == "networkidle"

    def test_add_new_tab_extraction(self):
        """Test adding new tab extraction workflow step"""
        builder = WorkflowBuilder()
        
        result = builder.add_new_tab_extraction(
            step_id="tab_step",
            link_selector=".external-link",
            extract_fields=["content"],
            description="Test new tab extraction"
        )
        
        assert result is builder
        assert len(builder.steps) == 1
        
        step = builder.steps[0]
        assert step.step_id == "tab_step"
        assert step.action == "open_new_tab"
        assert step.target_selector == ".external-link"
        assert step.extract_fields == ["content"]
        assert step.description == "Test new tab extraction"

    def test_add_extract_only(self):
        """Test adding extract-only workflow step"""
        builder = WorkflowBuilder()
        
        result = builder.add_extract_only(
            step_id="extract_step",
            target_selector=".data-container",
            extract_fields=["info"],
            description="Test extract only"
        )
        
        assert result is builder
        assert len(builder.steps) == 1
        
        step = builder.steps[0]
        assert step.step_id == "extract_step"
        assert step.action == "extract"
        assert step.target_selector == ".data-container"
        assert step.extract_fields == ["info"]
        assert step.description == "Test extract only"

    def test_workflow_builder_chaining(self):
        """Test workflow builder method chaining"""
        builder = WorkflowBuilder()
        
        result = builder.add_click_and_extract(
            "step1", ".link1", ["field1"], "First step"
        ).add_new_tab_extraction(
            "step2", ".link2", ["field2"], "Second step"
        ).add_extract_only(
            "step3", ".container", ["field3"], "Third step"
        )
        
        assert result is builder
        assert len(builder.steps) == 3
        
        assert builder.steps[0].step_id == "step1"
        assert builder.steps[1].step_id == "step2"
        assert builder.steps[2].step_id == "step3"

    def test_build_method(self):
        """Test build method returns copy of steps"""
        builder = WorkflowBuilder()
        builder.add_click_and_extract("step1", ".link", ["field"], "Test")
        
        steps = builder.build()
        
        assert len(steps) == 1
        assert steps[0].step_id == "step1"
        
        # Should be a copy, not the original list
        builder.steps.append("extra")
        assert len(steps) == 1  # Original copy unchanged


@pytest.mark.asyncio
class TestAdvancedCrawler:
    """Test AdvancedCrawler functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.selections = [
            ElementSelection("items", ".product", "items_container", "Product items"),
            ElementSelection("title", ".title", "data_field", "Product title"),
            ElementSelection("price", ".price", "data_field", "Product price")
        ]
        
        self.pagination_config = ElementSelection(
            "next", ".pagination .next", "pagination", "Next page"
        )
        
        self.config = CrawlerConfiguration(
            name="Test Config",
            base_url="https://test.com",
            selections=self.selections,
            workflows=[],
            pagination_config=self.pagination_config,
            max_pages=2,
            delay_ms=100
        )

    def test_advanced_crawler_initialization(self):
        """Test AdvancedCrawler initialization"""
        crawler = AdvancedCrawler(self.config, headless=True)
        
        assert crawler.config == self.config
        assert crawler.headless is True
        assert crawler.browser is None
        assert crawler.context is None
        assert crawler.main_page is None
        assert crawler.data == []
        assert crawler.navigation_history == []
        assert crawler.visited_urls == set()

    def test_get_items_selector(self):
        """Test _get_items_selector method"""
        crawler = AdvancedCrawler(self.config)
        
        items_selector = crawler._get_items_selector()
        
        assert items_selector is not None
        assert items_selector.name == "items"
        assert items_selector.selector == ".product"
        assert items_selector.element_type == "items_container"

    def test_get_items_selector_no_container(self):
        """Test _get_items_selector when no items container exists"""
        config_no_items = CrawlerConfiguration(
            name="No Items",
            base_url="https://test.com",
            selections=[  # No items_container type
                ElementSelection("title", ".title", "data_field", "Title")
            ],
            workflows=[]
        )
        
        crawler = AdvancedCrawler(config_no_items)
        items_selector = crawler._get_items_selector()
        
        assert items_selector is None

    def test_find_selection_by_name(self):
        """Test _find_selection_by_name method"""
        crawler = AdvancedCrawler(self.config)
        
        # Find existing selection
        title_selection = crawler._find_selection_by_name("title")
        assert title_selection is not None
        assert title_selection.name == "title"
        assert title_selection.selector == ".title"
        
        # Find non-existing selection
        missing_selection = crawler._find_selection_by_name("nonexistent")
        assert missing_selection is None

    async def test_extract_element_value_text(self):
        """Test _extract_element_value with text extraction"""
        crawler = AdvancedCrawler(self.config)
        
        mock_element = AsyncMock()
        mock_element.text_content = AsyncMock(return_value="Test Text")
        
        selection = ElementSelection("test", ".test", "data_field", "Test", "text")
        
        result = await crawler._extract_element_value(mock_element, selection)
        assert result == "Test Text"

    async def test_extract_element_value_href(self):
        """Test _extract_element_value with href extraction"""
        crawler = AdvancedCrawler(self.config)
        
        mock_element = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="https://test.com/link")
        
        selection = ElementSelection("test", ".test", "data_field", "Test", "href")
        
        result = await crawler._extract_element_value(mock_element, selection)
        assert result == "https://test.com/link"

    async def test_extract_element_value_attribute(self):
        """Test _extract_element_value with custom attribute"""
        crawler = AdvancedCrawler(self.config)
        
        mock_element = AsyncMock()
        mock_element.get_attribute = AsyncMock(return_value="custom_value")
        
        selection = ElementSelection(
            "test", ".test", "data_field", "Test", 
            extraction_type="attribute", 
            attribute_name="data-custom"
        )
        
        result = await crawler._extract_element_value(mock_element, selection)
        assert result == "custom_value"
        mock_element.get_attribute.assert_called_with("data-custom")

    def test_get_timestamp(self):
        """Test _get_timestamp method"""
        crawler = AdvancedCrawler(self.config)
        
        timestamp = crawler._get_timestamp()
        
        # Should be valid ISO format timestamp
        assert isinstance(timestamp, str)
        # Should be parseable as datetime
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)

    def test_is_field_for_current_page_same_domain_path(self):
        """Test _is_field_for_current_page with same domain and path"""
        crawler = AdvancedCrawler(self.config)
        
        field_url = "https://example.com/products"
        current_url = "https://example.com/products"
        
        result = crawler._is_field_for_current_page(field_url, current_url)
        assert result is True

    def test_is_field_for_current_page_different_domain(self):
        """Test _is_field_for_current_page with different domains"""
        crawler = AdvancedCrawler(self.config)
        
        field_url = "https://other.com/products"
        current_url = "https://example.com/products"
        
        result = crawler._is_field_for_current_page(field_url, current_url)
        assert result is False

    def test_is_field_for_current_page_more_specific_path(self):
        """Test _is_field_for_current_page with more specific field path"""
        crawler = AdvancedCrawler(self.config)
        
        field_url = "https://example.com/products/detail/123"  # More specific
        current_url = "https://example.com/products"           # Broader
        
        result = crawler._is_field_for_current_page(field_url, current_url)
        assert result is False  # Field is for detail page, we're on listing

    def test_is_field_for_current_page_broader_field_path(self):
        """Test _is_field_for_current_page with broader field path"""
        crawler = AdvancedCrawler(self.config)
        
        field_url = "https://example.com/products"           # Broader
        current_url = "https://example.com/products/detail"  # More specific
        
        result = crawler._is_field_for_current_page(field_url, current_url)
        assert result is True  # Field applies to broader scope

    def test_get_extraction_summary(self):
        """Test get_extraction_summary method"""
        crawler = AdvancedCrawler(self.config)
        
        # Add test data
        crawler.data = [
            ExtractionResult({}, "https://test.com/page1", "2024-01-01", []),
            ExtractionResult({}, "https://test.com/page2", "2024-01-01", ["workflow1"]),
            ExtractionResult({}, "https://test.com/page1", "2024-01-01", [])
        ]
        
        crawler.navigation_history = [
            NavigationState("https://test.com/page1", 1, 0, {}),
            NavigationState("https://test.com/page2", 2, 0, {})
        ]
        
        summary = crawler.get_extraction_summary()
        
        assert summary['total_items'] == 3
        assert summary['unique_sources'] == 2  # page1 and page2
        assert summary['workflow_usage'] == 1  # One item has workflow_path
        assert summary['pages_visited'] == 2


class TestLoadInteractiveConfig:
    """Test load_interactive_config function"""

    @patch('builtins.open')
    @patch('json.load')
    def test_load_interactive_config_success(self, mock_json_load, mock_open):
        """Test successful loading of interactive configuration"""
        config_data = {
            'name': 'Test Config',
            'base_url': 'https://test.com',
            'selections': [
                {
                    'name': 'title',
                    'selector': '.title',
                    'element_type': 'data_field',
                    'description': 'Title field',
                    'extraction_type': 'text'
                }
            ],
            'workflows': [
                {
                    'step_id': 'step1',
                    'action': 'click',
                    'target_selector': '.link',
                    'description': 'Click link',
                    'extract_fields': ['detail'],
                    'wait_condition': 'networkidle'
                }
            ],
            'pagination_config': {
                'name': 'next',
                'selector': '.next',
                'element_type': 'pagination',
                'description': 'Next page',
                'extraction_type': 'text'
            },
            'max_pages': 5,
            'delay_ms': 2000
        }
        
        mock_json_load.return_value = config_data
        
        config = load_interactive_config("test_config.json")
        
        assert isinstance(config, CrawlerConfiguration)
        assert config.name == 'Test Config'
        assert config.base_url == 'https://test.com'
        assert len(config.selections) == 1
        assert len(config.workflows) == 1
        assert config.pagination_config is not None
        assert config.max_pages == 5
        assert config.delay_ms == 2000

    @patch('builtins.open')
    @patch('json.load')
    def test_load_interactive_config_no_pagination(self, mock_json_load, mock_open):
        """Test loading configuration without pagination"""
        config_data = {
            'name': 'Test Config',
            'base_url': 'https://test.com',
            'selections': [],
            'workflows': [],
            'pagination_config': None,
            'max_pages': None,
            'delay_ms': 1000
        }
        
        mock_json_load.return_value = config_data
        
        config = load_interactive_config("test_config.json")
        
        assert config.pagination_config is None
        assert config.max_pages is None
        assert config.delay_ms == 1000


@pytest.mark.asyncio
class TestAdvancedCrawlerIntegration:
    """Integration tests for AdvancedCrawler with mocked browser"""

    def setup_method(self):
        """Set up test fixtures"""
        self.selections = [
            ElementSelection("items", ".product", "items_container", "Products"),
            ElementSelection("title", ".title", "data_field", "Title"),
            ElementSelection("price", ".price", "data_field", "Price")
        ]
        
        self.config = CrawlerConfiguration(
            name="Test Config",
            base_url="https://test.com",
            selections=self.selections,
            workflows=[],
            max_pages=1
        )

    @patch('app.advanced_crawler.async_playwright')
    async def test_context_manager_setup(self, mock_playwright):
        """Test async context manager setup and teardown"""
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright_instance.firefox.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        
        crawler = AdvancedCrawler(self.config, headless=True)
        
        async with crawler:
            assert crawler.browser == mock_browser
            assert crawler.context == mock_context
            assert crawler.main_page == mock_page
        
        # Verify cleanup
        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_playwright_instance.stop.assert_called_once()

    @patch('app.advanced_crawler.async_playwright')
    async def test_extract_item_data(self, mock_playwright):
        """Test _extract_item_data method"""
        # Set up mocks
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright_instance.firefox.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        
        # Mock page URL
        mock_page.url = "https://test.com"
        
        crawler = AdvancedCrawler(self.config)
        
        # Mock item element and its sub-elements
        mock_item = AsyncMock()
        mock_title_element = AsyncMock()
        mock_title_element.text_content = AsyncMock(return_value="Test Title")
        mock_price_element = AsyncMock()
        mock_price_element.text_content = AsyncMock(return_value="$10.99")
        
        mock_item.query_selector = AsyncMock(side_effect=lambda sel: {
            '.title': mock_title_element,
            '.price': mock_price_element
        }.get(sel))
        
        async with crawler:
            result = await crawler._extract_item_data(mock_item)
        
        expected = {
            'title': 'Test Title',
            'price': '$10.99'
        }
        
        # Remove 'items' field from comparison as it's skipped in extraction
        filtered_result = {k: v for k, v in result.items() if k != 'items'}
        assert filtered_result == expected

    def test_save_results_no_data(self):
        """Test save_results when no data exists"""
        crawler = AdvancedCrawler(self.config)
        crawler.data = []
        
        # Should not raise an exception
        crawler.save_results()

    @patch('builtins.open')
    @patch('json.dump')
    def test_save_results_json_format(self, mock_json_dump, mock_open_func):
        """Test saving results in JSON format"""
        crawler = AdvancedCrawler(self.config)
        crawler.data = [
            ExtractionResult(
                data={'title': 'Test'},
                source_url='https://test.com',
                extraction_time='2024-01-01T10:00:00',
                workflow_path=[]
            )
        ]
        
        crawler.save_results("test_output.json", "json")
        
        mock_open_func.assert_called_once_with("test_output.json", 'w', encoding='utf-8')
        
        # Check that json.dump was called with serializable data
        call_args = mock_json_dump.call_args
        serialized_data = call_args[0][0]
        
        assert len(serialized_data) == 1
        assert serialized_data[0]['data'] == {'title': 'Test'}
        assert serialized_data[0]['source_url'] == 'https://test.com'
        assert serialized_data[0]['extraction_time'] == '2024-01-01T10:00:00'
        assert serialized_data[0]['workflow_path'] == []


class TestAdvancedCrawlerHelperMethods:
    """Test AdvancedCrawler helper methods without browser setup"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = CrawlerConfiguration(
            name="Test",
            base_url="https://test.com",
            selections=[],
            workflows=[]
        )
        self.crawler = AdvancedCrawler(self.config)

    def test_get_base_url(self):
        """Test _get_base_url method"""
        test_cases = [
            ("https://example.com/path/page", "https://example.com"),
            ("http://test.org/deep/nested/path", "http://test.org"),
            ("https://subdomain.example.com/page", "https://subdomain.example.com")
        ]
        
        for full_url, expected_base in test_cases:
            result = self.crawler._get_base_url(full_url)
            assert result == expected_base
