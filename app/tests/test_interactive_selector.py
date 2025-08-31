#!/usr/bin/env python3
"""
Unit tests for interactive_selector.py

Tests the interactive element selection interface.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, mock_open
import json

from app.interactive.selector import InteractiveSelector
from app.models import ElementSelection, WorkflowStep, CrawlerConfiguration


class TestElementSelection:
    """Test ElementSelection dataclass"""

    def test_element_selection_creation_minimal(self):
        """Test creating ElementSelection with minimal parameters"""
        selection = ElementSelection(
            name="test_field",
            selector=".test",
            element_type="data_field",
            description="Test field",
        )

        assert selection.name == "test_field"
        assert selection.selector == ".test"
        assert selection.element_type == "data_field"
        assert selection.description == "Test field"
        assert selection.extraction_type == "text"  # Default
        assert selection.attribute_name is None
        assert selection.workflow_action is None

    def test_element_selection_creation_full(self):
        """Test creating ElementSelection with all parameters"""
        verification_attrs = {"class": "test-class", "title": "Test Title"}

        selection = ElementSelection(
            name="test_field",
            selector=".test",
            element_type="navigation",
            description="Test navigation",
            extraction_type="href",
            attribute_name="data-custom",
            workflow_action="click",
            original_content="Click me",
            verification_attributes=verification_attrs,
            page_url="https://test.com/page1",
        )

        assert selection.extraction_type == "href"
        assert selection.attribute_name == "data-custom"
        assert selection.workflow_action == "click"
        assert selection.original_content == "Click me"
        assert selection.verification_attributes == verification_attrs
        assert selection.page_url == "https://test.com/page1"

    def test_element_selection_types(self):
        """Test different element types are handled correctly"""
        types = ["data_field", "items_container", "pagination", "navigation"]

        for element_type in types:
            selection = ElementSelection(
                name=f"test_{element_type}",
                selector=f".{element_type}",
                element_type=element_type,
                description=f"Test {element_type}",
            )
            assert selection.element_type == element_type


class TestWorkflowStep:
    """Test WorkflowStep dataclass"""

    def test_workflow_step_creation_minimal(self):
        """Test creating WorkflowStep with minimal parameters"""
        step = WorkflowStep(
            step_id="test_step",
            action="click",
            target_selector=".link",
            description="Test step",
        )

        assert step.step_id == "test_step"
        assert step.action == "click"
        assert step.target_selector == ".link"
        assert step.description == "Test step"
        assert step.extract_fields is None
        assert step.wait_condition == "networkidle"  # Default
        assert step.wait_selector is None

    def test_workflow_step_creation_full(self):
        """Test creating WorkflowStep with all parameters"""
        extract_fields = ["field1", "field2"]

        step = WorkflowStep(
            step_id="test_step",
            action="open_new_tab",
            target_selector=".external-link",
            description="Open in new tab",
            extract_fields=extract_fields,
            wait_condition="selector",
            wait_selector=".loaded-content",
        )

        assert step.extract_fields == extract_fields
        assert step.wait_condition == "selector"
        assert step.wait_selector == ".loaded-content"

    def test_workflow_step_actions(self):
        """Test different workflow actions"""
        actions = ["click", "extract", "navigate_back", "open_new_tab"]

        for action in actions:
            step = WorkflowStep(
                step_id=f"test_{action}",
                action=action,
                target_selector=f".{action}",
                description=f"Test {action}",
            )
            assert step.action == action


class TestCrawlerConfiguration:
    """Test CrawlerConfiguration dataclass"""

    def test_crawler_configuration_creation_minimal(self):
        """Test creating CrawlerConfiguration with minimal parameters"""
        selections = [ElementSelection("items", ".item", "items_container", "Items")]

        config = CrawlerConfiguration(
            name="Test Config",
            base_url="https://test.com",
            selections=selections,
            workflows=[],
        )

        assert config.name == "Test Config"
        assert config.base_url == "https://test.com"
        assert config.selections == selections
        assert config.workflows == []
        assert config.pagination_config is None
        assert config.max_pages is None
        assert config.delay_ms == 1000

    def test_crawler_configuration_creation_full(self):
        """Test creating CrawlerConfiguration with all parameters"""
        selections = [
            ElementSelection("items", ".item", "items_container", "Items"),
            ElementSelection("title", ".title", "data_field", "Title"),
        ]

        workflows = [WorkflowStep("step1", "click", ".link", "Test step")]

        pagination_config = ElementSelection("next", ".next", "pagination", "Next page")

        config = CrawlerConfiguration(
            name="Full Config",
            base_url="https://test.com",
            selections=selections,
            workflows=workflows,
            pagination_config=pagination_config,
            max_pages=10,
            delay_ms=2000,
        )

        assert len(config.selections) == 2
        assert len(config.workflows) == 1
        assert config.pagination_config == pagination_config
        assert config.max_pages == 10
        assert config.delay_ms == 2000


@pytest.mark.asyncio
class TestInteractiveSelector:
    """Test InteractiveSelector functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.selector = InteractiveSelector(headless=True)

    def test_interactive_selector_initialization(self):
        """Test InteractiveSelector initialization"""
        selector = InteractiveSelector(headless=False)

        assert selector.headless is False
        assert selector.browser is None
        assert selector.page is None
        assert selector.selections == []
        assert selector.workflows == []
        assert selector.current_mode == "selection"

    @patch("app.interactive.selector.async_playwright")
    async def test_context_manager_setup(self, mock_playwright):
        """Test async context manager setup for InteractiveSelector"""
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        mock_playwright.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )
        mock_playwright_instance.firefox.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)

        selector = InteractiveSelector(headless=True)

        async with selector:
            assert selector.browser == mock_browser
            assert selector.context == mock_context
            assert selector.page == mock_page

        # Verify cleanup
        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()

    async def test_get_configuration_no_data(self):
        """Test get_configuration when no selections were made"""
        selector = InteractiveSelector()

        # Mock page with no configuration data
        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=None)
        mock_page.url = "https://test.com"
        selector.page = mock_page

        config = await selector.get_configuration()
        assert config is None

    async def test_get_configuration_success(self):
        """Test successful get_configuration"""
        selector = InteractiveSelector()

        # Mock page with configuration data
        mock_page = AsyncMock()
        config_data = {
            "selections": [
                {
                    "name": "title",
                    "selector": ".title",
                    "element_type": "data_field",
                    "description": "Title field",
                    "extraction_type": "text",
                    "attribute_name": None,
                    "workflow_action": None,
                    "original_content": None,
                    "verification_attributes": None,
                    "page_url": None,
                }
            ],
            "workflows": [],
        }

        mock_page.evaluate = AsyncMock(return_value=config_data)
        mock_page.url = "https://test.com"
        selector.page = mock_page

        config = await selector.get_configuration()

        assert config is not None
        assert isinstance(config, CrawlerConfiguration)
        assert config.base_url == "https://test.com"
        assert len(config.selections) == 1
        assert config.selections[0].name == "title"

    async def test_get_configuration_with_navigation_workflow_generation(self):
        """Test workflow generation from navigation selections"""
        selector = InteractiveSelector()

        # Mock page with navigation selections
        mock_page = AsyncMock()
        config_data = {
            "selections": [
                {
                    "name": "items",
                    "selector": ".item",
                    "element_type": "items_container",
                    "description": "Items",
                    "extraction_type": "text",
                    "attribute_name": None,
                    "workflow_action": None,
                    "original_content": None,
                    "verification_attributes": None,
                    "page_url": None,
                },
                {
                    "name": "nav_link",
                    "selector": ".detail-link",
                    "element_type": "navigation",
                    "description": "Navigation link",
                    "extraction_type": "href",
                    "attribute_name": None,
                    "workflow_action": "click",
                    "original_content": None,
                    "verification_attributes": None,
                    "page_url": None,
                },
            ],
            "workflows": [],
        }

        # Mock page selections data for workflow generation
        page_selections = {
            "https://test.com": [{"name": "nav_link", "element_type": "navigation"}],
            "https://test.com/detail": [
                {"name": "detail_field", "element_type": "data_field"}
            ],
        }

        mock_page.evaluate = AsyncMock(
            side_effect=[config_data, page_selections, "https://test.com"]
        )
        mock_page.url = "https://test.com"
        selector.page = mock_page

        config = await selector.get_configuration()

        assert config is not None
        assert len(config.workflows) == 1  # Should have generated workflow
        assert config.workflows[0].step_id == "nav_nav_link"
        assert config.workflows[0].action == "click"

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    async def test_save_configuration(self, mock_json_dump, mock_file):
        """Test saving configuration to file"""
        selections = [ElementSelection("title", ".title", "data_field", "Title")]

        config = CrawlerConfiguration(
            name="Test Config",
            base_url="https://test.com",
            selections=selections,
            workflows=[],
        )

        selector = InteractiveSelector()
        await selector.save_configuration(config, "test_config.json")

        mock_file.assert_called_once_with("test_config.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    def test_preview_configuration(self, capsys):
        """Test preview_configuration output"""
        selections = [
            ElementSelection("items", ".item", "items_container", "Items"),
            ElementSelection("title", ".title", "data_field", "Title"),
            ElementSelection("price", ".price", "data_field", "Price"),
        ]

        workflows = [WorkflowStep("step1", "click", ".link", "Test step", ["detail"])]

        pagination_config = ElementSelection("next", ".next", "pagination", "Next page")

        config = CrawlerConfiguration(
            name="Preview Test",
            base_url="https://test.com",
            selections=selections,
            workflows=workflows,
            pagination_config=pagination_config,
        )

        selector = InteractiveSelector()
        selector.preview_configuration(config)

        captured = capsys.readouterr()
        assert "Preview Test" in captured.out
        assert "https://test.com" in captured.out
        assert "3 total" in captured.out  # 3 selections
        assert "1 steps" in captured.out  # 1 workflow step
        assert ".next" in captured.out  # Pagination selector


class TestInteractiveSelectorMethods:
    """Test InteractiveSelector helper methods without browser setup"""

    def setup_method(self):
        """Set up test fixtures"""
        self.selector = InteractiveSelector(headless=True)

    @patch("asyncio.get_event_loop")
    async def test_wait_for_user_completion(self, mock_get_loop):
        """Test _wait_for_user_completion method"""
        mock_loop = Mock()
        mock_get_loop.return_value = mock_loop
        mock_loop.run_in_executor = AsyncMock(return_value=True)

        await self.selector._wait_for_user_completion()

        mock_loop.run_in_executor.assert_called_once()
        # Verify the executor was called with None and a callable
        args = mock_loop.run_in_executor.call_args[0]
        assert args[0] is None
        assert callable(args[1])


class TestInteractiveSelectorIntegration:
    """Integration tests for InteractiveSelector with mocked browser"""

    @pytest.mark.asyncio
    @patch("app.interactive.selector.async_playwright")
    async def test_start_selection_session_setup(self, mock_playwright):
        """Test start_selection_session setup process"""
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        mock_playwright.return_value.start = AsyncMock(
            return_value=mock_playwright_instance
        )
        mock_playwright_instance.firefox.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)

        selector = InteractiveSelector(headless=True)

        # Mock the UI injection and user completion methods
        selector._inject_ui_after_load = AsyncMock()
        selector._setup_navigation_detection = AsyncMock()
        selector._wait_for_user_completion = AsyncMock()

        async with selector:
            await selector.start_selection_session("https://test.com")

        # Verify page navigation
        mock_page.goto.assert_called_once_with("https://test.com")
        mock_page.wait_for_load_state.assert_called_with("networkidle")

        # Verify UI setup
        selector._inject_ui_after_load.assert_called_once()
        selector._setup_navigation_detection.assert_called_once()
        selector._wait_for_user_completion.assert_called_once()


