from dibkb_scraper import AmazonScraper
asin = "B0CBNR2ML6"

scraper = AmazonScraper(asin)
scraper.page_html_to_text()
print(scraper.get_all_reviews())

