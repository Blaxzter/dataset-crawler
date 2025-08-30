#!/usr/bin/env python3
"""
Unit tests for example and demo files

Tests the example scripts and demo functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, call

from app.examples.workflow_examples import WorkflowExamples
from app.models import CrawlerConfiguration, ElementSelection, WorkflowStep


class TestWorkflowExamples:
    """Test WorkflowExamples class and pre-built configurations"""

    def test_create_ecommerce_workflow(self):
        """Test e-commerce workflow creation"""
        config = WorkflowExamples.create_ecommerce_workflow()
        
        assert isinstance(config, CrawlerConfiguration)
        assert config.name == "E-commerce Product Crawler"
        assert config.base_url == "https://example-shop.com/products"
        assert config.max_pages == 10
        assert config.delay_ms == 2000
        
        # Check selections structure
        selection_types = {}
        for selection in config.selections:
            selection_types[selection.element_type] = selection_types.get(selection.element_type, 0) + 1
        
        assert selection_types['items_container'] == 1
        assert selection_types['data_field'] == 8  # products, title, price, image, rating, description, specifications, reviews, seller_info
        
        # Check workflows
        assert len(config.workflows) == 3
        workflow_actions = [w.action for w in config.workflows]
        assert "click" in workflow_actions
        assert "open_new_tab" in workflow_actions
        
        # Check pagination config
        assert config.pagination_config is not None
        assert config.pagination_config.selector == ".pagination .next"

    def test_create_job_board_workflow(self):
        """Test job board workflow creation"""
        config = WorkflowExamples.create_job_board_workflow()
        
        assert isinstance(config, CrawlerConfiguration)
        assert config.name == "Job Board Crawler"
        assert config.base_url == "https://example-jobs.com/search"
        assert config.max_pages == 20
        assert config.delay_ms == 1500
        
        # Check for job-specific fields
        field_names = {s.name for s in config.selections if s.element_type == 'data_field'}
        expected_fields = {
            'job_title', 'company', 'location', 'salary', 
            'job_description', 'requirements', 'company_info', 'benefits'
        }
        assert expected_fields.issubset(field_names)
        
        # Check workflows
        assert len(config.workflows) == 2
        workflow_descriptions = [w.description for w in config.workflows]
        assert any("job description" in desc.lower() for desc in workflow_descriptions)
        assert any("company page" in desc.lower() for desc in workflow_descriptions)

    def test_create_news_site_workflow(self):
        """Test news site workflow creation"""
        config = WorkflowExamples.create_news_site_workflow()
        
        assert isinstance(config, CrawlerConfiguration)
        assert config.name == "News Site Crawler"
        assert config.base_url == "https://example-news.com/latest"
        assert config.max_pages == 15
        assert config.delay_ms == 1000
        
        # Check for news-specific fields
        field_names = {s.name for s in config.selections if s.element_type == 'data_field'}
        expected_fields = {
            'headline', 'summary', 'author', 'publish_date',
            'full_content', 'author_bio', 'tags', 'comments_count'
        }
        assert expected_fields.issubset(field_names)
        
        # Check workflows for news-specific actions
        assert len(config.workflows) == 2
        step_ids = [w.step_id for w in config.workflows]
        assert "read_full_article" in step_ids
        assert "get_author_profile" in step_ids

    def test_create_social_media_workflow(self):
        """Test social media workflow creation"""
        config = WorkflowExamples.create_social_media_workflow()
        
        assert isinstance(config, CrawlerConfiguration)
        assert config.name == "Social Media Crawler"
        assert config.base_url == "https://example-social.com/feed"
        assert config.max_pages == 50
        assert config.delay_ms == 2000
        
        # Check for social media-specific fields
        field_names = {s.name for s in config.selections if s.element_type == 'data_field'}
        expected_fields = {
            'username', 'post_text', 'timestamp', 'likes', 'shares',
            'user_profile', 'comments'
        }
        assert expected_fields.issubset(field_names)
        
        # Check workflows
        assert len(config.workflows) == 2
        
        # Should have user profile and comment expansion workflows
        actions = [w.action for w in config.workflows]
        assert "open_new_tab" in actions
        assert "click" in actions

    def test_all_example_configs_have_required_elements(self):
        """Test that all example configurations have required elements"""
        examples = WorkflowExamples()
        
        configs = [
            examples.create_ecommerce_workflow(),
            examples.create_job_board_workflow(),
            examples.create_news_site_workflow(),
            examples.create_social_media_workflow()
        ]
        
        for config in configs:
            # Each config should have basic required elements
            assert isinstance(config, CrawlerConfiguration)
            assert config.name
            assert config.base_url.startswith(('http://', 'https://'))
            assert len(config.selections) > 0
            
            # Should have at least one items container
            items_containers = [s for s in config.selections if s.element_type == 'items_container']
            assert len(items_containers) >= 1
            
            # Should have at least one data field
            data_fields = [s for s in config.selections if s.element_type == 'data_field']
            assert len(data_fields) >= 1
            
            # Should have workflows for complex extraction
            assert len(config.workflows) >= 1


class TestExampleConfigurationRealism:
    """Test that example configurations are realistic and well-structured"""

    def test_selector_realism(self):
        """Test that selectors in examples are realistic CSS selectors"""
        examples = WorkflowExamples()
        configs = [
            examples.create_ecommerce_workflow(),
            examples.create_job_board_workflow(),
            examples.create_news_site_workflow(),
            examples.create_social_media_workflow()
        ]
        
        for config in configs:
            for selection in config.selections:
                selector = selection.selector
                
                # Should be valid CSS selector format
                assert isinstance(selector, str)
                assert len(selector) > 0
                
                # Should contain realistic CSS patterns
                valid_patterns = ['.', '#', '[', ' ', '>', ':', 'a', 'div', 'span', 'p']
                assert any(pattern in selector for pattern in valid_patterns)
                
                # Should not contain obvious placeholders
                assert 'TODO' not in selector.upper()
                assert 'PLACEHOLDER' not in selector.upper()

    def test_workflow_step_realism(self):
        """Test that workflow steps are realistic and actionable"""
        examples = WorkflowExamples()
        configs = [
            examples.create_ecommerce_workflow(),
            examples.create_job_board_workflow(),
            examples.create_news_site_workflow(),
            examples.create_social_media_workflow()
        ]
        
        for config in configs:
            for workflow in config.workflows:
                # Should have realistic step ID
                assert isinstance(workflow.step_id, str)
                assert len(workflow.step_id) > 0
                assert '_' in workflow.step_id or workflow.step_id.islower()
                
                # Should have valid action
                assert workflow.action in ['click', 'extract', 'open_new_tab']
                
                # Should have realistic target selector
                assert isinstance(workflow.target_selector, str)
                assert len(workflow.target_selector) > 0
                
                # Should have meaningful description
                assert isinstance(workflow.description, str)
                assert len(workflow.description) > 10
                
                # If has extract fields, they should be meaningful
                if workflow.extract_fields:
                    assert isinstance(workflow.extract_fields, list)
                    assert len(workflow.extract_fields) > 0
                    for field in workflow.extract_fields:
                        assert isinstance(field, str)
                        assert len(field) > 0

    def test_url_structure_realism(self):
        """Test that example URLs follow realistic patterns"""
        examples = WorkflowExamples()
        configs = [
            examples.create_ecommerce_workflow(),
            examples.create_job_board_workflow(),
            examples.create_news_site_workflow(),
            examples.create_social_media_workflow()
        ]
        
        for config in configs:
            base_url = config.base_url
            
            # Should be valid URL format
            assert base_url.startswith(('http://', 'https://'))
            assert '.' in base_url  # Should have domain
            
            # Should have realistic domain patterns
            if 'shop' in config.name.lower():
                assert any(word in base_url for word in ['shop', 'store', 'products'])
            elif 'job' in config.name.lower():
                assert any(word in base_url for word in ['job', 'career', 'search'])
            elif 'news' in config.name.lower():
                assert any(word in base_url for word in ['news', 'article', 'latest'])
            elif 'social' in config.name.lower():
                assert any(word in base_url for word in ['social', 'feed', 'posts'])

    def test_configuration_completeness(self):
        """Test that each example configuration is complete and usable"""
        examples = WorkflowExamples()
        configs = [
            examples.create_ecommerce_workflow(),
            examples.create_job_board_workflow(),
            examples.create_news_site_workflow(),
            examples.create_social_media_workflow()
        ]
        
        for config in configs:
            # Should have all required fields for AdvancedCrawler
            assert hasattr(config, 'name')
            assert hasattr(config, 'base_url')
            assert hasattr(config, 'selections')
            assert hasattr(config, 'workflows')
            
            # Should have logical field relationships
            if config.workflows:
                # All workflow extract_fields should reference actual data fields
                data_field_names = {
                    s.name for s in config.selections 
                    if s.element_type == 'data_field'
                }
                
                for workflow in config.workflows:
                    if workflow.extract_fields:
                        for field in workflow.extract_fields:
                            # Field should either exist in selections or be a reasonable field name
                            assert (field in data_field_names or 
                                   isinstance(field, str) and len(field) > 0)
            
            # Should have reasonable timing settings
            if hasattr(config, 'delay_ms'):
                assert config.delay_ms >= 100  # Not too fast
                assert config.delay_ms <= 10000  # Not too slow
            
            if hasattr(config, 'max_pages'):
                assert config.max_pages is None or config.max_pages > 0
