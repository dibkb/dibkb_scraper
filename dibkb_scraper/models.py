from typing import List, Optional, Dict
from dataclasses import dataclass


@dataclass
class StarRating:
    count: Optional[int] = None
    percentage: Optional[int] = None

@dataclass
class RatingStats:
    one_star: StarRating = None
    two_star: StarRating = None
    three_star: StarRating = None
    four_star: StarRating = None
    five_star: StarRating = None

@dataclass
class Ratings:
    rating: Optional[float] = None
    review_count: Optional[int] = None
    rating_stats : RatingStats = None

@dataclass
class RatingPercentage:
    one_star: Optional[int] = None
    two_star: Optional[int] = None
    three_star: Optional[int] = None
    four_star: Optional[int] = None
    five_star: Optional[int] = None

@dataclass
class Description:
    highlights: List[str] = None

@dataclass
class Specifications:
    technical: Dict[str, str] = None
    additional: Dict[str, str] = None
    details: Dict[str, str] = None

@dataclass
class Product:
    title: Optional[str] = None
    image: Optional[List[str]] = None
    price: float = None
    categories: List[str] = None
    description: Description = None
    specifications: Specifications = None
    ratings: Ratings = None
    reviews: List[str] = None

@dataclass
class AmazonProductResponse:
    product: Product
    error: Optional[str] = None 