class TestConfigurationDataValidation:
    """Test configuration data validation and transformation"""

    def test_valid_element_types(self):
        """Test that only valid element types are accepted"""
        valid_types = ["data_field", "items_container", "pagination", "navigation"]

        for element_type in valid_types:
            selection = ElementSelection(
                name="test",
                selector=".test",
                element_type=element_type,
                description="Test",
            )
            assert selection.element_type == element_type

    def test_valid_extraction_types(self):
        """Test different extraction types"""
        extraction_types = ["text", "href", "src", "attribute"]

        for extraction_type in extraction_types:
            selection = ElementSelection(
                name="test",
                selector=".test",
                element_type="data_field",
                description="Test",
                extraction_type=extraction_type,
            )
            assert selection.extraction_type == extraction_type

    def test_valid_workflow_actions(self):
        """Test different workflow actions"""
        actions = ["click", "extract", "navigate_back", "open_new_tab"]

        for action in actions:
            step = WorkflowStep(
                step_id="test",
                action=action,
                target_selector=".test",
                description="Test",
            )
            assert step.action == action

    def test_wait_conditions(self):
        """Test different wait conditions"""
        wait_conditions = ["networkidle", "domcontentloaded", "selector"]

        for condition in wait_conditions:
            step = WorkflowStep(
                step_id="test",
                action="click",
                target_selector=".test",
                description="Test",
                wait_condition=condition,
            )
            assert step.wait_condition == condition


