from .models import (
    AmazonProductResponse, Description, 
    Pricing, Product, Ratings, Specifications
)
from .utils import extract_numbers, extract_text, filter_unicode, AMAZON_HEADERS
import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union



class AmazonScraper:
    def __init__(self, asin: str):
        self.asin = asin
        self.url = f"https://www.amazon.in/dp/{self.asin}"
        self.headers = AMAZON_HEADERS
        self.soup = self._get_soup()
    

    def page_html_to_text(self,name:Optional[str]=None):
        if not name:
            name = self.asin
        with open(f"{name}.txt", "w") as f:
            f.write(self.soup.prettify())

    def _get_soup(self) -> Optional[BeautifulSoup]:
        try:
            response = httpx.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes
            return BeautifulSoup(response.text, 'html.parser')
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"Error fetching the page: {str(e)}")
            return None

    def get_product_title(self) -> Optional[str]:
        try:
            title_elem = self.soup.find('span', {'id': 'productTitle'})
            return title_elem.text.strip() if title_elem else None
        except AttributeError:
            return None

    def get_mrp(self) -> Optional[float]:
        try:
            mrp_elem = self.soup.find("span", {"class": "a-size-mini a-color-secondary aok-nowrap a-text-strike"})
            if mrp_elem:
                return extract_numbers(mrp_elem.text.strip())
            return None
        except AttributeError:
            return None

    def get_selling_price(self) -> Optional[float]:
        try:
            price_elem = self.soup.find("span", {"class": "a-price-whole"})
            if price_elem:
                return extract_numbers(price_elem.text.strip())
            return None
        except AttributeError:
            return None

    def get_tags(self) -> List[str]:
        try:
            breadcrumbs = self.soup.find("ul", {"class": "a-unordered-list a-horizontal a-size-small"})
            if breadcrumbs:
                return [x.text.strip() for x in breadcrumbs.find_all("a")]
            return []
        except AttributeError:
            return []

    def get_technical_info(self) -> Dict[str, str]:
        try:
            table = self.soup.find("table", {"class": "prodDetTable", "id":"productDetails_techSpec_section_1"})

            if not table:
                return {}
                
            info = {}
            for tr in table.find_all("tr"):
                try:
                    key = filter_unicode(tr.find("th").text.strip())
                    value = filter_unicode(tr.find("td").text.strip())
                    info[key] = value
                except AttributeError:
                    continue
            return info
        except AttributeError:
            return {}
        
    def get_additional_info(self)->Dict[str,str]:
        try:
            table = self.soup.find("table", {"class": "prodDetTable", "id":"productDetails_detailBullets_sections1"})

            if not table:
                return {}
            info = {}

            for tr in table.find_all("tr"):
                try:
                    key = filter_unicode(tr.find("th").text.strip())
                    value = filter_unicode(tr.find("td").text.strip())
                    info[key] = value
                except AttributeError:
                    continue
            return info
        except AttributeError:
            return {}

    def get_product_details(self)->Dict[str,str]:
        try:
            div = self.soup.find("div", {"id": "detailBullets_feature_div"})
            if not div:
                return {}
            info = {}
            for li in div.find_all("span",{"class" : "a-list-item"}):
                spans = li.find_all("span")
                if len(spans) == 2:
                    key = extract_text(spans[0].text.strip())
                    value = extract_text(spans[1].text.strip())
                    info[key] = value
            return info

        except Exception as e:
            return {"error": str(e)}

    def get_ratings(self) -> Ratings:
        try:
            result = Ratings(
                rating=None,
                review_count=None
            )
            
            # Get rating
            rating_elem = self.soup.find("span", {"data-hook": "rating-out-of-text"})
            if rating_elem:
                ratings_text = rating_elem.text.strip().split()
                if ratings_text and len(ratings_text) >= 1:
                    try:
                        result.rating = float(ratings_text[0])
                    except (ValueError, TypeError):
                        pass

            # Get review count
            review_elem = self.soup.find("span", {"data-hook": "total-review-count"})
            if review_elem:
                review_text = review_elem.text.strip().replace(',', '') 
                try:
                    result.review_count = int(''.join(filter(str.isdigit, review_text)))
                except (ValueError, TypeError):
                    pass

            # Try alternative rating source if main one failed
            if result.rating is None:
                try:
                    alt_review_elem = self.soup.find("span", {"class": "reviewCountTextLinkedHistogram"})
                    if alt_review_elem and alt_review_elem.get("title"):
                        result.rating = float(alt_review_elem["title"].strip().split()[0])
                except (ValueError, TypeError, AttributeError):
                    pass

            return result
            
        except Exception as e:
            return Ratings(
                rating=None,
                review_count=None
            )

    def get_about(self) -> Union[List[str], Dict[str, str]]:
        try:
            if not self.soup:
                return {"error": "No page content available"}

            about_elem = self.soup.find("div", {"id": "feature-bullets"})
            if not about_elem:
                return []

            lis = about_elem.find_all("span", {
                "class": "a-list-item",
                "hidden": None 
            })

            about_list = [
                x.text.strip()
                for x in lis
                if x and x.text and x.text.strip()
            ]
            
            return about_list

        except AttributeError as e:
            return {"error": f"Failed to parse page structure: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}


    def get_all_details(self) -> AmazonProductResponse:
        """Get all product details in a single dictionary"""
        if not self.soup:
            return AmazonProductResponse(
                error="Failed to fetch page",
                product=Product(
                    pricing=Pricing(),
                    description=Description(),
                    specifications=Specifications(),
                    ratings=Ratings()
                )
            )
            
        return AmazonProductResponse(
            product=Product(
                title=self.get_product_title(),
                pricing=Pricing(
                    mrp=self.get_mrp(),
                    selling_price=self.get_selling_price()
                ),
                categories=self.get_tags(),
                description=Description(
                    highlights=self.get_about()
                ),
                specifications=Specifications(
                    technical=self.get_technical_info(),
                    additional=self.get_additional_info(),
                    details=self.get_product_details()
                ),
                ratings=self.get_ratings()
            )
        )


# scraper = AmazonScraper("B00935MGKK")
# # scraper.page_html_to_text()
# print(scraper.get_all_details())