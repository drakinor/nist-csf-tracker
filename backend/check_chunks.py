from app.database import engine
from sqlmodel import Session, select
from app.models import ArtifactChunk

session = Session(engine)
chunks = session.exec(select(ArtifactChunk)).all()
print(f'\n📊 Database Status:')
print(f'Total chunks: {len(chunks)}')

for c in chunks[:5]:
    preview = c.text[:80].replace('\n', ' ')
    print(f'  Chunk {c.id} (artifact {c.artifact_id}): {preview}...')
