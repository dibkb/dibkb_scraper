import random
from playwright_stealth import stealth_async
from playwright.async_api import async_playwright
from fake_useragent import UserAgent
from typing import Dict

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
                headless=True,
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
    
    async def get_html_content(self, url: str, max_retries: int = 3):
        """
        Navigate to a URL and return the HTML content of the page.
        
        Args:
            url: The URL to navigate to
            max_retries: Maximum number of retries on connection failure
            
        Returns:
            The HTML content of the page
        """
        if not self._browser or not self._initialized:
            await self.initialize()
            if not self._initialized:
                return None
        
        retries = 0
        while retries < max_retries:
            try:
                # Define random viewport dimensions and common headers
                viewport_width = random.randint(1920, 2560)
                viewport_height = random.randint(1080, 1440)
                ua = UserAgent()
                user_agent = ua.random
                headers = {
                    'User-Agent': user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                }

                # Create browser context
                try:
                    context = await self._browser.new_context(
                        viewport={'width': viewport_width, 'height': viewport_height},
                        user_agent=user_agent,
                        ignore_https_errors=True,
                        extra_http_headers=headers,
                        locale='en-US',
                        timezone_id='America/New_York',
                        geolocation={'latitude': 40.730610, 'longitude': -73.935242},  # New York coordinates
                        permissions=['geolocation']
                    )
                except Exception as e:
                    print(f"Error creating context: {e}")
                    retries += 1
                    continue
                
                # Add cookie handling for specific sites
                if "amazon" in url:
                    await context.add_cookies([
                        {
                            "name": "session-id",
                            "value": str(random.randint(10000000, 99999999)),
                            "domain": ".amazon.in" if "amazon.in" in url else ".amazon.com",
                            "path": "/"
                        },
                        {
                            "name": "i18n-prefs",
                            "value": "USD",
                            "domain": ".amazon.in" if "amazon.in" in url else ".amazon.com",
                            "path": "/"
                        }
                    ])
                
                page = await context.new_page()
                await stealth_async(page)
                
                # Add random mouse movements to appear more human-like
                await page.mouse.move(random.randint(0, viewport_width), random.randint(0, viewport_height))
                
                # Navigate to the URL with timeout, catching connection errors
                try:
                    response = await page.goto(url, timeout=30000)
                except Exception as e:
                    print(f"Navigation error: {e}")
                    await context.close()
                    retries += 1
                    continue
                
                # Check if we got blocked or redirected to CAPTCHA
                current_url = page.url
                if "captcha" in current_url.lower() or "robot" in current_url.lower():
                    print(f"Hit CAPTCHA or bot detection at {current_url}")
                    await context.close()
                    if retries < max_retries - 1:
                        retries += 1
                        continue
                    return None
                
                # Scroll down a bit to trigger any lazy loading
                await page.evaluate("""
                    window.scrollTo({
                        top: 1000,
                        behavior: 'smooth'
                    });
                """)
                
                # Wait a bit more for any dynamic content
                await page.wait_for_timeout(3000)
                
                # Get the HTML content
                html_content = await page.content()
                
                # Close the context when done
                await context.close()
                
                # Check if response looks like a bot detection page
                if len(html_content) < 5000 and ("robot" in html_content.lower() or 
                                                "captcha" in html_content.lower() or
                                                "blocked" in html_content.lower() or
                                                "verify" in html_content.lower()):
                    print("Got bot detection page response")
                    if retries < max_retries - 1:
                        retries += 1
                        continue
                    return None
                
                return html_content
                
            except Exception as e:
                print(f"Error getting HTML content: {e}")
                retries += 1
                if retries >= max_retries:
                    return None
                print(f"Retrying... (attempt {retries}/{max_retries})")
        
        return None

# Example usage:
# async def main():
#     scraper = PlaywrightScraper()
#     await scraper.initialize()
#     html = await scraper.get_html_content("https://example.com")
#     print(html)
#     await scraper.close()