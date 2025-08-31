#!/usr/bin/env python3
"""
Unit tests for workflow_configurator.py

Tests the workflow configuration and management system.
"""

import pytest
import asyncio
import os
import json
from unittest.mock import Mock, AsyncMock, patch, mock_open

from app.interactive.configurator import WorkflowConfigurator
from app.models import CrawlerConfiguration, ElementSelection, WorkflowStep
from app.advanced.workflow_builder import WorkflowBuilder


class TestWorkflowConfigurator:
    """Test WorkflowConfigurator functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.configurator = WorkflowConfigurator()

    def test_workflow_configurator_initialization(self):
        """Test WorkflowConfigurator initialization"""
        configurator = WorkflowConfigurator()

        assert configurator.configurations == {}
        assert configurator.config_directory == "crawler_configs"

    @patch("os.path.exists", return_value=False)
    @patch("os.makedirs")
    def test_ensure_config_directory_creates_directory(
        self, mock_makedirs, mock_exists
    ):
        """Test that config directory is created if it doesn't exist"""
        configurator = WorkflowConfigurator()

        mock_makedirs.assert_called_once_with("crawler_configs")

    @patch("os.path.exists", return_value=True)
    @patch("os.makedirs")
    def test_ensure_config_directory_exists(self, mock_makedirs, mock_exists):
        """Test that existing config directory is not recreated"""
        configurator = WorkflowConfigurator()
        configurator._ensure_config_directory()

        mock_makedirs.assert_not_called()

    def test_create_programmatic_workflow(self):
        """Test creating a programmatic workflow"""
        configurator = WorkflowConfigurator()

        data_fields = {
            "title": ".product-title",
            "price": ".price-tag",
            "rating": ".rating",
        }

        workflow_builder = configurator.create_programmatic_workflow(
            name="test_workflow",
            base_url="https://shop.com",
            items_selector=".product-card",
            data_fields=data_fields,
            pagination_selector=".next-page",
        )

        # Check that configuration was created
        assert "test_workflow" in configurator.configurations
        config = configurator.configurations["test_workflow"]

        assert config.name == "test_workflow"
        assert config.base_url == "https://shop.com"

        # Check selections
        selections_by_type = {}
        for selection in config.selections:
            if selection.element_type not in selections_by_type:
                selections_by_type[selection.element_type] = []
            selections_by_type[selection.element_type].append(selection)

        # Should have items container
        assert "items_container" in selections_by_type
        assert len(selections_by_type["items_container"]) == 1
        assert selections_by_type["items_container"][0].selector == ".product-card"

        # Should have data fields
        assert "data_field" in selections_by_type
        assert len(selections_by_type["data_field"]) == 3

        # Check pagination config
        assert config.pagination_config is not None
        assert config.pagination_config.selector == ".next-page"

        # Check return value is WorkflowBuilder
        assert isinstance(workflow_builder, WorkflowBuilder)

    def test_add_workflow_to_config(self):
        """Test adding workflow steps to existing configuration"""
        configurator = WorkflowConfigurator()

        # Create base configuration
        config = CrawlerConfiguration(
            name="test_config", base_url="https://test.com", selections=[], workflows=[]
        )
        configurator.configurations["test_config"] = config

        # Create workflow steps
        workflow_steps = [
            WorkflowStep("step1", "click", ".link1", "First step"),
            WorkflowStep("step2", "extract", ".data", "Second step"),
        ]

        configurator.add_workflow_to_config("test_config", workflow_steps)

        # Check that workflows were added
        updated_config = configurator.configurations["test_config"]
        assert len(updated_config.workflows) == 2
        assert updated_config.workflows[0].step_id == "step1"
        assert updated_config.workflows[1].step_id == "step2"

    def test_add_workflow_to_nonexistent_config(self):
        """Test adding workflow to non-existent configuration"""
        configurator = WorkflowConfigurator()

        workflow_steps = [WorkflowStep("step1", "click", ".link", "Test")]

        # Should not raise exception, but workflow won't be added
        configurator.add_workflow_to_config("nonexistent", workflow_steps)

        assert "nonexistent" not in configurator.configurations

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_load_configuration_success(self, mock_json_load, mock_file):
        """Test successful configuration loading"""
        config_data = {
            "name": "Loaded Config",
            "base_url": "https://loaded.com",
            "selections": [
                {
                    "name": "title",
                    "selector": ".title",
                    "element_type": "data_field",
                    "description": "Title",
                    "extraction_type": "text",
                    "attribute_name": None,
                    "workflow_action": None,
                    "original_content": None,
                    "verification_attributes": None,
                    "page_url": None,
                }
            ],
            "workflows": [
                {
                    "step_id": "step1",
                    "action": "click",
                    "target_selector": ".link",
                    "description": "Test step",
                    "extract_fields": ["detail"],
                    "wait_condition": "networkidle",
                    "wait_selector": None,
                }
            ],
            "pagination_config": {
                "name": "next",
                "selector": ".next",
                "element_type": "pagination",
                "description": "Next page",
                "extraction_type": "text",
                "attribute_name": None,
                "workflow_action": None,
                "original_content": None,
                "verification_attributes": None,
                "page_url": None,
            },
            "max_pages": 10,
            "delay_ms": 2000,
        }

        mock_json_load.return_value = config_data

        configurator = WorkflowConfigurator()
        config = configurator.load_configuration("test_config.json")

        assert config is not None
        assert config.name == "Loaded Config"
        assert config.base_url == "https://loaded.com"
        assert len(config.selections) == 1
        assert len(config.workflows) == 1
        assert config.pagination_config is not None
        assert config.max_pages == 10
        assert config.delay_ms == 2000

        # Check that config was added to configurations
        assert "Loaded Config" in configurator.configurations

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_configuration_file_not_found(self, mock_file):
        """Test loading configuration when file doesn't exist"""
        configurator = WorkflowConfigurator()

        config = configurator.load_configuration("nonexistent.json")

        assert config is None
        assert "nonexistent" not in configurator.configurations

    @patch("builtins.open")
    @patch("json.load", side_effect=json.JSONDecodeError("Invalid JSON", "doc", 0))
    def test_load_configuration_invalid_json(self, mock_json_load, mock_file):
        """Test loading configuration with invalid JSON"""
        configurator = WorkflowConfigurator()

        config = configurator.load_configuration("invalid.json")

        assert config is None

    def test_list_configurations_empty(self, capsys):
        """Test list_configurations with no configurations"""
        configurator = WorkflowConfigurator()

        with patch("os.listdir", return_value=[]):
            configurator.list_configurations()

        captured = capsys.readouterr()
        assert "No configurations found" in captured.out

    def test_list_configurations_with_data(self, capsys):
        """Test list_configurations with loaded configurations"""
        configurator = WorkflowConfigurator()

        # Add a configuration to memory
        config = CrawlerConfiguration(
            name="Memory Config",
            base_url="https://test.com",
            selections=[
                ElementSelection("title", ".title", "data_field", "Title"),
                ElementSelection("price", ".price", "data_field", "Price"),
            ],
            workflows=[WorkflowStep("step1", "click", ".link", "Test step")],
        )
        configurator.configurations["Memory Config"] = config

        # Mock file listing
        with patch("os.listdir", return_value=["saved_config.json", "other_file.txt"]):
            configurator.list_configurations()

        captured = capsys.readouterr()
        assert "Memory Config" in captured.out
        assert "2 fields, 1 workflows" in captured.out
        assert "saved_config" in captured.out
        assert "other_file.txt" not in captured.out  # Should filter out non-JSON files


