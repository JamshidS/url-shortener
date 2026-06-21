import random
import string

from sqlalchemy.orm import Session

from app.algorithms.base_encoder import Base62Encoder
from app.algorithms.bloom_filter import BloomFilter
from app.algorithms.distributed_id import DistributedIDGenerator
from app.algorithms.redis_bloomfilter import RedisBloomFilter
from app.model.url import Url
from app.schema.url import UrlCreate, UrlResponse
from app.repositories.url import save_and_flush


SHORT_CODE_LENGTH = 7


def url_code_generator_with_base_conversion(unique_id: int, encoder: Base62Encoder) -> str:
    return encoder.encode_fixed_length(unique_id, SHORT_CODE_LENGTH)



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

    url_data.short_code = short_code
    url = Url(**url_data.model_dump())
    save_and_flush(session, url)

    return UrlResponse.model_validate(url)



def create_url_with_redis_bloom_filter(url_data: UrlCreate, session: Session, redis_bloom_filter: RedisBloomFilter) -> UrlResponse:
    """
    Generate a short URL from the original URL using Redis Bloom filter.

    Args:
        url_data (UrlCreate): The original URL data.
        session (Session): The SQLAlchemy session.
        redis_bloom_filter (RedisBloomFilter): The Redis Bloom filter instance.
    """

    def _generate_code() -> str:
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(7))

    short_code = None
    while True:
        code = _generate_code()

        # 1. Fast check (Redis)
        if redis_bloom_filter.contains(code):
            continue
        else:
            redis_bloom_filter.add(code) 
            short_code = code
            break

    url_data.short_code = short_code
    url = Url(**url_data.model_dump())
    save_and_flush(session, url)

    return UrlResponse.model_validate(url)


def create_url_with_base_conversion(url_data: UrlCreate, session: Session, id_generator: DistributedIDGenerator, base62_encoder: Base62Encoder) -> UrlResponse:
    """
    Generate a short URL from the original URL using base conversion.

    Args:
        url_data (UrlCreate): The original URL data.
        session (Session): The SQLAlchemy session.
        id_generator (DistributedIDGenerator): The distributed ID generator.
        base62_encoder (Base62Encoder): The Base62 encoder instance.
    """
    
    unique_id = id_generator.next_id()
    short_code = url_code_generator_with_base_conversion(unique_id, base62_encoder)

    url_data.short_code = short_code
    url = Url(**url_data.model_dump()) 
    save_and_flush(session, url)
    return UrlResponse.model_validate(url)