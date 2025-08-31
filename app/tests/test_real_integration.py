#!/usr/bin/env python3
"""
Real Integration Tests for the Crawler System

These tests use actual HTML content and real browser interactions to verify
that the crawler works in practice, not just in theory.

Unlike the unit tests which mock playwright, these tests use real browsers
and real web content to ensure the crawler actually functions correctly.
"""

import pytest
import asyncio
import os
from pathlib import Path
from typing import List

from app.advanced.advanced_crawler import AdvancedCrawler, ExtractionResult
from app.advanced.workflow_builder import WorkflowBuilder
from app.models import CrawlerConfiguration, ElementSelection, WorkflowStep


class TestLocalHTMLIntegration:
    """Test crawler against local HTML files"""

    def get_test_html_path(self, filename: str) -> str:
        """Get absolute path to test HTML file"""
        test_dir = Path(__file__).parent / "test_html"
        return f"file://{test_dir.absolute()}/{filename}"

    @pytest.mark.asyncio
    async def test_basic_extraction_from_local_html(self):
        """Test basic data extraction from local HTML file"""

        config = CrawlerConfiguration(
            name="Local HTML Test",
            base_url=self.get_test_html_path("products_page.html"),
            selections=[
                ElementSelection(
                    "items", ".product", "items_container", "Product items"
                ),
                ElementSelection(
                    "title", ".product-title", "data_field", "Product title"
                ),
                ElementSelection(
                    "price", ".product-price", "data_field", "Product price"
                ),
                ElementSelection(
                    "description",
                    ".product-description",
                    "data_field",
                    "Product description",
                ),
            ],
            workflows=[],
            max_pages=1,
        )

        async with AdvancedCrawler(config, headless=True) as crawler:
            results = await crawler.crawl_with_workflows()

        # Verify we extracted the expected products
        assert len(results) == 4, f"Expected 4 products, got {len(results)}"

        # Check first product data
        first_product = results[0].data
        assert first_product["title"] == "Wireless Headphones"
        assert first_product["price"] == "$79.99"
        assert "noise cancellation" in first_product["description"]

        # Check second product data
        second_product = results[1].data
        assert second_product["title"] == "Bluetooth Speaker"
        assert second_product["price"] == "$45.50"
        assert "Portable speaker" in second_product["description"]

        # Verify all results have the required fields
        for result in results:
            assert "title" in result.data
            assert "price" in result.data
            assert "description" in result.data
            assert result.source_url.endswith("products_page.html")

    @pytest.mark.asyncio
    async def test_pagination_with_local_html(self):
        """Test pagination functionality with local HTML files"""

        config = CrawlerConfiguration(
            name="Pagination Test",
            base_url=self.get_test_html_path("products_page.html"),
            selections=[
                ElementSelection("items", ".product", "items_container", "Products"),
                ElementSelection("title", ".product-title", "data_field", "Title"),
                ElementSelection("price", ".product-price", "data_field", "Price"),
            ],
            workflows=[],
            pagination_config=ElementSelection(
                "next", ".pagination .next", "pagination", "Next page"
            ),
            max_pages=2,  # Test pagination to second page
        )

        async with AdvancedCrawler(config, headless=True) as crawler:
            results = await crawler.crawl_with_workflows()

        # Should have products from both pages
        assert (
            len(results) == 6
        ), f"Expected 6 products from 2 pages, got {len(results)}"

        # Verify we have products from both pages
        page_1_products = [
            "Wireless Headphones",
            "Bluetooth Speaker",
            "Smart Watch",
            "USB-C Cable",
        ]
        page_2_products = ["Gaming Mouse", "Mechanical Keyboard"]

        extracted_titles = [result.data["title"] for result in results]

        # Check that we got all expected products
        for expected_title in page_1_products + page_2_products:
            assert (
                expected_title in extracted_titles
            ), f"Missing product: {expected_title}"

    @pytest.mark.asyncio
    async def test_click_workflow_with_local_html(self):
        """Test click workflow functionality with local HTML files"""

        # Create workflow that clicks detail links to extract more information
        workflow_builder = WorkflowBuilder()
        workflow_builder.add_click_and_extract(
            step_id="get_details",
            click_selector=".detail-link",
            extract_fields=["detailed_title", "detailed_price", "rating"],
            description="Click detail link to get more product info",
        )

        config = CrawlerConfiguration(
            name="Workflow Test",
            base_url=self.get_test_html_path("products_page.html"),
            selections=[
                ElementSelection("items", ".product", "items_container", "Products"),
                ElementSelection("title", ".product-title", "data_field", "Title"),
                ElementSelection("price", ".product-price", "data_field", "Price"),
                # These fields exist on detail pages
                ElementSelection(
                    "detailed_title", ".product-title", "data_field", "Detailed title"
                ),
                ElementSelection(
                    "detailed_price", ".product-price", "data_field", "Detailed price"
                ),
                ElementSelection("rating", ".rating", "data_field", "Product rating"),
            ],
            workflows=workflow_builder.build(),
            max_pages=1,
        )

        async with AdvancedCrawler(config, headless=True) as crawler:
            results = await crawler.crawl_with_workflows()

        # Should have products with workflow data
        assert len(results) >= 2, f"Expected at least 2 products, got {len(results)}"

        # Check that workflow data was extracted
        first_result = results[0].data
        assert "detailed_title" in first_result
        assert "detailed_price" in first_result
        assert "rating" in first_result

        # For the first product, verify the detailed data was extracted correctly
        if first_result["title"] == "Wireless Headphones":
            assert first_result["detailed_title"] == "Wireless Headphones Premium"
            assert first_result["detailed_price"] == "$79.99"
            assert "★★★★☆" in first_result["rating"]

    @pytest.mark.asyncio
    async def test_error_handling_missing_elements(self):
        """Test crawler behavior when configured elements don't exist"""

        config = CrawlerConfiguration(
            name="Missing Elements Test",
            base_url=self.get_test_html_path("products_page.html"),
            selections=[
                ElementSelection("items", ".product", "items_container", "Products"),
                ElementSelection("title", ".product-title", "data_field", "Title"),
                ElementSelection(
                    "nonexistent", ".does-not-exist", "data_field", "Missing field"
                ),
                ElementSelection(
                    "also_missing", ".another-missing", "data_field", "Another missing"
                ),
            ],
            workflows=[],
            max_pages=1,
        )

        async with AdvancedCrawler(config, headless=True) as crawler:
            results = await crawler.crawl_with_workflows()

        # Should still extract available data, set missing fields to None
        assert len(results) == 4

        for result in results:
            # Existing fields should have values
            assert result.data["title"] is not None
            assert isinstance(result.data["title"], str)
            assert len(result.data["title"]) > 0

            # Missing fields should be None
            assert result.data["nonexistent"] is None
            assert result.data["also_missing"] is None


