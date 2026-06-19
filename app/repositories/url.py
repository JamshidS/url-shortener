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
    session.flush()  # Flush the session to persist changes