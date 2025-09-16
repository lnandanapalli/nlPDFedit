from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from datetime import datetime

from ..models import (
    ChatMessageRequest, 
    ChatMessageResponse, 
    MessageType,
    SessionState
)
from ..services.llm_service import LLMService
from ..services.session_manager import SessionManager

router = APIRouter()

# Dependency injection
def get_llm_service():
    return LLMService()

def get_session_manager():
    return SessionManager()


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    llm_service: LLMService = Depends(get_llm_service),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Send a chat message and get LLM response"""
    
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        session = session_manager.get_or_create_session(session_id)
        
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
        
        # Process with LLM
        assistant_response = await llm_service.process_message(
            request.content,
            session_id,
            session.pdf_files,
            session.chat_history
        )
        
        # Add assistant response to session
        session.chat_history.append(assistant_response)
        
        # Update session
        session_manager.update_session(session)
        
        return assistant_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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