@pytest.mark.asyncio
class TestWorkflowConfiguratorIntegration:
    """Integration tests for WorkflowConfigurator with mocked dependencies"""

    def setup_method(self):
        """Set up test fixtures"""
        self.configurator = WorkflowConfigurator()

    @patch("app.interactive.configurator.InteractiveSelector")
    async def test_create_interactive_configuration(self, mock_selector_class):
        """Test creating interactive configuration"""
        # Setup mocks
        mock_selector = AsyncMock()
        mock_selector_class.return_value.__aenter__ = AsyncMock(
            return_value=mock_selector
        )
        mock_selector_class.return_value.__aexit__ = AsyncMock(return_value=None)

        # Mock configuration creation
        test_config = CrawlerConfiguration(
            name="test_config", base_url="https://test.com", selections=[], workflows=[]
        )

        mock_selector.start_selection_session = AsyncMock()
        mock_selector.get_configuration = AsyncMock(return_value=test_config)
        mock_selector.save_configuration = AsyncMock()
        mock_selector.preview_configuration = Mock()

        # Test the method
        result = await self.configurator.create_interactive_configuration(
            "https://test.com", "test_config"
        )

        assert result is not None
        assert result.name == "test_config"
        assert "test_config" in self.configurator.configurations

        # Verify method calls
        mock_selector.start_selection_session.assert_called_once_with(
            "https://test.com"
        )
        mock_selector.get_configuration.assert_called_once()
        mock_selector.save_configuration.assert_called_once()
        mock_selector.preview_configuration.assert_called_once()

    @patch("app.interactive.configurator.AdvancedCrawler")
    async def test_test_configuration(self, mock_crawler_class):
        """Test testing a configuration"""
        # Create test configuration
        config = CrawlerConfiguration(
            name="test_config", base_url="https://test.com", selections=[], workflows=[]
        )
        self.configurator.configurations["test_config"] = config

        # Setup crawler mock as async context manager
        mock_crawler = AsyncMock()
        mock_crawler_instance = AsyncMock()
        mock_crawler_instance.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler_instance.__aexit__ = AsyncMock(return_value=None)
        mock_crawler_class.return_value = mock_crawler_instance

        # Mock crawl results with realistic data
        from app.advanced.advanced_crawler import ExtractionResult

        test_results = [
            ExtractionResult(
                data={"title": "Test Product"},
                source_url="https://test.com/product1",
                extraction_time="2024-01-01T10:00:00",
                workflow_path=["basic_extraction"],
            )
        ]
        mock_crawler.crawl_with_workflows = AsyncMock(return_value=test_results)
        mock_crawler.get_extraction_summary = Mock(
            return_value={"total_items": 1, "unique_sources": 1, "workflow_usage": 0}
        )

        # Test the method
        result = await self.configurator.test_configuration("test_config", max_pages=1)

        # Verify configuration was modified with max_pages
        assert config.max_pages == 1

        # Verify crawler was instantiated correctly
        mock_crawler_class.assert_called_once_with(config, headless=False)

        # Verify async context manager was used
        mock_crawler_instance.__aenter__.assert_called_once()
        mock_crawler_instance.__aexit__.assert_called_once()

        # Verify crawler methods were called
        mock_crawler.crawl_with_workflows.assert_called_once()
        mock_crawler.get_extraction_summary.assert_called_once()

        assert result is True

    async def test_test_configuration_not_found(self):
        """Test testing non-existent configuration"""
        result = await self.configurator.test_configuration("nonexistent")
        assert result is False

    @patch("app.interactive.configurator.AdvancedCrawler")
    async def test_run_full_crawl(self, mock_crawler_class):
        """Test running full crawl"""
        # Create test configuration
        config = CrawlerConfiguration(
            name="full_crawl_test",
            base_url="https://test.com",
            selections=[],
            workflows=[],
        )
        self.configurator.configurations["full_crawl_test"] = config

        # Setup crawler mock as async context manager
        mock_crawler = AsyncMock()
        mock_crawler_instance = AsyncMock()
        mock_crawler_instance.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler_instance.__aexit__ = AsyncMock(return_value=None)
        mock_crawler_class.return_value = mock_crawler_instance

        # Mock crawl results - test with realistic data structure
        from app.advanced.advanced_crawler import ExtractionResult

        test_results = [
            ExtractionResult(
                data={"title": "Test Item 1", "price": "$10.99"},
                source_url="https://test.com/item1",
                extraction_time="2024-01-01T10:00:00",
                workflow_path=["basic_extraction"],
            ),
            ExtractionResult(
                data={"title": "Test Item 2", "price": "$15.99"},
                source_url="https://test.com/item2",
                extraction_time="2024-01-01T10:01:00",
                workflow_path=["basic_extraction"],
            ),
        ]

        mock_crawler.crawl_with_workflows = AsyncMock(return_value=test_results)
        mock_crawler.save_results = Mock()
        mock_crawler.get_extraction_summary = Mock(
            return_value={"total_items": 2, "unique_sources": 2, "workflow_usage": 1}
        )

        # Test the method
        result = await self.configurator.run_full_crawl(
            "full_crawl_test", "output.json"
        )

        # Verify behavior: configuration was passed correctly
        mock_crawler_class.assert_called_once_with(config, headless=True)

        # Verify async context manager was used
        mock_crawler_instance.__aenter__.assert_called_once()
        mock_crawler_instance.__aexit__.assert_called_once()

        # Verify crawler methods were called
        mock_crawler.crawl_with_workflows.assert_called_once()
        mock_crawler.save_results.assert_called_once_with("output.json")
        mock_crawler.get_extraction_summary.assert_called_once()

        # Verify return value
        assert result == test_results
        assert len(result) == 2
        assert result[0].data["title"] == "Test Item 1"

    async def test_run_full_crawl_not_found(self):
        """Test running full crawl with non-existent configuration"""
        result = await self.configurator.run_full_crawl("nonexistent")
        assert result is None

    @patch("app.interactive.configurator.AdvancedCrawler")
    async def test_run_full_crawl_with_exception(self, mock_crawler_class):
        """Test run_full_crawl handles exceptions properly"""
        # Create test configuration
        config = CrawlerConfiguration(
            name="failing_crawl_test",
            base_url="https://test.com",
            selections=[],
            workflows=[],
        )
        self.configurator.configurations["failing_crawl_test"] = config

        # Setup crawler mock that raises an exception
        mock_crawler = AsyncMock()
        mock_crawler_instance = AsyncMock()
        mock_crawler_instance.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler_instance.__aexit__ = AsyncMock(return_value=None)
        mock_crawler_class.return_value = mock_crawler_instance

        # Make crawl_with_workflows raise an exception
        mock_crawler.crawl_with_workflows = AsyncMock(
            side_effect=Exception("Network timeout")
        )

        # Test the method handles exceptions gracefully
        result = await self.configurator.run_full_crawl(
            "failing_crawl_test", "output.json"
        )

        # Should return None when exception occurs
        assert result is None

        # Verify crawler was still instantiated and context manager used
        mock_crawler_class.assert_called_once_with(config, headless=True)
        mock_crawler_instance.__aenter__.assert_called_once()
        mock_crawler_instance.__aexit__.assert_called_once()

        # Verify the failing method was attempted
        mock_crawler.crawl_with_workflows.assert_called_once()

    @patch("app.interactive.configurator.AdvancedCrawler")
    async def test_run_full_crawl_default_output_filename(self, mock_crawler_class):
        """Test run_full_crawl uses default output filename when none provided"""
        # Create test configuration
        config = CrawlerConfiguration(
            name="default_output_test",
            base_url="https://test.com",
            selections=[],
            workflows=[],
        )
        self.configurator.configurations["default_output_test"] = config

        # Setup crawler mock
        mock_crawler = AsyncMock()
        mock_crawler_instance = AsyncMock()
        mock_crawler_instance.__aenter__ = AsyncMock(return_value=mock_crawler)
        mock_crawler_instance.__aexit__ = AsyncMock(return_value=None)
        mock_crawler_class.return_value = mock_crawler_instance

        from app.advanced.advanced_crawler import ExtractionResult

        test_results = [
            ExtractionResult(
                data={"test": "data"},
                source_url="https://test.com",
                extraction_time="2024-01-01T10:00:00",
                workflow_path=["basic"],
            )
        ]

        mock_crawler.crawl_with_workflows = AsyncMock(return_value=test_results)
        mock_crawler.save_results = Mock()
        mock_crawler.get_extraction_summary = Mock(
            return_value={"total_items": 1, "unique_sources": 1, "workflow_usage": 1}
        )

        # Test with no output_file specified
        result = await self.configurator.run_full_crawl("default_output_test")

        # Verify default filename was used
        mock_crawler.save_results.assert_called_once_with(
            "default_output_test_results.json"
        )
        assert result == test_results


