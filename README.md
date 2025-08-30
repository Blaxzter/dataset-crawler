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

### 🎯 Interactive Element Selection
- **Visual element selection**: Click on webpage elements to select them for extraction
- **Live configuration**: Build crawler configs by interacting directly with the target website
- **Real-time feedback**: See selected elements highlighted as you work
- **Multiple selection modes**: Data fields, item containers, pagination controls

### 🔄 Advanced Workflows
- **Sub-page navigation**: Click elements to navigate to detail pages and extract data
- **Multi-tab extraction**: Open links in new tabs for parallel data collection
- **Complex click sequences**: Define sophisticated interaction patterns
- **Workflow chaining**: Combine multiple extraction steps into comprehensive workflows
- **Navigation state management**: Automatically handle back navigation and context switching

## 📁 Package Structure

The codebase has been organized into logical modules for better maintainability:

```
app/
├── core/               # Basic crawling functionality
├── advanced/           # Sophisticated workflow-based crawling  
├── interactive/        # Visual element selection tools
├── examples/           # Usage examples and demonstrations
├── utils/              # Utility scripts and helpers
└── tests/              # Comprehensive test suite
```

### 🔧 Core Package (`app/core/`)

#### `config.py`
**Purpose**: Configuration classes and preset site configurations
- `SiteConfig`: Dataclass for basic site crawling configuration
- `PresetConfigs`: Static methods providing ready-to-use configurations for popular sites (Hacker News Jobs, Quotes to Scrape, Reddit)
- Defines selectors, pagination settings, and delays for common scraping targets

#### `crawler.py`
**Purpose**: Basic paginated web crawler implementation
- `CrawlerConfig`: Configuration dataclass for crawler settings
- `PaginatedCrawler`: Main crawler class with async context manager support
- Features: Data extraction, pagination handling, clickability validation, output to JSON/CSV
- Supports custom extraction functions and intelligent next-page navigation

### 🚀 Advanced Package (`app/advanced/`)

#### `advanced_crawler.py`
**Purpose**: Enhanced crawler with sophisticated workflow support
- `AdvancedCrawler`: Advanced crawler supporting complex multi-step extraction workflows
- `ExtractionResult`: Dataclass for structured extraction results with metadata
- `NavigationState`: Tracks navigation state and context during crawling
- Features: Sub-page navigation, new tab handling, workflow execution, back navigation

#### `workflow_builder.py`
**Purpose**: Programmatic workflow creation utilities
- `WorkflowBuilder`: Fluent API for building complex workflows programmatically
- Methods for creating click-and-extract, new-tab, and extract-only workflow steps
- Supports method chaining for intuitive workflow construction

### 🎯 Interactive Package (`app/interactive/`)

#### `selector.py` (formerly `interactive_selector.py`)
**Purpose**: Visual element selection interface for building crawler configurations
- `InteractiveSelector`: Browser-based UI for visually selecting webpage elements
- `ElementSelection`: Dataclass representing a selected element with extraction metadata
- `WorkflowStep`: Dataclass defining workflow actions and navigation steps
- `CrawlerConfiguration`: Complete configuration structure for advanced crawling
- Features: Live element highlighting, multi-mode selection, persistent state management

#### `configurator.py` (formerly `workflow_configurator.py`)
**Purpose**: Complete workflow management and configuration system
- `WorkflowConfigurator`: Central management class for creating and running crawler configurations
- Methods for interactive configuration creation, testing, and full crawl execution
- Configuration loading/saving with JSON persistence
- Integration between visual selector and advanced crawler systems

### 📚 Examples Package (`app/examples/`)

#### `basic_examples.py` (formerly `example.py`)
**Purpose**: Basic usage examples for traditional crawling
- Examples of simple paginated crawling with preset configurations
- Custom extractor function demonstrations
- Single page crawling scenarios
- Shows JSON and CSV output options

#### `interactive_demo.py`
**Purpose**: Complete feature demonstration system
- `InteractiveCrawlerDemo`: Main demo class with menu-driven interface
- Comprehensive demonstrations of all interactive features
- Visual selection demos, programmatic workflow creation
- Integration examples showing full system capabilities

#### `usage_guide.py`
**Purpose**: Feature-specific usage demonstrations
- Detailed demonstrations of user element selection
- Sophisticated workflow pattern examples
- Real-world scenario implementations (e-commerce, news, social media)
- Step-by-step tutorials for complex extraction patterns

#### `workflow_examples.py`
**Purpose**: Pre-built workflow templates for common use cases
- `WorkflowExamples`: Static methods providing ready-to-use workflow configurations
- E-commerce workflow: Product details, reviews, seller information
- Job board workflow: Job descriptions, company information
- News site workflow: Full articles, author profiles
- Social media workflow: User profiles, engagement data

### 🛠️ Utils Package (`app/utils/`)

#### `test_ui.py`
**Purpose**: Quick UI functionality verification
- Tests interactive selector UI rendering and functionality
- Verifies browser compatibility and UI element behavior
- Simple test workflow for validating visual selection interface

#### `config_runner.py` (formerly `run_my_config.py`)
**Purpose**: Script for loading and running saved configurations
- Loads configurations from JSON files
- Provides interactive menu for testing vs full crawling
- Configuration editing and cleanup utilities
- Quick runner for specific configurations

