from fastapi import APIRouter, HTTPException, Depends
from typing import List
import asyncio
import logging

from ..models import PDFOperationRequest, PDFFileInfo
from ..services.pdf_service import PDFService
from ..services.session_manager import SessionManager

router = APIRouter(prefix="/api/pdf", tags=["pdf"])
logger = logging.getLogger(__name__)

@router.post("/operation", response_model=PDFFileInfo)
async def perform_pdf_operation(
    request: PDFOperationRequest,
    pdf_service: PDFService = Depends(lambda: PDFService()),
    session_manager: SessionManager = Depends(lambda: SessionManager())
):
    """
    Perform a PDF operation like extract, merge, split, rotate, etc.
    """
    try:
        logger.info(f"Performing PDF operation: {request.operation_type}")
        
        # Validate that the session exists and has the required files
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Validate that all input PDF IDs exist in the session
        session_file_ids = {file.id for file in session.pdf_files}
        missing_files = set(request.input_pdf_ids) - session_file_ids
        if missing_files:
            raise HTTPException(
                status_code=400, 
                detail=f"Files not found in session: {list(missing_files)}"
            )
        
        # Get the actual file paths
        input_files = [
            file for file in session.pdf_files 
            if file.id in request.input_pdf_ids
        ]
        
        # Perform the operation
        result = await pdf_service.perform_operation(
            operation_type=request.operation_type,
            input_files=input_files,
            parameters=request.parameters,
            session_id=request.session_id
        )
        
        # Add the result file to the session
        session_manager.add_pdf_file(request.session_id, result)
        
        logger.info(f"PDF operation completed: {result.id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing PDF operation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")

@router.get("/operations", response_model=List[str])
async def get_available_operations():
    """
    Get a list of available PDF operations.
    """
    operations = [
        "extract_text",
        "extract_pages", 
        "merge_pdfs",
        "split_pdf",
        "rotate_pages",
        "add_watermark",
        "compress_pdf",
        "get_page_count",
        "get_metadata"
    ]
    return operations

@router.get("/operation/{operation_type}/parameters")
async def get_operation_parameters(operation_type: str):
    """
    Get the required and optional parameters for a specific PDF operation.
    """
    parameter_specs = {
        "extract_text": {
            "required": [],
            "optional": {
                "page_numbers": "List of page numbers to extract (default: all pages)",
                "start_page": "Starting page number (1-indexed)",
                "end_page": "Ending page number (1-indexed)"
            }
        },
        "extract_pages": {
            "required": ["page_numbers"],
            "optional": {
                "output_filename": "Name for the output file"
            }
        },
        "merge_pdfs": {
            "required": [],
            "optional": {
                "output_filename": "Name for the merged file"
            }
        },
        "split_pdf": {
            "required": [],
            "optional": {
                "split_type": "Type of split: 'pages' or 'ranges'",
                "pages_per_file": "Number of pages per file (for 'pages' split)",
                "page_ranges": "List of page ranges (for 'ranges' split)"
            }
        },
        "rotate_pages": {
            "required": ["rotation"],
            "optional": {
                "page_numbers": "List of page numbers to rotate (default: all pages)"
            }
        },
        "add_watermark": {
            "required": ["watermark_text"],
            "optional": {
                "position": "Watermark position: 'center', 'top-left', 'top-right', 'bottom-left', 'bottom-right'",
                "opacity": "Watermark opacity (0.0 to 1.0)",
                "font_size": "Font size for the watermark",
                "color": "Watermark color (RGB hex or name)"
            }
        },
        "compress_pdf": {
            "required": [],
            "optional": {
                "quality": "Compression quality: 'low', 'medium', 'high'",
                "image_quality": "Image compression quality (0-100)"
            }
        },
        "get_page_count": {
            "required": [],
            "optional": {}
        },
        "get_metadata": {
            "required": [],
            "optional": {}
        }
    }
    
    if operation_type not in parameter_specs:
        raise HTTPException(status_code=404, detail="Operation type not found")
    
    return parameter_specs[operation_type]