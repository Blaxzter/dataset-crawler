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
    
    def __init__(self, page: Page):
        self.page = page
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
                <div class="crawler-title">Element Selector</div>
                
                <div style="margin-bottom: 10px;">
                    <button class="crawler-btn active" onclick="setCrawlerMode('data', this)">Data Field</button>
                    <button class="crawler-btn" onclick="setCrawlerMode('items', this)">Items</button><br>
                    <button class="crawler-btn" onclick="setCrawlerMode('pagination', this)">Pagination</button>
                    <button class="crawler-btn" onclick="setCrawlerMode('nav', this)">Navigation</button><br>
                    <button class="crawler-btn" onclick="toggleWorkflowMode(this)" id="workflow-btn">🔧 Workflow Mode</button>
                </div>
                
                <input type="text" class="crawler-input" id="field-name" placeholder="Field name...">
                
                <div style="text-align: center; margin-bottom: 10px;">
                    <button class="crawler-btn" onclick="window.finishCrawlerConfig()">Finish & Save</button>
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
            self.logger.info(f"✅ {result}")
        except Exception as e:
            self.logger.error(f"❌ UI injection failed: {e}")
    
    def _get_ui_javascript(self):
        """Get the main UI JavaScript code"""
        return """
            // Set up global variables and functions with persistent storage
            window.crawlerMode = 'data';
            
            // Load persistent state from sessionStorage
            try {
                window.crawlerSelections = JSON.parse(sessionStorage.getItem('crawlerSelections')) || [];
                window.crawlerNavigationHistory = JSON.parse(sessionStorage.getItem('crawlerNavigationHistory')) || [];
                window.crawlerPageSelections = JSON.parse(sessionStorage.getItem('crawlerPageSelections')) || {};
                window.crawlerOriginalUrl = sessionStorage.getItem('crawlerOriginalUrl') || window.location.href;
            } catch (e) {
                console.log('Initializing fresh crawler state');
                window.crawlerSelections = [];
                window.crawlerNavigationHistory = [];
                window.crawlerPageSelections = {};
                window.crawlerOriginalUrl = window.location.href;
            }
            
            window.crawlerLogHistory = [];
            window.crawlerWorkflowMode = false;
            
            // If this is the first time, set original URL
            if (!sessionStorage.getItem('crawlerOriginalUrl')) {
                sessionStorage.setItem('crawlerOriginalUrl', window.location.href);
                window.crawlerOriginalUrl = window.location.href;
            }
            
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
            
            // Function to set crawler mode
            window.setCrawlerMode = (mode, buttonElement) => {
                window.crawlerMode = mode;
                document.querySelectorAll('.crawler-btn').forEach(btn => btn.classList.remove('active'));
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
            
            // Workflow mode toggle
            window.toggleWorkflowMode = (buttonElement) => {
                window.crawlerWorkflowMode = !window.crawlerWorkflowMode;
                if (window.crawlerWorkflowMode) {
                    buttonElement.style.background = '#ff4444';
                    buttonElement.textContent = '🔧 Workflow: ON';
                    logMessage('Workflow Mode: ENABLED - Nav selections will create workflows', 'mode');
                } else {
                    buttonElement.style.background = '#007cba';
                    buttonElement.textContent = '🔧 Workflow Mode';
                    logMessage('Workflow Mode: DISABLED - Nav selections for manual use only', 'mode');
                }
            };
            
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
                        cleanupBtn.onclick = () => {
                            sessionStorage.removeItem('crawlerSelections');
                            sessionStorage.removeItem('crawlerNavigationHistory');
                            sessionStorage.removeItem('crawlerPageSelections');
                            sessionStorage.removeItem('crawlerOriginalUrl');
                            logMessage('🧹 Session storage cleared', 'info');
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
                    // Persist updated history
                    sessionStorage.setItem('crawlerNavigationHistory', JSON.stringify(window.crawlerNavigationHistory));
                    
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
            
            // Helper function to save all state to sessionStorage
            function saveStateToStorage() {
                try {
                    sessionStorage.setItem('crawlerSelections', JSON.stringify(window.crawlerSelections || []));
                    sessionStorage.setItem('crawlerNavigationHistory', JSON.stringify(window.crawlerNavigationHistory || []));
                    sessionStorage.setItem('crawlerPageSelections', JSON.stringify(window.crawlerPageSelections || {}));
                    sessionStorage.setItem('crawlerOriginalUrl', window.crawlerOriginalUrl || window.location.href);
                } catch (e) {
                    console.warn('Failed to save crawler state:', e);
                }
            }
            
            // Function to update navigation status
            function updateNavigationStatus() {
                const navStatus = document.getElementById('nav-status');
                const backBtn = document.getElementById('back-btn');
                
                console.log('Navigation Status Check:', {
                    current: window.location.href,
                    original: window.crawlerOriginalUrl,
                    historyLength: window.crawlerNavigationHistory?.length || 0
                });
                
                if (navStatus) {
                    const isOriginalPage = window.location.href === window.crawlerOriginalUrl;
                    const hasHistory = window.crawlerNavigationHistory && window.crawlerNavigationHistory.length > 0;
                    
                    if (isOriginalPage && !hasHistory) {
                        navStatus.textContent = 'Original Page';
                        if (backBtn) backBtn.style.display = 'none';
                    } else {
                        navStatus.textContent = `Navigated Page (${window.crawlerNavigationHistory?.length || 0} back)`;
                        if (backBtn) backBtn.style.display = 'inline-block';
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
                
                // Handle navigation mode differently
                if (window.crawlerMode === 'nav') {
                    // If it's a link, follow it
                    if (e.target.tagName.toLowerCase() === 'a' || e.target.closest('a')) {
                        const link = e.target.tagName.toLowerCase() === 'a' ? e.target : e.target.closest('a');
                        const href = link.href;
                        
                        if (href && !href.startsWith('javascript:') && !href.startsWith('#')) {
                            // Store current URL in navigation history (with persistence)
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

            except Exception as e:
                self.logger.error(f"⚠️ Error re-injecting UI after navigation: {e}")

        # Set up the page navigation listener
        self.page.on(
            "domcontentloaded",
            lambda: asyncio.create_task(handle_navigation(self.page)),
        )

