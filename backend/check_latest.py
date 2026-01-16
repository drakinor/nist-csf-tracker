from app.database import engine
from sqlmodel import Session, select
from app.models import Artifact, ArtifactChunk

s = Session(engine)
a = s.exec(select(Artifact).order_by(Artifact.id.desc()).limit(1)).first()
print(f'Latest artifact: ID={a.id}, type={a.type}, title={a.title}')
print(f'Source URL: {a.source_url}')

chunks = s.exec(select(ArtifactChunk).where(ArtifactChunk.artifact_id == a.id)).all()
print(f'\nChunks: {len(chunks)}')
if chunks:
    print(f'First chunk preview: {chunks[0].text[:150]}')
    print(f'Locator: {chunks[0].locator_json}')
