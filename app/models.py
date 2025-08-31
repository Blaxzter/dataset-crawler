#!/usr/bin/env python3
"""
Shared data models for the crawler system

This module contains the core data structures used across the crawler system
to avoid circular import dependencies.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class ElementSelection:
    name: str
    selector: str
    element_type: str  # 'data_field', 'items_container', 'pagination', 'navigation'
    description: str
    extraction_type: str = "text"  # 'text', 'href', 'src', 'attribute'
    attribute_name: Optional[str] = None
    workflow_action: Optional[str] = None  # 'click', 'hover', 'extract_only'
    original_content: Optional[str] = (
        None  # Store original text content for content verification
    )
    verification_attributes: Optional[Dict[str, str]] = (
        None  # Store attributes for element verification
    )
    page_url: Optional[str] = None  # Track which page this selection was made on


@dataclass
class WorkflowStep:
    step_id: str
    action: str  # 'click', 'extract', 'navigate_back', 'open_new_tab'
    target_selector: str
    description: str
    extract_fields: Optional[List[str]] = None
    wait_condition: str = "networkidle"  # 'networkidle', 'domcontentloaded', 'selector'
    wait_selector: Optional[str] = None


@dataclass
class CrawlerConfiguration:
    name: str
    base_url: str
    selections: List[ElementSelection]
    workflows: List[WorkflowStep]
    pagination_config: Optional[ElementSelection] = None
    max_pages: Optional[int] = None
    delay_ms: int = 1000
