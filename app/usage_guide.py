#!/usr/bin/env python3
"""
Usage Guide: Interactive Web Crawler Features

This script demonstrates the exact features requested:
1. User element selection for data extraction and pagination
2. Sophisticated extraction workflows (click → navigate → extract → back)
3. New tab handling for sub-page extraction
"""

import asyncio
from workflow_configurator import WorkflowConfigurator
from interactive_selector import InteractiveSelector


async def demo_user_element_selection():
    """
    FEATURE 1: User selects elements on webpage for extraction and pagination

    This demonstrates how users can visually select:
    - What information to extract and map to JSON
    - Which elements control pagination
    """

    print("🎯 FEATURE 1: User Element Selection Demo")
    print("=" * 50)
    print("This feature allows users to:")
    print("✨ Click on webpage elements to select them for data extraction")
    print("📄 Define pagination controls visually")
    print("📋 Map selections to JSON structure automatically")
    print()

    # Example URL - you can change this to any site
    demo_url = input(
        "🌐 Enter URL to configure (or press Enter for quotes demo): "
    ).strip()
    if not demo_url:
        demo_url = "http://quotes.toscrape.com/"

    print(f"\n🚀 Starting interactive selection for: {demo_url}")
    print("\n📋 Browser Instructions:")
    print("1. Control panel appears in top-right corner")
    print("2. Select 'Items Container' → Click on container with repeated items")
    print("3. Select 'Data Field' → Click on each field you want to extract")
    print("4. Enter field names in the input box before clicking")
    print("5. Select 'Pagination' → Click on next/previous buttons")
    print("6. Click 'Finish & Save' when done")
    print("7. Press Enter in this terminal when finished")

    async with InteractiveSelector(headless=False) as selector:
        await selector.start_selection_session(demo_url)

        config = await selector.get_configuration()
        if config:
            print("\n✅ Configuration created successfully!")
            selector.preview_configuration(config)

            # Save the configuration
            config_name = f"user_selected_{demo_url.split('/')[-2] or 'config'}"
            await selector.save_configuration(config, f"{config_name}.json")
            print(f"💾 Saved as: {config_name}.json")

            return config
        else:
            print("❌ No configuration was created")
            return None


async def demo_sophisticated_workflows():
    """
    FEATURE 2: Sophisticated extraction workflows

    This demonstrates:
    - Click on element → find information on new page → step back to pagination
    - Open sub-page in new tab for extraction
    """

    print("\n🔄 FEATURE 2: Sophisticated Workflow Demo")
    print("=" * 50)
    print("This feature enables:")
    print(
        "🔗 Click element → Navigate to sub-page → Extract data → Return to main page"
    )
    print("🆕 Open links in new tabs → Extract data → Continue main page crawl")
    print("🔄 Complex multi-step extraction sequences")
    print()

    configurator = WorkflowConfigurator()

    # Create example with sophisticated workflows
    workflow_builder = configurator.create_programmatic_workflow(
        name="sophisticated_demo",
        base_url="http://quotes.toscrape.com/",
        items_selector=".quote",
        data_fields={"text": ".text", "author": ".author", "tags": ".tags"},
        pagination_selector="li.next a",
    )

    # Add sophisticated workflow: click author → get author details → back to quotes
    workflow_steps = (
        workflow_builder.add_click_and_extract(
            step_id="get_author_details",
            click_selector=".author ~ a",  # Click on author link next to author name
            extract_fields=["author_bio", "author_born_date", "author_born_location"],
            description="Click author link → Navigate to author page → Extract bio → Return to quotes",
        )
        .add_new_tab_extraction(
            step_id="get_goodreads_info",
            link_selector=".goodreads-link",  # If there were goodreads links
            extract_fields=["goodreads_rating", "book_count"],
            description="Open author's Goodreads profile in new tab → Extract info",
        )
        .build()
    )

    configurator.add_workflow_to_config("sophisticated_demo", workflow_steps)

    print("✅ Sophisticated workflow created!")
    print("\n🔍 Workflow Details:")
    config = configurator.configurations["sophisticated_demo"]

    for i, step in enumerate(config.workflows, 1):
        print(f"\n  Step {i}: {step.description}")
        print(f"     Action: {step.action}")
        print(f"     Target: {step.target_selector}")
        if step.extract_fields:
            print(f"     Extracts: {', '.join(step.extract_fields)}")

    test_workflow = (
        input("\n🧪 Test this sophisticated workflow? (y/N): ").strip().lower()
    )
    if test_workflow == "y":
        print("\n🚀 Testing sophisticated workflow...")
        await configurator.test_configuration("sophisticated_demo", max_pages=1)


