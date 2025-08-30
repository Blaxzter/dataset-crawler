#!/usr/bin/env python3
"""
Workflow Examples and Use Cases

This module provides ready-to-use examples of complex crawling workflows
for common scenarios like e-commerce, news sites, job boards, etc.
"""

import asyncio
from workflow_configurator import WorkflowConfigurator
from advanced_crawler import WorkflowBuilder
from interactive_selector import ElementSelection, WorkflowStep, CrawlerConfiguration

class WorkflowExamples:
    """Collection of pre-built workflow examples for common use cases"""
    
    @staticmethod
    def create_ecommerce_workflow() -> CrawlerConfiguration:
        """E-commerce product pages with reviews and detailed info"""
        
        selections = [
            ElementSelection("products", ".product-card", "items_container", "Product cards"),
            ElementSelection("title", ".product-title", "data_field", "Product title"),
            ElementSelection("price", ".price", "data_field", "Product price"),
            ElementSelection("image", ".product-image img", "data_field", "Product image", "src"),
            ElementSelection("rating", ".rating", "data_field", "Product rating"),
            ElementSelection("description", ".product-description", "data_field", "Full description"),
            ElementSelection("specifications", ".specs-table", "data_field", "Product specs"),
            ElementSelection("reviews", ".review-item", "data_field", "Customer reviews"),
            ElementSelection("seller_info", ".seller-name", "data_field", "Seller information")
        ]
        
        workflows = [
            WorkflowStep(
                step_id="get_product_details",
                action="click",
                target_selector=".product-title a",
                description="Click product title to view detailed page",
                extract_fields=["description", "specifications"],
                wait_condition="networkidle"
            ),
            WorkflowStep(
                step_id="get_reviews",
                action="open_new_tab",
                target_selector=".reviews-tab a",
                description="Open reviews in new tab",
                extract_fields=["reviews"],
                wait_condition="networkidle"
            ),
            WorkflowStep(
                step_id="get_seller_details",
                action="click",
                target_selector=".seller-link",
                description="Click seller link for seller information",
                extract_fields=["seller_info"],
                wait_condition="networkidle"
            )
        ]
        
        pagination_config = ElementSelection(
            "next_page", ".pagination .next", "pagination", "Next page button"
        )
        
        return CrawlerConfiguration(
            name="E-commerce Product Crawler",
            base_url="https://example-shop.com/products",
            selections=selections,
            workflows=workflows,
            pagination_config=pagination_config,
            max_pages=10,
            delay_ms=2000
        )

    @staticmethod  
    def create_job_board_workflow() -> CrawlerConfiguration:
        """Job board with detailed job descriptions and company info"""
        
        selections = [
            ElementSelection("jobs", ".job-listing", "items_container", "Job listings"),
            ElementSelection("job_title", ".job-title", "data_field", "Job title"),
            ElementSelection("company", ".company-name", "data_field", "Company name"),
            ElementSelection("location", ".job-location", "data_field", "Job location"),
            ElementSelection("salary", ".salary-range", "data_field", "Salary range"),
            ElementSelection("job_description", ".job-description", "data_field", "Full job description"),
            ElementSelection("requirements", ".requirements", "data_field", "Job requirements"),
            ElementSelection("company_info", ".company-overview", "data_field", "Company information"),
            ElementSelection("benefits", ".benefits-list", "data_field", "Job benefits")
        ]
        
        workflows = [
            WorkflowStep(
                step_id="get_job_details",
                action="click", 
                target_selector=".job-title a",
                description="Click job title to view full job description",
                extract_fields=["job_description", "requirements", "benefits"],
                wait_condition="networkidle"
            ),
            WorkflowStep(
                step_id="get_company_details",
                action="open_new_tab",
                target_selector=".company-name a", 
                description="Open company page in new tab",
                extract_fields=["company_info"],
                wait_condition="networkidle"
            )
        ]
        
        pagination_config = ElementSelection(
            "next_jobs", ".pagination .next", "pagination", "Next page of jobs"
        )
        
        return CrawlerConfiguration(
            name="Job Board Crawler",
            base_url="https://example-jobs.com/search",
            selections=selections,
            workflows=workflows,
            pagination_config=pagination_config,
            max_pages=20,
            delay_ms=1500
        )

    @staticmethod
    def create_news_site_workflow() -> CrawlerConfiguration:
        """News site with article content and author information"""
        
        selections = [
            ElementSelection("articles", ".article-card", "items_container", "News articles"),
            ElementSelection("headline", ".headline", "data_field", "Article headline"),
            ElementSelection("summary", ".summary", "data_field", "Article summary"),
            ElementSelection("author", ".author-name", "data_field", "Author name"),
            ElementSelection("publish_date", ".publish-date", "data_field", "Publication date"),
            ElementSelection("full_content", ".article-body", "data_field", "Full article content"),
            ElementSelection("author_bio", ".author-bio", "data_field", "Author biography"),
            ElementSelection("tags", ".article-tags .tag", "data_field", "Article tags"),
            ElementSelection("comments_count", ".comments-count", "data_field", "Number of comments")
        ]
        
        workflows = [
            WorkflowStep(
                step_id="read_full_article",
                action="click",
                target_selector=".headline a",
                description="Click headline to read full article",
                extract_fields=["full_content", "tags", "comments_count"],
                wait_condition="networkidle"
            ),
            WorkflowStep(
                step_id="get_author_profile",
                action="click",
                target_selector=".author-name a",
                description="Click author name to get profile information", 
                extract_fields=["author_bio"],
                wait_condition="networkidle"
            )
        ]
        
        pagination_config = ElementSelection(
            "next_articles", ".pagination .next", "pagination", "Next page of articles"
        )
        
        return CrawlerConfiguration(
            name="News Site Crawler",
            base_url="https://example-news.com/latest",
            selections=selections,
            workflows=workflows,
            pagination_config=pagination_config,
            max_pages=15,
            delay_ms=1000
        )

    @staticmethod
    def create_social_media_workflow() -> CrawlerConfiguration:
        """Social media posts with user profiles and engagement data"""
        
        selections = [
            ElementSelection("posts", ".post-item", "items_container", "Social media posts"),
            ElementSelection("username", ".username", "data_field", "User name"),
            ElementSelection("post_text", ".post-content", "data_field", "Post content"),
            ElementSelection("timestamp", ".post-time", "data_field", "Post timestamp"),
            ElementSelection("likes", ".like-count", "data_field", "Number of likes"),
            ElementSelection("shares", ".share-count", "data_field", "Number of shares"),
            ElementSelection("user_profile", ".user-bio", "data_field", "User profile info"),
            ElementSelection("comments", ".comment-text", "data_field", "Post comments")
        ]
        
        workflows = [
            WorkflowStep(
                step_id="get_user_profile",
                action="open_new_tab",
                target_selector=".username a",
                description="Open user profile in new tab",
                extract_fields=["user_profile"],
                wait_condition="networkidle"
            ),
            WorkflowStep(
                step_id="expand_comments",
                action="click",
                target_selector=".load-more-comments",
                description="Click to load more comments",
                extract_fields=["comments"],
                wait_condition="selector",
                wait_selector=".comments-loaded"
            )
        ]
        
        return CrawlerConfiguration(
            name="Social Media Crawler",
            base_url="https://example-social.com/feed",
            selections=selections,
            workflows=workflows,
            max_pages=50,
            delay_ms=2000
        )

