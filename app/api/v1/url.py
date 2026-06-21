from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.algorithms.base_encoder import Base62Encoder
from app.algorithms.bloom_filter import BloomFilter
from app.algorithms.distributed_id import DistributedIDGenerator
from app.algorithms.redis_bloomfilter import RedisBloomFilter
from app.api.dependencies import (
    get_base62_encoder,
    get_bloom_filter,
    get_distributed_id_generator,
    get_redis_bloom_filter,
)
from app.core.config import get_settings
from app.core.database import get_db
from app.schema.url import ErrorResponse, UrlCreate, UrlResponse
from app.services.url_generator import UrlService

router = APIRouter(prefix="/api/v1/urls", tags=["urls"])
SessionDependency = Annotated[Session, Depends(get_db)]
ShortCode = Annotated[str, Path(min_length=4, max_length=10)]


def service_for(session: Session) -> UrlService:
    return UrlService(
        session,
        short_code_length=get_settings().short_code_length,
    )


@router.post(
    "/with-base-conversion",
    response_model=UrlResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
def create_with_base_conversion(
    payload: UrlCreate,
    session: SessionDependency,
    id_generator: Annotated[
        DistributedIDGenerator,
        Depends(get_distributed_id_generator),
    ],
    encoder: Annotated[Base62Encoder, Depends(get_base62_encoder)],
) -> UrlResponse:
    url = service_for(session).create_with_distributed_id(
        payload,
        id_generator,
        encoder,
    )
    return UrlResponse.model_validate(url)


@router.post(
    "/with-bloom-filter",
    response_model=UrlResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
def create_with_bloom_filter(
    payload: UrlCreate,
    session: SessionDependency,
    bloom_filter: Annotated[BloomFilter, Depends(get_bloom_filter)],
) -> UrlResponse:
    url = service_for(session).create_with_local_bloom(payload, bloom_filter)
    return UrlResponse.model_validate(url)


@router.post(
    "/with-redis-bloom-filter",
    response_model=UrlResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
def create_with_redis_bloom_filter(
    payload: UrlCreate,
    session: SessionDependency,
    bloom_filter: Annotated[
        RedisBloomFilter,
        Depends(get_redis_bloom_filter),
    ],
) -> UrlResponse:
    url = service_for(session).create_with_redis_bloom(payload, bloom_filter)
    return UrlResponse.model_validate(url)


@router.get(
    "/{short_code}/permanent",
    response_class=RedirectResponse,
    status_code=status.HTTP_301_MOVED_PERMANENTLY,
    responses={404: {"model": ErrorResponse}, 410: {"model": ErrorResponse}},
)
def redirect_permanently(
    short_code: ShortCode,
    session: SessionDependency,
) -> RedirectResponse:
    return RedirectResponse(
        service_for(session).resolve(short_code),
        status_code=status.HTTP_301_MOVED_PERMANENTLY,
    )


@router.get(
    "/{short_code}/temporary",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
    responses={404: {"model": ErrorResponse}, 410: {"model": ErrorResponse}},
)
def redirect_temporarily(
    short_code: ShortCode,
    session: SessionDependency,
) -> RedirectResponse:
    return RedirectResponse(
        service_for(session).resolve(short_code),
        status_code=status.HTTP_302_FOUND,
    )