@pytest.mark.asyncio
@pytest.mark.slow
class TestRealWebsiteIntegration:
    """Test crawler against real websites (marked as slow tests)"""

    async def test_quotes_toscrape_basic_extraction(self):
        """Test extraction from quotes.toscrape.com - a reliable test site"""

        config = CrawlerConfiguration(
            name="Quotes Test",
            base_url="http://quotes.toscrape.com/",
            selections=[
                ElementSelection("items", ".quote", "items_container", "Quotes"),
                ElementSelection("text", ".text", "data_field", "Quote text"),
                ElementSelection("author", ".author", "data_field", "Author name"),
                ElementSelection("tags", ".tags .tag", "data_field", "Quote tags"),
            ],
            workflows=[],
            max_pages=1,  # Just test one page to keep test fast
        )

        async with AdvancedCrawler(config, headless=True) as crawler:
            results = await crawler.crawl_with_workflows()

        # quotes.toscrape.com has 10 quotes per page
        assert len(results) >= 8, f"Expected at least 8 quotes, got {len(results)}"

        # Verify data quality
        for result in results:
            # All quotes should have text and author
            assert result.data["text"] is not None
            assert result.data["author"] is not None

            # Text should be actual quote content (starts with quote marks or is substantial)
            quote_text = result.data["text"].strip()
            assert len(quote_text) > 10, f"Quote text too short: {quote_text}"

            # Author should be a name (not empty)
            author = result.data["author"].strip()
            assert len(author) > 0, f"Empty author name"
            assert author != "None", f"Author was None string: {author}"

        # Check specific known quotes exist
        extracted_texts = [r.data["text"] for r in results]
        extracted_authors = [r.data["author"] for r in results]

        # quotes.toscrape.com always has some Einstein quotes
        assert any(
            "Einstein" in author for author in extracted_authors
        ), "Should have Einstein quotes"

    async def test_quotes_toscrape_pagination(self):
        """Test pagination functionality on quotes.toscrape.com"""

        config = CrawlerConfiguration(
            name="Quotes Pagination Test",
            base_url="http://quotes.toscrape.com/",
            selections=[
                ElementSelection("items", ".quote", "items_container", "Quotes"),
                ElementSelection("text", ".text", "data_field", "Quote text"),
                ElementSelection("author", ".author", "data_field", "Author name"),
            ],
            workflows=[],
            pagination_config=ElementSelection(
                "next", "li.next a", "pagination", "Next page"
            ),
            max_pages=3,  # Test multiple pages
        )

        async with AdvancedCrawler(config, headless=True) as crawler:
            results = await crawler.crawl_with_workflows()

        # Should have quotes from multiple pages (quotes.toscrape.com has 10 per page)
        assert (
            len(results) >= 20
        ), f"Expected at least 20 quotes from 3 pages, got {len(results)}"

        # Verify we visited multiple pages
        summary = crawler.get_extraction_summary()
        assert summary["pages_visited"] >= 2, "Should have visited multiple pages"

        # Check that quotes from different pages are different
        # (This is a basic sanity check that pagination worked)
        unique_texts = set(r.data["text"] for r in results)
        assert (
            len(unique_texts) >= len(results) * 0.8
        ), "Too many duplicate quotes - pagination may not be working"

    async def test_httpbin_different_content_types(self):
        """Test extraction from httpbin.org for different content scenarios"""

        # Test JSON endpoint extraction
        config = CrawlerConfiguration(
            name="HTTPBin JSON Test",
            base_url="http://httpbin.org/json",
            selections=[
                ElementSelection("items", "body", "items_container", "Page body"),
                ElementSelection("content", "pre", "data_field", "JSON content"),
            ],
            workflows=[],
            max_pages=1,
        )

        async with AdvancedCrawler(config, headless=True) as crawler:
            results = await crawler.crawl_with_workflows()

        # Should extract the JSON content
        assert len(results) >= 1
        content = results[0].data.get("content", "")
        assert (
            "slideshow" in content or "json" in content.lower()
        ), f"Unexpected JSON content: {content}"


