import secrets
import string
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.algorithms.base_encoder import Base62Encoder
from app.algorithms.bloom_filter import BloomFilter
from app.algorithms.distributed_id import DistributedIDGenerator
from app.algorithms.redis_bloomfilter import RedisBloomFilter
from app.core.exceptions import (
    ShortCodeConflictError,
    ShortUrlExpiredError,
    ShortUrlNotFoundError,
)
from app.model.url import Url
from app.repositories.url import UrlRepository
from app.schema.url import UrlCreate

ALPHABET = string.ascii_letters + string.digits
MAX_RANDOM_INSERT_ATTEMPTS = 5


class UrlService:
    def __init__(self, session: Session, *, short_code_length: int):
        self.session = session
        self.repository = UrlRepository(session)
        self.short_code_length = short_code_length

    def create_with_distributed_id(
        self,
        payload: UrlCreate,
        id_generator: DistributedIDGenerator,
        encoder: Base62Encoder,
    ) -> Url:
        short_code = encoder.encode_fixed_length(
            id_generator.next_id(),
            self.short_code_length,
        )
        return self._persist(payload, short_code)

    def create_with_local_bloom(
        self,
        payload: UrlCreate,
        bloom_filter: BloomFilter,
    ) -> Url:
        for _ in range(MAX_RANDOM_INSERT_ATTEMPTS):
            short_code = self._random_code()
            if bloom_filter.contains(short_code):
                continue
            bloom_filter.add(short_code)
            try:
                return self._persist(payload, short_code)
            except ShortCodeConflictError:
                continue
        raise ShortCodeConflictError("Could not allocate a unique short code")

    def create_with_redis_bloom(
        self,
        payload: UrlCreate,
        bloom_filter: RedisBloomFilter,
    ) -> Url:
        for _ in range(MAX_RANDOM_INSERT_ATTEMPTS):
            short_code = self._random_code()
            if not bloom_filter.add(short_code):
                continue
            try:
                return self._persist(payload, short_code)
            except ShortCodeConflictError:
                continue
        raise ShortCodeConflictError("Could not allocate a unique short code")

    def resolve(self, short_code: str) -> str:
        url = self.repository.get_active_by_short_code(short_code)
        if url is None:
            raise ShortUrlNotFoundError("Short URL not found")

        now = datetime.now(UTC)
        expires_at = url.expires_at
        if expires_at is not None:
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=UTC)
            if expires_at <= now:
                raise ShortUrlExpiredError("Short URL has expired")
        return url.original_url

    def _persist(self, payload: UrlCreate, short_code: str) -> Url:
        url = Url(
            original_url=str(payload.original_url),
            short_code=short_code,
            expires_at=payload.expires_at,
        )
        try:
            self.repository.add(url)
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ShortCodeConflictError("Short code already exists") from exc
        return url

    def _random_code(self) -> str:
        return "".join(
            secrets.choice(ALPHABET) for _ in range(self.short_code_length)
        )
