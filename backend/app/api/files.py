from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import FileResponse
from typing import List
import os
import uuid
import aiofiles
from datetime import datetime
from pathlib import Path

from ..models import FileUploadResponse, PDFFileInfo, ErrorResponse
from ..services.file_service import FileService
from ..services.session_manager import SessionManager

router = APIRouter()

# Dependency injection - Use global session manager instance
def get_file_service():
    return FileService()

def get_session_manager():
    from ..services.session_manager import session_manager
    return session_manager


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Upload a PDF file"""
    
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Validate file size (50MB limit)
        max_size = 50 * 1024 * 1024  # 50MB
        if file.size and file.size > max_size:
            raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
        
        # Process file upload
        file_info = await file_service.save_uploaded_file(file, session_id)
        
        # Add to session
        session = session_manager.get_or_create_session(session_id)
        session.pdf_files.append(file_info)
        
        # Set as current PDF if it's the first one
        if not session.current_pdf_id:
            session.current_pdf_id = file_info.id
            
        session_manager.update_session(session)
        
        return FileUploadResponse(
            file_id=file_info.id,
            filename=file_info.original_filename,
            file_size=file_info.file_size,
            page_count=file_info.page_count,
            upload_path=file_info.file_path
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{session_id}", response_model=List[PDFFileInfo])
async def list_files(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get list of uploaded files for a session"""
    
    try:
        session = session_manager.get_or_create_session(session_id)
        return session.pdf_files
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """Download a file by ID"""
    
    try:
        file_path = await file_service.get_file_path(file_id)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            media_type='application/pdf',
            filename=os.path.basename(file_path)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    session_id: str,
    file_service: FileService = Depends(get_file_service),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Delete a file"""
    
    try:
        # Remove from file system
        await file_service.delete_file(file_id)
        
        # Remove from session
        session = session_manager.get_or_create_session(session_id)
        session.pdf_files = [f for f in session.pdf_files if f.id != file_id]
        
        # Update current PDF if deleted
        if session.current_pdf_id == file_id:
            session.current_pdf_id = session.pdf_files[0].id if session.pdf_files else None
            
        session_manager.update_session(session)
        
        return {"message": "File deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/set-current")
async def set_current_file(
    session_id: str,
    file_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Set current working PDF"""
    
    try:
        session = session_manager.get_or_create_session(session_id)
        
        # Validate file exists in session
        file_exists = any(f.id == file_id for f in session.pdf_files)
        if not file_exists:
            raise HTTPException(status_code=404, detail="File not found in session")
        
        session.current_pdf_id = file_id
        session_manager.update_session(session)
        
        return {"message": "Current PDF updated", "current_pdf_id": file_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{file_id}", response_model=PDFFileInfo)
async def get_file_info(
    file_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """Get detailed information about a file"""
    
    try:
        file_info = await file_service.get_file_info(file_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        return file_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))