async def demo_real_world_scenario():
    """
    FEATURE 3: Real-world complex scenario

    Demonstrates a real e-commerce scenario with multiple extraction levels
    """

    print("\n🛍️ REAL-WORLD SCENARIO: E-commerce Product Crawler")
    print("=" * 50)
    print("Scenario: Extract product data with detailed specs and reviews")
    print()

    configurator = WorkflowConfigurator()

    # Create realistic e-commerce workflow
    workflow_builder = configurator.create_programmatic_workflow(
        name="ecommerce_comprehensive",
        base_url="https://example-shop.com/products",
        items_selector=".product-card",
        data_fields={
            "title": ".product-title",
            "price": ".price-current",
            "original_price": ".price-original",
            "discount": ".discount-percent",
            "image": ".product-image img",
            "rating": ".rating-stars",
            "review_count": ".review-count",
        },
        pagination_selector=".pagination .next-page",
    )

    # Complex multi-step workflow
    workflow_steps = (
        workflow_builder.add_click_and_extract(
            step_id="product_details",
            click_selector=".product-title a",
            extract_fields=[
                "detailed_description",
                "specifications",
                "shipping_info",
                "return_policy",
                "availability",
            ],
            description="📦 Click product → Extract detailed specifications → Return to listing",
        )
        .add_new_tab_extraction(
            step_id="review_analysis",
            link_selector=".reviews-tab-link",
            extract_fields=[
                "review_summary",
                "top_positive_review",
                "top_negative_review",
                "verified_purchase_percentage",
            ],
            description="⭐ Open reviews in new tab → Analyze customer feedback",
        )
        .add_click_and_extract(
            step_id="seller_verification",
            click_selector=".seller-info a",
            extract_fields=[
                "seller_rating",
                "seller_response_time",
                "seller_location",
                "years_selling",
            ],
            description="🏪 Click seller → Get seller credibility info → Return to product",
        )
        .add_new_tab_extraction(
            step_id="price_history",
            link_selector=".price-history-link",
            extract_fields=[
                "lowest_price_30_days",
                "highest_price_30_days",
                "price_trend",
            ],
            description="📈 Open price history → Track price changes over time",
        )
        .build()
    )

    configurator.add_workflow_to_config("ecommerce_comprehensive", workflow_steps)

    print("✅ Comprehensive e-commerce workflow created!")
    print("\n🔍 This workflow demonstrates:")
    print("• Multi-level data extraction (product → details → reviews → seller)")
    print("• Mixed navigation (click-through + new tabs)")
    print("• Automatic return navigation to continue pagination")
    print("• Complex data mapping to structured JSON")

    config = configurator.configurations["ecommerce_comprehensive"]

    print(f"\n📊 Extraction Plan:")
    print(
        f"Base fields: {len([s for s in config.selections if s.element_type == 'data_field'])} data points"
    )
    print(f"Workflow steps: {len(config.workflows)} sophisticated extraction steps")
    print(
        f"Total possible fields per item: ~{len([s for s in config.selections if s.element_type == 'data_field']) + sum(len(w.extract_fields or []) for w in config.workflows)}"
    )


async def main():
    """Run all demonstrations"""

    print("🕷️ Interactive Web Crawler - Feature Demonstrations")
    print("=" * 60)
    print("This demo shows the exact features you requested:")
    print()
    print("🎯 Feature 1: User element selection for data extraction + pagination")
    print("🔄 Feature 2: Sophisticated workflows (click → navigate → extract → back)")
    print("🆕 Feature 3: New tab extraction capabilities")
    print()

    while True:
        print("\n" + "=" * 60)
        print("Choose demonstration:")
        print()
        print("1. 🎯 User Element Selection (Visual point-and-click)")
        print("2. 🔄 Sophisticated Workflows (Multi-step extraction)")
        print("3. 🛍️ Real-World Scenario (E-commerce with all features)")
        print("4. 📚 Quick Tutorial (All features combined)")
        print("0. 🚪 Exit")

        choice = input("\nEnter choice (0-4): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            await demo_user_element_selection()
        elif choice == "2":
            await demo_sophisticated_workflows()
        elif choice == "3":
            await demo_real_world_scenario()
        elif choice == "4":
            print("\n📚 Running complete tutorial...")
            await demo_user_element_selection()
            await demo_sophisticated_workflows()
            await demo_real_world_scenario()
        else:
            print("❌ Invalid choice")


if __name__ == "__main__":
    print("🚀 Starting Interactive Web Crawler Usage Guide...")
    asyncio.run(main())
