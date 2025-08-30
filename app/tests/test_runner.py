#!/usr/bin/env python3
"""
Test Runner for Interactive Web Crawler System

Provides utilities for running specific test suites and generating reports.
"""

import sys
import subprocess
from pathlib import Path


def run_all_tests():
    """Run all tests with coverage reporting"""
    print("🧪 Running all crawler system tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "app/tests/",
            "-v",
            "--tb=short",
            "--color=yes"
        ], capture_output=False, check=False)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Some tests failed (exit code: {result.returncode})")
        
        return result.returncode
        
    except FileNotFoundError:
        print("❌ pytest not found. Install with: uv add pytest")
        return 1


def run_specific_test_file(test_file: str):
    """Run tests from a specific file"""
    print(f"🧪 Running tests from {test_file}...")
    print("=" * 50)
    
    test_path = Path("app/tests") / test_file
    if not test_path.exists():
        print(f"❌ Test file not found: {test_path}")
        return 1
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            str(test_path),
            "-v",
            "--tb=short",
            "--color=yes"
        ], capture_output=False, check=False)
        
        return result.returncode
        
    except FileNotFoundError:
        print("❌ pytest not found. Install with: uv add pytest")
        return 1


def run_tests_by_category():
    """Run tests organized by functionality category"""
    categories = {
        "Core": ["test_config.py", "test_crawler.py"],
        "Advanced": ["test_advanced_crawler.py"],
        "Interactive": ["test_interactive_selector.py", "test_workflow_configurator.py"],
        "Examples": ["test_examples.py"],
        "Integration": ["test_integration.py"]
    }
    
    print("🎯 Running tests by category...")
    print("=" * 50)
    
    total_failures = 0
    
    for category, test_files in categories.items():
        print(f"\n📁 {category} Tests:")
        print("-" * 30)
        
        for test_file in test_files:
            result = run_specific_test_file(test_file)
            if result != 0:
                total_failures += 1
                print(f"❌ {test_file} failed")
            else:
                print(f"✅ {test_file} passed")
    
    print(f"\n📊 Category Test Summary:")
    print(f"Total categories: {len(categories)}")
    print(f"Failed test files: {total_failures}")
    
    return total_failures


def run_quick_tests():
    """Run a quick subset of tests for rapid feedback"""
    print("⚡ Running quick test suite...")
    print("=" * 50)
    
    quick_tests = [
        "app/tests/test_config.py::TestSiteConfig::test_site_config_creation",
        "app/tests/test_config.py::TestPresetConfigs::test_quotes_to_scrape_config",
        "app/tests/test_crawler.py::TestCrawlerConfig::test_crawler_config_creation",
        "app/tests/test_advanced_crawler.py::TestExtractionResult::test_extraction_result_creation",
        "app/tests/test_interactive_selector.py::TestElementSelection::test_element_selection_creation_minimal",
        "app/tests/test_workflow_configurator.py::TestWorkflowConfigurator::test_workflow_configurator_initialization"
    ]
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest"
        ] + quick_tests + [
            "-v", "--tb=line", "--color=yes"
        ], capture_output=False, check=False)
        
        return result.returncode
        
    except FileNotFoundError:
        print("❌ pytest not found. Install with: uv add pytest")
        return 1


def check_test_coverage():
    """Check test coverage across the codebase"""
    print("📊 Checking test coverage...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "app/tests/",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "-v"
        ], capture_output=False, check=False)
        
        if result.returncode == 0:
            print("\n📈 Coverage report generated in htmlcov/")
        
        return result.returncode
        
    except FileNotFoundError:
        print("❌ pytest-cov not found. Install with: uv add pytest-cov")
        return 1


def main():
    """Main test runner interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test runner for Interactive Web Crawler System")
    parser.add_argument(
        "command",
        choices=["all", "quick", "category", "coverage", "file"],
        help="Type of test run to execute"
    )
    parser.add_argument(
        "--file",
        help="Specific test file to run (for 'file' command)"
    )
    
    args = parser.parse_args()
    
    if args.command == "all":
        return run_all_tests()
    elif args.command == "quick":
        return run_quick_tests()
    elif args.command == "category":
        return run_tests_by_category()
    elif args.command == "coverage":
        return check_test_coverage()
    elif args.command == "file":
        if not args.file:
            print("❌ --file argument required for 'file' command")
            return 1
        return run_specific_test_file(args.file)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
