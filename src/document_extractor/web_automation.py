"""
Web Form Automation Module
Uses Playwright to automate web form filling
"""

from typing import Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser
import time


class WebFormAutomator:
    """Automates web form filling using Playwright"""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the web automator
        
        Args:
            headless: Whether to run browser in headless mode (default: True)
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
    
    def start_browser(self):
        """Start the browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
    
    def close_browser(self):
        """Close the browser"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def fill_form_by_selectors(self, url: str, field_mapping: Dict[str, str], 
                              submit_button_selector: Optional[str] = None,
                              wait_time: int = 2) -> bool:
        """
        Fill a web form using CSS selectors
        
        Args:
            url: URL of the form page
            field_mapping: Dictionary mapping field names to CSS selectors
                          Example: {"name": "#name-input", "email": "input[name='email']"}
            submit_button_selector: CSS selector for submit button (optional)
            wait_time: Time to wait after filling (seconds)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.page:
                self.start_browser()
            
            # Navigate to the form
            self.page.goto(url)
            self.page.wait_for_load_state("networkidle")
            
            # Fill each field
            for field_name, selector in field_mapping.items():
                try:
                    element = self.page.locator(selector)
                    if element.count() > 0:
                        element.fill(field_mapping.get(field_name, ""))
                        time.sleep(0.2)  # Small delay between fields
                    else:
                        print(f"Warning: Field '{field_name}' with selector '{selector}' not found")
                except Exception as e:
                    print(f"Error filling field '{field_name}': {str(e)}")
            
            # Wait before submitting
            time.sleep(wait_time)
            
            # Submit if button selector provided
            if submit_button_selector:
                try:
                    self.page.locator(submit_button_selector).click()
                    self.page.wait_for_load_state("networkidle")
                    return True
                except Exception as e:
                    print(f"Error clicking submit button: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error filling form: {str(e)}")
            return False
    
    def fill_form_by_labels(self, url: str, data: Dict[str, str],
                           submit_button_text: Optional[str] = None,
                           wait_time: int = 2) -> bool:
        """
        Fill a web form by finding fields by their labels
        
        Args:
            url: URL of the form page
            data: Dictionary of field labels to values
                  Example: {"Name": "John Doe", "Email": "john@example.com"}
            submit_button_text: Text on the submit button (optional)
            wait_time: Time to wait after filling (seconds)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.page:
                self.start_browser()
            
            # Navigate to the form
            self.page.goto(url)
            self.page.wait_for_load_state("networkidle")
            
            # Fill each field by label
            for label, value in data.items():
                try:
                    # Try to find input by label text
                    label_element = self.page.locator(f"label:has-text('{label}')")
                    if label_element.count() > 0:
                        # Get the associated input
                        input_id = label_element.get_attribute("for")
                        if input_id:
                            self.page.fill(f"#{input_id}", value)
                        else:
                            # Try to find input near the label
                            input_element = label_element.locator("..").locator("input, textarea, select")
                            if input_element.count() > 0:
                                input_element.fill(value)
                    else:
                        # Try to find by placeholder or name
                        self.page.fill(f"input[placeholder*='{label}'], input[name*='{label.lower()}']", value)
                    
                    time.sleep(0.2)
                except Exception as e:
                    print(f"Error filling field '{label}': {str(e)}")
            
            # Wait before submitting
            time.sleep(wait_time)
            
            # Submit if button text provided
            if submit_button_text:
                try:
                    self.page.locator(f"button:has-text('{submit_button_text}'), input[value*='{submit_button_text}']").click()
                    self.page.wait_for_load_state("networkidle")
                    return True
                except Exception as e:
                    print(f"Error clicking submit button: {str(e)}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error filling form: {str(e)}")
            return False
    
    def take_screenshot(self, file_path: str):
        """Take a screenshot of the current page"""
        if self.page:
            self.page.screenshot(path=file_path)
    
    def wait_for_element(self, selector: str, timeout: int = 10000):
        """Wait for an element to appear"""
        if self.page:
            self.page.wait_for_selector(selector, timeout=timeout)
    
    def __enter__(self):
        """Context manager entry"""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_browser()

