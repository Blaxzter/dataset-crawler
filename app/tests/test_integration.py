#!/usr/bin/env python3
"""
Integration tests for the crawler system

Tests end-to-end functionality across multiple components.
"""

import pytest
import asyncio
import tempfile
import os
import json
from unittest.mock import Mock, AsyncMock, patch

from app.core.crawler import PaginatedCrawler, CrawlerConfig
from app.core.config import PresetConfigs
from app.advanced.advanced_crawler import AdvancedCrawler, load_interactive_config
from app.interactive.configurator import WorkflowConfigurator
from app.models import CrawlerConfiguration, ElementSelection, WorkflowStep


@pytest.mark.asyncio
class TestBasicCrawlerIntegration:
    """Test integration between config and basic crawler"""

    async def test_preset_config_with_crawler_integration(self):
        """Test using preset configurations with PaginatedCrawler"""
        # Get a preset configuration
        site_config = PresetConfigs.quotes_to_scrape()
        
        # Convert to CrawlerConfig
        crawler_config = CrawlerConfig(
            base_url=site_config.base_url,
            selectors=site_config.selectors,
            pagination_selector=site_config.pagination_selector,
            max_pages=1,  # Limit for testing
            delay_ms=site_config.delay_ms,
            headless=True
        )
        
        # Verify configuration structure
        assert crawler_config.base_url == "http://quotes.toscrape.com/"
        assert 'items' in crawler_config.selectors
        assert 'text' in crawler_config.selectors
        assert 'author' in crawler_config.selectors
        assert 'tags' in crawler_config.selectors
        assert crawler_config.pagination_selector == 'li.next a'

    def test_all_preset_configs_are_valid(self):
        """Test that all preset configurations are properly structured"""
        presets = [
            PresetConfigs.hacker_news_jobs(),
            PresetConfigs.quotes_to_scrape(),
            PresetConfigs.reddit_subreddit("python")
        ]
        
        for preset in presets:
            # Check required fields
            assert hasattr(preset, 'name')
            assert hasattr(preset, 'base_url')
            assert hasattr(preset, 'selectors')
            assert isinstance(preset.selectors, dict)
            assert 'items' in preset.selectors
            
            # Check URL validity
            assert preset.base_url.startswith(('http://', 'https://'))
            
            # Check pagination is configured
            assert hasattr(preset, 'pagination_selector')
            
            # Check timing settings
            assert hasattr(preset, 'delay_ms')
            assert isinstance(preset.delay_ms, int)
            assert preset.delay_ms > 0


@pytest.mark.asyncio
class TestAdvancedCrawlerIntegration:
    """Test integration of advanced crawler components"""

    def setup_method(self):
        """Set up test fixtures"""
        self.selections = [
            ElementSelection("items", ".product", "items_container", "Products"),
            ElementSelection("title", ".title", "data_field", "Title"),
            ElementSelection("price", ".price", "data_field", "Price"),
            ElementSelection("detail", ".detail", "data_field", "Detail description")
        ]
        
        self.workflows = [
            WorkflowStep(
                step_id="get_details",
                action="click",
                target_selector=".detail-link",
                description="Get product details",
                extract_fields=["detail"],
                wait_condition="networkidle"
            )
        ]
        
        self.config = CrawlerConfiguration(
            name="Integration Test",
            base_url="https://test.com",
            selections=self.selections,
            workflows=self.workflows,
            max_pages=1
        )

    def test_configuration_to_crawler_integration(self):
        """Test that CrawlerConfiguration integrates properly with AdvancedCrawler"""
        crawler = AdvancedCrawler(self.config, headless=True)
        
        # Test crawler has access to configuration
        assert crawler.config == self.config
        
        # Test helper methods work with configuration
        items_selector = crawler._get_items_selector()
        assert items_selector is not None
        assert items_selector.selector == ".product"
        
        title_selection = crawler._find_selection_by_name("title")
        assert title_selection is not None
        assert title_selection.selector == ".title"

    def test_workflow_builder_to_configuration_integration(self):
        """Test WorkflowBuilder integration with configuration"""
        from app.advanced_crawler import WorkflowBuilder
        
        builder = WorkflowBuilder()
        workflows = builder.add_click_and_extract(
            "step1", ".link", ["field1"], "Test step"
        ).add_new_tab_extraction(
            "step2", ".external", ["field2"], "External step"
        ).build()
        
        # Create configuration with built workflows
        config = CrawlerConfiguration(
            name="Builder Integration",
            base_url="https://test.com",
            selections=self.selections,
            workflows=workflows
        )
        
        # Verify workflows are properly integrated
        assert len(config.workflows) == 2
        assert all(isinstance(w, WorkflowStep) for w in config.workflows)
        assert config.workflows[0].action == "click"
        assert config.workflows[1].action == "open_new_tab"


