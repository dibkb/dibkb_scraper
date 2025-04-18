from dibkb_scraper import AmazonScraper
from dibkb_scraper.playwright import PlaywrightScraper
import asyncio
from bs4 import BeautifulSoup
asin = "B0DB2LWFNY"
# asin = "B0C1N2YPX6"



async def main():
    scraper = PlaywrightScraper()
    await scraper.initialize()
    html = await scraper.get_html_content(f"https://www.amazon.in/dp/{asin}")
    soup = BeautifulSoup(html, "html.parser")
    await scraper.close()
    # print("--------------------------------")
    print(soup)
    print("--------------------------------")
    scraper = AmazonScraper(asin,soup)
    print(scraper.get_competitors())
    print("--------------------------------")
if __name__ == "__main__":
    asyncio.run(main())
