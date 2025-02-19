from dibkb_scraper import AmazonScraper
asin = "B09ZV233RH"

scraper = AmazonScraper(asin)
print(scraper.get_rating_percentage())
