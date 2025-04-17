from dibkb_scraper import AmazonScraper
from dibkb_scraper.playwright import PlaywrightScraper
import asyncio
asin = "B0DFB26FD8"

scraper = AmazonScraper(asin)
print(scraper.get_html())

# async def main():
#     scraper = PlaywrightScraper()
#     await scraper.initialize()
#     print(await scraper.get_html_content("https://www.amazon.in/dp/B0DFB26FD8"))
#     await scraper.close()

# if __name__ == "__main__":
#     asyncio.run(main())
