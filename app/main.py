import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.algorithms.base_encoder import Base62Encoder
from app.algorithms.bloom_filter import BloomFilter
from app.algorithms.distributed_id import DistributedIDGenerator
from app.algorithms.redis_bloomfilter import RedisBloomFilter
from app.api.v1.health import router as health_router
from app.api.v1.url import router as url_router
from app.clients.redis import create_redis_client
from app.core.config import Settings, get_settings
from app.core.exceptions import (
    IdSpaceExhaustedError,
    ShortCodeConflictError,
    ShortUrlExpiredError,
    ShortUrlNotFoundError,
)
from app.middlewares import add_cors_middleware

logger = logging.getLogger(__name__)


def configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def create_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        redis_client = create_redis_client(settings)
        redis_client.ping()

        redis_bloom_filter = RedisBloomFilter(
            redis_client,
            key=settings.redis_bloom_key,
        )
        redis_bloom_filter.initialize(
            error_rate=settings.redis_bloom_error_rate,
            capacity=settings.redis_bloom_capacity,
        )

        app.state.redis_client = redis_client
        app.state.redis_bloom_filter = redis_bloom_filter
        app.state.bloom_filter = BloomFilter(
            expected_items=settings.redis_bloom_capacity,
            false_positive_rate=settings.redis_bloom_error_rate,
        )
        app.state.base62_encoder = Base62Encoder()
        app.state.distributed_id_generator = DistributedIDGenerator(
            redis_client,
            key=settings.redis_id_counter_key,
            block_size=settings.id_block_size,
            max_id=62**settings.short_code_length - 1,
        )

        logger.info("Application startup complete")
        try:
            yield
        finally:
            redis_client.close()
            logger.info("Application shutdown complete")

    return lifespan


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ShortUrlNotFoundError)
    async def not_found_handler(
        request: Request,
        exc: ShortUrlNotFoundError,
    ) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=404)

    @app.exception_handler(ShortUrlExpiredError)
    async def expired_handler(
        request: Request,
        exc: ShortUrlExpiredError,
    ) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=410)

    @app.exception_handler(ShortCodeConflictError)
    async def conflict_handler(
        request: Request,
        exc: ShortCodeConflictError,
    ) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=409)

    @app.exception_handler(IdSpaceExhaustedError)
    async def exhausted_handler(
        request: Request,
        exc: IdSpaceExhaustedError,
    ) -> JSONResponse:
        return JSONResponse(
            {"detail": str(exc)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/v1/docs",
        redoc_url="/v1/docs/redoc",
        openapi_url="/v1/openapi.json",
        lifespan=create_lifespan(settings),
    )
    add_cors_middleware(application, settings.cors_origins)
    register_exception_handlers(application)
    application.include_router(health_router)
    application.include_router(url_router)
    return application


app = create_app()
