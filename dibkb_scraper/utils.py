import re
from typing import Dict,List
from fake_useragent import UserAgent
def filter_unicode(input_string)->str:
    return input_string.encode('ascii', 'ignore').decode()

def extract_text(text: str) -> str:
    """
    Filters out unicode characters and extra whitespace, returning clean text.
    Example: 'Product Dimensions\u200f:\u200e' -> 'Product Dimensions'
    """
    # Remove unicode characters and clean up whitespace
    cleaned = re.sub(r'[\u200e\u200f\n\t:]', '', text)
    # Remove multiple spaces and strip
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def make_headers()->Dict[str,str]:
    ua=UserAgent()
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Referer": "https://www.google.com/",
        "Alt-Used": "www.amazon.in"
    }

AMAZON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Referer": "https://www.google.com/",
    "Alt-Used": "www.amazon.in"
} 


def extract_image_id(images:List[str])->List[str]:
    img_ids = [
        image.split("/I/")[-1].split("._")[0]
        for image in images
        if len(image.split("/I/")) > 1
    ]
    valid_ids = [img_id for img_id in img_ids if len(img_id) == 11]
    return valid_ids