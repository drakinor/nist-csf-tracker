"""Pytest configuration and shared fixtures."""
import pytest
from sqlmodel import Session, create_engine, SQLModel
from app.models import Control, Artifact, ArtifactChunk


@pytest.fixture
def session():
    """Create a test database session with in-memory SQLite."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