class TestConfigurationFileIntegration:
    """Test configuration file loading and saving integration"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_save_and_load_configuration_roundtrip(self):
        """Test saving and loading configuration preserves all data"""
        # Create complex configuration
        selections = [
            ElementSelection(
                name="items",
                selector=".product-card",
                element_type="items_container",
                description="Product cards"
            ),
            ElementSelection(
                name="title",
                selector=".product-title",
                element_type="data_field",
                description="Product title",
                extraction_type="text"
            ),
            ElementSelection(
                name="link",
                selector=".product-link",
                element_type="navigation",
                description="Product link",
                extraction_type="href",
                workflow_action="click",
                original_content="View Details"
            )
        ]
        
        workflows = [
            WorkflowStep(
                step_id="get_details",
                action="click",
                target_selector=".product-link",
                description="Get product details",
                extract_fields=["description", "specs"],
                wait_condition="networkidle"
            )
        ]
        
        pagination_config = ElementSelection(
            name="next_page",
            selector=".pagination .next",
            element_type="pagination",
            description="Next page button",
            original_content="Next"
        )
        
        original_config = CrawlerConfiguration(
            name="Roundtrip Test",
            base_url="https://shop.com/products",
            selections=selections,
            workflows=workflows,
            pagination_config=pagination_config,
            max_pages=5,
            delay_ms=2000
        )
        
        # Save configuration manually (simulating the save process)
        from dataclasses import asdict
        config_dict = asdict(original_config)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2)
        
        # Load configuration using the function
        loaded_config = load_interactive_config(self.config_file)
        
        # Verify all data was preserved
        assert loaded_config.name == original_config.name
        assert loaded_config.base_url == original_config.base_url
        assert loaded_config.max_pages == original_config.max_pages
        assert loaded_config.delay_ms == original_config.delay_ms
        
        # Check selections
        assert len(loaded_config.selections) == len(original_config.selections)
        for orig, loaded in zip(original_config.selections, loaded_config.selections):
            assert orig.name == loaded.name
            assert orig.selector == loaded.selector
            assert orig.element_type == loaded.element_type
            assert orig.extraction_type == loaded.extraction_type
        
        # Check workflows
        assert len(loaded_config.workflows) == len(original_config.workflows)
        for orig, loaded in zip(original_config.workflows, loaded_config.workflows):
            assert orig.step_id == loaded.step_id
            assert orig.action == loaded.action
            assert orig.target_selector == loaded.target_selector
            assert orig.extract_fields == loaded.extract_fields
        
        # Check pagination config
        assert loaded_config.pagination_config.name == original_config.pagination_config.name
        assert loaded_config.pagination_config.selector == original_config.pagination_config.selector


@pytest.mark.asyncio
class TestWorkflowConfiguratorIntegration:
    """Test integration between WorkflowConfigurator and other components"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Patch the config directory to use temp directory
        with patch.object(WorkflowConfigurator, '_ensure_config_directory'):
            self.configurator = WorkflowConfigurator()
            self.configurator.config_directory = self.temp_dir

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_programmatic_to_advanced_crawler_integration(self):
        """Test programmatic workflow creation to AdvancedCrawler integration"""
        # Create programmatic workflow
        workflow_builder = self.configurator.create_programmatic_workflow(
            name="integration_test",
            base_url="https://test.com",
            items_selector=".item",
            data_fields={"title": ".title", "price": ".price"}
        )
        
        # Add workflow steps
        workflow_steps = workflow_builder.add_click_and_extract(
            "details", ".detail-link", ["description"], "Get details"
        ).build()
        
        self.configurator.add_workflow_to_config("integration_test", workflow_steps)
        
        # Get configuration and create crawler
        config = self.configurator.configurations["integration_test"]
        crawler = AdvancedCrawler(config, headless=True)
        
        # Verify crawler can access all configuration elements
        assert crawler.config == config
        
        items_selector = crawler._get_items_selector()
        assert items_selector.selector == ".item"
        
        title_selection = crawler._find_selection_by_name("title")
        assert title_selection.selector == ".title"
        
        assert len(crawler.config.workflows) == 1
        assert crawler.config.workflows[0].step_id == "details"

    def test_file_save_load_integration(self):
        """Test saving and loading configurations through WorkflowConfigurator"""
        # Create configuration
        workflow_builder = self.configurator.create_programmatic_workflow(
            name="file_test",
            base_url="https://test.com",
            items_selector=".item",
            data_fields={"title": ".title"}
        )
        
        # Save configuration to file
        config = self.configurator.configurations["file_test"]
        config_file = os.path.join(self.temp_dir, "file_test.json")
        
        from dataclasses import asdict
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(config), f)
        
        # Clear configurations and reload
        self.configurator.configurations.clear()
        
        loaded_config = self.configurator.load_configuration("file_test.json")
        
        assert loaded_config is not None
        assert loaded_config.name == "file_test"
        assert loaded_config.base_url == "https://test.com"
        assert "file_test" in self.configurator.configurations


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow scenarios"""

    def test_complex_workflow_configuration_structure(self):
        """Test that complex workflow configurations maintain proper structure"""
        
        # Create a complex scenario with multiple workflow types
        selections = [
            # Basic container and data
            ElementSelection("products", ".product-card", "items_container", "Product cards"),
            ElementSelection("title", ".title", "data_field", "Product title"),
            ElementSelection("price", ".price", "data_field", "Current price"),
            
            # Detail page fields
            ElementSelection("description", ".full-description", "data_field", "Product description"),
            ElementSelection("specifications", ".spec-table", "data_field", "Technical specs"),
            
            # Review page fields  
            ElementSelection("reviews", ".review-text", "data_field", "Customer reviews"),
            ElementSelection("rating", ".average-rating", "data_field", "Average rating"),
            
            # Navigation elements
            ElementSelection("detail_link", ".product-title a", "navigation", "Product detail link"),
            ElementSelection("review_link", ".reviews-tab a", "navigation", "Reviews tab link"),
            
            # Pagination
            ElementSelection("next_page", ".pagination .next", "pagination", "Next page")
        ]
        
        workflows = [
            WorkflowStep(
                step_id="get_product_details",
                action="click",
                target_selector=".product-title a",
                description="Navigate to product details page",
                extract_fields=["description", "specifications"],
                wait_condition="networkidle"
            ),
            WorkflowStep(
                step_id="get_customer_reviews",
                action="open_new_tab",
                target_selector=".reviews-tab a",
                description="Open reviews in new tab",
                extract_fields=["reviews", "rating"],
                wait_condition="networkidle"
            )
        ]
        
        # Find pagination config from selections
        pagination_config = next(
            (s for s in selections if s.element_type == "pagination"), 
            None
        )
        
        config = CrawlerConfiguration(
            name="Complex E-commerce Crawler",
            base_url="https://shop.example.com/products",
            selections=selections,
            workflows=workflows,
            pagination_config=pagination_config,
            max_pages=10,
            delay_ms=1500
        )
        
        # Verify configuration structure
        assert len(config.selections) == 10
        assert len(config.workflows) == 2
        assert config.pagination_config is not None
        
        # Verify selection types distribution
        type_counts = {}
        for selection in config.selections:
            type_counts[selection.element_type] = type_counts.get(selection.element_type, 0) + 1
        
        assert type_counts['items_container'] == 1
        assert type_counts['data_field'] == 6
        assert type_counts['navigation'] == 2
        assert type_counts['pagination'] == 1
        
        # Verify workflow steps reference valid fields
        all_field_names = {s.name for s in config.selections if s.element_type == 'data_field'}
        
        for workflow in config.workflows:
            if workflow.extract_fields:
                for field in workflow.extract_fields:
                    assert field in all_field_names, f"Workflow references unknown field: {field}"

    def test_workflow_configurator_complete_flow(self):
        """Test complete flow through WorkflowConfigurator"""
        configurator = WorkflowConfigurator()
        
        # Step 1: Create programmatic workflow
        workflow_builder = configurator.create_programmatic_workflow(
            name="complete_flow_test",
            base_url="https://test.com",
            items_selector=".item",
            data_fields={"title": ".title", "summary": ".summary"}
        )
        
        # Step 2: Add workflow steps
        workflow_steps = workflow_builder.add_click_and_extract(
            "details", ".detail-link", ["full_content"], "Get full content"
        ).build()
        
        configurator.add_workflow_to_config("complete_flow_test", workflow_steps)
        
        # Step 3: Verify configuration is ready for AdvancedCrawler
        config = configurator.configurations["complete_flow_test"]
        
        # Should be able to create AdvancedCrawler without errors
        crawler = AdvancedCrawler(config, headless=True)
        
        # Verify crawler can find all required elements
        items_selector = crawler._get_items_selector()
        assert items_selector is not None
        
        title_field = crawler._find_selection_by_name("title")
        assert title_field is not None
        
        # Verify workflows are accessible
        assert len(crawler.config.workflows) == 1
        assert crawler.config.workflows[0].step_id == "details"


class TestConfigurationValidation:
    """Test configuration validation across components"""

    def test_valid_configuration_requirements(self):
        """Test that configurations meet minimum requirements"""
        
        # Test valid minimal configuration
        minimal_config = CrawlerConfiguration(
            name="Minimal",
            base_url="https://test.com",
            selections=[
                ElementSelection("items", ".item", "items_container", "Items")
            ],
            workflows=[]
        )
        
        # Should be able to create crawler
        crawler = AdvancedCrawler(minimal_config)
        assert crawler._get_items_selector() is not None

    def test_configuration_missing_items_container(self):
        """Test configuration without items container"""
        
        # Configuration with only data fields, no items container
        no_items_config = CrawlerConfiguration(
            name="No Items",
            base_url="https://test.com",
            selections=[
                ElementSelection("title", ".title", "data_field", "Title")
            ],
            workflows=[]
        )
        
        crawler = AdvancedCrawler(no_items_config)
        assert crawler._get_items_selector() is None

    def test_workflow_field_reference_validation(self):
        """Test that workflow fields reference existing selections"""
        
        selections = [
            ElementSelection("items", ".item", "items_container", "Items"),
            ElementSelection("existing_field", ".field", "data_field", "Existing field")
        ]
        
        # Workflow referencing non-existent field
        workflows = [
            WorkflowStep(
                "test_step", "click", ".link", "Test",
                extract_fields=["nonexistent_field"]
            )
        ]
        
        config = CrawlerConfiguration(
            name="Invalid Refs",
            base_url="https://test.com",
            selections=selections,
            workflows=workflows
        )
        
        crawler = AdvancedCrawler(config)
        
        # Should not find the non-existent field
        assert crawler._find_selection_by_name("existing_field") is not None
        assert crawler._find_selection_by_name("nonexistent_field") is None


class TestErrorHandlingIntegration:
    """Test error handling across integrated components"""

    def test_configuration_loading_error_handling(self):
        """Test error handling in configuration loading"""
        configurator = WorkflowConfigurator()
        
        # Test loading non-existent file
        config = configurator.load_configuration("nonexistent.json")
        assert config is None
        
        # Test loading file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content {")
            invalid_file = f.name
        
        try:
            config = configurator.load_configuration(invalid_file)
            assert config is None
        finally:
            os.unlink(invalid_file)

    @pytest.mark.asyncio  
    async def test_crawler_error_handling(self):
        """Test error handling in crawler operations"""
        config = CrawlerConfiguration(
            name="Error Test",
            base_url="https://invalid-url-that-should-fail.com",
            selections=[
                ElementSelection("items", ".item", "items_container", "Items")
            ],
            workflows=[]
        )
        
        # Creating crawler should not fail
        crawler = AdvancedCrawler(config, headless=True)
        assert crawler.config == config
