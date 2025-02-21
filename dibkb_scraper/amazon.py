import math
from .models import (
    AmazonProductResponse, Description, RatingPercentage,
    Product, RatingStats, Ratings, Review, Specifications, StarRating
)
from .utils import extract_text, filter_unicode, AMAZON_HEADERS
import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union
import json



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

    def get_selling_price(self) -> Optional[float]:
        try:
            price_elem = self.soup.find("div", {"class": "a-section aok-hidden twister-plus-buying-options-price-data"})
            if price_elem:
                price_data = json.loads(price_elem.text.strip())
                display_price = price_data["desktop_buybox_group_1"][0]["displayPrice"]
                price = float(display_price.replace("₹", "").replace(",", ""))
                return price
            return None
        except (AttributeError, json.JSONDecodeError, KeyError):
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

    def get_rating_percentage(self) -> RatingPercentage:
        try:
            rating_percentage = self.soup.find_all("span", {"class": "_cr-ratings-histogram_style_histogram-column-space__RKUAd"})[5:10]
            
            if not rating_percentage:
                return RatingPercentage(
                    one_star=None,
                    two_star=None,
                    three_star=None,
                    four_star=None,
                    five_star=None
                )
            
            ratings = []
            for span in rating_percentage:
                try:
                    text = span.text.strip()
                    value = int(text.replace("%", ""))
                    if 0 <= value <= 100:  # Validate percentage range
                        ratings.append(value)
                    else:
                        raise ValueError("Percentage out of range")
                except (ValueError, AttributeError):
                    ratings.append(None)

            if len(ratings) != 5 or None in ratings:
                return RatingPercentage(
                    one_star=None,
                    two_star=None,
                    three_star=None,
                    four_star=None,
                    five_star=None
                )
            
            return RatingPercentage(
                five_star=ratings[0],
                four_star=ratings[1],
                three_star=ratings[2],
                two_star=ratings[3],
                one_star=ratings[4]
            )

        
        except Exception as e:
            return RatingPercentage(
                one_star=None,
                two_star=None,
                three_star=None,
                four_star=None,
                five_star=None
            )

    def get_ratings(self) -> Ratings:
        try:
            result = Ratings(
                rating=None,
                review_count=None,
                rating_stats=None
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
            
            rating_percentage = self.get_rating_percentage()
            

            number_to_word = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five'}
            star_ratings = {}
            for stars in range(1, 6):
                percentage = getattr(rating_percentage, f"{number_to_word[stars]}_star")

                count = math.floor(percentage * result.review_count / 100) if percentage and result.review_count else None

                star_ratings[f"{number_to_word[stars]}_star"] = StarRating(count=count, percentage=percentage)
            
            result.rating_stats = RatingStats(**star_ratings)

            return result
            
        except Exception as e:
            return Ratings(
                rating=None,
                review_count=None,
                rating_stats=None
            )

    def get_product_images(self) -> Optional[List[str]]:
        try:
            images = []
            
            # Get main product image
            if img_parent := self.soup.find("div", {"id": "imgTagWrapperId"}):
                if img_element := img_parent.find("img"):
                    if img_url := img_element.get("src"):
                        images.append(img_url)

            # Get thumbnail images
            for img in self.soup.find_all("span", {"class": "a-button a-button-thumbnail a-button-toggle"}):
                try:
                    if img_element := img.find("img"):
                        if img_url := img_element.get("src"):
                            images.append(img_url)
                except AttributeError:
                    continue

            # Extract valid image IDs
            img_ids = [
                image.split("/I/")[-1].split("._")[0]
                for image in images
                if len(image.split("/I/")) > 1  # Ensure URL contains "/I/" segment
            ]
            
            # Filter for valid 11-char IDs
            valid_ids = [img_id for img_id in img_ids if len(img_id) == 11]
            
            return valid_ids if valid_ids else None

        except Exception as e:
            print(f"Error extracting product images: {str(e)}")
            return None

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

    def get_all_reviews(self) -> List[Review]:
        """
        Retrieves all reviews from the product page.
        
        Returns:
            List[Dict[str, Optional[str]]]: List of reviews, each containing user, rating, title, text and date
        """
        reviews = []
        try:
            review_elems = self.soup.find_all("div", {"class": "cr-lightbox-review-information"})
            
            for review in review_elems[1:]:
                review_data = {
                    "user": None,
                    "rating": None,
                    "title": None,
                    "text": None,
                    "date": None
                }
                
                try:
                    if user_elem := review.find("span", {"class": "a-profile-name"}):
                        review_data["user"] = user_elem.text.strip()

                    if rating_elem := review.find("span", {"class": "a-icon-alt"}):
                        rating_text = rating_elem.text.strip().split()[0]
                        review_data["rating"] = rating_text
                        
                    if title_elem := review.find("h5", {"class": "cr-lightbox-review-title"}):
                        review_data["title"] = title_elem.text.strip()
                        
                    if text_elem := review.find("span", {"class": "cr-lightbox-review-body"}):
                        review_data["text"] = text_elem.text.strip()
                    if date_elem := review.find("span", {"class": "cr-lightbox-review-origin"}):
                        date_text = date_elem.text.strip()
                        if "on" in date_text:
                            review_data["date"] = date_text.split("on")[1].strip()
                        else:
                            review_data["date"] = date_text
                    reviews.append(Review(**review_data))
                    
                except AttributeError as e:
                    print(f"Error parsing individual review: {str(e)}")
                    continue
                    
            return reviews
            
        except Exception as e:
            print(f"Error fetching reviews: {str(e)}")
            return []
            
            
            
    def get_all_details(self) -> AmazonProductResponse:
        """Get all product details in a single dictionary"""
        if not self.soup:
            return AmazonProductResponse(
                error="Failed to fetch page",
                product=Product(
                    pricing = None,
                    description=Description(),
                    specifications=Specifications(),
                    ratings=Ratings(),
                    reviews=[]
                )
            )
        return AmazonProductResponse(
            product=Product(
                title=self.get_product_title(),
                image = self.get_product_images(),
                price = self.get_selling_price(),
                categories=self.get_tags(),
                description=Description(
                    highlights=self.get_about()
                ),
                specifications=Specifications(
                    technical=self.get_technical_info(),
                    additional=self.get_additional_info(),
                    details=self.get_product_details()
                ),
                ratings=self.get_ratings(),
                reviews=self.get_all_reviews()
            )
        )


# scraper = AmazonScraper("B00935MGKK")
# # scraper.page_html_to_text()
# print(scraper.get_all_details())