# Interactive Web Crawler System

A powerful Python application that provides both traditional programmatic web crawling and interactive visual element selection for web scraping. Built with Playwright for reliable browser automation.

## 🌟 Features

### Core Crawling
- Asynchronous crawling using Playwright
- Configurable data extraction with CSS selectors  
- Automatic pagination handling
- Custom data extraction functions
- Multiple output formats (JSON, CSV)
- Built-in delay and rate limiting
- Preset configurations for common sites

### 🎯 Interactive Element Selection (NEW!)
- **Visual element selection**: Click on webpage elements to select them for extraction
- **Live configuration**: Build crawler configs by interacting directly with the target website
- **Real-time feedback**: See selected elements highlighted as you work
- **Multiple selection modes**: Data fields, item containers, pagination controls

### 🔄 Advanced Workflows (NEW!)
- **Sub-page navigation**: Click elements to navigate to detail pages and extract data
- **Multi-tab extraction**: Open links in new tabs for parallel data collection
- **Complex click sequences**: Define sophisticated interaction patterns
- **Workflow chaining**: Combine multiple extraction steps into comprehensive workflows
- **Navigation state management**: Automatically handle back navigation and context switching

## Installation

```bash
# Using uv (recommended)
uv add playwright
uv run playwright install

# Or using pip
pip install playwright
playwright install
```

## 🚀 Quick Start

### Option 1: Interactive Visual Configuration
Perfect for non-programmers or exploring new websites:

```bash
# Start the interactive configurator
uv run interactive_demo.py

# Or use the quick start example
uv run interactive_demo.py quick
```

### Option 2: Traditional Programmatic Setup
For developers who prefer code-based configuration:

```python
import asyncio
from crawler import PaginatedCrawler, CrawlerConfig

async def main():
    config = CrawlerConfig(
        base_url="http://quotes.toscrape.com/",
        selectors={
            'items': '.quote',
            'text': '.text',
            'author': '.author',
            'tags': '.tags a'
        },
        pagination_selector='li.next a',
        max_pages=5,
        output_format="json"
    )
    
    async with PaginatedCrawler(config) as crawler:
        data = await crawler.crawl()
        crawler.save_data()

asyncio.run(main())
```

### Option 3: Advanced Workflows
For complex extraction scenarios:

```python
import asyncio
from workflow_configurator import WorkflowConfigurator
from advanced_crawler import AdvancedCrawler

async def main():
    configurator = WorkflowConfigurator()
    
    # Create workflow programmatically
    workflow_builder = configurator.create_programmatic_workflow(
        name="product_crawler",
        base_url="https://shop.example.com",
        items_selector=".product-card",
        data_fields={
            "title": ".product-title",
            "price": ".price-tag"
        },
        pagination_selector=".next-page"
    )
    
    # Add complex extraction steps
    workflow_builder.add_click_and_extract(
        "get_details",
        ".product-link",
        ["description", "specs"],
        "Click to get product details"
    )
    
    configurator.add_workflow_to_config("product_crawler", workflow_builder.build())
    
    # Run the crawl
    await configurator.run_full_crawl("product_crawler")

asyncio.run(main())
```

## 📖 Usage Examples

```bash
# Traditional examples
uv run example.py

# Interactive element selection demo
uv run interactive_selector.py

# Complete workflow configurator
uv run workflow_configurator.py

# Pre-built workflow examples
uv run workflow_examples.py

# Full feature demonstration
uv run interactive_demo.py
```

## 🎯 Interactive Element Selection

The interactive selector allows you to visually configure crawlers by clicking on webpage elements:

### How it Works
1. **Launch Interactive Mode**: Run `uv run interactive_selector.py` 
2. **Navigate to Target Site**: Enter the URL you want to crawl
3. **Visual Selection**: A browser window opens with a control panel
4. **Click to Select**: Click elements on the page to select them
5. **Configure Types**: Choose element types (data fields, containers, pagination)
6. **Save Configuration**: Generated config can be reused for future crawls

### Selection Modes
- **Data Field**: Click on elements containing data you want to extract
- **Items Container**: Click on the container that holds repeated items  
- **Pagination**: Click on next/previous page buttons
- **Navigation**: Click on elements for complex workflow steps

