#!/usr/bin/env python3
"""
Shared test fixtures and configuration for the crawler test suite
"""

import pytest
import asyncio
import tempfile
import shutil
from unittest.mock import AsyncMock, Mock

from app.core.config import SiteConfig
from app.core.crawler import CrawlerConfig
from app.models import CrawlerConfiguration, ElementSelection, WorkflowStep


@pytest.fixture
def basic_site_config():
    """Basic SiteConfig fixture for testing"""
    return SiteConfig(
        name="Test Site",
        base_url="https://test.com",
        selectors={
            'items': '.item',
            'title': '.title',
            'author': '.author'
        },
        pagination_selector='.next',
        max_pages=3,
        delay_ms=1000
    )


@pytest.fixture
def basic_crawler_config():
    """Basic CrawlerConfig fixture for testing"""
    return CrawlerConfig(
        base_url="https://test.com",
        selectors={
            'items': '.quote',
            'text': '.text',
            'author': '.author'
        },
        pagination_selector='.next',
        max_pages=2,
        delay_ms=500,
        headless=True,
        output_format="json",
        output_file="test_data"
    )


@pytest.fixture
def sample_element_selections():
    """Sample ElementSelection objects for testing"""
    return [
        ElementSelection(
            name="items",
            selector=".product-card",
            element_type="items_container",
            description="Product cards container"
        ),
        ElementSelection(
            name="title",
            selector=".product-title",
            element_type="data_field",
            description="Product title",
            extraction_type="text"
        ),
        ElementSelection(
            name="price",
            selector=".price-tag",
            element_type="data_field",
            description="Product price",
            extraction_type="text"
        ),
        ElementSelection(
            name="link",
            selector=".product-link",
            element_type="navigation",
            description="Product detail link",
            extraction_type="href",
            workflow_action="click"
        ),
        ElementSelection(
            name="next_page",
            selector=".pagination .next",
            element_type="pagination",
            description="Next page button",
            original_content="Next"
        )
    ]


@pytest.fixture
def sample_workflow_steps():
    """Sample WorkflowStep objects for testing"""
    return [
        WorkflowStep(
            step_id="get_product_details",
            action="click",
            target_selector=".product-link",
            description="Navigate to product details page",
            extract_fields=["description", "specifications"],
            wait_condition="networkidle"
        ),
        WorkflowStep(
            step_id="get_reviews",
            action="open_new_tab",
            target_selector=".reviews-tab",
            description="Open reviews in new tab",
            extract_fields=["reviews", "rating"],
            wait_condition="networkidle"
        ),
        WorkflowStep(
            step_id="extract_metadata",
            action="extract",
            target_selector=".metadata",
            description="Extract additional metadata",
            extract_fields=["category", "brand"]
        )
    ]


@pytest.fixture
def sample_crawler_configuration(sample_element_selections, sample_workflow_steps):
    """Complete CrawlerConfiguration fixture for testing"""
    # Find pagination config from selections
    pagination_config = next(
        (s for s in sample_element_selections if s.element_type == "pagination"),
        None
    )
    
    return CrawlerConfiguration(
        name="Sample Configuration",
        base_url="https://example.com/products",
        selections=sample_element_selections,
        workflows=sample_workflow_steps,
        pagination_config=pagination_config,
        max_pages=5,
        delay_ms=1500
    )


@pytest.fixture
def mock_playwright():
    """Mock playwright setup for browser-related tests"""
    mock_playwright_instance = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    
    # Setup the mock chain
    mock_playwright_instance.firefox.launch = AsyncMock(return_value=mock_browser)
    mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.new_page = AsyncMock(return_value=mock_page)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    
    # Default page behavior
    mock_page.goto = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.query_selector = AsyncMock(return_value=None)
    mock_page.query_selector_all = AsyncMock(return_value=[])
    mock_page.url = "https://test.com"
    mock_page.evaluate = AsyncMock(return_value=None)
    
    return {
        'playwright_instance': mock_playwright_instance,
        'browser': mock_browser,
        'context': mock_context,
        'page': mock_page
    }


@pytest.fixture
def mock_element():
    """Mock browser element for testing"""
    element = AsyncMock()
    element.text_content = AsyncMock(return_value="Test Text")
    element.get_attribute = AsyncMock(return_value=None)
    element.is_visible = AsyncMock(return_value=True)
    element.click = AsyncMock()
    element.evaluate = AsyncMock(return_value="auto")  # Default computed style
    
    return element


@pytest.fixture
def temp_config_dir():
    """Temporary directory for configuration file testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Async test utilities
@pytest.fixture
def async_mock_context():
    """Utility for creating async context manager mocks"""
    def create_async_context_mock(return_value=None):
        mock_context = Mock()
        mock_context.__aenter__ = AsyncMock(return_value=return_value or mock_context)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        return mock_context
    
    return create_async_context_mock


# Test data generators
@pytest.fixture
def sample_extraction_data():
    """Sample data that would be extracted during crawling"""
    return [
        {
            'title': 'Product 1',
            'price': '$19.99',
            'rating': '4.5 stars',
            'description': 'Great product with excellent features'
        },
        {
            'title': 'Product 2', 
            'price': '$29.99',
            'rating': '4.2 stars',
            'description': 'Another excellent product'
        },
        {
            'title': 'Product 3',
            'price': '$39.99',
            'rating': '4.8 stars',
            'description': 'Premium product with advanced features'
        }
    ]


@pytest.fixture
def complex_config_data():
    """Complex configuration data for testing serialization/deserialization"""
    return {
        'name': 'Complex Test Config',
        'base_url': 'https://complex-site.com',
        'selections': [
            {
                'name': 'items',
                'selector': '.product-grid .product-card',
                'element_type': 'items_container',
                'description': 'Product cards container',
                'extraction_type': 'text',
                'attribute_name': None,
                'workflow_action': None,
                'original_content': None,
                'verification_attributes': None,
                'page_url': 'https://complex-site.com'
            },
            {
                'name': 'title',
                'selector': '.product-title h3',
                'element_type': 'data_field',
                'description': 'Product title',
                'extraction_type': 'text',
                'attribute_name': None,
                'workflow_action': None,
                'original_content': None,
                'verification_attributes': None,
                'page_url': 'https://complex-site.com'
            },
            {
                'name': 'detail_link',
                'selector': '.product-title a',
                'element_type': 'navigation',
                'description': 'Link to product details',
                'extraction_type': 'href',
                'attribute_name': None,
                'workflow_action': 'click',
                'original_content': 'View Details',
                'verification_attributes': {'class': 'product-link'},
                'page_url': 'https://complex-site.com'
            }
        ],
        'workflows': [
            {
                'step_id': 'extract_details',
                'action': 'click',
                'target_selector': '.product-title a',
                'description': 'Extract detailed product information',
                'extract_fields': ['full_description', 'specifications'],
                'wait_condition': 'networkidle',
                'wait_selector': None
            }
        ],
        'pagination_config': {
            'name': 'next_button',
            'selector': '.pagination button.next',
            'element_type': 'pagination',
            'description': 'Next page button',
            'extraction_type': 'text',
            'attribute_name': None,
            'workflow_action': None,
            'original_content': 'Next →',
            'verification_attributes': {'aria-label': 'Next page'},
            'page_url': 'https://complex-site.com'
        },
        'max_pages': 10,
        'delay_ms': 2000
    }
