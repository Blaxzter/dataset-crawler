#!/usr/bin/env python3
"""
Run Your Visual Configuration

Simple script to load and run your saved visual crawler configuration
"""

import asyncio
import json
from app.interactive.configurator import WorkflowConfigurator

async def run_saved_config():
    """Load and run your saved visual configuration"""
    
    print("🚀 Visual Configuration Crawler Runner")
    print("=" * 40)
    
    # Initialize configurator
    configurator = WorkflowConfigurator()
    
    # List available configurations
    print("📋 Available Configurations:")
    configurator.list_configurations()
    
    # Load your OpenCode configuration
    config_name = "OpenCode"
    print(f"\n🔧 Loading configuration: {config_name}")
    
    config = configurator.load_configuration("OpenCode.json")
    
    if config:
        print("\n✅ Configuration loaded successfully!")
        
        # Clean up the selectors (remove .crawler-highlight artifacts)
        print("🧹 Cleaning up selectors...")
        for selection in config.selections:
            if ".crawler-highlight" in selection.selector:
                selection.selector = selection.selector.replace(".crawler-highlight", "")
                print(f"  Cleaned: {selection.name} -> {selection.selector}")
        
        # Show configuration preview
        print("\n🔍 Configuration Preview:")
        print(f"📍 URL: {config.base_url}")
        print(f"📊 Fields: {len(config.selections)} selections")
        
        for selection in config.selections:
            print(f"  • {selection.name} ({selection.element_type}): {selection.selector}")
        
        # Ask user what to do
        print("\n🎯 What would you like to do?")
        print("1. 🧪 Test crawl (1 page only)")
        print("2. 🚀 Full crawl") 
        print("3. 🔧 Edit configuration first")
        print("0. ❌ Cancel")
        
        choice = input("\nEnter choice (0-3): ").strip()
        
        if choice == '1':
            print("\n🧪 Starting test crawl...")
            await configurator.test_configuration(config_name, max_pages=1)
            
        elif choice == '2':
            pages = input("📄 How many pages to crawl? (Enter for all): ").strip()
            if pages.isdigit():
                config.max_pages = int(pages)
            
            output_file = input("💾 Output filename (Enter for default): ").strip()
            output_file = output_file or f"{config_name}_results.json"
            
            print(f"\n🚀 Starting full crawl...")
            await configurator.run_full_crawl(config_name, output_file)
            
        elif choice == '3':
            await edit_configuration_interactive(config)
            
    else:
        print("❌ Could not load configuration")

async def edit_configuration_interactive(config):
    """Allow user to interactively edit the configuration"""
    
    print("\n🔧 Configuration Editor")
    print("=" * 30)
    
    # Fix field names
    print("📝 Let's give your fields better names:")
    for i, selection in enumerate(config.selections):
        print(f"\nField {i+1}: {selection.name}")
        print(f"  Current selector: {selection.selector}")
        print(f"  Current type: {selection.element_type}")
        
        new_name = input(f"  New name (Enter to keep '{selection.name}'): ").strip()
        if new_name:
            selection.name = new_name
        
        # Fix element type if needed
        if selection.element_type not in ['data_field', 'items_container', 'pagination']:
            print(f"  ⚠️  Element type '{selection.element_type}' should be one of:")
            print("     - data_field (extract this data)")
            print("     - items_container (container holding repeated items)")  
            print("     - pagination (next page button)")
            
            new_type = input(f"  New type: ").strip()
            if new_type in ['data_field', 'items_container', 'pagination']:
                selection.element_type = new_type
    
    # Add missing items container if needed
    has_items = any(s.element_type == 'items_container' for s in config.selections)
    if not has_items:
        print("\n⚠️  No items container found. This is required for proper crawling.")
        add_items = input("Add an items container? (y/N): ").strip().lower()
        if add_items == 'y':
            items_selector = input("Enter CSS selector for items container: ").strip()
            if items_selector:
                from app.models import ElementSelection
                items_selection = ElementSelection(
                    name="items",
                    selector=items_selector,
                    element_type="items_container", 
                    description="Items container"
                )
                config.selections.append(items_selection)
    
    # Save updated configuration
    config_file = f"crawler_configs/{config.name}.json"
    
    # Convert to dict for saving
    from dataclasses import asdict
    config_dict = asdict(config)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Configuration updated and saved to {config_file}")

async def quick_run_opencode():
    """Quick runner specifically for your OpenCode configuration"""
    
    print("🚀 Quick OpenCode Crawler")
    print("=" * 25)
    
    configurator = WorkflowConfigurator()
    
    # Load and fix the configuration
    config = configurator.load_configuration("OpenCode.json")
    
    if config:
        # Clean selectors
        for selection in config.selections:
            selection.selector = selection.selector.replace(".crawler-highlight", "")
        
        # Quick test
        print("🧪 Running quick test...")
        success = await configurator.test_configuration("OpenCode", max_pages=1)
        
        if success:
            run_full = input("\n✅ Test successful! Run full crawl? (y/N): ").strip().lower()
            if run_full == 'y':
                await configurator.run_full_crawl("OpenCode")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        asyncio.run(quick_run_opencode())
    else:
        asyncio.run(run_saved_config())