## 🔄 Advanced Workflows

Create sophisticated extraction patterns that go beyond simple data scraping:

### Workflow Types
- **Click and Extract**: Navigate to sub-pages to get detailed information
- **New Tab Extraction**: Open links in new tabs for parallel data collection
- **Multi-step Sequences**: Chain multiple interactions for complex data gathering

### Example Workflow Scenarios
- **E-commerce**: Click product → extract details → open reviews tab → get ratings
- **Job Boards**: Click job → extract description → visit company page → get company info
- **News Sites**: Click headline → read article → get author info → collect related articles

## 📚 Configuration Options

### Traditional CrawlerConfig
- `base_url`: Starting URL to crawl
- `selectors`: Dict of CSS selectors for data extraction
- `pagination_selector`: CSS selector for "next page" button  
- `max_pages`: Maximum pages to crawl (optional)
- `delay_ms`: Delay between pages in milliseconds
- `headless`: Run browser in headless mode
- `output_format`: "json" or "csv"
- `output_file`: Output filename (without extension)

### Advanced CrawlerConfiguration
- `name`: Configuration name for identification
- `base_url`: Starting URL
- `selections`: List of ElementSelection objects (visual selections)
- `workflows`: List of WorkflowStep objects (interaction patterns)
- `pagination_config`: ElementSelection for pagination
- `max_pages`: Page limit
- `delay_ms`: Timing control

### ElementSelection
- `name`: Field name for extracted data
- `selector`: CSS selector for the element
- `element_type`: Type of selection (data_field, items_container, pagination, navigation)
- `extraction_type`: How to extract value (text, href, src, attribute)
- `workflow_action`: Optional action (click, hover, extract_only)

### WorkflowStep
- `step_id`: Unique identifier
- `action`: Action type (click, extract, navigate_back, open_new_tab)  
- `target_selector`: CSS selector for target element
- `extract_fields`: Fields to extract after action
- `wait_condition`: What to wait for (networkidle, domcontentloaded, selector)

## 🛠️ Usage Patterns

### 1. Quick Interactive Setup
```bash
uv run interactive_demo.py
# Follow the visual interface to configure your crawler
```

### 2. Test Before Full Crawl
```python
from workflow_configurator import WorkflowConfigurator

configurator = WorkflowConfigurator()
await configurator.create_interactive_configuration("https://example.com")
await configurator.test_configuration("my_config", max_pages=1)
await configurator.run_full_crawl("my_config")
```

### 3. Programmatic Workflow Building
```python
from advanced_crawler import WorkflowBuilder

builder = WorkflowBuilder()
builder.add_click_and_extract(
    "details", 
    ".detail-link", 
    ["description", "specs"],
    "Get product details"
).add_new_tab_extraction(
    "reviews",
    ".reviews-link", 
    ["rating", "comments"],
    "Extract reviews in new tab"
)
```

### 4. Load and Modify Existing Configs
```python
config = configurator.load_configuration("my_saved_config.json")
# Modify configuration as needed
await configurator.run_full_crawl("my_saved_config")
```

## 📁 Project Structure

### Core Files
- `crawler.py`: Original basic crawler implementation
- `config.py`: Configuration classes and presets  
- `example.py`: Basic usage examples

### Interactive System (NEW!)
- `interactive_selector.py`: Visual element selection interface
- `advanced_crawler.py`: Enhanced crawler with workflow support
- `workflow_configurator.py`: Complete workflow management system
- `interactive_demo.py`: Full feature demonstrations
- `workflow_examples.py`: Pre-built workflow templates

### Configuration Storage
- `crawler_configs/`: Directory for saved configurations (auto-created)
- `*.json`: Saved crawler configurations for reuse

## 🎮 Getting Started Tutorial

1. **Try the Quick Start**:
   ```bash
   uv sync
   uv run interactive_demo.py quick
   ```

2. **Create Your First Interactive Configuration**:
   ```bash
   uv run interactive_demo.py
   # Choose option 1: "Interactive Element Selection"
   # Enter any website URL you want to crawl
   ```

3. **Explore Pre-built Examples**:
   ```bash
   uv run workflow_examples.py
   ```

4. **Run Traditional Examples**:
   ```bash
   uv run example.py
   ```