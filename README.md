# AmazonScraper Python Package Documentation

AmazonScraper is a Python package for scraping product details from Amazon.in using a product's ASIN. It retrieves various pieces of information including the product title, pricing, categories, technical details, additional specifications, ratings, and feature highlights.

## Downloads

[![PyPI Downloads](https://static.pepy.tech/badge/dibkb-scraper)](https://pepy.tech/projects/dibkb-scraper)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Saving the HTML](#saving-the-html)
- [API Reference](#api-reference)
  - [AmazonScraper Class](#amazonscraper-class)
  - [Data Models](#data-models)
- [Error Handling](#error-handling)
- [License](#license)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)

## Overview

AmazonScraper is designed to extract detailed information from an Amazon.in product page by parsing its HTML. With this package, users can retrieve:

- **Product Title**
- **Pricing Details** (MRP and Selling Price)
- **Category Tags (Breadcrumbs)**
- **Technical and Additional Specifications**
- **Detailed Product Information (Bullet Points)**
- **Ratings and Review Counts**
- **Feature Highlights (About Section)**

## Features

- **Comprehensive Scraping**: Extracts all relevant product data in one go.
- **Robust Error Handling**: Gracefully handles missing data or page fetch errors.
- **Structured Data Models**: Returns data in easy-to-use Python dataclasses.
- **Customizable HTML Saving**: Option to save the prettified HTML for debugging.

## Requirements

- Python 3.7 or higher
- [httpx](https://www.python-httpx.org/) for HTTP requests
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for HTML parsing

Install the dependencies via pip:

```bash
pip install httpx beautifulsoup4 pydantic fake_useragent
```

## Installation

Clone or download the repository and ensure that the package structure (including the `models` and `utils` modules) is maintained. Then, include the package in your project as needed.

## Usage

### Basic Usage

Below is a sample code snippet to demonstrate how to use the AmazonScraper:

```python
from dibkb_scraper import AmazonScraper
# Initialize the scraper with a valid Amazon ASIN
asin = "B00935MGKK"
scraper = AmazonScraper(asin)

# Retrieve all product details
product_details = scraper.get_all_details()

# Access and print various product attributes
print("Title:", product_details.product.title)
print("MRP:", product_details.product.pricing.mrp)
print("Selling Price:", product_details.product.pricing.selling_price)
print("Categories:", product_details.product.categories)
print("Highlights:", product_details.product.description.highlights)
print("Technical Specs:", product_details.product.specifications.technical)
print("Additional Specs:", product_details.product.specifications.additional)
print("Detail Bullets:", product_details.product.specifications.details)
print("Ratings:", product_details.product.ratings.rating)
print("Review Count:", product_details.product.ratings.review_count)
```

### Saving the HTML

To save the prettified HTML of the product page (useful for debugging), use the `page_html_to_text` method:

```python
# Saves the HTML content to 'B00935MGKK.txt' (or a custom file name)
scraper.page_html_to_text("B00935MGKK_page")
```

## API Reference

### AmazonScraper Class

#### `__init__(self, asin: str)`

- **Parameters:**
  - `asin` (`str`): The Amazon Standard Identification Number of the product.
- **Description:** Initializes the scraper, constructs the product URL, sets HTTP headers, and retrieves the HTML content.

#### `page_html_to_text(self, name: Optional[str] = None)`

- **Parameters:**
  - `name` (`Optional[str]`): Optional filename for the output text file. Defaults to the ASIN if not provided.
- **Description:** Saves the prettified HTML of the product page into a text file.

#### `get_product_title(self) -> Optional[str]`

- **Returns:** The product title as a string, or `None` if not found.
- **Description:** Extracts and returns the product title from the page.

#### `get_mrp(self) -> Optional[float]`

- **Returns:** The Maximum Retail Price (MRP) as a float, or `None` if not found.
- **Description:** Extracts the MRP from the designated HTML element.

#### `get_selling_price(self) -> Optional[float]`

- **Returns:** The selling price as a float, or `None` if not found.
- **Description:** Retrieves the selling price from the page.

#### `get_tags(self) -> List[str]`

- **Returns:** A list of category tags (breadcrumbs) as strings.
- **Description:** Extracts breadcrumb links that indicate product categories.

#### `get_technical_info(self) -> Dict[str, str]`

- **Returns:** A dictionary of technical specifications in key-value pairs.
- **Description:** Parses the technical details table from the product page.

#### `get_additional_info(self) -> Dict[str, str]`

- **Returns:** A dictionary containing additional product details.
- **Description:** Extracts further details from the secondary details table.

#### `get_product_details(self) -> Dict[str, str]`

- **Returns:** A dictionary of detailed product information (e.g., bullet points).
- **Description:** Retrieves information from the "detail bullets" section of the product page.

#### `get_ratings(self) -> Ratings`

- **Returns:** A `Ratings` object containing the product's average rating and the total review count.
- **Description:** Extracts rating and review count, with a fallback method if the primary extraction fails.

#### `get_about(self) -> Union[List[str], Dict[str, str]]`

- **Returns:** A list of product description highlights, or an error dictionary if extraction fails.
- **Description:** Retrieves the feature bullets from the "feature-bullets" section.

#### `get_all_details(self) -> AmazonProductResponse`

- **Returns:** An `AmazonProductResponse` object that consolidates all scraped product details. If the page fails to load, the response includes an error message.
- **Description:** Aggregates all product data into a structured response.

### Data Models

The package uses several dataclasses to organize the scraped data:

#### Ratings

- **Attributes:**
  - `rating` (`Optional[float]`): The average product rating.
  - `review_count` (`Optional[int]`): The total number of reviews.

#### Pricing

- **Attributes:**
  - `mrp` (`Optional[float]`): The Maximum Retail Price.
  - `selling_price` (`Optional[float]`): The current selling price.

#### Description

- **Attributes:**
  - `highlights` (`List[str]`): A list of product highlight points.

#### Specifications

- **Attributes:**
  - `technical` (`Dict[str, str]`): Technical specifications from the product page.
  - `additional` (`Dict[str, str]`): Additional product details.
  - `details` (`Dict[str, str]`): Detailed information extracted from the bullet points.

#### Product

- **Attributes:**
  - `title` (`Optional[str]`): The product title.
  - `pricing` (`Pricing`): Pricing details of the product.
  - `categories` (`List[str]`): Category tags (breadcrumbs).
  - `description` (`Description`): Feature highlights.
  - `specifications` (`Specifications`): Detailed specifications.
  - `ratings` (`Ratings`): Rating information.

#### AmazonProductResponse

- **Attributes:**
  - `product` (`Product`): An object containing all the scraped product details.
  - `error` (`Optional[str]`): An error message if the scraping process fails.

## Error Handling

- **Page Fetch Errors:** If the scraper fails to retrieve the page (e.g., due to network issues or an invalid ASIN), the `AmazonProductResponse` will include an `error` field.
- **Parsing Exceptions:** Individual methods include exception handling to ensure that missing elements do not break the entire scraping process.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for full details.

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request with your suggestions or improvements.

## Disclaimer

This package is provided for educational and research purposes only. Users must comply with Amazon's terms of service and applicable laws when scraping websites. Use the package responsibly.
