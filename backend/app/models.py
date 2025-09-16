from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class PDFOperationType(str, Enum):
    EXTRACT_PAGES = "extract_pages"
    MERGE_PDFS = "merge_pdfs"
    SPLIT_PDF = "split_pdf"
    ROTATE_PAGES = "rotate_pages"
    COMPRESS_PDF = "compress_pdf"
    ADD_WATERMARK = "add_watermark"
    EXTRACT_TEXT = "extract_text"
    ADD_BOOKMARKS = "add_bookmarks"


class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ERROR = "error"


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None


class ChatMessage(BaseModel):
    id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    session_id: str
    operation_result: Optional[Dict[str, Any]] = None


class ChatMessageResponse(BaseModel):
    id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    session_id: str
    operation_result: Optional[Dict[str, Any]] = None


class PDFFileInfo(BaseModel):
    id: str
    name: str
    original_filename: str
    file_path: str
    file_size: int
    page_count: int
    created_at: datetime
    parent_id: Optional[str] = None
    is_temporary: bool = True


class PDFOperationRequest(BaseModel):
    operation_type: PDFOperationType
    input_pdf_ids: List[str]
    parameters: Dict[str, Any] = {}
    session_id: str


class PDFOperationResponse(BaseModel):
    operation_id: str
    operation_type: PDFOperationType
    status: str  # "pending", "processing", "completed", "failed"
    result_files: List[PDFFileInfo] = []
    error_message: Optional[str] = None
    created_at: datetime


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_size: int
    page_count: int
    upload_path: str


class SessionState(BaseModel):
    session_id: str
    current_pdf_id: Optional[str] = None
    pdf_files: List[PDFFileInfo] = []
    chat_history: List[ChatMessageResponse] = []
    created_at: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime