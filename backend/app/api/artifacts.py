from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlmodel import Session, select
from app.database import get_session
from app.models import Artifact, ArtifactChunk
from app.services.artifact_service import ArtifactService
from app.parsers.parser_service import ParserService

router = APIRouter()


@router.get("/", response_model=List[Artifact])
async def list_artifacts(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all ingested artifacts."""
    statement = select(Artifact).offset(skip).limit(limit).order_by(Artifact.collected_at.desc())
    artifacts = session.exec(statement).all()
    return artifacts


@router.get("/{artifact_id}", response_model=Artifact)
async def get_artifact(
    artifact_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific artifact by ID."""
    artifact = session.get(Artifact, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


@router.get("/{artifact_id}/chunks", response_model=List[ArtifactChunk])
async def get_artifact_chunks(
    artifact_id: int,
    session: Session = Depends(get_session)
):
    """Get all chunks for a specific artifact."""
    statement = select(ArtifactChunk).where(
        ArtifactChunk.artifact_id == artifact_id
    ).order_by(ArtifactChunk.chunk_index)
    chunks = session.exec(statement).all()
    return chunks


@router.post("/upload")
async def upload_artifact(
    file: UploadFile = File(...),
    tags: str = Form(None),
    session: Session = Depends(get_session)
):
    """Upload and process a document artifact."""
    artifact_service = ArtifactService(session)
    parser_service = ParserService()
    
    # Save the artifact
    artifact = await artifact_service.save_file(file, tags)
    
    # Parse and chunk the document
    try:
        chunks = await parser_service.parse_and_chunk(artifact)
        
        # Save chunks to database
        for idx, chunk in enumerate(chunks):
            db_chunk = ArtifactChunk(
                artifact_id=artifact.id,
                chunk_text=chunk["text"],
                locator_json=chunk["locator"],
                chunk_index=idx
            )
            session.add(db_chunk)
        
        session.commit()
        session.refresh(artifact)
        
        return {
            "artifact": artifact,
            "chunks_created": len(chunks),
            "message": "Artifact uploaded and processed successfully"
        }
    except Exception as e:
        # Rollback if parsing fails
        session.delete(artifact)
        session.commit()
        raise HTTPException(status_code=500, detail=f"Failed to parse artifact: {str(e)}")


@router.post("/ingest-url")
async def ingest_url(
    url: str = Form(...),
    tags: str = Form(None),
    session: Session = Depends(get_session)
):
    """Ingest a URL and create a local snapshot."""
    artifact_service = ArtifactService(session)
    parser_service = ParserService()
    
    try:
        # Fetch and save URL content
        artifact = await artifact_service.ingest_url(url, tags)
        
        # Parse and chunk the content
        chunks = await parser_service.parse_and_chunk(artifact)
        
        # Save chunks to database
        for idx, chunk in enumerate(chunks):
            db_chunk = ArtifactChunk(
                artifact_id=artifact.id,
                chunk_text=chunk["text"],
                locator_json=chunk["locator"],
                chunk_index=idx
            )
            session.add(db_chunk)
        
        session.commit()
        session.refresh(artifact)
        
        return {
            "artifact": artifact,
            "chunks_created": len(chunks),
            "message": "URL ingested and processed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest URL: {str(e)}")


@router.delete("/{artifact_id}")
async def delete_artifact(
    artifact_id: int,
    session: Session = Depends(get_session)
):
    """Delete an artifact and its chunks."""
    artifact = session.get(Artifact, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # Delete associated chunks
    statement = select(ArtifactChunk).where(ArtifactChunk.artifact_id == artifact_id)
    chunks = session.exec(statement).all()
    for chunk in chunks:
        session.delete(chunk)
    
    # Delete artifact file if it exists
    artifact_service = ArtifactService(session)
    artifact_service.delete_file(artifact)
    
    session.delete(artifact)
    session.commit()
    
    return {"message": "Artifact deleted successfully"}
