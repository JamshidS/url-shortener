from fastapi import FastAPI
import logging
from contextlib import asynccontextmanager
from app.algorithms.bloom_filter import BloomFilter
from app.middlewares import add_cors_middleware
from app.api.v1.url import router as url_router

logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bloom_filter = BloomFilter(
        expected_items=1_000_000,
        false_positive_rate=0.01
    )
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