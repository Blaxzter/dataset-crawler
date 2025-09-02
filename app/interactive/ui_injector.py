#!/usr/bin/env python3
"""
UI Injection Module for Interactive Selector

This module handles the injection of CSS and JavaScript components into web pages
to create the interactive element selection interface.
"""

import asyncio
import logging
from playwright.async_api import Page


class UIInjector:
    """Handles UI injection and page interaction setup"""
    
    def __init__(self, page: Page, browser_manager=None):
        self.page = page
        self.browser_manager = browser_manager
        self.logger = logging.getLogger(__name__)
    
    async def inject_legacy_ui(self):
        """Inject CSS and JavaScript for element selection interface (legacy method)"""
        js = """
        window.crawlerSelector = {
            mode: 'data_field',
            selections: [],
            workflows: [],
            currentField: '',
            
            init() {
                this.injectCSS();
                this.createUI();
                this.bindEvents();
            },
            
            injectCSS() {
                // Remove any existing styles first
                const existingStyle = document.getElementById('crawler-selector-styles');
                if (existingStyle) {
                    existingStyle.remove();
                }
                
                // Create and inject CSS styles dynamically
                const style = document.createElement('style');
                style.id = 'crawler-selector-styles';
                style.textContent = `
                    .crawler-highlight {
                        outline: 3px solid #ff4444 !important;
                        background-color: rgba(255, 68, 68, 0.1) !important;
                        cursor: pointer !important;
                        position: relative !important;
                    }
                    .crawler-selected {
                        outline: 3px solid #44ff44 !important;
                        background-color: rgba(68, 255, 68, 0.2) !important;
                        position: relative !important;
                    }
                    .crawler-pagination {
                        outline: 3px solid #4444ff !important;
                        background-color: rgba(68, 68, 255, 0.2) !important;
                        position: relative !important;
                    }
                    #crawler-ui {
                        position: fixed !important;
                        top: 20px !important;
                        right: 20px !important;
                        background: #ffffff !important;
                        border: 2px solid #333333 !important;
                        border-radius: 12px !important;
                        padding: 20px !important;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
                        z-index: 999999 !important;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
                        font-size: 14px !important;
                        width: 320px !important;
                        min-height: 200px !important;
                        box-sizing: border-box !important;
                    }
                    #crawler-ui * {
                        box-sizing: border-box !important;
                    }
                    #crawler-ui h3 {
                        margin: 0 0 15px 0 !important;
                        color: #333 !important;
                        font-size: 16px !important;
                        font-weight: bold !important;
                    }
                    .crawler-button {
                        background: #007cba !important;
                        color: white !important;
                        border: none !important;
                        padding: 10px 14px !important;
                        margin: 3px !important;
                        cursor: pointer !important;
                        border-radius: 6px !important;
                        font-size: 12px !important;
                        font-weight: 500 !important;
                        transition: background-color 0.2s ease !important;
                        display: inline-block !important;
                    }
                    .crawler-button:hover {
                        background: #005a87 !important;
                    }
                    .crawler-button.active {
                        background: #ff4444 !important;
                    }
                    .crawler-button:focus {
                        outline: 2px solid #007cba !important;
                        outline-offset: 2px !important;
                    }
                    #crawler-ui input {
                        width: 100% !important;
                        padding: 8px 12px !important;
                        border: 1px solid #ddd !important;
                        border-radius: 6px !important;
                        font-size: 13px !important;
                        margin: 5px 0 !important;
                        font-family: inherit !important;
                    }
                    #crawler-ui input:focus {
                        border-color: #007cba !important;
                        outline: none !important;
                        box-shadow: 0 0 0 3px rgba(0, 124, 186, 0.1) !important;
                    }

                    .crawler-mode-section {
                        margin: 10px 0 !important;
                        padding: 8px 0 !important;
                        border-bottom: 1px solid #eee !important;
                    }
                    .crawler-title {
                        margin: 0 0 15px 0 !important;
                        color: #333 !important;
                        font-size: 16px !important;
                        font-weight: bold !important;
                        text-align: center !important;
                    }
                    .crawler-input-section {
                        margin: 12px 0 !important;
                    }
                    .crawler-input {
                        width: 100% !important;
                        padding: 8px 12px !important;
                        border: 1px solid #ddd !important;
                        border-radius: 6px !important;
                        font-size: 13px !important;
                        box-sizing: border-box !important;
                    }
                    .crawler-action-section {
                        margin: 12px 0 !important;
                        text-align: center !important;
                    }
                    .crawler-log {
                        max-height: 120px !important;
                        overflow-y: auto !important;
                        border: 1px solid #ddd !important;
                        padding: 8px !important;
                        background: #f8f9fa !important;
                        font-size: 10px !important;
                        border-radius: 6px !important;
                        font-family: monospace !important;
                        line-height: 1.3 !important;
                        margin-top: 12px !important;
                    }
                `;
                document.head.appendChild(style);
                console.log('✅ Crawler CSS injected successfully');
            },
            
            createUI() {
                // Remove any existing UI first
                const existingUI = document.getElementById('crawler-ui');
                if (existingUI) {
                    existingUI.remove();
                }
                
                // Create main container
                const ui = document.createElement('div');
                ui.id = 'crawler-ui';
                
                // Create title
                const title = document.createElement('h3');
                title.className = 'crawler-title';
                title.textContent = 'Crawler Element Selector';
                ui.appendChild(title);
                
                // Create mode buttons section
                const modeSection = document.createElement('div');
                modeSection.className = 'crawler-mode-section';
                
                const modes = [
                    {id: 'data_field', label: 'Data Field', active: true},
                    {id: 'items_container', label: 'Items Container', active: false},
                    {id: 'pagination', label: 'Pagination', active: false},
                    {id: 'navigation', label: 'Navigation', active: false}
                ];
                
                modes.forEach(mode => {
                    const btn = document.createElement('button');
                    btn.className = 'crawler-button' + (mode.active ? ' active' : '');
                    btn.textContent = mode.label;
                    btn.onclick = () => this.setMode(mode.id);
                    modeSection.appendChild(btn);
                });
                
                ui.appendChild(modeSection);
                
                // Create input section
                const inputSection = document.createElement('div');
                inputSection.className = 'crawler-input-section';
                
                const fieldInput = document.createElement('input');
                fieldInput.type = 'text';
                fieldInput.id = 'field-name';
                fieldInput.className = 'crawler-input';
                fieldInput.placeholder = 'Field name...';
                inputSection.appendChild(fieldInput);
                
                ui.appendChild(inputSection);
                
                // Create action buttons
                const actionSection = document.createElement('div');
                actionSection.className = 'crawler-action-section';
                
                const workflowBtn = document.createElement('button');
                workflowBtn.className = 'crawler-button';
                workflowBtn.textContent = 'Start Workflow';
                workflowBtn.onclick = () => this.startWorkflow();
                actionSection.appendChild(workflowBtn);
                
                const finishBtn = document.createElement('button');
                finishBtn.className = 'crawler-button';
                finishBtn.textContent = 'Finish & Save';
                finishBtn.onclick = () => this.finishSelection();
                actionSection.appendChild(finishBtn);
                
                ui.appendChild(actionSection);
                
                // Create log section
                const logSection = document.createElement('div');
                logSection.id = 'crawler-log';
                logSection.className = 'crawler-log';
                ui.appendChild(logSection);
                
                // Add to body
                document.body.appendChild(ui);
                
                console.log('✅ Crawler UI created successfully');
                this.log('Crawler initialized. Hover over elements to highlight, click to select.');
            },
            
            setMode(mode) {
                this.mode = mode;
                // Remove active class from all mode buttons
                document.querySelectorAll('#crawler-ui .crawler-mode-section .crawler-button').forEach(btn => {
                    btn.classList.remove('active');
                });
                // Add active class to the clicked button
                const modeButtons = document.querySelectorAll('#crawler-ui .crawler-mode-section .crawler-button');
                const modeLabels = ['Data Field', 'Items Container', 'Pagination', 'Navigation'];
                const modeIds = ['data_field', 'items_container', 'pagination', 'navigation'];
                const modeIndex = modeIds.indexOf(mode);
                if (modeIndex >= 0 && modeButtons[modeIndex]) {
                    modeButtons[modeIndex].classList.add('active');
                }
                this.log(`Mode changed to: ${mode}`);
            },
            
            bindEvents() {
                document.addEventListener('mouseover', (e) => {
                    if (e.target.closest('#crawler-ui')) return;
                    this.highlightElement(e.target);
                });
                
                document.addEventListener('mouseout', (e) => {
                    if (e.target.closest('#crawler-ui')) return;
                    this.unhighlightElement(e.target);
                });
                
                document.addEventListener('click', (e) => {
                    if (e.target.closest('#crawler-ui')) return;
                    e.preventDefault();
                    e.stopPropagation();
                    this.selectElement(e.target);
                }, true);
            },
            
            highlightElement(element) {
                element.classList.add('crawler-highlight');
            },
            
            unhighlightElement(element) {
                element.classList.remove('crawler-highlight');
            },
            
            selectElement(element) {
                const fieldName = document.getElementById('field-name').value || `field_${this.selections.length + 1}`;
                const selector = this.generateSelector(element);
                
                element.classList.remove('crawler-highlight');
                element.classList.add('crawler-selected');
                
                const selection = {
                    name: fieldName,
                    selector: selector,
                    element_type: this.mode,
                    description: `${this.mode}: ${fieldName}`,
                    extraction_type: 'text'
                };
                
                this.selections.push(selection);
                this.log(`Selected: ${fieldName} -> ${selector}`);
                
                // Clear field name for next selection
                document.getElementById('field-name').value = '';
            },
            
            generateSelector(element) {
                // Try to generate a robust CSS selector
                if (element.id) {
                    return `#${element.id}`;
                }
                
                if (element.className) {
                    const classes = element.className.split(' ').filter(c => c.trim());
                    if (classes.length > 0) {
                        return `.${classes.join('.')}`;
                    }
                }
                
                // Fallback to tag name with position
                const tag = element.tagName.toLowerCase();
                const parent = element.parentElement;
                if (parent) {
                    const siblings = Array.from(parent.children).filter(child => 
                        child.tagName.toLowerCase() === tag
                    );
                    const index = siblings.indexOf(element);
                    return `${tag}:nth-of-type(${index + 1})`;
                }
                
                return tag;
            },
            
            startWorkflow() {
                this.log('Workflow mode: Click elements to define navigation sequence');
                this.mode = 'workflow';
            },
            
            finishSelection() {
                const config = {
                    selections: this.selections,
                    workflows: this.workflows
                };
                
                window.crawlerConfig = config;
                this.log(`Configuration ready! ${this.selections.length} selections, ${this.workflows.length} workflow steps`);
                console.log('Crawler Configuration:', config);
            },
            
            log(message) {
                const logDiv = document.getElementById('crawler-log');
                const timestamp = new Date().toLocaleTimeString();
                logDiv.innerHTML += `<div>[${timestamp}] ${message}</div>`;
                logDiv.scrollTop = logDiv.scrollHeight;
            }
        };
        
        // Auto-initialize when page loads
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => crawlerSelector.init());
        } else {
            crawlerSelector.init();
        }
        """
        
        await self.page.add_init_script(js)
    
    async def inject_modern_ui(self):
        """Inject enhanced UI using evaluate() - more reliable"""
        ui_creation_script = """
        () => {
            // Remove any existing elements first
            const existingStyle = document.getElementById('crawler-selector-styles');
            if (existingStyle) existingStyle.remove();
            
            const existingUI = document.getElementById('crawler-ui');
            if (existingUI) existingUI.remove();
            
            // Inject CSS
            const style = document.createElement('style');
            style.id = 'crawler-selector-styles';
            style.textContent = `
                #crawler-ui {
                    position: fixed !important;
                    top: 20px !important;
                    right: 20px !important;
                    background: white !important;
                    border: 2px solid #333 !important;
                    border-radius: 12px !important;
                    padding: 20px !important;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
                    z-index: 999999 !important;
                    font-family: Arial, sans-serif !important;
                    font-size: 14px !important;
                    width: 320px !important;
                    box-sizing: border-box !important;
                }
                
                .crawler-title {
                    margin: 0 0 15px 0 !important;
                    color: #333 !important;
                    font-size: 16px !important;
                    font-weight: bold !important;
                    text-align: center !important;
                }
                
                .crawler-btn {
                    background: #007cba !important;
                    color: white !important;
                    border: none !important;
                    padding: 8px 12px !important;
                    margin: 2px !important;
                    cursor: pointer !important;
                    border-radius: 6px !important;
                    font-size: 12px !important;
                    display: inline-block !important;
                }
                
                .crawler-btn:hover {
                    background: #005a87 !important;
                }
                
                .crawler-btn.active {
                    background: #ff4444 !important;
                }
                
                .crawler-btn.disabled {
                    background: #ccc !important;
                    color: #666 !important;
                    cursor: not-allowed !important;
                }
                
                .crawler-btn.disabled:hover {
                    background: #ccc !important;
                }
                
                .crawler-input {
                    width: 100% !important;
                    padding: 8px !important;
                    border: 1px solid #ddd !important;
                    border-radius: 6px !important;
                    margin: 10px 0 !important;
                    box-sizing: border-box !important;
                }
                
                .crawler-log {
                    max-height: 150px !important;
                    overflow-y: auto !important;
                    border: 1px solid #ddd !important;
                    padding: 8px !important;
                    background: #f8f8f8 !important;
                    font-size: 11px !important;
                    border-radius: 6px !important;
                    margin-top: 10px !important;
                    font-family: monospace !important;
                    line-height: 1.4 !important;
                }
                
                .log-entry {
                    margin: 2px 0 !important;
                    padding: 2px 0 !important;
                }
                
                .log-action { color: #007cba !important; font-weight: bold !important; }
                .log-element { color: #666 !important; }
                .log-selector { color: #0066cc !important; }
                .log-count { color: #ff6600 !important; }
                .log-nav { color: #cc0066 !important; }
                
                .crawler-highlight {
                    outline: 3px solid #ff4444 !important;
                    background-color: rgba(255, 68, 68, 0.1) !important;
                }
                
                .crawler-selected {
                    outline: 3px solid #44ff44 !important;
                    background-color: rgba(68, 255, 68, 0.2) !important;
                }
                
                .crawler-same-class {
                    outline: 2px solid #ffaa00 !important;
                    background-color: rgba(255, 170, 0, 0.15) !important;
                }
            `;
            document.head.appendChild(style);
            
            // Create UI
            const ui = document.createElement('div');
            ui.id = 'crawler-ui';
            
            ui.innerHTML = `
                <div class="crawler-title">Interactive Selector</div>
                
                <div id="step-indicator" style="margin-bottom: 10px; font-size: 12px; color: #666; text-align: center;">
                    Step 1: Select item containers
                </div>
                
                <div id="mode-buttons" style="margin-bottom: 10px;">
                    <button class="crawler-btn" onclick="setCrawlerMode('items', this)" id="items-btn" style="background: #ff4444;">Items Container</button><br>
                    <button class="crawler-btn disabled" onclick="setCrawlerMode('pagination', this)" id="pagination-btn" disabled>Pagination (Step 2)</button><br>
                    <button class="crawler-btn disabled" onclick="setCrawlerMode('data', this)" id="data-btn" disabled>Data Fields (Step 3)</button><br>
                    <button class="crawler-btn disabled" onclick="showOverview()" id="overview-btn" disabled>Overview (Step 4)</button>
                </div>
                
                <input type="text" class="crawler-input" id="field-name" placeholder="Field name...">
                
                <div style="text-align: center; margin-bottom: 10px;">
                    <button class="crawler-btn" id="next-step-btn" onclick="nextStep()" disabled>Next Step</button>
                    <button class="crawler-btn" onclick="window.finishCrawlerConfig()" id="finish-btn" style="display: none;">Finish & Save</button>
                    <button class="crawler-btn" id="workflow-btn" onclick="startWorkflowMode()" style="display: none; background: #cc0066;">⚙️ Workflows</button>
                </div>
                
                <div style="text-align: center; margin-bottom: 10px;">
                    <button class="crawler-btn" id="back-btn" onclick="navigateBack()" style="display: none; background: #ff6600;">← Back</button>
                </div>
                
                <div style="font-size: 11px; color: #666; margin-bottom: 8px; text-align: center;" id="nav-status">
                    ${window.location.href === window.crawlerOriginalUrl ? 'Original Page' : 'Navigated Page'}
                </div>
                
                <div class="crawler-log" id="crawler-log"></div>
            `;
            
            document.body.appendChild(ui);
            """ + self._get_ui_javascript() + """
            return 'UI injected successfully';
        }
        """
        
        try:
            result = await self.page.evaluate(ui_creation_script)
            
            # Inject backend state functions
            await self._inject_backend_state_functions()
            
            self.logger.info(f"✅ {result}")
        except Exception as e:
            self.logger.error(f"❌ UI injection failed: {e}")
    
    async def _inject_backend_state_functions(self):
        """Inject functions to communicate with Playwright backend for state management"""
        if not self.browser_manager:
            self.logger.warning("No browser manager provided - backend state functions not available")
            return
        
        try:
            # Expose backend state functions to the page (only if not already registered)
            await self.page.expose_function("playwrightGetState", self.browser_manager.get_state)
            await self.page.expose_function("playwrightSaveState", self.browser_manager.save_state)
            self.logger.info("✅ Backend state functions injected")
        except Exception as e:
            if "has been already registered" in str(e):
                self.logger.info("Backend state functions already registered, skipping...")
            else:
                self.logger.error(f"Failed to inject backend state functions: {e}")
    
    def _get_ui_javascript(self):
        """Get the main UI JavaScript code"""
        return """
            // Set up guided workflow state
            window.crawlerMode = 'items'; // Start with items container
            window.crawlerCurrentStep = 1;
            window.crawlerWorkflowMode = false;
            window.crawlerGuidedMode = true; // New guided mode
            
            // Initialize empty state - will be loaded from Playwright backend
            window.crawlerSelections = [];
            window.crawlerNavigationHistory = [];
            window.crawlerPageSelections = {};
            window.crawlerOriginalUrl = null;
            window.crawlerLogHistory = [];
            
            // Backend state management functions (communicate with Playwright)
            window.loadStateFromBackend = async () => {
                try {
                    // This will be injected by Python to load state from backend
                    const state = await window.playwrightGetState();
                    if (state) {
                        window.crawlerSelections = state.selections || [];
                        window.crawlerNavigationHistory = state.navigation_history || [];
                        window.crawlerPageSelections = state.page_selections || {};
                        window.crawlerOriginalUrl = state.original_url || window.location.href;
                        window.crawlerCurrentStep = state.current_step || 1;
                        console.log('✅ State loaded from Playwright backend:', state);
                        
                        // Update navigation status after state is loaded
                        setTimeout(updateNavigationStatus, 50);
                    }
                } catch (e) {
                    console.log('⚠️ Using fresh crawler state (no backend state found)');
                    window.crawlerOriginalUrl = window.location.href;
                }
            };
            
            window.saveStateToBackend = async () => {
                try {
                    const state = {
                        selections: window.crawlerSelections || [],
                        navigation_history: window.crawlerNavigationHistory || [],
                        page_selections: window.crawlerPageSelections || {},
                        original_url: window.crawlerOriginalUrl,
                        current_step: window.crawlerCurrentStep || 1
                    };
                    await window.playwrightSaveState(state);
                    console.log('✅ State saved to Playwright backend');
                } catch (e) {
                    console.warn('⚠️ Failed to save state to backend:', e);
                }
            };
            
            // Enhanced logging function
            function logMessage(message, type = 'info') {
                const logDiv = document.getElementById('crawler-log');
                const timestamp = new Date().toLocaleTimeString();
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry';
                
                let styledMessage = message;
                if (type === 'selection') {
                    styledMessage = message.replace(/Selected:/g, '<span class="log-action">Selected:</span>')
                                          .replace(/->([^<]+)/g, '-> <span class="log-selector">$1</span>');
                } else if (type === 'highlight') {
                    styledMessage = message.replace(/Highlighted:/g, '<span class="log-action">Highlighted:</span>')
                                          .replace(/(\\d+)/g, '<span class="log-count">$1</span>');
                } else if (type === 'navigation') {
                    styledMessage = message.replace(/Navigating:/g, '<span class="log-nav">Navigating:</span>');
                } else if (type === 'mode') {
                    styledMessage = message.replace(/Mode:/g, '<span class="log-action">Mode:</span>');
                }
                
                logEntry.innerHTML = `<span style="color: #999;">[${timestamp}]</span> ${styledMessage}`;
                logDiv.appendChild(logEntry);
                logDiv.scrollTop = logDiv.scrollHeight;
                
                // Keep log history limited
                window.crawlerLogHistory.push({timestamp, message, type});
                if (window.crawlerLogHistory.length > 50) {
                    window.crawlerLogHistory.shift();
                    if (logDiv.children.length > 50) {
                        logDiv.removeChild(logDiv.firstChild);
                    }
                }
            }
            
            // Guided workflow functions
            window.setCrawlerMode = (mode, buttonElement) => {
                // In guided mode, only allow mode if it's the current step or if it's enabled
                if (window.crawlerGuidedMode && buttonElement && buttonElement.disabled) {
                    logMessage('Complete the current step first!', 'info');
                    return;
                }
                
                // In workflow mode, allow navigation freely
                if (window.crawlerWorkflowMode && mode === 'nav') {
                    logMessage('💡 Navigation mode active - Click links to create workflows', 'info');
                }
                
                window.crawlerMode = mode;
                document.querySelectorAll('#mode-buttons .crawler-btn').forEach(btn => btn.classList.remove('active'));
                if (buttonElement) {
                    buttonElement.classList.add('active');
                }
                
                const modeNames = {
                    'data': 'Data Field',
                    'items': 'Items Container', 
                    'pagination': 'Pagination',
                    'nav': 'Navigation'
                };
                
                logMessage(`Mode: ${modeNames[mode] || mode}`, 'mode');
            };
            
            // Update UI based on current step
            function updateGuidedWorkflow() {
                const stepIndicator = document.getElementById('step-indicator');
                const nextBtn = document.getElementById('next-step-btn');
                const finishBtn = document.getElementById('finish-btn');
                const workflowBtn = document.getElementById('workflow-btn');
                
                // Count selections by type
                const itemsSelected = window.crawlerSelections.filter(s => s.element_type === 'items_container').length;
                const paginationSelected = window.crawlerSelections.filter(s => s.element_type === 'pagination').length;
                const dataSelected = window.crawlerSelections.filter(s => s.element_type === 'data_field').length;
                
                // Update step indicator and enable/disable buttons
                switch(window.crawlerCurrentStep) {
                    case 1: // Items step
                        stepIndicator.textContent = 'Step 1: Select item containers';
                        document.getElementById('items-btn').classList.add('active');
                        nextBtn.disabled = itemsSelected === 0;
                        nextBtn.textContent = 'Next: Pagination';
                        break;
                    case 2: // Pagination step
                        stepIndicator.textContent = 'Step 2: Select pagination (optional)';
                        enableButton('pagination-btn');
                        document.getElementById('pagination-btn').classList.add('active');
                        nextBtn.disabled = false; // Pagination is optional
                        nextBtn.textContent = 'Next: Data Fields';
                        break;
                    case 3: // Data fields step
                        stepIndicator.textContent = 'Step 3: Select data fields in items';
                        enableButton('data-btn');
                        document.getElementById('data-btn').classList.add('active');
                        nextBtn.disabled = dataSelected === 0;
                        nextBtn.textContent = 'Next: Overview';
                        break;
                    case 4: // Overview step
                        stepIndicator.textContent = 'Step 4: Overview and finish';
                        enableButton('overview-btn');
                        nextBtn.style.display = 'none';
                        finishBtn.style.display = 'inline-block';
                        workflowBtn.style.display = 'inline-block';
                        showOverview();
                        break;
                }
                
                // Save current step to backend
                saveStateToStorage();
            }
            
            function enableButton(buttonId) {
                const btn = document.getElementById(buttonId);
                btn.classList.remove('disabled');
                btn.disabled = false;
            }
            
            window.nextStep = () => {
                if (window.crawlerCurrentStep < 4) {
                    window.crawlerCurrentStep++;
                    // Set appropriate mode for next step
                    switch(window.crawlerCurrentStep) {
                        case 2:
                            window.crawlerMode = 'pagination';
                            break;
                        case 3:
                            window.crawlerMode = 'data';
                            break;
                    }
                    updateGuidedWorkflow();
                    logMessage(`Advanced to step ${window.crawlerCurrentStep}`, 'mode');
                }
            };
            
            window.showOverview = () => {
                const logDiv = document.getElementById('crawler-log');
                logDiv.innerHTML = ''; // Clear log for overview
                
                const itemsCount = window.crawlerSelections.filter(s => s.element_type === 'items_container').length;
                const paginationCount = window.crawlerSelections.filter(s => s.element_type === 'pagination').length;
                const dataCount = window.crawlerSelections.filter(s => s.element_type === 'data_field').length;
                
                logMessage('🎯 Configuration Overview:', 'info');
                logMessage(`• ${itemsCount} item container(s) selected`, 'info');
                logMessage(`• ${paginationCount} pagination element(s) selected`, 'info');
                logMessage(`• ${dataCount} data field(s) selected`, 'info');
                
                if (itemsCount > 0 && dataCount > 0) {
                    logMessage('✅ Ready to crawl! Your configuration looks good.', 'info');
                } else if (itemsCount === 0) {
                    logMessage('⚠️ Warning: No item containers selected', 'info');
                } else if (dataCount === 0) {
                    logMessage('⚠️ Warning: No data fields selected', 'info');
                }
                
                // Show selected elements details
                window.crawlerSelections.forEach((selection, index) => {
                    logMessage(`${index + 1}. ${selection.name} (${selection.element_type}): ${selection.selector}`, 'selection');
                });
            };
            
            window.startWorkflowMode = () => {
                window.crawlerGuidedMode = false;
                window.crawlerWorkflowMode = true;
                
                // Update UI for workflow mode
                document.getElementById('step-indicator').textContent = 'Workflow Mode: Create complex data extraction';
                
                // Replace mode buttons with workflow-specific ones
                const modeButtonsDiv = document.getElementById('mode-buttons');
                modeButtonsDiv.innerHTML = `
                    <button class="crawler-btn active" onclick="setCrawlerMode('data', this)" id="data-btn">Data Field</button>
                    <button class="crawler-btn" onclick="setCrawlerMode('nav', this)" id="nav-btn">🔗 Navigation</button><br>
                    <button class="crawler-btn" onclick="setCrawlerMode('items', this)" id="items-btn">Items Container</button>
                    <button class="crawler-btn" onclick="setCrawlerMode('pagination', this)" id="pagination-btn">Pagination</button>
                `;
                
                // Update button actions
                const nextStepBtn = document.getElementById('next-step-btn');
                const finishBtn = document.getElementById('finish-btn');
                const workflowBtn = document.getElementById('workflow-btn');
                
                nextStepBtn.style.display = 'none';
                finishBtn.style.display = 'inline-block';
                workflowBtn.textContent = '← Back to Guided';
                workflowBtn.onclick = () => backToGuided();
                
                logMessage('🔧 Workflow mode activated - Use Navigation button to click links!', 'mode');
                logMessage('💡 Click Navigation, then click links to create workflows', 'info');
            };
            
            window.backToGuided = () => {
                window.crawlerGuidedMode = true;
                window.crawlerWorkflowMode = false;
                window.crawlerCurrentStep = 4; // Back to overview
                
                // Restore guided mode UI
                const modeButtonsDiv = document.getElementById('mode-buttons');
                modeButtonsDiv.innerHTML = `
                    <button class="crawler-btn" onclick="setCrawlerMode('items', this)" id="items-btn">Items Container</button><br>
                    <button class="crawler-btn" onclick="setCrawlerMode('pagination', this)" id="pagination-btn">Pagination</button><br>
                    <button class="crawler-btn" onclick="setCrawlerMode('data', this)" id="data-btn">Data Fields</button><br>
                    <button class="crawler-btn" onclick="showOverview()" id="overview-btn">Overview</button>
                `;
                
                // Update buttons
                const nextStepBtn = document.getElementById('next-step-btn');
                const finishBtn = document.getElementById('finish-btn');
                const workflowBtn = document.getElementById('workflow-btn');
                
                nextStepBtn.style.display = 'none';
                finishBtn.style.display = 'inline-block';
                workflowBtn.textContent = '⚙️ Workflows';
                workflowBtn.onclick = () => startWorkflowMode();
                
                updateGuidedWorkflow();
                logMessage('📋 Back to guided mode', 'mode');
            };
            
            // Initialize guided workflow and navigation status
            setTimeout(async () => {
                await window.loadStateFromBackend();
                updateGuidedWorkflow();
                updateNavigationStatus();
                
                // Force update navigation status again after a brief delay 
                // in case state loading is async
                setTimeout(updateNavigationStatus, 200);
            }, 100);
            
            
            window.finishCrawlerConfig = () => {
                window.crawlerConfig = {
                    selections: window.crawlerSelections,
                    workflows: [],
                    pageSelections: window.crawlerPageSelections,
                    originalUrl: window.crawlerOriginalUrl,
                    navigationHistory: window.crawlerNavigationHistory
                };
                
                // Enhanced summary
                const navCount = window.crawlerSelections.filter(s => s.element_type === 'navigation').length;
                const dataCount = window.crawlerSelections.filter(s => s.element_type === 'data_field').length;
                const itemsCount = window.crawlerSelections.filter(s => s.element_type === 'items_container').length;
                const pagesVisited = Object.keys(window.crawlerPageSelections).length;
                
                logMessage(`Configuration saved! ${window.crawlerSelections.length} total selections:`, 'info');
                logMessage(`• ${dataCount} data fields, ${itemsCount} items containers, ${navCount} navigation elements`, 'info');
                logMessage(`• Selections made across ${pagesVisited} pages`, 'info');
                
                if (navCount > 0 && dataCount > 0) {
                    logMessage(`🎯 Workflow ready: Navigation + data extraction configured!`, 'info');
                } else if (navCount > 0) {
                    logMessage(`⚠️ Navigation configured but no data fields selected after navigation`, 'info');
                }
                
                console.log('Crawler config ready:', window.crawlerConfig);
                
                // Add cleanup button for session
                setTimeout(() => {
                    const ui = document.getElementById('crawler-ui');
                    if (ui) {
                        const cleanupBtn = document.createElement('button');
                        cleanupBtn.className = 'crawler-btn';
                        cleanupBtn.style.background = '#666';
                        cleanupBtn.style.fontSize = '10px';
                        cleanupBtn.style.marginTop = '10px';
                        cleanupBtn.textContent = 'Clear Session';
                        cleanupBtn.onclick = async () => {
                            // Clear backend state instead of sessionStorage
                            await window.playwrightSaveState({
                                selections: [],
                                navigation_history: [],
                                page_selections: {},
                                original_url: null,
                                current_step: 1
                            });
                            window.crawlerSelections = [];
                            window.crawlerNavigationHistory = [];
                            window.crawlerPageSelections = {};
                            window.crawlerOriginalUrl = null;
                            logMessage('🧹 Backend state cleared', 'info');
                        };
                        ui.appendChild(cleanupBtn);
                    }
                }, 500);
            };
            
            // Navigation functions
            window.navigateBack = () => {
                console.log('Navigation Debug:', {
                    currentUrl: window.location.href,
                    originalUrl: window.crawlerOriginalUrl,
                    historyLength: window.crawlerNavigationHistory?.length || 0,
                    history: window.crawlerNavigationHistory
                });
                
                if (window.crawlerNavigationHistory && window.crawlerNavigationHistory.length > 0) {
                    const previousUrl = window.crawlerNavigationHistory.pop();
                    // Persist updated history to backend
                    saveStateToStorage();
                    
                    logMessage(`Navigating back to: ${previousUrl}`, 'navigation');
                    window.location.href = previousUrl;
                } else if (window.crawlerOriginalUrl && window.location.href !== window.crawlerOriginalUrl) {
                    logMessage(`Navigating back to original page: ${window.crawlerOriginalUrl}`, 'navigation');
                    window.location.href = window.crawlerOriginalUrl;
                } else {
                    logMessage('Already at original page or no navigation history', 'info');
                    logMessage(`Debug: Current URL: ${window.location.href}`, 'info');
                    logMessage(`Debug: Original URL: ${window.crawlerOriginalUrl}`, 'info');
                    logMessage(`Debug: History length: ${window.crawlerNavigationHistory?.length || 0}`, 'info');
                }
            };
            
            // Helper function to save all state to backend (replacing sessionStorage)
            function saveStateToStorage() {
                // Use backend storage instead of sessionStorage
                window.saveStateToBackend();
            }
            
            // Function to update navigation status
            function updateNavigationStatus() {
                const navStatus = document.getElementById('nav-status');
                const backBtn = document.getElementById('back-btn');
                
                console.log('Navigation Status Check:', {
                    current: window.location.href,
                    original: window.crawlerOriginalUrl,
                    historyLength: window.crawlerNavigationHistory?.length || 0,
                    backBtnExists: !!backBtn,
                    navStatusExists: !!navStatus
                });
                
                if (navStatus) {
                    const isOriginalPage = window.location.href === window.crawlerOriginalUrl;
                    const hasHistory = window.crawlerNavigationHistory && window.crawlerNavigationHistory.length > 0;
                    
                    console.log('Navigation decision:', {
                        isOriginalPage,
                        hasHistory,
                        shouldShowBack: !isOriginalPage || hasHistory
                    });
                    
                    if (isOriginalPage && !hasHistory) {
                        navStatus.textContent = 'Original Page';
                        if (backBtn) {
                            backBtn.style.display = 'none';
                            console.log('✅ Back button hidden (original page, no history)');
                        }
                    } else {
                        // Show more detailed navigation info
                        const originalHost = new URL(window.crawlerOriginalUrl).hostname;
                        const currentHost = new URL(window.location.href).hostname;
                        const historyCount = window.crawlerNavigationHistory?.length || 0;
                        
                        if (originalHost === currentHost) {
                            navStatus.textContent = `Navigated: ${historyCount} steps from start`;
                        } else {
                            navStatus.textContent = `Navigated: ${historyCount} steps from ${originalHost}`;
                        }
                        
                        if (backBtn) {
                            backBtn.style.display = 'inline-block';
                            console.log('✅ Back button shown (navigated page or has history)');
                        } else {
                            console.log('⚠️ Back button element not found!');
                        }
                    }
                }
            }
            
            // Auto re-inject UI after navigation
            window.addEventListener('DOMContentLoaded', () => {
                if (!document.getElementById('crawler-ui') && window.crawlerSelections) {
                    setTimeout(() => {
                        // Re-inject the UI if it doesn't exist but we have crawler state
                        if (typeof injectCrawlerUI === 'function') {
                            injectCrawlerUI();
                        }
                    }, 1000);
                }
            });
            """ + self._get_element_interaction_code()
    
    def _get_element_interaction_code(self):
        """Get the element interaction and selection code"""
        return """
            // Function to highlight all elements with same class composition
            function highlightSameClassElements(targetElement) {
                // Remove any existing same-class highlights
                document.querySelectorAll('.crawler-same-class').forEach(el => {
                    el.classList.remove('crawler-same-class');
                });
                
                const targetClasses = Array.from(targetElement.classList)
                    .filter(c => !c.startsWith('crawler-'))
                    .sort();
                
                if (targetClasses.length === 0) return 0;
                
                let matchCount = 0;
                document.querySelectorAll('*').forEach(el => {
                    if (el.closest('#crawler-ui')) return;
                    if (el === targetElement) return;
                    
                    const elementClasses = Array.from(el.classList)
                        .filter(c => !c.startsWith('crawler-'))
                        .sort();
                    
                    // Check if class compositions match exactly
                    if (targetClasses.length === elementClasses.length && 
                        targetClasses.every((cls, i) => cls === elementClasses[i])) {
                        el.classList.add('crawler-same-class');
                        matchCount++;
                    }
                });
                
                return matchCount;
            }
            
            // Function to get element description for logging
            function getElementDescription(element) {
                const tag = element.tagName.toLowerCase();
                const text = element.textContent?.slice(0, 30).trim() || '';
                const classes = Array.from(element.classList)
                    .filter(c => !c.startsWith('crawler-'))
                    .join('.');
                
                let desc = `<${tag}`;
                if (element.id) desc += ` id="${element.id}"`;
                if (classes) desc += ` class="${classes}"`;
                desc += `>`;
                
                if (text) desc += ` "${text}${text.length >= 30 ? '...' : ''}"`;
                
                return desc;
            }
            
            // Set up event listeners
            document.addEventListener('click', async (e) => {
                if (e.target.closest('#crawler-ui')) {
                    return;
                }
                
                e.preventDefault();
                e.stopPropagation();
                
                const fieldName = document.getElementById('field-name').value || `field_${window.crawlerSelections.length + 1}`;
                const selector = generateSelector(e.target);
                const elementDesc = getElementDescription(e.target);
                const originalContent = e.target.textContent?.trim() || '';
                
                // Restrict navigation mode to workflow mode only
                if (window.crawlerMode === 'nav' && !window.crawlerWorkflowMode) {
                    logMessage('Navigation is only available in Workflow Mode! Use the Workflows button first.', 'info');
                    return;
                }
                
                // Handle navigation mode differently
                if (window.crawlerMode === 'nav') {
                    // If it's a link, follow it
                    if (e.target.tagName.toLowerCase() === 'a' || e.target.closest('a')) {
                        const link = e.target.tagName.toLowerCase() === 'a' ? e.target : e.target.closest('a');
                        const href = link.href;
                        
                        if (href && !href.startsWith('javascript:') && !href.startsWith('#')) {
                            // Store current URL in navigation history (with backend persistence)
                            window.crawlerNavigationHistory.push(window.location.href);
                            saveStateToStorage();
                            
                            logMessage(`Navigating: Following link to ${href}`, 'navigation');
                            logMessage(`Navigation history: ${window.crawlerNavigationHistory.length} pages stored`, 'info');
                            
                            // Add to selections for configuration
                            const navSelection = {
                                name: fieldName,
                                selector: selector,
                                element_type: 'navigation',
                                description: `Navigation: ${fieldName}`,
                                extraction_type: 'href',
                                workflow_action: 'click',
                                original_content: originalContent,
                                page_url: window.location.href
                            };
                            
                            window.crawlerSelections.push(navSelection);
                            
                            // Track selections per page for better workflow generation
                            const pageKey = window.location.href;
                            if (!window.crawlerPageSelections[pageKey]) {
                                window.crawlerPageSelections[pageKey] = [];
                            }
                            window.crawlerPageSelections[pageKey].push(navSelection);
                            
                            // Persist all state to sessionStorage
                            saveStateToStorage();
                            
                            // Store navigation state for re-injection
                            window.crawlerNavigatedFromNav = true;
                            
                            // Actually navigate immediately
                            window.location.href = href;
                            return;
                        } else {
                            logMessage(`Navigation: Link has no valid href (${href || 'empty'})`, 'navigation');
                        }
                    } else {
                        logMessage(`Navigation: Element selected but not a link ${elementDesc}`, 'navigation');
                    }
                }
                
                // Regular selection logic
                const matchCount = highlightSameClassElements(e.target);
                
                // Create selection object with enhanced context
                const selection = {
                    name: fieldName,
                    selector: selector,
                    element_type: window.crawlerMode === 'data' ? 'data_field' : 
                                 window.crawlerMode === 'items' ? 'items_container' : window.crawlerMode,
                    description: `${window.crawlerMode}: ${fieldName}`,
                    extraction_type: 'text',
                    page_url: window.location.href  // Track which page this selection was made on
                };
                
                // Track selections per page for better workflow generation
                const pageKey = window.location.href;
                if (!window.crawlerPageSelections[pageKey]) {
                    window.crawlerPageSelections[pageKey] = [];
                }
                window.crawlerPageSelections[pageKey].push(selection);
                
                // Store original content and additional context for pagination/navigation elements
                if (window.crawlerMode === 'pagination' || window.crawlerMode === 'nav') {
                    selection.original_content = originalContent;
                    
                    // Store additional attributes for verification (exclude crawler-added attributes)
                    const attributes = {};
                    ['title', 'aria-label', 'role'].forEach(attr => {
                        if (e.target.hasAttribute(attr)) {
                            attributes[attr] = e.target.getAttribute(attr);
                        }
                    });
                    
                    // Handle class attribute separately to filter out crawler classes
                    if (e.target.className) {
                        const originalClasses = e.target.className.split(' ')
                            .filter(c => c.trim() && !c.startsWith('crawler-'))
                            .join(' ');
                        if (originalClasses) {
                            attributes['class'] = originalClasses;
                        }
                    }
                    
                    if (Object.keys(attributes).length > 0) {
                        selection.verification_attributes = attributes;
                    }
                }
                
                window.crawlerSelections.push(selection);
                
                // Persist all state to sessionStorage
                saveStateToStorage();
                
                e.target.classList.add('crawler-selected');
                
                // Enhanced logging with element details and selector strategy
                const selectorFeatures = [];
                if (selector.includes('>')) selectorFeatures.push('parent-context');
                if (selector.includes('[')) selectorFeatures.push('attribute-based');
                if (selector.includes('.')) selectorFeatures.push('class-based');
                const selectorType = selectorFeatures.length > 0 ? selectorFeatures.join(' + ') : 'simple';
                
                logMessage(`Selected: ${fieldName} -> ${selector}`, 'selection');
                logMessage(`Strategy: ${selectorType}${window.crawlerMode === 'pagination' ? ' + text-verification' : ''}`, 'info');
                
                if (matchCount > 0) {
                    logMessage(`Highlighted: ${matchCount} elements with same class composition`, 'highlight');
                }
                
                // Show content verification info for pagination elements
                if (window.crawlerMode === 'pagination' && originalContent) {
                    logMessage(`Text content: "${originalContent}" (for exact matching)`, 'info');
                    logMessage(`Crawler will find all elements matching selector, then filter by text`, 'info');
                }
                
                logMessage(`Element: ${elementDesc}`, 'info');
                
                document.getElementById('field-name').value = '';
                
                // Update guided workflow after selection
                if (window.crawlerGuidedMode) {
                    updateGuidedWorkflow();
                }
                
            }, true);
            
            let hoverTimeout;
            document.addEventListener('mouseover', (e) => {
                if (e.target.closest('#crawler-ui')) return;
                e.target.classList.add('crawler-highlight');
                
                // Show preview of similar elements after a brief delay
                clearTimeout(hoverTimeout);
                hoverTimeout = setTimeout(() => {
                    const targetClasses = Array.from(e.target.classList)
                        .filter(c => !c.startsWith('crawler-'))
                        .sort();
                    
                    if (targetClasses.length > 0) {
                        let similarCount = 0;
                        document.querySelectorAll('*').forEach(el => {
                            if (el.closest('#crawler-ui')) return;
                            if (el === e.target) return;
                            
                            const elementClasses = Array.from(el.classList)
                                .filter(c => !c.startsWith('crawler-'))
                                .sort();
                            
                            if (targetClasses.length === elementClasses.length && 
                                targetClasses.every((cls, i) => cls === elementClasses[i])) {
                                similarCount++;
                            }
                        });
                        
                        if (similarCount > 0) {
                            const elementDesc = getElementDescription(e.target);
                            // Clear any previous preview messages
                            const logDiv = document.getElementById('crawler-log');
                            const entries = logDiv.querySelectorAll('.log-entry');
                            entries.forEach(entry => {
                                if (entry.innerHTML.includes('Preview:')) {
                                    entry.remove();
                                }
                            });
                            logMessage(`Preview: ${similarCount} similar elements found for ${elementDesc}`, 'info');
                        }
                    }
                }, 800); // 800ms delay to avoid spam
            });
            
            document.addEventListener('mouseout', (e) => {
                if (e.target.closest('#crawler-ui')) return;
                e.target.classList.remove('crawler-highlight');
                clearTimeout(hoverTimeout);
            });
            
            function generateSelector(element) {
                // For elements with ID, still prefer ID selector
                if (element.id) return '#' + element.id;
                
                // Simple, robust selector generation - avoid positional selectors
                function generateRobustSelector(el) {
                    let selector = el.tagName.toLowerCase();
                    
                    // Add classes if available (filtered to exclude crawler classes)
                    if (el.className) {
                        const classes = el.className.split(' ')
                            .filter(c => c.trim() && !c.startsWith('crawler-'));
                        if (classes.length > 0) {
                            selector += '.' + classes.join('.');
                        }
                    }
                    
                    // Add natural attributes for extra specificity (only for pagination/nav)
                    if (window.crawlerMode === 'pagination' || window.crawlerMode === 'nav') {
                        if (el.hasAttribute('title')) {
                            selector += `[title="${el.getAttribute('title')}"]`;
                        } else if (el.hasAttribute('aria-label')) {
                            selector += `[aria-label="${el.getAttribute('aria-label')}"]`;
                        } else if (el.hasAttribute('role')) {
                            selector += `[role="${el.getAttribute('role')}"]`;
                        } else if (el.hasAttribute('href')) {
                            // For links, include href pattern matching
                            const href = el.getAttribute('href');
                            if (href && (href.includes('page') || href.includes('next') || href.includes('prev'))) {
                                selector += `[href*="${href.includes('page') ? 'page' : href.includes('next') ? 'next' : 'prev'}"]`;
                            }
                        }
                    }
                    
                    // Add parent context if element selector is too generic
                    const parent = el.parentElement;
                    if (parent && parent.tagName.toLowerCase() !== 'body') {
                        try {
                            const testElements = document.querySelectorAll(selector);
                            if (testElements.length > 5) { // Too many matches, add parent context
                                let parentSelector = parent.tagName.toLowerCase();
                                if (parent.className) {
                                    const parentClasses = parent.className.split(' ')
                                        .filter(c => c.trim() && !c.startsWith('crawler-'))
                                        .slice(0, 2);
                                    if (parentClasses.length > 0) {
                                        parentSelector += '.' + parentClasses.join('.');
                                    }
                                }
                                // Add parent ID if available
                                if (parent.id) {
                                    parentSelector = `#${parent.id}`;
                                }
                                selector = `${parentSelector} > ${selector}`;
                            }
                        } catch (e) {
                            // If querySelector fails, just use simple selector
                            console.log('Selector test failed, using simple selector');
                        }
                    }
                    
                    return selector;
                }
                
                // Use enhanced selector for pagination and navigation elements
                if (window.crawlerMode === 'pagination' || window.crawlerMode === 'nav') {
                    return generateRobustSelector(element);
                }
                
                // For data fields and items, use simpler class-based selectors
                if (element.className) {
                    const classes = element.className.split(' ').filter(c => c.trim() && !c.startsWith('crawler-'));
                    if (classes.length > 0) {
                        // For items container, might want parent context too
                        if (window.crawlerMode === 'items') {
                            return generateRobustSelector(element);
                        }
                        return '.' + classes.join('.');
                    }
                }
                
                // Fallback with positional context
                return generateRobustSelector(element);
            }
            
            // Initialize navigation status and welcome message
            setTimeout(() => {
                updateNavigationStatus();
                
                // Check if this is a re-injection after navigation
                const isReinjection = window.crawlerSelections && window.crawlerSelections.length > 0;
                const isNavigated = window.location.href !== window.crawlerOriginalUrl;
                
                if (isReinjection && isNavigated) {
                    logMessage('🔄 UI re-injected after navigation!', 'info');
                    logMessage(`📍 Current page: ${window.location.href}`, 'navigation');
                    logMessage(`🏠 Original page: ${window.crawlerOriginalUrl}`, 'info');
                    logMessage(`📦 ${window.crawlerSelections.length} selections preserved`, 'info');
                    logMessage(`🧭 Navigation history: ${window.crawlerNavigationHistory?.length || 0} pages`, 'info');
                } else if (isReinjection) {
                    logMessage('🔄 UI re-injected with preserved state!', 'info');
                    logMessage(`📦 ${window.crawlerSelections.length} selections preserved`, 'info');
                } else {
                    logMessage('🎯 Crawler initialized successfully!', 'info');
                    logMessage('💡 Hover over elements to preview, click to select', 'info');
                    logMessage('✨ Strategy: Structural selectors + text verification for pagination', 'info');
                    logMessage('🧭 Navigation mode: Click links to follow them automatically', 'info');
                    logMessage('↩️ Use Back button to return to previous pages', 'info');
                    logMessage('⚡ No positional selectors - robust across page changes!', 'info');
                }
            }, 100);
        """
    
    async def setup_navigation_detection(self):
        """Set up automatic UI re-injection after page navigation"""
        async def handle_navigation(page):
            try:
                # Wait for page to load
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)

                # Check if UI exists, if not re-inject
                ui_exists = await page.evaluate(
                    "() => !!document.getElementById('crawler-ui')"
                )
                if not ui_exists:
                    self.logger.info("🔄 Page navigated, re-injecting UI...")
                    await self.inject_modern_ui()
                else:
                    # UI exists, but make sure backend functions are available
                    await self._inject_backend_state_functions()

            except Exception as e:
                self.logger.error(f"⚠️ Error re-injecting UI after navigation: {e}")

        # Set up the page navigation listener
        self.page.on(
            "domcontentloaded",
            lambda: asyncio.create_task(handle_navigation(self.page)),
        )

