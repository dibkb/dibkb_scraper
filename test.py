from dibkb_scraper import AmazonScraper
asin = "B071VNHMX2"
scraper = AmazonScraper(asin)
print(scraper.get_all_details())