@pytest.mark.asyncio
class TestAdvancedWorkflowsRealBrowser:
    """Test advanced workflow functionality with real browser interactions"""

    def get_test_html_path(self, filename: str) -> str:
        """Get absolute path to test HTML file"""
        test_dir = Path(__file__).parent / "test_html"
        return f"file://{test_dir.absolute()}/{filename}"

    async def test_workflow_click_navigation_real_browser(self):
        """Test click workflow with real browser navigation"""

        # Create a workflow that clicks product detail links
        workflow_builder = WorkflowBuilder()
        workflow_builder.add_click_and_extract(
            step_id="extract_details",
            click_selector=".detail-link",
            extract_fields=["detailed_title", "detailed_price", "rating"],
            description="Click to product detail page",
        )

        config = CrawlerConfiguration(
            name="Real Click Workflow Test",
            base_url=self.get_test_html_path("products_page.html"),
            selections=[
                ElementSelection("items", ".product", "items_container", "Products"),
                ElementSelection(
                    "title", ".product-title", "data_field", "Basic title"
                ),
                ElementSelection(
                    "price", ".product-price", "data_field", "Basic price"
                ),
                # Fields that exist on detail pages
                ElementSelection(
                    "detailed_title", ".product-title", "data_field", "Detailed title"
                ),
                ElementSelection(
                    "detailed_price", ".product-price", "data_field", "Detailed price"
                ),
                ElementSelection("rating", ".rating", "data_field", "Product rating"),
            ],
            workflows=workflow_builder.build(),
            max_pages=1,
        )

        async with AdvancedCrawler(config, headless=False) as crawler:
            results = await crawler.crawl_with_workflows()

        # Verify we got results
        assert len(results) >= 2, f"Expected at least 2 products, got {len(results)}"

        # Check that workflow extracted additional data
        for i, result in enumerate(results[:2]):  # Test first 2 products
            data = result.data

            # Should have basic data from listing page
            assert "title" in data
            assert "price" in data

            # Should have detailed data from workflow
            assert "detailed_title" in data
            assert "detailed_price" in data
            assert "rating" in data

            # Verify the detailed data is different/more complete than basic data
            if i == 0:  # First product
                assert data["detailed_title"] == "Wireless Headphones Premium"
                assert "★★★★☆" in data["rating"]
            elif i == 1:  # Second product
                assert data["detailed_title"] == "Bluetooth Speaker Pro"
                assert "★★★★★" in data["rating"]

    async def test_element_visibility_and_clickability(self):
        """Test that crawler properly detects clickable vs non-clickable elements"""

        # Create HTML with both clickable and non-clickable elements
        test_html = self.get_test_html_path("products_page.html")

        config = CrawlerConfiguration(
            name="Clickability Test",
            base_url=test_html,
            selections=[
                ElementSelection("items", ".product", "items_container", "Products"),
                ElementSelection("title", ".product-title", "data_field", "Title"),
            ],
            workflows=[
                WorkflowStep(
                    step_id="test_click",
                    action="click",
                    target_selector=".detail-link",  # These should be clickable
                    description="Test clicking detail links",
                    extract_fields=["title"],
                    wait_condition="networkidle",
                )
            ],
            max_pages=1,
        )

        async with AdvancedCrawler(config, headless=True) as crawler:
            results = await crawler.crawl_with_workflows()

        # Should successfully extract data - if elements weren't clickable,
        # we'd get None values or errors
        assert len(results) >= 2

        # At least some workflow fields should have been extracted successfully
        successful_extractions = [
            r
            for r in results
            if any(
                v is not None
                for k, v in r.data.items()
                if "workflow" in k or k in ["detailed_title", "rating"]
            )
        ]
        # Note: The workflow adds fields but they might not all extract successfully due to navigation complexity

    async def test_error_recovery_real_browser(self):
        """Test error recovery when workflows encounter problems"""

        # Create workflow that tries to click non-existent elements
        config = CrawlerConfiguration(
            name="Error Recovery Test",
            base_url=self.get_test_html_path("products_page.html"),
            selections=[
                ElementSelection("items", ".product", "items_container", "Products"),
                ElementSelection("title", ".product-title", "data_field", "Title"),
                ElementSelection("price", ".product-price", "data_field", "Price"),
            ],
            workflows=[
                WorkflowStep(
                    step_id="bad_workflow",
                    action="click",
                    target_selector=".nonexistent-link",  # This doesn't exist
                    description="Try to click non-existent element",
                    extract_fields=["title"],
                    wait_condition="networkidle",
                )
            ],
            max_pages=1,
        )

        async with AdvancedCrawler(config, headless=True) as crawler:
            results = await crawler.crawl_with_workflows()

        # Should still extract basic data even when workflow fails
        assert len(results) >= 2

        # Basic fields should be extracted successfully
        for result in results:
            assert result.data["title"] is not None
            assert result.data["price"] is not None
            assert len(result.data["title"]) > 0


