from dibkb_scraper import AmazonScraper
asin = "B0DRC6HQN3"

scraper = AmazonScraper(asin)
# scraper.page_html_to_text()
print(scraper.get_all_details())