async def demo_workflow_examples():
    """Demonstrate the pre-built workflow examples"""
    
    print("📚 Pre-built Workflow Examples Demo")
    print("=" * 40)
    
    configurator = WorkflowConfigurator()
    examples = WorkflowExamples()
    
    # Register example configurations
    configs = {
        "E-commerce": examples.create_ecommerce_workflow(),
        "Job Board": examples.create_job_board_workflow(), 
        "News Site": examples.create_news_site_workflow(),
        "Social Media": examples.create_social_media_workflow()
    }
    
    for name, config in configs.items():
        configurator.configurations[config.name] = config
        print(f"✅ {name} workflow loaded: {config.name}")
    
    print(f"\n📋 Available Example Workflows:")
    configurator.list_configurations()
    
    print(f"\n🎯 These examples demonstrate:")
    print("• Multi-step data extraction workflows")
    print("• Sub-page navigation and data retrieval")
    print("• New tab handling for additional information") 
    print("• Complex pagination scenarios")
    print("• Different extraction types (text, attributes, links)")
    
    use_example = input("\n🧪 Test an example workflow? Enter name or 'n' to skip: ").strip()
    
    if use_example and use_example.lower() != 'n':
        # Find matching configuration
        matching_config = None
        for config in configs.values():
            if use_example.lower() in config.name.lower():
                matching_config = config
                break
        
        if matching_config:
            print(f"\n🧪 Testing: {matching_config.name}")
            await configurator.test_configuration(matching_config.name, max_pages=1)
        else:
            print(f"❌ No configuration found matching '{use_example}'")

if __name__ == "__main__":
    asyncio.run(demo_workflow_examples())
