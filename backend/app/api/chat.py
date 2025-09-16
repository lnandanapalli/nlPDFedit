from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from datetime import datetime

from ..models import (
    ChatMessageRequest, 
    ChatMessageResponse, 
    MessageType,
    SessionState,
    PDFFileInfo
)
from ..services.llm_service import LLMService
from ..services.command_parser_service import CommandParserService
from ..services.pdf_service import PDFService
from ..services.session_manager import SessionManager

router = APIRouter()

# Dependency injection - Use global session manager instance
def get_llm_service():
    return LLMService()

def get_command_parser_service():
    return CommandParserService()

def get_pdf_service():
    return PDFService()

def get_session_manager():
    from ..services.session_manager import session_manager
    return session_manager


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    llm_service: LLMService = Depends(get_llm_service),
    command_parser: CommandParserService = Depends(get_command_parser_service),
    pdf_service: PDFService = Depends(get_pdf_service),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Send a chat message using clean architecture:
    User Input -> LLM (Command Generation) -> Parser (Validation) -> PDF Service (Execution)
    """
    
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        session = session_manager.get_or_create_session(session_id)
        
        # Debug: Log session info
        print(f"DEBUG: Session ID: {session_id}")
        print(f"DEBUG: Number of PDF files in session: {len(session.pdf_files)}")
        for i, pdf in enumerate(session.pdf_files):
            print(f"DEBUG: PDF {i+1}: {pdf.name} (ID: {pdf.id})")
        
        # Create user message
        user_message = ChatMessageResponse(
            id=str(uuid.uuid4()),
            content=request.content,
            message_type=MessageType.USER,
            timestamp=datetime.now(),
            session_id=session_id
        )
        
        # Add to session history
        session.chat_history.append(user_message)
        
        # Step 1: Generate structured command using LLM
        llm_result = await llm_service.generate_command(
            request.content,
            len(session.pdf_files),
            session.chat_history[-10:]  # Last 10 messages for context
        )
        
        if not llm_result['success']:
            error_response = ChatMessageResponse(
                id=str(uuid.uuid4()),
                content=f"❌ LLM Error: {llm_result['error']}",
                message_type=MessageType.ERROR,
                timestamp=datetime.now(),
                session_id=session_id
            )
            session.chat_history.append(error_response)
            session_manager.update_session(session)
            return error_response
        
        # Step 2: Parse and validate the LLM command
        command_result = command_parser.parse_llm_response(llm_result['response'])
        
        if not command_result['success']:
            error_response = ChatMessageResponse(
                id=str(uuid.uuid4()),
                content=f"❌ Command Parse Error: {command_result['error']}",
                message_type=MessageType.ERROR,
                timestamp=datetime.now(),
                session_id=session_id,
                operation_result={
                    "error": command_result['error'],
                    "raw_llm_response": llm_result['response']
                }
            )
            session.chat_history.append(error_response)
            session_manager.update_session(session)
            return error_response
        
        # Step 3: Check if PDF files are needed
        execution_plan = command_result['execution_plan']
        
        # Check if the operation needs PDF files
        needs_pdf_files = execution_plan['requires_pdf_selection'] in ['single', 'multiple']
        
        if not session.pdf_files and needs_pdf_files:
            no_files_response = ChatMessageResponse(
                id=str(uuid.uuid4()),
                content="❌ No PDF files available. Please upload a PDF file first to perform this operation.",
                message_type=MessageType.ERROR,
                timestamp=datetime.now(),
                session_id=session_id
            )
            session.chat_history.append(no_files_response)
            session_manager.update_session(session)
            return no_files_response
        
        # Step 4: Select appropriate input files
        input_files = command_parser.select_input_files(execution_plan, session.pdf_files)
        
        if not input_files and needs_pdf_files:
            no_suitable_files_response = ChatMessageResponse(
                id=str(uuid.uuid4()),
                content="❌ No suitable PDF files found for this operation.",
                message_type=MessageType.ERROR,
                timestamp=datetime.now(),
                session_id=session_id
            )
            session.chat_history.append(no_suitable_files_response)
            session_manager.update_session(session)
            return no_suitable_files_response
        
        # Step 5: Execute PDF operation
        try:
            result_file = await pdf_service.perform_operation(
                command_result['command_type'],
                input_files,
                command_result['parameters'],
                session_id
            )
            
            # Step 6: Generate success response
            success_response = _create_success_response(
                command_result['command_type'],
                command_result['parameters'],
                result_file,
                input_files,
                session_id
            )
            
            # Add result file to session if it's a PDF
            if result_file and execution_plan['output_type'] in ['pdf', 'multiple_pdf']:
                session.pdf_files.append(result_file)
            
            session.chat_history.append(success_response)
            session_manager.update_session(session)
            return success_response
            
        except Exception as pdf_error:
            error_response = ChatMessageResponse(
                id=str(uuid.uuid4()),
                content=f"❌ PDF Operation Error: {str(pdf_error)}",
                message_type=MessageType.ERROR,
                timestamp=datetime.now(),
                session_id=session_id,
                operation_result={
                    "operation": command_result['command_type'],
                    "parameters": command_result['parameters'],
                    "status": "failed",
                    "error": str(pdf_error),
                    "show_retry": True
                }
            )
            session.chat_history.append(error_response)
            session_manager.update_session(session)
            return error_response
        
    except Exception as e:
        error_response = ChatMessageResponse(
            id=str(uuid.uuid4()),
            content=f"❌ System Error: {str(e)}",
            message_type=MessageType.ERROR,
            timestamp=datetime.now(),
            session_id=session_id or str(uuid.uuid4())
        )
        return error_response


def _create_success_response(
    operation: str,
    parameters: dict,
    result_file: PDFFileInfo,
    input_files: List[PDFFileInfo],
    session_id: str
) -> ChatMessageResponse:
    """Create a success response for completed operations"""
    
    # Operation-specific success messages
    success_messages = {
        "extract_pages": f"✅ Successfully extracted pages {parameters.get('pages', [])}",
        "merge_pdfs": f"✅ Successfully merged {len(input_files)} PDF files",
        "split_pdf": f"✅ Successfully split PDF into separate files",
        "rotate_pages": f"✅ Successfully rotated pages {parameters.get('pages', [])} by {parameters.get('rotation', 0)}°",
        "compress_pdf": f"✅ Successfully compressed PDF",
        "add_watermark": f"✅ Successfully added watermark '{parameters.get('watermark_text', '')}'",
        "extract_text": f"✅ Successfully extracted text content"
    }
    
    content = success_messages.get(operation, f"✅ Operation {operation} completed")
    
    if result_file:
        content += f"\n\n📁 **Output file:** {result_file.name}"
        
        if hasattr(result_file, 'file_size') and result_file.file_size:
            content += f" ({result_file.file_size // 1024} KB)"
            
        if hasattr(result_file, 'page_count') and result_file.page_count:
            content += f" • {result_file.page_count} pages"
        
        # Add user-friendly download instructions
        content += f"\n\n⬇️ **Your file is ready for download!**"
        content += f"\nClick the download button below or use this link:"
        content += f"\n🔗 [Download {result_file.name}](/api/v1/files/download/{result_file.id})"
    
    return ChatMessageResponse(
        id=str(uuid.uuid4()),
        content=content,
        message_type=MessageType.ASSISTANT,
        timestamp=datetime.now(),
        session_id=session_id,
        operation_result={
            "operation": operation,
            "parameters": parameters,
            "status": "completed",
            "result_file": {
                "id": result_file.id,
                "name": result_file.name,
                "path": result_file.file_path,
                "download_url": f"/api/v1/files/download/{result_file.id}",
                "file_size": getattr(result_file, 'file_size', 0),
                "page_count": getattr(result_file, 'page_count', 0),
                "file_type": "pdf" if result_file.name.endswith('.pdf') else "text"
            } if result_file else None,
            "show_download_button": True,
            "download_ready": True
        }
    )


@router.get("/history/{session_id}", response_model=List[ChatMessageResponse])
async def get_chat_history(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get chat history for a session"""
    
    try:
        session = session_manager.get_or_create_session(session_id)
        return session.chat_history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{session_id}")
async def clear_chat_history(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Clear chat history for a session"""
    
    try:
        session = session_manager.get_or_create_session(session_id)
        
        session.chat_history = []
        session_manager.update_session(session)
        
        return {"message": "Chat history cleared"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[str])
async def get_active_sessions(
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get list of active session IDs"""
    
    try:
        return session_manager.get_active_sessions()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))