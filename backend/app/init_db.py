"""Initialize database tables."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import SQLModel
from app.database import engine
from app.models import (
    Artifact, ArtifactChunk, Control, Evidence,
    Score, Gap, Action, RiskAcceptance, ScoreEvent
)


def init_db():
    """Create all tables in the database."""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✓ Database initialized successfully!")
    print(f"Database location: {engine.url}")


if __name__ == "__main__":
    init_db()
