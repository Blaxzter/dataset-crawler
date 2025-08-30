#!/usr/bin/env python3
import asyncio
from crawler import PaginatedCrawler, CrawlerConfig
from config import PresetConfigs

async def crawl_quotes_example():
    """Example crawling quotes.toscrape.com"""
    site_config = PresetConfigs.quotes_to_scrape()
    
    config = CrawlerConfig(
        base_url=site_config.base_url,
        selectors=site_config.selectors,
        pagination_selector=site_config.pagination_selector,
        max_pages=site_config.max_pages,
        delay_ms=site_config.delay_ms,
        output_format="json",
        output_file="quotes_data"
    )
    
    async with PaginatedCrawler(config) as crawler:
        data = await crawler.crawl()
        crawler.save_data()
        print(f"Crawled {len(data)} quotes")
        return data

async def crawl_with_custom_extractor():
    """Example with custom data extraction logic"""
    config = CrawlerConfig(
        base_url="http://quotes.toscrape.com/",
        selectors={},  # Not used with custom extractor
        pagination_selector='li.next a',
        max_pages=3,
        delay_ms=1000,
        output_format="csv",
        output_file="custom_quotes"
    )
    
    async def custom_extractor(page):
        """Custom extraction function"""
        quotes_data = []
        quotes = await page.query_selector_all('.quote')
        
        for quote in quotes:
            text_elem = await quote.query_selector('.text')
            author_elem = await quote.query_selector('.author')
            tags_elems = await quote.query_selector_all('.tags a')
            
            text = await text_elem.text_content() if text_elem else ""
            author = await author_elem.text_content() if author_elem else ""
            tags = [await tag.text_content() for tag in tags_elems]
            
            quotes_data.append({
                'quote_text': text.strip('"'),
                'author_name': author,
                'tags_list': ', '.join(tags),
                'word_count': len(text.split())
            })
        
        return quotes_data
    
    async with PaginatedCrawler(config) as crawler:
        data = await crawler.crawl(custom_extractor)
        crawler.save_data()
        print(f"Crawled {len(data)} quotes with custom logic")
        return data

async def crawl_single_page_example():
    """Example crawling a single page without pagination"""
    config = CrawlerConfig(
        base_url="http://quotes.toscrape.com/page/1/",
        selectors={
            'items': '.quote',
            'text': '.text',
            'author': '.author',
            'tags': '.tags'
        },
        pagination_selector='.next',  # No pagination
        max_pages=1,
        output_format="json",
        output_file="single_page_quotes"
    )
    
    async with PaginatedCrawler(config) as crawler:
        data = await crawler.crawl()
        crawler.save_data()
        print(f"Crawled {len(data)} quotes from single page")
        return data

async def main():
    print("=== Paginated Crawler Examples ===\n")
    
    print("1. Basic pagination crawl:")
    await crawl_quotes_example()
    print()
    
    print("2. Custom extractor example:")
    await crawl_with_custom_extractor()
    print()
    
    print("3. Single page crawl:")
    await crawl_single_page_example()
    print()
    
    print("All examples completed!")

if __name__ == "__main__":
    asyncio.run(main())