import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from ..models import PDFFileInfo


class FileService:
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
    async def save_uploaded_file(self, file: any, session_id: str) -> PDFFileInfo:
        """Save an uploaded file and return file info"""
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create session directory
        session_dir = self.upload_dir / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Save file with unique name
        file_extension = Path(file.filename).suffix
        unique_filename = f"{file_id}{file_extension}"
        file_path = session_dir / unique_filename
        
        # Save file contents
        async with aiofiles.open(file_path, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)
        
        # Get file size
        file_size = len(content)
        
        # TODO: Get actual page count from PDF
        page_count = 1  # Placeholder
        
        return PDFFileInfo(
            id=file_id,
            name=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file_size,
            page_count=page_count,
            created_at=datetime.now(),
            parent_id=None,
            is_temporary=True
        )
    
    async def get_file_path(self, file_id: str, session_id: str) -> Optional[Path]:
        """Get the file path for a given file ID and session"""
        session_dir = self.upload_dir / session_id
        
        # Search for file with this ID
        for file_path in session_dir.glob(f"{file_id}.*"):
            if file_path.is_file():
                return file_path
        
        return None
    
    async def delete_file(self, file_id: str, session_id: str) -> bool:
        """Delete a file by ID and session"""
        file_path = await self.get_file_path(file_id, session_id)
        
        if file_path and file_path.exists():
            file_path.unlink()
            return True
        
        return False
    
    async def delete_session_files(self, session_id: str) -> bool:
        """Delete all files for a session"""
        session_dir = self.upload_dir / session_id
        
        if session_dir.exists():
            # Delete all files in session directory
            for file_path in session_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
            
            # Remove empty directory
            session_dir.rmdir()
            return True
        
        return False
    
    async def list_session_files(self, session_id: str) -> List[str]:
        """List all files in a session directory"""
        session_dir = self.upload_dir / session_id
        
        if not session_dir.exists():
            return []
        
        return [f.name for f in session_dir.iterdir() if f.is_file()]


# Global instance
file_service = FileService()