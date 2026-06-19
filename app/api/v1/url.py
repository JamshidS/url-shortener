from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from typing import List, Dict
import logging

from requests import session
from sqlalchemy.orm import Session as SQLAlchemySession
from app.algorithms.bloom_filter import BloomFilter, get_bloom_filter
from app.core.database import get_db
from app.schema.url import UrlCreate, UrlResponse 
from app.services.url_generator import create_url_with_bloom_filter, create_url_with_base_conversion

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/urls",  
    tags=["urls"], 
    responses={404: {"description": "Not found"}},
)


@router.post("/with-bloom-filter", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
async def create_url(
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
