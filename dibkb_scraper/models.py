from typing import List, Optional, Dict, Union
from dataclasses import dataclass

@dataclass
class Ratings:
    rating: Optional[float] = None
    review_count: Optional[int] = None

@dataclass
class Pricing:
    mrp: Optional[float] = None
    selling_price: Optional[float] = None

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
    pricing: Pricing = None
    categories: List[str] = None
    description: Description = None
    specifications: Specifications = None
    ratings: Ratings = None

@dataclass
class AmazonProductResponse:
    product: Product
    error: Optional[str] = None 