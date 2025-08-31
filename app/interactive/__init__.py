"""
Interactive crawling functionality

This package contains the visual element selection system:
- Interactive browser-based element selector
- Visual configuration builder
- Workflow configurator and management
- Configuration persistence and loading
"""

from .selector import InteractiveSelector
from .configurator import WorkflowConfigurator

__all__ = ["InteractiveSelector", "WorkflowConfigurator"]
