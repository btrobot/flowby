"""
Playwright Browser Wrapper

Provides a simple interface to launch and manage Playwright browsers.
"""

from typing import Optional
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext


class PlaywrightWrapper:
    """
    Wrapper for Playwright browsers

    Manages browser lifecycle and provides a simple API for browser automation.
    """

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def launch(
        self, browser_type: str = "chromium", headless: bool = False, **launch_options
    ) -> Page:
        """
        Launch a browser and return the page

        Args:
            browser_type: Browser type ('chromium', 'firefox', 'webkit')
            headless: Whether to run in headless mode
            **launch_options: Additional launch options

        Returns:
            Page object for automation

        Raises:
            ValueError: If browser_type is invalid
        """
        self.playwright = sync_playwright().start()

        # Select browser
        if browser_type == "chromium":
            browser_launcher = self.playwright.chromium
        elif browser_type == "firefox":
            browser_launcher = self.playwright.firefox
        elif browser_type == "webkit":
            browser_launcher = self.playwright.webkit
        else:
            raise ValueError(f"Invalid browser type: {browser_type}")

        # Launch browser
        self.browser = browser_launcher.launch(headless=headless, **launch_options)

        # Create context and page
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

        return self.page

    def get_page(self) -> Optional[Page]:
        """
        获取当前页面对象

        Returns:
            当前的 Page 对象，如果未初始化则返回 None
        """
        return self.page

    def close(self):
        """Close the browser and cleanup resources"""
        if self.page:
            self.page.close()
            self.page = None

        if self.context:
            self.context.close()
            self.context = None

        if self.browser:
            self.browser.close()
            self.browser = None

        if self.playwright:
            self.playwright.stop()
            self.playwright = None

    def __enter__(self):
        """Context manager support"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()
