from typing import Any, List, Optional, Dict
from dataclasses import dataclass
from pydantic import BaseModel

class StarRating(BaseModel):
    count: Optional[int] = None
    percentage: Optional[int] = None

class RatingStats(BaseModel):
    one_star: StarRating = None
    two_star: StarRating = None
    three_star: StarRating = None
    four_star: StarRating = None
    five_star: StarRating = None

class Ratings(BaseModel):
    rating: Optional[float] = None
    review_count: Optional[int] = None
    rating_stats : RatingStats = None

class RatingPercentage(BaseModel):
    one_star: Optional[int] = None
    two_star: Optional[int] = None
    three_star: Optional[int] = None
    four_star: Optional[int] = None
    five_star: Optional[int] = None

class Description(BaseModel):
    highlights: List[str] = None

class Specifications(BaseModel):
    technical: Dict[str, str] = None
    additional: Dict[str, str] = None
    details: Dict[str, str] = None

class Competitor(BaseModel):
    asin: str
    title: str
    img_id: str
    price: float
    
class Product(BaseModel):
    title: Optional[str] = None
    image: Optional[List[str]] = None
    price: float = None
    categories: List[str] = None
    description: Description = None
    specifications: Specifications = None
    ratings: Dict[str,Any] = None
    reviews: List[str] = None
    related_products: List[Competitor] = None


class AmazonProductResponse(BaseModel):
    product: Product
    error: Optional[str] = None 


