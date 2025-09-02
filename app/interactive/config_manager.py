#!/usr/bin/env python3
"""
Configuration Management Module for Interactive Selector

This module handles saving, loading, and previewing crawler configurations
created through the interactive element selector.
"""

import json
import logging
from typing import Optional, List
from dataclasses import asdict
from playwright.async_api import Page

# Import shared models to avoid circular dependencies
from app.models import ElementSelection, WorkflowStep, CrawlerConfiguration


class ConfigManager:
    """Manages crawler configuration operations"""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(__name__)
    
    async def extract_configuration(self) -> Optional[CrawlerConfiguration]:
        """Extract the configuration created by user selections"""
        try:
            config_data = await self.page.evaluate(
                "() => window.crawlerConfig || {selections: window.crawlerSelections || [], workflows: []}"
            )

            if not config_data or not config_data.get("selections"):
                self.logger.warning("No configuration data found")
                return None

            # Convert to our dataclass format
            selections = []
            for selection_data in config_data.get("selections", []):
                # Handle both old and new format
                if isinstance(selection_data, dict):
                    selections.append(ElementSelection(**selection_data))
                else:
                    selections.append(selection_data)

            workflows = []
            for workflow_data in config_data.get("workflows", []):
                if isinstance(workflow_data, dict):
                    workflows.append(WorkflowStep(**workflow_data))
                else:
                    workflows.append(workflow_data)

            # Auto-generate intelligent workflows from navigation selections
            nav_selections = [s for s in selections if s.element_type == "navigation"]
            if nav_selections:
                self.logger.info(
                    f"Found {len(nav_selections)} navigation elements, generating intelligent workflows..."
                )
                
                workflows.extend(await self._generate_workflows_from_navigation(nav_selections))

            # Find pagination configuration
            pagination_config = self._find_pagination_config(selections)
            current_url = self.page.url

            return CrawlerConfiguration(
                name=f"Interactive Config - {current_url.split('//')[-1].split('/')[0]}",
                base_url=current_url,
                selections=selections,
                workflows=workflows,
                pagination_config=pagination_config,
            )

        except Exception as e:
            self.logger.error(f"Error extracting configuration: {e}")
            return None
    
    async def _generate_workflows_from_navigation(self, nav_selections: List[ElementSelection]) -> List[WorkflowStep]:
        """Generate intelligent workflows from navigation selections"""
        workflows = []
        
        # Get page selection data for smarter workflow generation
        page_selections = await self.page.evaluate(
            "() => window.crawlerPageSelections || {}"
        )
        original_url = await self.page.evaluate(
            "() => window.crawlerOriginalUrl"
        )

        self.logger.info(
            f"Building workflows from {len(page_selections)} pages of selections..."
        )

        for nav_selection in nav_selections:
            # Find fields selected on detail pages (pages visited via navigation)
            detail_fields = []
            list_page_fields = []

            for page_url, page_selects in page_selections.items():
                if page_url == original_url:  # List page
                    list_page_fields.extend(
                        [
                            s["name"]
                            for s in page_selects
                            if s.get("element_type") in ["data_field", "items_container"]
                        ]
                    )
                else:  # Detail pages
                    detail_fields.extend(
                        [
                            s["name"]
                            for s in page_selects
                            if s.get("element_type") in ["data_field", "items_container"]
                        ]
                    )

            # Only create workflow if we have detail fields to extract
            if detail_fields:
                workflow_step = WorkflowStep(
                    step_id=f"nav_{nav_selection.name}",
                    action="click",
                    target_selector=nav_selection.selector,
                    description=f"Navigate via {nav_selection.name} and extract detail data",
                    extract_fields=detail_fields,
                    wait_condition="networkidle",
                )
                workflows.append(workflow_step)

                self.logger.info(f"✅ Workflow created: {nav_selection.name}")
                self.logger.info(f"   Click: {nav_selection.selector}")
                self.logger.info(f"   Extract: {detail_fields}")
            else:
                self.logger.warning(
                    f"⚠️ Navigation {nav_selection.name} has no detail fields to extract"
                )
                self.logger.info(
                    "   Tip: Navigate to detail page and select data fields there"
                )
        
        return workflows
    
    def _find_pagination_config(self, selections: List[ElementSelection]) -> Optional[ElementSelection]:
        """Find pagination configuration from selections"""
        for selection in selections:
            if selection.element_type == "pagination":
                return selection
        return None
    
    async def save_configuration(self, config: CrawlerConfiguration, filename: str):
        """Save configuration to JSON file"""
        config_dict = asdict(config)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Configuration saved to {filename}")
    
    async def load_configuration(self, filename: str) -> Optional[CrawlerConfiguration]:
        """Load configuration from JSON file"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                config_dict = json.load(f)
            
            # Convert dictionaries back to dataclasses
            selections = [ElementSelection(**sel) for sel in config_dict.get("selections", [])]
            workflows = [WorkflowStep(**wf) for wf in config_dict.get("workflows", [])]
            
            pagination_config = None
            if config_dict.get("pagination_config"):
                pagination_config = ElementSelection(**config_dict["pagination_config"])
            
            return CrawlerConfiguration(
                name=config_dict.get("name", "Loaded Configuration"),
                base_url=config_dict.get("base_url", ""),
                selections=selections,
                workflows=workflows,
                pagination_config=pagination_config,
            )
        
        except Exception as e:
            self.logger.error(f"Error loading configuration from {filename}: {e}")
            return None
    
    def preview_configuration(self, config: CrawlerConfiguration):
        """Print a human-readable preview of the configuration"""
        print(f"\n🔧 Configuration Preview: {config.name}")
        print(f"🌐 Base URL: {config.base_url}")

        if config.selections:
            print(f"\n📊 Data Fields ({len(config.selections)} total):")
            for selection in config.selections:
                print(
                    f"  • {selection.name} ({selection.element_type}): {selection.selector}"
                )

        if config.pagination_config:
            print(f"\n📄 Pagination: {config.pagination_config.selector}")

        if config.workflows:
            print(f"\n🔄 Workflows ({len(config.workflows)} steps):")
            for i, step in enumerate(config.workflows, 1):
                print(f"  {i}. {step.description} -> {step.target_selector}")
                if step.extract_fields:
                    print(f"     Extract: {', '.join(step.extract_fields)}")
    
    def get_configuration_summary(self, config: CrawlerConfiguration) -> dict:
        """Get a summary of the configuration for programmatic use"""
        nav_count = len([s for s in config.selections if s.element_type == "navigation"])
        data_count = len([s for s in config.selections if s.element_type == "data_field"])
        items_count = len([s for s in config.selections if s.element_type == "items_container"])
        pagination_count = 1 if config.pagination_config else 0
        
        return {
            "total_selections": len(config.selections),
            "data_fields": data_count,
            "items_containers": items_count,
            "navigation_elements": nav_count,
            "pagination_elements": pagination_count,
            "workflows": len(config.workflows),
            "has_workflows": len(config.workflows) > 0,
            "workflow_ready": nav_count > 0 and data_count > 0,
        }
    
    def validate_configuration(self, config: CrawlerConfiguration) -> tuple[bool, List[str]]:
        """Validate configuration and return validation status and issues"""
        issues = []
        
        if not config.base_url:
            issues.append("No base URL specified")
        
        if not config.selections:
            issues.append("No elements selected")
        
        # Check for required data fields
        data_fields = [s for s in config.selections if s.element_type == "data_field"]
        if not data_fields:
            issues.append("No data fields selected - cannot extract data")
        
        # Check for item containers if multiple data fields exist
        items_containers = [s for s in config.selections if s.element_type == "items_container"]
        if len(data_fields) > 1 and not items_containers:
            issues.append("Multiple data fields but no items container selected")
        
        # Check workflow consistency
        nav_elements = [s for s in config.selections if s.element_type == "navigation"]
        if nav_elements and not config.workflows:
            issues.append("Navigation elements selected but no workflows generated")
        
        # Check selector validity (basic check)
        for selection in config.selections:
            if not selection.selector or selection.selector.strip() == "":
                issues.append(f"Empty selector for field '{selection.name}'")
        
        return len(issues) == 0, issues