### 🧪 Tests Package (`app/tests/`)

Comprehensive unit test suite covering all functionality:
- `test_config.py`: Tests for configuration classes and presets
- `test_crawler.py`: Tests for basic crawler functionality
- `test_advanced_crawler.py`: Tests for advanced crawler and workflows
- `test_interactive_selector.py`: Tests for visual selection interface
- `test_workflow_configurator.py`: Tests for workflow management
- `test_integration.py`: End-to-end integration tests
- `test_examples.py`: Tests for example templates and demos
- `conftest.py`: Shared test fixtures and utilities
- `test_runner.py`: Test execution utilities and coverage reporting

### Configuration Storage

#### `crawler_configs/A.json`
**Purpose**: Example saved crawler configuration
- Complete configuration for https://opencode.de/de/software
- Shows real-world complex selectors and workflow definitions
- Includes navigation selectors, data fields, pagination, and workflow steps
- Demonstrates multi-page extraction with click-through navigation

## 🔄 Migration Guide

The codebase has been refactored for better organization. Here's how to update your imports:

### Old → New Import Mapping

```python
# Core functionality
from app.config import SiteConfig, PresetConfigs
from app.crawler import CrawlerConfig, PaginatedCrawler
# ↓ New imports ↓
from app.core.config import SiteConfig, PresetConfigs
from app.core.crawler import CrawlerConfig, PaginatedCrawler

# Advanced functionality  
from app.advanced_crawler import AdvancedCrawler, WorkflowBuilder
# ↓ New imports ↓
from app.advanced.advanced_crawler import AdvancedCrawler
from app.advanced.workflow_builder import WorkflowBuilder

# Interactive functionality
from app.interactive_selector import InteractiveSelector, ElementSelection
from app.workflow_configurator import WorkflowConfigurator
# ↓ New imports ↓
from app.interactive.selector import InteractiveSelector, ElementSelection
from app.interactive.configurator import WorkflowConfigurator

# Examples
from app.workflow_examples import WorkflowExamples
# ↓ New imports ↓
from app.examples.workflow_examples import WorkflowExamples
```

### Convenience Imports

For easier usage, you can import main classes directly from the app package:

```python
# All-in-one imports (recommended for most use cases)
from app import (
    PaginatedCrawler, CrawlerConfig, PresetConfigs,
    AdvancedCrawler, WorkflowBuilder,
    InteractiveSelector, WorkflowConfigurator
)
```

### Updated Script Locations

- `app/example.py` → `app/examples/basic_examples.py`
- `app/run_my_config.py` → `app/utils/config_runner.py`
- `app/interactive_selector.py` → `app/interactive/selector.py`
- `app/workflow_configurator.py` → `app/interactive/configurator.py`

## Installation

```bash
# Using uv (recommended)
uv sync
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
uv run app/examples/interactive_demo.py

# Or use the quick start example
uv run app/examples/interactive_demo.py quick
```

### Option 2: Traditional Programmatic Setup
For developers who prefer code-based configuration:

```python
import asyncio
from app.core.crawler import PaginatedCrawler, CrawlerConfig

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
from app.interactive.configurator import WorkflowConfigurator
from app.advanced.workflow_builder import WorkflowBuilder

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
uv run app/examples/basic_examples.py

# Interactive element selection demo
uv run app/interactive/selector.py

# Complete workflow configurator
uv run app/interactive/configurator.py

# Pre-built workflow examples
uv run app/examples/workflow_examples.py

# Full feature demonstration
uv run app/examples/interactive_demo.py

# Quick UI test
uv run app/utils/test_ui.py

# Test refactored structure
uv run demo_refactored.py
```

## 🎯 Interactive Element Selection

The interactive selector allows you to visually configure crawlers by clicking on webpage elements:

### How it Works
1. **Launch Interactive Mode**: Run `uv run app/interactive/selector.py` 
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
from app.interactive.configurator import WorkflowConfigurator

configurator = WorkflowConfigurator()
await configurator.create_interactive_configuration("https://example.com")
await configurator.test_configuration("my_config", max_pages=1)
await configurator.run_full_crawl("my_config")
```

### 3. Programmatic Workflow Building
```python
from app.advanced.workflow_builder import WorkflowBuilder

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
   uv run app/examples/interactive_demo.py quick
   ```

2. **Create Your First Interactive Configuration**:
   ```bash
   uv run app/examples/interactive_demo.py
   # Choose option 1: "Interactive Element Selection" 
   # Enter any website URL you want to crawl
   ```

3. **Explore Pre-built Examples**:
   ```bash
   uv run app/examples/workflow_examples.py
   ```

4. **Run Traditional Examples**:
   ```bash
   uv run app/examples/basic_examples.py
   ```

5. **Test the Refactored System**:
   ```bash
   uv run demo_refactored.py
   ```

6. **Run Tests**:
   ```bash
   # Run all tests
   python -m pytest app/tests/
   
   # Quick test suite
   python app/tests/test_runner.py quick
   
   # Test with coverage
   python app/tests/test_runner.py coverage
   ```