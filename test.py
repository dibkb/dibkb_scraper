from dibkb_scraper import AmazonScraper
from dibkb_scraper.playwright import PlaywrightScraper
import asyncio
asin = "B0DB2LWFNY"



async def main():
    # scraper = PlaywrightScraper()
    # await scraper.initialize()
    # html = (await scraper.get_html_content(f"https://www.amazon.in/dp/{asin}"))
    # await scraper.close()
    # print(html)
    # print("--------------------------------")
    scraper = AmazonScraper(asin)
    soup = scraper._get_soup()
    print(soup)
    print("--------------------------------")
    print(scraper.get_all_details())
    print("--------------------------------")
if __name__ == "__main__":
    asyncio.run(main())