class TestWorkflowConfiguratorProgrammaticWorkflows:
    """Test programmatic workflow creation functionality"""

    def test_create_workflow_with_all_field_types(self):
        """Test creating workflow with various field types"""
        configurator = WorkflowConfigurator()

        data_fields = {
            "text_field": ".text",
            "link_field": ".link",
            "image_field": ".image img",
            "attribute_field": ".custom",
        }

        workflow_builder = configurator.create_programmatic_workflow(
            name="comprehensive_test",
            base_url="https://test.com",
            items_selector=".item",
            data_fields=data_fields,
        )

        config = configurator.configurations["comprehensive_test"]

        # Check that all data fields were created
        data_field_selections = [
            s for s in config.selections if s.element_type == "data_field"
        ]
        assert len(data_field_selections) == 4

        # Check specific selectors
        selector_map = {s.name: s.selector for s in data_field_selections}
        assert selector_map["text_field"] == ".text"
        assert selector_map["link_field"] == ".link"
        assert selector_map["image_field"] == ".image img"
        assert selector_map["attribute_field"] == ".custom"

    def test_create_workflow_without_pagination(self):
        """Test creating workflow without pagination"""
        configurator = WorkflowConfigurator()

        workflow_builder = configurator.create_programmatic_workflow(
            name="no_pagination",
            base_url="https://test.com",
            items_selector=".item",
            data_fields={"title": ".title"},
            pagination_selector=None,
        )

        config = configurator.configurations["no_pagination"]
        assert config.pagination_config is None

    def test_workflow_builder_integration(self):
        """Test integration between WorkflowConfigurator and WorkflowBuilder"""
        configurator = WorkflowConfigurator()

        # Create base workflow
        workflow_builder = configurator.create_programmatic_workflow(
            name="builder_test",
            base_url="https://test.com",
            items_selector=".item",
            data_fields={"title": ".title"},
        )

        # Add workflow steps using builder
        workflow_steps = (
            workflow_builder.add_click_and_extract(
                "get_details",
                ".detail-link",
                ["description", "specs"],
                "Get product details",
            )
            .add_new_tab_extraction(
                "get_reviews", ".review-link", ["rating", "comments"], "Get reviews"
            )
            .build()
        )

        configurator.add_workflow_to_config("builder_test", workflow_steps)

        # Verify the workflow was properly integrated
        config = configurator.configurations["builder_test"]
        assert len(config.workflows) == 2
        assert config.workflows[0].step_id == "get_details"
        assert config.workflows[1].step_id == "get_reviews"


