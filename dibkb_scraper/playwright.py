import random
from playwright_stealth import stealth_async
from playwright.async_api import async_playwright

class PlaywrightScraper:
    """
    A singleton class for managing Playwright browser instances and web scraping.
    """
    _instance = None
    _browser = None
    _playwright = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlaywrightScraper, cls).__new__(cls)
            cls._initialized = False
        return cls._instance
    
    async def initialize(self):
        """Initialize the browser if not already initialized."""
        if self._initialized:
            return
        
        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                ]
            )
            self._initialized = True
            print("Browser initialized successfully")
        except Exception as e:
            print(f"Failed to initialize browser: {e}")
    
    async def close(self):
        """Close the browser and playwright instance."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        
        self._initialized = False
        print("Browser closed")
    
    async def get_html_content(self, url: str):
        """
        Navigate to a URL and return the HTML content of the page.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            The HTML content of the page
        """
        if not self._browser or not self._initialized:
            await self.initialize()
            if not self._initialized:
                return None
        
        try:
            # Define random viewport dimensions and common headers
            viewport_width = random.randint(1024, 1920)
            viewport_height = random.randint(768, 1080)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            }

            # Create new page with enhanced configuration
            context = await self._browser.new_context(
                viewport={'width': viewport_width, 'height': viewport_height},
                user_agent=headers['User-Agent'],
                ignore_https_errors=True,
                extra_http_headers=headers,
                locale='en-US',
                timezone_id='America/New_York',
                geolocation={'latitude': 40.730610, 'longitude': -73.935242},  # New York coordinates
                permissions=['geolocation']
            )
            
            page = await context.new_page()
            await stealth_async(page)
            
            # Navigate to the URL
            await page.goto(url)
            
            # Get the HTML content
            html_content = await page.content()
            
            # Close the context when done
            await context.close()
            
            return html_content
            
        except Exception as e:
            print(f"Error getting HTML content: {e}")
            return None

# Example usage:
# async def main():
#     scraper = PlaywrightScraper()
#     await scraper.initialize()
#     html = await scraper.get_html_content("https://example.com")
#     print(html)
#     await scraper.close()