#!/usr/bin/env python3
"""
Quick UI Test

Simple test to verify the interactive selector UI is working properly
"""

import asyncio
from app.interactive.selector import InteractiveSelector

async def test_ui_rendering():
    """Test the UI rendering on a simple page"""
    
    print("🔥 Testing Interactive Selector UI with Firefox")
    print("=" * 50)
    
    test_url = "http://quotes.toscrape.com/"
    
    print(f"🌐 Opening test page: {test_url}")
    print(f"🦊 Using Firefox for better rendering compatibility")
    print()
    print("📋 Look for:")
    print("  ✅ Normal page content (actual quotes, not blue boxes)")
    print("  ✅ Control panel in top-right corner")
    print("  ✅ Four mode buttons with proper text labels")
    print("  ✅ Input field for field names")
    print("  ✅ Action buttons at bottom")
    print("  ✅ Log area showing messages")
    print("  ✅ Elements highlight red when you hover")
    print()
    print("🎯 Test the interface:")
    print("  1. Click 'Items Container' button")
    print("  2. Click on a quote box (.quote element)")
    print("  3. Click 'Data Field' button")  
    print("  4. Enter 'quote_text' in the field")
    print("  5. Click on the quote text")
    print("  6. Enter 'author_name' in the field")
    print("  7. Click on the author name")
    print("  8. Click 'Finish & Save'")
    print()
    print("⌨️  Press Enter when done testing...")
    
    async with InteractiveSelector(headless=False) as selector:
        await selector.start_selection_session(test_url)
        
        config = await selector.get_configuration()
        if config:
            print("\n✅ UI Test Successful!")
            print("📊 Configuration created with:")
            for selection in config.selections:
                print(f"  • {selection.name}: {selection.selector}")
        else:
            print("❌ UI Test Failed - No configuration created")

if __name__ == "__main__":
    asyncio.run(test_ui_rendering())
