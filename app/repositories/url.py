from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.url import Url


class UrlRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, url: Url) -> Url:
        self.session.add(url)
        self.session.flush()
        return url

    def get_active_by_short_code(self, short_code: str) -> Url | None:
        statement = select(Url).where(
            Url.short_code == short_code,
            Url.is_active.is_(True),
        )
        return self.session.scalar(statement)
