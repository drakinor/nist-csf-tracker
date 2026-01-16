import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import UploadFile
from sqlmodel import Session
import requests
from bs4 import BeautifulSoup
from readability import Document

from app.config import settings
from app.models import Artifact


class ArtifactService:
    """Service for managing artifact storage and retrieval."""
    
    def __init__(self, session: Session):
        self.session = session
        self.artifacts_path = settings.artifacts_path_absolute
    
    async def save_file(self, file: UploadFile, tags: Optional[str] = None) -> Artifact:
        """Save an uploaded file and create artifact record."""
        # Read file content
        content = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Determine file type
        filename = file.filename or "unknown"
        file_ext = Path(filename).suffix.lower()
        file_type = self._get_file_type(file_ext)
        
        # Create storage path
        storage_filename = f"{file_hash}{file_ext}"
        storage_path = self.artifacts_path / storage_filename
        
        # Save file
        with open(storage_path, "wb") as f:
            f.write(content)
        
        # Create artifact record
        artifact = Artifact(
            title=filename,
            type=file_type,
            source_path=str(storage_path),
            collected_at=datetime.utcnow(),
            hash=file_hash,
            tags=tags,
            file_size=len(content)
        )
        
        self.session.add(artifact)
        self.session.commit()
        self.session.refresh(artifact)
        
        return artifact
    
    async def ingest_url(self, url: str, tags: Optional[str] = None) -> Artifact:
        """Fetch URL content and create a local snapshot. Supports HTML pages and PDFs."""
        # Fetch URL
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'NIST-CSF-Tracker/1.0'
        })
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
            # Handle PDF
            content = response.content
            content_hash = hashlib.sha256(content).hexdigest()
            
            # Save PDF file
            pdf_filename = f"{content_hash}.pdf"
            pdf_path = self.artifacts_path / pdf_filename
            
            with open(pdf_path, "wb") as f:
                f.write(content)
            
            # Extract title from URL
            title = url.split('/')[-1] or "Downloaded PDF"
            
            artifact = Artifact(
                title=title,
                type="pdf",
                source_path=str(pdf_path),
                source_url=url,
                collected_at=datetime.utcnow(),
                hash=content_hash,
                tags=tags,
                file_size=len(content)
            )
        else:
            # Handle HTML
            # Extract main content using readability
            doc = Document(response.text)
            title = doc.title()
            html_content = doc.summary()
            
            # Parse with BeautifulSoup to get clean text
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text(separator='\n', strip=True)
            
            # Create hash
            content_hash = hashlib.sha256(text_content.encode()).hexdigest()
            
            # Save HTML snapshot
            snapshot_filename = f"{content_hash}.html"
            snapshot_path = self.artifacts_path / snapshot_filename
            
            with open(snapshot_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # Also save plain text version
            text_filename = f"{content_hash}.txt"
            text_path = self.artifacts_path / text_filename
            
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text_content)
            
            artifact = Artifact(
                title=title or url,
                type="url",
                source_path=str(text_path),
                source_url=url,
                collected_at=datetime.utcnow(),
                hash=content_hash,
                tags=tags,
                file_size=len(text_content),
                metadata_json={"snapshot_html": str(snapshot_path)}
            )
        
        self.session.add(artifact)
        self.session.commit()
        self.session.refresh(artifact)
        
        return artifact
    
    def delete_file(self, artifact: Artifact):
        """Delete artifact files from storage."""
        if artifact.source_path:
            path = Path(artifact.source_path)
            if path.exists():
                path.unlink()
        
        # Delete HTML snapshot if exists
        if artifact.metadata_json and "snapshot_html" in artifact.metadata_json:
            snapshot_path = Path(artifact.metadata_json["snapshot_html"])
            if snapshot_path.exists():
                snapshot_path.unlink()
    
    def _get_file_type(self, ext: str) -> str:
        """Determine file type from extension."""
        type_map = {
            ".docx": "docx",
            ".doc": "docx",
            ".pdf": "pdf",
            ".txt": "txt",
            ".md": "md",
            ".xlsx": "xlsx",
            ".xls": "xlsx"
        }
        return type_map.get(ext, "unknown")