class TestConfigurationComplexity:
    """Test complex configuration scenarios"""

    def test_multi_step_workflow_configuration(self):
        """Test configuration with multiple workflow steps"""
        selections = [
            ElementSelection("items", ".product", "items_container", "Products"),
            ElementSelection("title", ".title", "data_field", "Title"),
            ElementSelection("detail", ".detail", "data_field", "Detail"),
            ElementSelection("review", ".review", "data_field", "Review"),
        ]

        workflows = [
            WorkflowStep(
                "get_details",
                "click",
                ".detail-link",
                "Get product details",
                ["detail"],
            ),
            WorkflowStep(
                "get_reviews",
                "open_new_tab",
                ".review-link",
                "Get reviews in new tab",
                ["review"],
            ),
        ]

        config = CrawlerConfiguration(
            name="Complex Config",
            base_url="https://shop.com",
            selections=selections,
            workflows=workflows,
        )

        # Verify configuration structure
        assert len(config.selections) == 4
        assert len(config.workflows) == 2

        # Verify workflow relationships
        detail_workflow = config.workflows[0]
        review_workflow = config.workflows[1]

        assert detail_workflow.action == "click"
        assert review_workflow.action == "open_new_tab"
        assert "detail" in detail_workflow.extract_fields
        assert "review" in review_workflow.extract_fields

    def test_configuration_with_all_element_types(self):
        """Test configuration containing all element types"""
        selections = [
            ElementSelection("items", ".item", "items_container", "Items container"),
            ElementSelection("title", ".title", "data_field", "Data field"),
            ElementSelection("next", ".next", "pagination", "Pagination element"),
            ElementSelection("link", ".link", "navigation", "Navigation element"),
        ]

        config = CrawlerConfiguration(
            name="All Types",
            base_url="https://test.com",
            selections=selections,
            workflows=[],
        )

        # Count selections by type
        type_counts = {}
        for selection in config.selections:
            type_counts[selection.element_type] = (
                type_counts.get(selection.element_type, 0) + 1
            )

        assert type_counts["items_container"] == 1
        assert type_counts["data_field"] == 1
        assert type_counts["pagination"] == 1
        assert type_counts["navigation"] == 1
