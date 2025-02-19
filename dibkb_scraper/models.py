from typing import List, Optional, Dict
from dataclasses import dataclass

@dataclass
class Ratings:
    rating: Optional[float] = None
    review_count: Optional[int] = None

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
    price: float = None
    categories: List[str] = None
    description: Description = None
    specifications: Specifications = None
    ratings: Ratings = None

@dataclass
class AmazonProductResponse:
    product: Product
    error: Optional[str] = None 