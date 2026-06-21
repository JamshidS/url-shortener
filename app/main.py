from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from app.algorithms import bloom_filter
from app.algorithms.bloom_filter import BloomFilter
from app.algorithms.redis_bloomfilter import RedisBloomFilter
from app.middlewares import add_cors_middleware
from app.api.v1.url import router as url_router
from app.clients.redis import redis_client

logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bloom_filter = BloomFilter(
        expected_items=1_000_000,
        false_positive_rate=0.01
    )

    redis_bloom_filter = RedisBloomFilter(redis_client)

    redis_bloom_filter.initialize(
        error_rate=0.01,
        capacity=365_000_000_000
    )

    app.state.redis_bloom_filter = redis_bloom_filter

    yield
    

app = FastAPI(
    title="URL Shortener API",
    description="A simple URL shortener service built with FastAPI.",
    version="1.0.0",
    docs_url="/v1/docs",         
    redoc_url="/v1/docs/redoc",    
    openapi_url="/v1/openapi.json",  
    lifespan=lifespan 
)

add_cors_middleware(app)

app.include_router(url_router)  # Include the URL router
logger.info("Routes have been included successfully...")
logger.info("FastAPI application is ready to accept requests...")