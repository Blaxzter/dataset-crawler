#!/usr/bin/env python3
"""
Interactive Web Crawler Demo

Complete demonstration of the interactive web crawler system that allows
users to visually select elements and define sophisticated extraction workflows.
"""

import asyncio
import sys
from app.interactive.configurator import WorkflowConfigurator
from app.advanced.advanced_crawler import AdvancedCrawler
from app.advanced.workflow_builder import WorkflowBuilder
from app.models import ElementSelection, WorkflowStep, CrawlerConfiguration

class InteractiveCrawlerDemo:
    def __init__(self):
        self.configurator = WorkflowConfigurator()

    async def run_complete_demo(self):
        """Run a complete demonstration of all features"""
        
        print("🕷️  Interactive Web Crawler System")
        print("=" * 50)
        print("This system allows you to:")
        print("✨ Visually select elements on web pages")
        print("🔄 Define complex extraction workflows")
        print("📄 Handle pagination automatically")
        print("🆕 Navigate to sub-pages and new tabs")
        print("💾 Save and reuse configurations")
        
        while True:
            print("\n" + "=" * 50)
            print("🎯 Choose a demo scenario:")
            print()
            print("1. 📊 Interactive Element Selection (Visual)")
            print("2. 🔧 Programmatic Workflow Creation")  
            print("3. 🧪 Test Existing Configuration")
            print("4. 🚀 Full Crawl Example")
            print("5. 🛠️  Advanced Workflow Demo")
            print("6. 📋 List All Configurations")
            print("0. 🚪 Exit")
            
            choice = input("\nEnter your choice (0-6): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                await self._demo_interactive_selection()
            elif choice == '2':
                await self._demo_programmatic_workflow()
            elif choice == '3':
                await self._demo_test_configuration()
            elif choice == '4':
                await self._demo_full_crawl()
            elif choice == '5':
                await self._demo_advanced_workflows()
            elif choice == '6':
                self._demo_list_configurations()
            else:
                print("❌ Invalid choice. Please try again.")

    async def _demo_interactive_selection(self):
        """Demo: Interactive visual element selection"""
        print("\n📊 Interactive Element Selection Demo")
        print("-" * 40)
        
        url = input("🌐 Enter URL to configure (or press Enter for demo URL): ").strip()
        if not url:
            url = "http://quotes.toscrape.com/"
        
        config_name = input("📝 Enter configuration name (optional): ").strip()
        
        print(f"\n🎯 Starting interactive selection for: {url}")
        print("\n📋 Instructions for the browser window:")
        print("1. Use the control panel in the top-right corner")
        print("2. Select 'Items Container' mode and click on the container holding repeated items")
        print("3. Switch to 'Data Field' mode and click on fields you want to extract")
        print("4. Switch to 'Pagination' mode and click on next/previous buttons")
        print("5. Click 'Finish & Save' when done")
        print("6. Return to this terminal and press Enter")
        
        config = await self.configurator.create_interactive_configuration(url, config_name)
        
        if config:
            print("✅ Configuration created successfully!")
            self._show_config_preview(config)
        else:
            print("❌ No configuration was created")

    async def _demo_programmatic_workflow(self):
        """Demo: Creating workflows programmatically"""
        print("\n🔧 Programmatic Workflow Creation Demo")
        print("-" * 40)
        
        # Create a sample e-commerce configuration
        workflow_builder = self.configurator.create_programmatic_workflow(
            name="demo_ecommerce",
            base_url="https://example-shop.com",
            items_selector=".product-item",
            data_fields={
                "title": ".product-title",
                "price": ".price-tag",
                "image": ".product-image img",
                "rating": ".rating-value"
            },
            pagination_selector=".pagination .next"
        )
        
        # Add sophisticated workflow steps
        workflow_steps = workflow_builder.add_click_and_extract(
            step_id="product_details",
            click_selector=".product-title a",
            extract_fields=["full_description", "specifications", "stock_status"],
            description="Click product to get detailed information"
        ).add_new_tab_extraction(
            step_id="user_reviews",
            link_selector=".reviews-link",
            extract_fields=["review_summary", "review_count", "avg_rating"],
            description="Extract review data in new tab"
        ).add_click_and_extract(
            step_id="seller_info", 
            click_selector=".seller-profile-link",
            extract_fields=["seller_name", "seller_rating", "shipping_info"],
            description="Get seller information"
        ).build()
        
        self.configurator.add_workflow_to_config("demo_ecommerce", workflow_steps)
        
        config = self.configurator.configurations["demo_ecommerce"]
        print("✅ Programmatic workflow created!")
        self._show_config_preview(config)

    async def _demo_test_configuration(self):
        """Demo: Test a configuration with limited scope"""
        print("\n🧪 Configuration Testing Demo")
        print("-" * 40)
        
        self.configurator.list_configurations()
        config_name = input("\n📝 Enter configuration name to test: ").strip()
        
        if config_name:
            max_pages = input("🔢 Max pages to test (default: 1): ").strip()
            max_pages = int(max_pages) if max_pages.isdigit() else 1
            
            success = await self.configurator.test_configuration(config_name, max_pages)
            
            if success:
                continue_crawl = input("\n✅ Test successful! Run full crawl? (y/N): ").strip().lower()
                if continue_crawl == 'y':
                    await self.configurator.run_full_crawl(config_name)

    async def _demo_full_crawl(self):
        """Demo: Run a full crawl operation"""
        print("\n🚀 Full Crawl Demo")
        print("-" * 40)
        
        self.configurator.list_configurations()
        config_name = input("\n📝 Enter configuration name to crawl: ").strip()
        
        if config_name:
            output_file = input("📄 Enter output filename (optional): ").strip() or None
            
            results = await self.configurator.run_full_crawl(config_name, output_file)
            
            if results:
                print("\n🎉 Crawl completed! Check the output file for results.")

    async def _demo_advanced_workflows(self):
        """Demo: Advanced workflow patterns"""
        print("\n🛠️  Advanced Workflow Patterns Demo")
        print("-" * 40)
        
        print("Creating examples of advanced workflow patterns...")
        
        # Complex multi-step workflow example
        config = CrawlerConfiguration(
            name="advanced_workflow_demo",
            base_url="https://example-news.com",
            selections=[
                ElementSelection("articles", ".article-item", "items_container", "News articles"),
                ElementSelection("headline", ".headline", "data_field", "Article headline"),
                ElementSelection("summary", ".summary", "data_field", "Article summary"),
                ElementSelection("author_name", ".author-info .name", "data_field", "Author name"),
                ElementSelection("full_article", ".article-content", "data_field", "Full article text"),
                ElementSelection("author_bio", ".author-biography", "data_field", "Author biography"),
                ElementSelection("related_articles", ".related-article", "data_field", "Related articles")
            ],
            workflows=[
                WorkflowStep(
                    step_id="read_full_article",
                    action="click",
                    target_selector=".headline a",
                    description="Click headline to read full article",
                    extract_fields=["full_article"],
                    wait_condition="networkidle"
                ),
                WorkflowStep(
                    step_id="get_author_info",
                    action="click", 
                    target_selector=".author-name a",
                    description="Click author name to get biography",
                    extract_fields=["author_bio"],
                    wait_condition="networkidle"
                ),
                WorkflowStep(
                    step_id="collect_related",
                    action="extract",
                    target_selector=".sidebar",
                    description="Extract related articles from sidebar",
                    extract_fields=["related_articles"]
                )
            ],
            pagination_config=ElementSelection("next", ".pagination .next", "pagination", "Next page"),
            max_pages=3
        )
        
        self.configurator.configurations["advanced_workflow_demo"] = config
        
        print("✅ Advanced workflow configuration created!")
        self._show_config_preview(config)
        
        test_it = input("\n🧪 Would you like to test this configuration? (y/N): ").strip().lower()
        if test_it == 'y':
            await self.configurator.test_configuration("advanced_workflow_demo")

    def _demo_list_configurations(self):
        """Demo: List all configurations with details"""
        print("\n📋 Configuration Listing Demo")
        print("-" * 40)
        self.configurator.list_configurations()

    def _show_config_preview(self, config: CrawlerConfiguration):
        """Show a detailed preview of a configuration"""
        print(f"\n🔍 Configuration Details: {config.name}")
        print(f"🌐 Base URL: {config.base_url}")
        
        data_fields = [s for s in config.selections if s.element_type == 'data_field']
        items = [s for s in config.selections if s.element_type == 'items_container']
        
        if items:
            print(f"\n📦 Items Container:")
            for item in items:
                print(f"  • {item.selector}")
        
        if data_fields:
            print(f"\n📊 Data Fields ({len(data_fields)}):")
            for field in data_fields:
                print(f"  • {field.name}: {field.selector}")
        
        if config.pagination_config:
            print(f"\n📄 Pagination: {config.pagination_config.selector}")
        
        if config.workflows:
            print(f"\n🔄 Workflows ({len(config.workflows)} steps):")
            for i, step in enumerate(config.workflows, 1):
                print(f"  {i}. {step.description}")
                if step.extract_fields:
                    print(f"     Extracts: {', '.join(step.extract_fields)}")

async def quick_start_example():
    """Quick start example for new users"""
    
    print("🚀 Quick Start Example")
    print("=" * 30)
    print("This will create a configuration for quotes.toscrape.com")
    
    configurator = WorkflowConfigurator()
    
    # Create simple configuration
    workflow_builder = configurator.create_programmatic_workflow(
        name="quotes_simple",
        base_url="http://quotes.toscrape.com/",
        items_selector=".quote",
        data_fields={
            "text": ".text",
            "author": ".author", 
            "tags": ".tags"
        },
        pagination_selector="li.next a"
    )
    
    print("✅ Simple configuration created!")
    
    # Test it
    print("\n🧪 Testing configuration...")
    success = await configurator.test_configuration("quotes_simple", max_pages=1)
    
    if success:
        print("\n🎉 Test successful! Configuration is working.")
    else:
        print("\n❌ Test failed. Check the configuration.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        asyncio.run(quick_start_example())
    else:
        asyncio.run(InteractiveCrawlerDemo().run_complete_demo())
