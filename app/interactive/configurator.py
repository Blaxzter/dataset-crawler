#!/usr/bin/env python3
"""
Workflow Configurator for Interactive Web Crawling

This module provides a complete interface for users to:
1. Visually select elements on web pages
2. Define complex extraction workflows
3. Configure pagination and navigation
4. Generate reusable crawler configurations
"""

import asyncio
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.interactive.selector import InteractiveSelector
from app.models import CrawlerConfiguration, ElementSelection, WorkflowStep
from app.advanced.advanced_crawler import AdvancedCrawler
from app.advanced.workflow_builder import WorkflowBuilder


class WorkflowConfigurator:
    def __init__(self):
        self.configurations: Dict[str, CrawlerConfiguration] = {}
        self.config_directory = "crawler_configs"
        self._ensure_config_directory()

    def _ensure_config_directory(self):
        """Create configurations directory if it doesn't exist"""
        if not os.path.exists(self.config_directory):
            os.makedirs(self.config_directory)

    async def create_interactive_configuration(
        self, url: str, config_name: Optional[str] = None
    ) -> Optional[CrawlerConfiguration]:
        """Create a new configuration using the interactive selector"""

        print(f"\n🎯 Creating Interactive Configuration")
        print(f"📍 Target URL: {url}")
        print("\n🔧 You'll be able to:")
        print("• Click elements to select data fields")
        print("• Define items containers")
        print("• Set up pagination controls")
        print("• Configure navigation workflows")

        config_name = (
            config_name or f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        async with InteractiveSelector(headless=False) as selector:
            await selector.start_selection_session(url)

            config = await selector.get_configuration()
            if config:
                config.name = config_name

                # Save configuration
                config_file = os.path.join(self.config_directory, f"{config_name}.json")
                await selector.save_configuration(config, config_file)

                self.configurations[config_name] = config

                print(f"✅ Configuration '{config_name}' created successfully!")
                selector.preview_configuration(config)

                return config

        return None

    def create_programmatic_workflow(
        self,
        name: str,
        base_url: str,
        items_selector: str,
        data_fields: Dict[str, str],
        pagination_selector: Optional[str] = None,
    ) -> WorkflowBuilder:
        """Create a workflow programmatically with fluent API"""

        # Create base selections
        selections = [
            ElementSelection(
                name="items",
                selector=items_selector,
                element_type="items_container",
                description="Main items container",
            )
        ]

        # Add data field selections
        for field_name, field_selector in data_fields.items():
            selections.append(
                ElementSelection(
                    name=field_name,
                    selector=field_selector,
                    element_type="data_field",
                    description=f"Data field: {field_name}",
                )
            )

        # Add pagination if specified
        pagination_config = None
        if pagination_selector:
            pagination_config = ElementSelection(
                name="pagination",
                selector=pagination_selector,
                element_type="pagination",
                description="Pagination control",
            )

        # Create base configuration
        config = CrawlerConfiguration(
            name=name,
            base_url=base_url,
            selections=selections,
            workflows=[],
            pagination_config=pagination_config,
        )

        self.configurations[name] = config

        return WorkflowBuilder()

    def add_workflow_to_config(
        self, config_name: str, workflow_steps: List[WorkflowStep]
    ):
        """Add workflow steps to an existing configuration"""
        if config_name in self.configurations:
            self.configurations[config_name].workflows.extend(workflow_steps)

    async def test_configuration(self, config_name: str, max_pages: int = 1) -> bool:
        """Test a configuration with limited pages"""
        if config_name not in self.configurations:
            # Try to load from file first
            print(f"🔍 Configuration '{config_name}' not in memory, attempting to load from file...")
            loaded_config = self.load_configuration(config_name)
            if not loaded_config:
                print(f"❌ Configuration '{config_name}' not found in memory or files")
                return False

        config = self.configurations[config_name]
        config.max_pages = max_pages

        print(f"\n🧪 Testing configuration: {config_name}")

        try:
            async with AdvancedCrawler(config, headless=False) as crawler:
                results = await crawler.crawl_with_workflows()
                summary = crawler.get_extraction_summary()

                print(f"\n📊 Test Results:")
                print(f"Items extracted: {summary['total_items']}")
                print(f"Sources visited: {summary['unique_sources']}")
                print(f"Workflow executions: {summary['workflow_usage']}")

                if results:
                    print(f"\n📄 Sample data:")
                    print(json.dumps(results[0].data, indent=2))

                return True

        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

    async def run_full_crawl(
        self, config_name: str, output_file: Optional[str] = None
    ) -> Optional[List]:
        """Run a full crawl using the specified configuration"""
        if config_name not in self.configurations:
            # Try to load from file first
            print(f"🔍 Configuration '{config_name}' not in memory, attempting to load from file...")
            loaded_config = self.load_configuration(config_name)
            if not loaded_config:
                print(f"❌ Configuration '{config_name}' not found in memory or files")
                return None

        config = self.configurations[config_name]
        output_file = output_file or f"{config_name}_results.json"

        print(f"\n🚀 Running full crawl: {config_name}")

        try:
            async with AdvancedCrawler(config, headless=True) as crawler:
                results = await crawler.crawl_with_workflows()
                crawler.save_results(output_file)

                summary = crawler.get_extraction_summary()
                print(f"\n✅ Crawl completed successfully!")
                print(f"📊 Final Summary:")
                print(f"Total items: {summary['total_items']}")
                print(f"Unique sources: {summary['unique_sources']}")
                print(f"Output saved to: {output_file}")

                return results

        except Exception as e:
            print(f"❌ Crawl failed: {e}")
            return None

    def load_configuration(self, config_file: str) -> Optional[CrawlerConfiguration]:
        """Load a configuration from file"""
        try:
            if not config_file.endswith(".json"):
                config_file += ".json"

            full_path = os.path.join(self.config_directory, config_file)

            with open(full_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            selections = [ElementSelection(**sel) for sel in config_data["selections"]]
            workflows = [WorkflowStep(**wf) for wf in config_data["workflows"]]

            pagination_config = None
            if config_data.get("pagination_config"):
                pagination_config = ElementSelection(**config_data["pagination_config"])

            config = CrawlerConfiguration(
                name=config_data["name"],
                base_url=config_data["base_url"],
                selections=selections,
                workflows=workflows,
                pagination_config=pagination_config,
                max_pages=config_data.get("max_pages"),
                delay_ms=config_data.get("delay_ms", 1000),
            )

            self.configurations[config.name] = config
            print(f"✅ Loaded configuration: {config.name}")
            return config

        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            return None

    def list_configurations(self):
        """List all available configurations"""
        print(f"\n📋 Available Configurations:")

        # Get all unique configuration names (from memory and files)
        all_configs = set()
        
        # Add loaded configurations
        memory_configs = set(self.configurations.keys())
        all_configs.update(memory_configs)
        
        # Add saved configuration files
        config_files = [
            f.replace(".json", "") for f in os.listdir(self.config_directory) if f.endswith(".json")
        ]
        file_configs = set(config_files)
        all_configs.update(file_configs)
        
        if all_configs:
            print("\n📝 Available configurations:")
            for i, name in enumerate(sorted(all_configs), 1):
                status = []
                if name in memory_configs:
                    config = self.configurations[name]
                    workflow_count = len(config.workflows)
                    field_count = len([s for s in config.selections if s.element_type == "data_field"])
                    status.append(f"💾 loaded: {field_count} fields, {workflow_count} workflows")
                if name in file_configs:
                    status.append("💿 saved")
                
                status_str = " | ".join(status) if status else "❓ unknown"
                print(f"  {i}. {name} ({status_str})")
            
            print(f"\n💡 You can reference configurations by name (e.g., 'A') or number (e.g., '1')")
        else:
            print("  No configurations found. Create one with create_interactive_configuration()")
    
    def resolve_config_name(self, user_input: str) -> Optional[str]:
        """Resolve configuration name from user input (name or number)"""
        if not user_input:
            return None
            
        # Get all available configurations
        all_configs = set()
        all_configs.update(self.configurations.keys())
        
        # Add saved files
        try:
            config_files = [
                f.replace(".json", "") for f in os.listdir(self.config_directory) if f.endswith(".json")
            ]
            all_configs.update(config_files)
        except:
            pass
            
        all_configs = sorted(all_configs)
        
        # Check if input is a number
        if user_input.isdigit():
            index = int(user_input) - 1
            if 0 <= index < len(all_configs):
                return all_configs[index]
        
        # Check if input is a direct name match
        if user_input in all_configs:
            return user_input
            
        return None


async def main_configurator_demo():
    """Main demonstration of the workflow configurator"""

    configurator = WorkflowConfigurator()

    print("🎛️  Advanced Web Crawler Workflow Configurator")
    print("=" * 50)

    while True:
        print("\nChoose an action:")
        print("1. Create interactive configuration")
        print("2. Test existing configuration")
        print("3. Run full crawl")
        print("4. List configurations")
        print("5. Load configuration from file")
        print("6. Create programmatic workflow example")
        print("0. Exit")

        choice = input("\nEnter choice (0-6): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            url = input("Enter URL to configure: ").strip()
            if url:
                config_name = (
                    input("Enter configuration name (optional): ").strip() or None
                )
                await configurator.create_interactive_configuration(url, config_name)
        elif choice == "2":
            configurator.list_configurations()
            user_input = input("Enter configuration name or number to test: ").strip()
            config_name = configurator.resolve_config_name(user_input)
            if config_name:
                await configurator.test_configuration(config_name)
            elif user_input:
                print(f"❌ Configuration '{user_input}' not found")
        elif choice == "3":
            configurator.list_configurations()
            user_input = input("Enter configuration name or number to crawl: ").strip()
            config_name = configurator.resolve_config_name(user_input)
            if config_name:
                output_file = (
                    input("Enter output filename (optional): ").strip() or None
                )
                await configurator.run_full_crawl(config_name, output_file)
            elif user_input:
                print(f"❌ Configuration '{user_input}' not found")
        elif choice == "4":
            configurator.list_configurations()
        elif choice == "5":
            config_file = input("Enter configuration filename: ").strip()
            if config_file:
                configurator.load_configuration(config_file)
        elif choice == "6":
            await demo_programmatic_workflow(configurator)


async def demo_programmatic_workflow(configurator: WorkflowConfigurator):
    """Demonstrate creating workflows programmatically"""

    print("\n🔨 Creating Programmatic Workflow Example")

    # Create a workflow for e-commerce product pages
    workflow_builder = configurator.create_programmatic_workflow(
        name="ecommerce_products",
        base_url="https://example-shop.com/products",
        items_selector=".product-card",
        data_fields={
            "title": ".product-title",
            "price": ".price",
            "thumbnail": ".product-image img",
            "rating": ".rating-stars",
        },
        pagination_selector=".pagination .next-page",
    )

    # Add complex workflow steps
    workflow_steps = (
        workflow_builder.add_click_and_extract(
            step_id="get_product_details",
            click_selector=".product-title a",
            extract_fields=["description", "specifications", "availability"],
            description="Click product title to get detailed information",
        )
        .add_new_tab_extraction(
            step_id="get_reviews",
            link_selector=".reviews-tab a",
            extract_fields=["review_text", "reviewer_name", "review_rating"],
            description="Open reviews in new tab to extract review data",
        )
        .build()
    )

    configurator.add_workflow_to_config("ecommerce_products", workflow_steps)

    print("✅ Programmatic workflow created!")
    print("📋 Configuration includes:")
    print("  • Basic product data extraction")
    print("  • Click-through to product detail pages")
    print("  • New tab extraction for reviews")
    print("  • Automatic pagination handling")


if __name__ == "__main__":
    asyncio.run(main_configurator_demo())