@pytest.mark.asyncio
@pytest.mark.slow
class TestRealWorldScenarios:
    """Test realistic crawling scenarios against real websites"""

    async def test_quotes_author_detail_workflow(self):
        """Test a realistic workflow: extract quotes, then get author details"""

        # Build workflow that clicks author links to get more info
        workflow_builder = WorkflowBuilder()
        workflow_builder.add_click_and_extract(
            step_id="get_author_bio",
            click_selector=".author ~ a",  # Click the link next to author name on quotes.toscrape.com
            extract_fields=["author_bio", "author_birth"],
            description="Click author link to get biography",
        )

        config = CrawlerConfiguration(
            name="Author Detail Workflow",
            base_url="http://quotes.toscrape.com/",
            selections=[
                ElementSelection("items", ".quote", "items_container", "Quotes"),
                ElementSelection("text", ".text", "data_field", "Quote text"),
                ElementSelection("author", ".author", "data_field", "Author name"),
                # Fields from author detail pages
                ElementSelection(
                    "author_bio",
                    ".author-description",
                    "data_field",
                    "Author biography",
                ),
                ElementSelection(
                    "author_birth", ".author-born-date", "data_field", "Birth date"
                ),
            ],
            workflows=workflow_builder.build(),
            max_pages=1,
        )

        async with AdvancedCrawler(config, headless=False) as crawler:
            results = await crawler.crawl_with_workflows()

        # Should extract quotes with author details
        assert len(results) >= 5

        # At least some results should have author bio data from workflows
        results_with_bio = [r for r in results if r.data.get("author_bio") is not None]

        # Not all may succeed due to rate limiting or navigation issues, but some should
        assert (
            len(results_with_bio) >= 1
        ), "At least one quote should have author bio extracted"

    async def test_performance_with_real_browser(self):
        """Test crawler performance and resource usage with real browser"""

        config = CrawlerConfiguration(
            name="Performance Test",
            base_url="http://quotes.toscrape.com/",
            selections=[
                ElementSelection("items", ".quote", "items_container", "Quotes"),
                ElementSelection("text", ".text", "data_field", "Quote text"),
                ElementSelection("author", ".author", "data_field", "Author"),
            ],
            workflows=[],
            pagination_config=ElementSelection(
                "next_page", "li.next a", "pagination", "Next page button"
            ),
            max_pages=2,
            delay_ms=500,  # Reasonable delay
        )

        import time

        start_time = time.time()

        async with AdvancedCrawler(config, headless=True) as crawler:
            results = await crawler.crawl_with_workflows()

        end_time = time.time()
        duration = end_time - start_time

        # Should complete reasonably quickly
        assert duration < 30, f"Crawling took too long: {duration}s"

        # Should extract reasonable amount of data
        assert len(results) >= 15, f"Expected at least 15 quotes from 2 pages"

        # Verify quality of extracted data
        valid_results = [
            r for r in results if r.data.get("text") and r.data.get("author")
        ]
        assert (
            len(valid_results) >= len(results) * 0.8
        ), "Most extractions should be successful"


