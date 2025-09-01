"""
Interactive crawling functionality

This package contains the visual element selection system:
- Interactive browser-based element selector
- Visual configuration builder
- Workflow configurator and management
- Configuration persistence and loading

The package is now modularized into:
- browser_manager: Browser setup and management
- ui_injector: UI injection and page interaction
- config_manager: Configuration handling
- selector_core: Main InteractiveSelector class
- demo: CLI interface and demonstration
- selector: Main entry point for backward compatibility
"""

from .selector import (
    InteractiveSelector,
    interactive_selection_demo,
    run_interactive_demo_with_url,
    validate_existing_config,
)
from .configurator import WorkflowConfigurator
from .browser_manager import BrowserManager
from .ui_injector import UIInjector
from .config_manager import ConfigManager
from .selector_core import InteractiveSelector as CoreSelector
from .demo import interactive_selection_demo as demo_main

__all__ = [
    "InteractiveSelector",
    "WorkflowConfigurator",
    "BrowserManager",
    "UIInjector",
    "ConfigManager",
    "CoreSelector",
    "interactive_selection_demo",
    "run_interactive_demo_with_url",
    "validate_existing_config",
    "demo_main",
]
