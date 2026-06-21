from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.algorithms.base_encoder import Base62Encoder
from app.core.database import Base
from app.schema.url import UrlCreate
from app.services.url_generator import UrlService


class StubIdGenerator:
    def next_id(self) -> int:
        return 1


def test_create_and_resolve_url() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = UrlService(session, short_code_length=7)
        url = service.create_with_distributed_id(
            UrlCreate(original_url="https://example.com"),
            StubIdGenerator(),
            Base62Encoder(),
        )

        assert url.short_code == "aaaaaab"
        assert service.resolve(url.short_code) == "https://example.com/"
