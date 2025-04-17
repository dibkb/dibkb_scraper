import math
from .models import (
    AmazonProductResponse, Competitor, Description, RatingPercentage,
    Product, RatingStats, Ratings, Specifications, StarRating
)
from .utils import extract_text, filter_unicode, make_headers
import httpx
from bs4 import BeautifulSoup
from typing import Any, Dict, List, Optional, Union
import json



class AmazonScraper:
    def __init__(self, asin: str):
        self.asin = asin
        self.url = f"https://www.amazon.in/dp/{self.asin}"
        self.headers = make_headers()
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
            
            price_elem = self.soup.find("span", {"class": "a-price-whole"})
            if price_elem:
                price = float(price_elem.text.strip().replace("₹", "").replace(",", ""))
                
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

    def get_ratings(self)->Dict[str,Any]:
        try:
            result = {}
            
            # Get rating
            rating_elem = self.soup.find("span", {"data-hook": "rating-out-of-text"})
            if rating_elem:
                ratings_text = rating_elem.text.strip().split()
                if ratings_text and len(ratings_text) >= 1:
                    try:
                        result["rating"] = float(ratings_text[0])
                    except (ValueError, TypeError):
                        pass

            # Get review count
            review_elem = self.soup.find("span", {"data-hook": "total-review-count"})
            if review_elem:
                review_text = review_elem.text.strip().replace(',', '') 
                try:
                    result["review_count"] = int(''.join(filter(str.isdigit, review_text)))
                except (ValueError, TypeError):
                    pass

            # Try alternative rating source if main one failed
            if result["rating"] is None:
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

                count = math.floor(percentage * result["review_count"] / 100) if percentage and result["review_count"] else None

                star_ratings[f"{number_to_word[stars]}_star"] = {"count":count, "percentage":percentage}

            result["rating_stats"] = star_ratings
            return result
            
        except Exception as e:
            return {}

    def get_product_images(self) -> Optional[List[str]]:
        try:
            # Find the script that contains the image data
            script = self.soup.find("script", text=lambda t: t and "ImageBlockATF" in t)
            if not script:
                return None
            
            # Extract the colorImages data using string manipulation
            script_text = script.text
            start_idx = script_text.find("'colorImages': { 'initial': ")
            if start_idx == -1:
                return None
            
            # Find the matching closing bracket
            start_idx += len("'colorImages': { 'initial': ")
            bracket_count = 0
            end_idx = start_idx
            
            for i in range(start_idx, len(script_text)):
                if script_text[i] == '[':
                    bracket_count += 1
                elif script_text[i] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_idx = i + 1
                        break
            
            json_str = script_text[start_idx:end_idx]
            image_data = json.loads(json_str)
            
            # Extract hiRes URLs from the image data
            images = [img["hiRes"] for img in image_data if "hiRes" in img]
            
            # Extract image IDs as before
            img_ids = [
                image.split("/I/")[-1].split("._")[0]
                for image in images
                if len(image.split("/I/")) > 1
            ]
            
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

    def get_all_reviews(self) -> List[str]:
        """
        Retrieves all reviews from the product page.
        
        Returns:
            List[Dict[str, Optional[str]]]: List of reviews, each containing user, rating, title, text and date
        """
        reviews = []
        try:

            review_elem = self.soup.find_all("div", {"class": "review-text-content"})

            for x in review_elem:
                reviews.append(x.text.strip())
            
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
                reviews=self.get_all_reviews(),
                related_products=self.get_related_products()
            )
        )
    
    def get_html(self) -> str:
        return self.soup.prettify()
    
    def get_related_products(self) -> List[Competitor]:
        try:
            competitors: List[Dict[str, Any]] = []
            carousel_items = self.soup.find_all("li", {"class": "a-carousel-card"}) or []
            
            for item in carousel_items:
                try:
                    # Find div and safely get data
                    div = item.find("div", {"data-adfeedbackdetails": True})
                    if not div or not div.get("data-adfeedbackdetails"):
                        continue
                        
                    data = div.get("data-adfeedbackdetails", "{}")
                    competitor_data = json.loads(data)
                    
                    # Skip if missing required data
                    if not isinstance(competitor_data, dict):
                        continue
                        
                    competitors.append(competitor_data)
                    
                except (json.JSONDecodeError, AttributeError) as e:
                    print(f"Error parsing carousel item: {str(e)}")
                    continue

            results: List[Competitor] = []
            for competitor in competitors:
                try:
                    # Safely extract data with fallbacks
                    result = {
                        "asin": competitor.get("asin", ""),
                        "title": competitor.get("title", ""),
                        "price": competitor.get("priceAmount", None),
                        "img_id": ""
                    }
                    
                    # Safely extract image ID
                    try:
                        img_data = competitor.get("adCreativeImage", {})
                        if isinstance(img_data, dict):
                            low_res = img_data.get("lowResolutionImage", {})
                            if isinstance(low_res, dict):
                                img_url = low_res.get("url", "")
                                if "/" in img_url and "._" in img_url:
                                    result["img_id"] = img_url.split("/I/")[-1].split("._")[0]
                    except (AttributeError, IndexError) as e:
                        print(f"Error extracting image ID: {str(e)}")
                    
                    # Only add if we have minimum required data
                    if result["asin"] and result["title"]:
                        results.append(Competitor(**result))
                        
                except Exception as e:
                    print(f"Error processing competitor data: {str(e)}")
                    continue

            return results
            
        except Exception as e:
            print(f"Error in get_related_products: {str(e)}")
            return []


# scraper = AmazonScraper("B00935MGKK")
# # scraper.page_html_to_text()
# print(scraper.get_all_details())