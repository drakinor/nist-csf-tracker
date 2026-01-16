import asyncio
from app.database import engine
from sqlmodel import Session, select
from app.models import Artifact, ArtifactChunk
from app.parsers.parser_service import ParserService

session = Session(engine)
artifact = session.exec(select(Artifact).where(Artifact.id == 3)).first()
print(f'📄 Artifact: {artifact.title} (Type: {artifact.type})')
print(f'📂 Path: {artifact.source_path}')

parser = ParserService()
print('\n🔍 Parsing PDF...')
chunks = asyncio.run(parser.parse_and_chunk(artifact))
print(f'✓ Extracted {len(chunks)} chunks\n')

for i, chunk in enumerate(chunks[:3], 1):
    locator = chunk['locator']
    text_preview = chunk['text'][:150].replace('\n', ' ')
    print(f'Chunk {i} (page {locator["page"]}):\n  {text_preview}...\n')

print(f'\n💾 Saving {len(chunks)} chunks to database...')
for chunk_data in chunks:
    chunk = ArtifactChunk(
        artifact_id=artifact.id,
        text=chunk_data['text'],
        locator_json=chunk_data['locator']
    )
    session.add(chunk)

session.commit()
print(f'✓ Saved {len(chunks)} chunks!')
