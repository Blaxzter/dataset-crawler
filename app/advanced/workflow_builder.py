#!/usr/bin/env python3
"""
Workflow Builder for Advanced Crawling

This module provides a fluent API for building complex crawling workflows
programmatically, allowing developers to create sophisticated multi-step
data extraction patterns.
"""

from typing import List
from app.models import WorkflowStep


class WorkflowBuilder:
    """Helper class for building complex workflows programmatically"""

    def __init__(self):
        self.steps: List[WorkflowStep] = []

    def add_click_and_extract(
        self,
        step_id: str,
        click_selector: str,
        extract_fields: List[str],
        description: str = "",
    ) -> "WorkflowBuilder":
        """Add a workflow step that clicks an element and extracts data from the resulting page"""
        step = WorkflowStep(
            step_id=step_id,
            action="click",
            target_selector=click_selector,
            description=description or f"Click {click_selector} and extract data",
            extract_fields=extract_fields,
            wait_condition="networkidle",
        )
        self.steps.append(step)
        return self

    def add_new_tab_extraction(
        self,
        step_id: str,
        link_selector: str,
        extract_fields: List[str],
        description: str = "",
    ) -> "WorkflowBuilder":
        """Add a workflow step that opens a link in new tab and extracts data"""
        step = WorkflowStep(
            step_id=step_id,
            action="open_new_tab",
            target_selector=link_selector,
            description=description or f"Open {link_selector} in new tab and extract",
            extract_fields=extract_fields,
            wait_condition="networkidle",
        )
        self.steps.append(step)
        return self

    def add_extract_only(
        self,
        step_id: str,
        target_selector: str,
        extract_fields: List[str],
        description: str = "",
    ) -> "WorkflowBuilder":
        """Add a workflow step that only extracts data without navigation"""
        step = WorkflowStep(
            step_id=step_id,
            action="extract",
            target_selector=target_selector,
            description=description or f"Extract from {target_selector}",
            extract_fields=extract_fields,
        )
        self.steps.append(step)
        return self

    def build(self) -> List[WorkflowStep]:
        """Return the built workflow steps"""
        return self.steps.copy()
