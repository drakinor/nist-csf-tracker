from sqlmodel import Session, create_engine
from app.config import settings

# Create database engine
engine = create_engine(
    str(settings.database_url),
    echo=False,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)


def get_session():
    """Dependency for getting database sessions."""
    with Session(engine) as session:
        yield session
