#!/usr/bin/env python3
"""
Demonstration of the refactored crawler system

This script shows how to use the newly organized codebase with clean imports
and better structure.
"""

import asyncio

# Clean imports from the refactored structure
from app.core import PaginatedCrawler, CrawlerConfig, PresetConfigs
from app.advanced import AdvancedCrawler, WorkflowBuilder
from app.interactive import WorkflowConfigurator, InteractiveSelector
from app.examples import WorkflowExamples


async def demo_core_functionality():
    """Demonstrate core crawling functionality"""
    print("🔧 Core Functionality Demo")
    print("=" * 30)
    
    # Use preset configuration
    site_config = PresetConfigs.quotes_to_scrape()
    
    # Convert to crawler config
    config = CrawlerConfig(
        base_url=site_config.base_url,
        selectors=site_config.selectors,
        pagination_selector=site_config.pagination_selector,
        max_pages=1,  # Limited for demo
        delay_ms=site_config.delay_ms,
        headless=True
    )
    
    print(f"✅ Created configuration for: {site_config.name}")
    print(f"📍 Target URL: {config.base_url}")
    print(f"📊 Extracting fields: {list(config.selectors.keys())}")


async def demo_advanced_workflows():
    """Demonstrate advanced workflow functionality"""
    print("\n🚀 Advanced Workflows Demo")
    print("=" * 30)
    
    # Use workflow builder for programmatic creation
    workflow_builder = WorkflowBuilder()
    
    workflows = workflow_builder.add_click_and_extract(
        step_id="get_details",
        click_selector=".product-link",
        extract_fields=["description", "specs"],
        description="Extract detailed product information"
    ).add_new_tab_extraction(
        step_id="get_reviews",
        link_selector=".reviews-tab",
        extract_fields=["rating", "review_count"],
        description="Get reviews in new tab"
    ).build()
    
    print(f"✅ Created workflow with {len(workflows)} steps:")
    for i, step in enumerate(workflows, 1):
        print(f"  {i}. {step.description}")


def demo_interactive_tools():
    """Demonstrate interactive tools"""
    print("\n🎯 Interactive Tools Demo")
    print("=" * 30)
    
    # Show how to set up interactive configuration
    configurator = WorkflowConfigurator()
    
    print("✅ WorkflowConfigurator initialized")
    print("📋 Available methods:")
    print("  • create_interactive_configuration() - Visual element selection")
    print("  • create_programmatic_workflow() - Code-based workflow creation")
    print("  • test_configuration() - Test with limited pages")
    print("  • run_full_crawl() - Execute full crawling operation")


def demo_example_templates():
    """Demonstrate pre-built example templates"""
    print("\n📚 Example Templates Demo")
    print("=" * 30)
    
    examples = WorkflowExamples()
    
    # Show available templates
    templates = [
        ("E-commerce", examples.create_ecommerce_workflow()),
        ("Job Board", examples.create_job_board_workflow()),
        ("News Site", examples.create_news_site_workflow()),
        ("Social Media", examples.create_social_media_workflow())
    ]
    
    print("✅ Available workflow templates:")
    for name, config in templates:
        workflow_count = len(config.workflows)
        field_count = len([s for s in config.selections if s.element_type == 'data_field'])
        print(f"  • {name}: {field_count} fields, {workflow_count} workflows")


async def demo_package_structure():
    """Demonstrate the clean package structure"""
    print("\n📁 Refactored Package Structure")
    print("=" * 35)
    
    print("🏗️  New organization:")
    print("  📦 app/")
    print("    ├── 🔧 core/          - Basic crawling (config, crawler)")
    print("    ├── 🚀 advanced/      - Sophisticated workflows")
    print("    ├── 🎯 interactive/   - Visual element selection")
    print("    ├── 📚 examples/      - Demos and templates")
    print("    ├── 🛠️  utils/         - Helper tools")
    print("    └── 🧪 tests/         - Comprehensive test suite")
    print()
    print("✨ Benefits:")
    print("  • Clear separation of concerns")
    print("  • Logical grouping of functionality")
    print("  • Better import paths")
    print("  • Easier navigation and maintenance")
    print("  • Modular architecture")


async def main():
    """Run all demonstrations"""
    print("🕷️  Refactored Interactive Web Crawler System")
    print("=" * 50)
    print("Demonstrating the improved code organization and structure")
    print()
    
    await demo_core_functionality()
    await demo_advanced_workflows()
    demo_interactive_tools()
    demo_example_templates()
    await demo_package_structure()
    
    print("\n🎉 Refactored system demonstration complete!")
    print("\n📖 Usage:")
    print("  • Run tests: python -m pytest app/tests/")
    print("  • Quick tests: python app/tests/test_runner.py quick")
    print("  • Interactive demo: python app/examples/interactive_demo.py")
    print("  • Basic examples: python app/examples/basic_examples.py")


if __name__ == "__main__":
    asyncio.run(main())