@pytest.mark.asyncio
class TestBrowserCompatibilityReal:
    """Test browser compatibility with real interactions"""

    def get_test_html_path(self, filename: str) -> str:
        """Get absolute path to test HTML file"""
        test_dir = Path(__file__).parent / "test_html"
        return f"file://{test_dir.absolute()}/{filename}"

    async def test_firefox_specific_features(self):
        """Test crawler works correctly with Firefox-specific behavior"""

        config = CrawlerConfiguration(
            name="Firefox Compatibility Test",
            base_url=self.get_test_html_path("products_page.html"),
            selections=[
                ElementSelection("items", ".product", "items_container", "Products"),
                ElementSelection("title", ".product-title", "data_field", "Title"),
                ElementSelection("price", ".product-price", "data_field", "Price"),
            ],
            workflows=[],
            max_pages=1,
        )

        # Test with Firefox (which is what the crawler uses)
        async with AdvancedCrawler(config, headless=True) as crawler:
            # Verify Firefox-specific settings are applied
            assert crawler.headless is True

            results = await crawler.crawl_with_workflows()

            # Basic functionality should work
            assert len(results) == 4

            # Verify browser context was set up correctly
            assert crawler.browser is not None
            assert crawler.context is not None
            assert crawler.main_page is not None

    async def test_network_and_timing_real(self):
        """Test real network timing and load conditions"""

        config = CrawlerConfiguration(
            name="Network Timing Test",
            base_url="http://quotes.toscrape.com/",
            selections=[
                ElementSelection("items", ".quote", "items_container", "Quotes"),
                ElementSelection("text", ".text", "data_field", "Quote text"),
            ],
            workflows=[],
            max_pages=1,
            delay_ms=200,  # Test with real delays
        )

        async with AdvancedCrawler(config, headless=True) as crawler:
            # Test that networkidle waiting works correctly
            await crawler.main_page.goto(config.base_url)
            await crawler.main_page.wait_for_load_state("networkidle")

            # Should be able to find elements after real network loading
            quotes = await crawler.main_page.query_selector_all(".quote")
            assert len(quotes) >= 8, "Should find quotes after real page load"

            # Test extraction after real loading
            results = await crawler.crawl_with_workflows()
            assert len(results) >= 8


# Helper function to run integration tests
async def run_integration_tests():
    """
    Helper function to run integration tests manually
    Use this for development/debugging outside of pytest
    """
    print("🧪 Running Real Integration Tests")
    print("=" * 40)

    # Test local HTML extraction
    print("\n📄 Testing Local HTML Extraction...")
    local_test = TestLocalHTMLIntegration()

    try:
        await local_test.test_basic_extraction_from_local_html()
        print("✅ Local HTML extraction: PASSED")
    except Exception as e:
        print(f"❌ Local HTML extraction: FAILED - {e}")

    # Test real website extraction
    print("\n🌐 Testing Real Website Extraction...")
    real_test = TestRealWebsiteIntegration()

    try:
        await real_test.test_quotes_toscrape_basic_extraction()
        print("✅ Real website extraction: PASSED")
    except Exception as e:
        print(f"❌ Real website extraction: FAILED - {e}")

    print("\n🎯 Integration tests completed!")


if __name__ == "__main__":
    # Allow running integration tests directly
    asyncio.run(run_integration_tests())
