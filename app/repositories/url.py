from sqlalchemy.orm import Session

from app.model.url import Url

def save_and_flush(session: Session, url: Url):
    """
    Save the URL object to the database and flush the session.

    Args:
        session (Session): The SQLAlchemy session.
        url (Url): The URL object to be saved.
    """
    session.add(url)
    session.commit() 
    session.flush()  # Flush the session to persist changes


def find_by_short_code(session: Session, short_code: str) -> Url | None:
    """Return an active URL for the supplied short code."""
    return (
        session.query(Url)
        .filter(
            Url.short_code == short_code,
            Url.is_active.is_(True),
        )
        .first()
    )
