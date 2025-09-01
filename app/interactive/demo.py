#!/usr/bin/env python3
"""
Demo and CLI Interface Module for Interactive Selector

This module provides the command-line interface and demonstration
functionality for the interactive web crawler element selector.
"""

import asyncio
import logging
from .selector_core import InteractiveSelector


async def interactive_selection_demo():
    """Demonstration of the interactive selector"""
    print("🚀 Starting Interactive Web Crawler Element Selector")

    url = input("Enter the URL to configure: ").strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    async with InteractiveSelector(headless=False) as selector:
        await selector.start_selection_session(url)

        config = await selector.get_configuration()
        if config:
            selector.preview_configuration(config)

            # Show configuration summary
            summary = selector.get_configuration_summary(config)
            print(f"\n📊 Configuration Summary:")
            print(f"   Total selections: {summary['total_selections']}")
            print(f"   Data fields: {summary['data_fields']}")
            print(f"   Items containers: {summary['items_containers']}")
            print(f"   Navigation elements: {summary['navigation_elements']}")
            print(f"   Workflows: {summary['workflows']}")

            if summary["workflow_ready"]:
                print("   ✅ Workflow ready: Can extract data from multiple pages")
            elif summary["navigation_elements"] > 0:
                print("   ⚠️ Navigation configured but no data fields on target pages")

            # Validate configuration
            is_valid, issues = selector.validate_configuration(config)
            if not is_valid:
                print(f"\n⚠️ Configuration Issues:")
                for issue in issues:
                    print(f"   • {issue}")

            save_config = input("\nSave this configuration? (y/N): ").strip().lower()
            if save_config == "y":
                filename = (
                    input("Enter filename (without .json): ").strip()
                    or "crawler_config"
                )
                await selector.save_configuration(config, f"{filename}.json")
                print(f"✅ Configuration saved to {filename}.json")
        else:
            print("❌ No configuration created")


async def run_interactive_demo_with_url(url: str, headless: bool = False):
    """Run the interactive demo with a specific URL (programmatic interface)"""
    async with InteractiveSelector(headless=headless) as selector:
        await selector.start_selection_session(url)
        return await selector.get_configuration()


async def validate_existing_config(filename: str):
    """Validate an existing configuration file"""
    print(f"🔍 Validating configuration: {filename}")

    # Create a temporary selector to use config manager
    async with InteractiveSelector(headless=True) as selector:
        config = await selector.load_configuration(filename)

        if not config:
            print("❌ Could not load configuration file")
            return

        print(f"✅ Configuration loaded: {config.name}")

        # Show preview
        selector.preview_configuration(config)

        # Show summary
        summary = selector.get_configuration_summary(config)
        print(f"\n📊 Configuration Summary:")
        print(f"   Total selections: {summary['total_selections']}")
        print(f"   Data fields: {summary['data_fields']}")
        print(f"   Items containers: {summary['items_containers']}")
        print(f"   Navigation elements: {summary['navigation_elements']}")
        print(f"   Workflows: {summary['workflows']}")

        # Validate
        is_valid, issues = selector.validate_configuration(config)
        if is_valid:
            print("\n✅ Configuration is valid")
        else:
            print(f"\n⚠️ Configuration Issues:")
            for issue in issues:
                print(f"   • {issue}")


def main():
    """Main CLI entry point"""
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "validate" and len(sys.argv) > 2:
            asyncio.run(validate_existing_config(sys.argv[2]))
        elif sys.argv[1] == "demo" and len(sys.argv) > 2:
            asyncio.run(run_interactive_demo_with_url(sys.argv[2]))
        else:
            print("Usage:")
            print("  python demo.py                    # Interactive demo")
            print("  python demo.py demo <url>         # Demo with specific URL")
            print("  python demo.py validate <file>    # Validate existing config")
    else:
        asyncio.run(interactive_selection_demo())


if __name__ == "__main__":
    main()
