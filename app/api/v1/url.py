from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
import logging

from sqlalchemy.orm import Session as SQLAlchemySession
from app.algorithms.base_encoder import Base62Encoder, get_base62_encoder
from app.algorithms.bloom_filter import BloomFilter, get_bloom_filter
from app.algorithms.distributed_id import DistributedIDGenerator, get_distributed_id_generator
from app.algorithms.redis_bloomfilter import RedisBloomFilter, get_redis_bloom_filter
from app.core.database import get_db
from app.repositories.url import find_by_short_code
from app.schema.url import UrlCreate, UrlResponse 
from app.services.url_generator import create_url_with_bloom_filter, create_url_with_base_conversion as generate_url_with_base_conversion, create_url_with_redis_bloom_filter as generate_url_with_redis_bloom_filter

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/urls",  
    tags=["urls"], 
    responses={404: {"description": "Not found"}},
)


def get_redirect_target(short_code: str, session: SQLAlchemySession) -> str:
    url = find_by_short_code(session, short_code)

    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    if url.expires_at is not None and url.expires_at <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Short URL has expired",
        )

    return url.original_url


@router.post("/with-bloom-filter", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
def create_url(
    request_body: UrlCreate,
    session: SQLAlchemySession = Depends(get_db),
    bloom_filter: BloomFilter = Depends(get_bloom_filter)
) -> UrlResponse:
    """
    Create a new short URL from the original URL.

    Args:
        request_body (UrlCreate): The original URL data.
        session (SQLAlchemySession): The SQLAlchemy session.
        bloom_filter (BloomFilter): The Bloom filter instance.

    Returns:
        UrlResponse: The created short URL data.
    """
    return create_url_with_bloom_filter(request_body, session, bloom_filter)


@router.post("/with-redis-bloom-filter", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
def create_url_with_redis_bloom_filter(
    request_body: UrlCreate,
    session: SQLAlchemySession = Depends(get_db),
    redis_bloom_filter: RedisBloomFilter = Depends(get_redis_bloom_filter)
) -> UrlResponse:
    """
    Create a new short URL from the original URL using Redis Bloom filter.

    Args:
        request_body (UrlCreate): The original URL data.
        session (SQLAlchemySession): The SQLAlchemy session.
        redis_bloom_filter (RedisBloomFilter): The Redis Bloom filter instance.

    Returns:
        UrlResponse: The created short URL data.
    """
    return generate_url_with_redis_bloom_filter(request_body, session, redis_bloom_filter)


@router.post("/with-base-conversion", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
def create_url_with_base_conversion(
    request_body: UrlCreate,
    session: SQLAlchemySession = Depends(get_db),
    id_generator: DistributedIDGenerator = Depends(get_distributed_id_generator),
    base62_encoder: Base62Encoder = Depends(get_base62_encoder)
) -> UrlResponse:
    """
    Create a new short URL from the original URL using base conversion.

    Args:
        request_body (UrlCreate): The original URL data.
        session (SQLAlchemySession): The SQLAlchemy session.
        id_generator (DistributedIDGenerator): The distributed ID generator.
        base62_encoder (Base62Encoder): The Base62 encoder instance.

    Returns:
        UrlResponse: The created short URL data.
    """
    return generate_url_with_base_conversion(request_body, session, id_generator, base62_encoder)


@router.get(
    "/{short_code}/permanent",
    response_class=RedirectResponse,
    status_code=status.HTTP_301_MOVED_PERMANENTLY,
)
def redirect_permanently(
    short_code: str,
    session: SQLAlchemySession = Depends(get_db),
) -> RedirectResponse:
    """Redirect permanently to the original URL."""
    return RedirectResponse(
        url=get_redirect_target(short_code, session),
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
    )


@router.get(
    "/{short_code}/temporary",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
)
def redirect_temporarily(
    short_code: str,
    session: SQLAlchemySession = Depends(get_db),
) -> RedirectResponse:
    """Redirect temporarily to the original URL."""
    return RedirectResponse(
        url=get_redirect_target(short_code, session),
        status_code=status.HTTP_302_FOUND,
    )
