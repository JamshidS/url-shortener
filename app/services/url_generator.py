from random import random
import string

from sqlalchemy.orm import Session

from app.algorithms.bloom_filter import BloomFilter
from app.model.url import Url
from app.schema.url import UrlCreate, UrlResponse
from app.repositories.url import save_and_flush

def create_url_with_bloom_filter(url_data: UrlCreate, session: Session, bloom_filter: BloomFilter) -> UrlResponse:
    """
    Generate a short URL from the original URL.

    Args:
        url_data (UrlCreate): The original URL data.
        session (Session): The SQLAlchemy session.
        bloom_filter (BloomFilter): The Bloom filter instance.
    """

    def _generate_code() -> str:
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(7))

    short_code = None
    while True:
        code = _generate_code()

        # 1. Fast check (memory)
        if bloom_filter.contains(code):
            continue
        else:
            bloom_filter.add(code) 
            short_code = code
            break

    url_data.short_url = short_code
    url = Url(**url_data.dict())
    save_and_flush(session, url)

    return UrlResponse(**url.dict())


def create_url_with_base_conversion(url_data: UrlCreate, session: Session) -> UrlResponse:
    """
    Generate a short URL from the original URL using base conversion.

    Args:
        url_data (UrlCreate): The original URL data.
        session (Session): The SQLAlchemy session.
    """

    ## We will add the logic to generate a unique short code here in the future...

    url = Url(**url_data.dict())
    save_and_flush(session, url)

    return UrlResponse(**url.dict())