class TestConfigurationFileManagement:
    """Test configuration file loading and saving"""

    def setup_method(self):
        """Set up test fixtures"""
        self.configurator = WorkflowConfigurator()

    @patch("os.path.join")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_load_configuration_file_path_handling(
        self, mock_json_load, mock_file, mock_path_join
    ):
        """Test proper file path handling in load_configuration"""
        mock_path_join.return_value = "crawler_configs/test.json"
        mock_json_load.return_value = {
            "name": "Test",
            "base_url": "https://test.com",
            "selections": [],
            "workflows": [],
            "pagination_config": None,
        }

        # Test with .json extension
        config = self.configurator.load_configuration("test.json")
        mock_path_join.assert_called_with("crawler_configs", "test.json")

        # Reset mock
        mock_path_join.reset_mock()

        # Test without .json extension
        config = self.configurator.load_configuration("test")
        mock_path_join.assert_called_with("crawler_configs", "test.json")

    @patch("os.listdir")
    def test_list_configurations_file_filtering(self, mock_listdir, capsys):
        """Test that list_configurations properly filters JSON files"""
        mock_listdir.return_value = [
            "config1.json",
            "config2.json",
            "not_config.txt",
            "data.csv",
            "backup.json",
        ]

        configurator = WorkflowConfigurator()
        configurator.list_configurations()

        captured = capsys.readouterr()

        # Should show JSON files without extension
        assert "config1" in captured.out
        assert "config2" in captured.out
        assert "backup" in captured.out

        # Should not show non-JSON files
        assert "not_config.txt" not in captured.out
        assert "data.csv" not in captured.out
