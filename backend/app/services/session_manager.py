from typing import Dict, List, Optional
from datetime import datetime
import uuid
from ..models import PDFFileInfo, ChatMessage, SessionState

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}
    
    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        session = SessionState(
            session_id=session_id,
            pdf_files=[],
            chat_history=[],
            created_at=datetime.now().isoformat()
        )
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get a session by ID."""
        return self.sessions.get(session_id)
    
    def get_or_create_session(self, session_id: str) -> SessionState:
        """Get a session by ID, or create it if it doesn't exist."""
        session = self.sessions.get(session_id)
        if not session:
            session = SessionState(
                session_id=session_id,
                pdf_files=[],
                chat_history=[],
                created_at=datetime.now().isoformat()
            )
            self.sessions[session_id] = session
        return session
    
    def add_pdf_file(self, session_id: str, pdf_file: PDFFileInfo) -> bool:
        """Add a PDF file to a session."""
        session = self.get_session(session_id)
        if session:
            session.pdf_files.append(pdf_file)
            return True
        return False
    
    def remove_pdf_file(self, session_id: str, file_id: str) -> bool:
        """Remove a PDF file from a session."""
        session = self.get_session(session_id)
        if session:
            session.pdf_files = [f for f in session.pdf_files if f.id != file_id]
            return True
        return False
    
    def get_pdf_files(self, session_id: str) -> List[PDFFileInfo]:
        """Get all PDF files in a session."""
        session = self.get_session(session_id)
        return session.pdf_files if session else []
    
    def add_chat_message(self, session_id: str, message: ChatMessage) -> bool:
        """Add a chat message to a session."""
        session = self.get_session(session_id)
        if session:
            session.chat_history.append(message)
            return True
        return False
    
    def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """Get chat history for a session."""
        session = self.get_session(session_id)
        return session.chat_history if session else []
    
    def clear_chat_history(self, session_id: str) -> bool:
        """Clear chat history for a session."""
        session = self.get_session(session_id)
        if session:
            session.chat_history = []
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(self) -> List[str]:
        """List all session IDs."""
        return list(self.sessions.keys())
    
    def update_session(self, session: SessionState) -> bool:
        """Update a session."""
        if session.session_id in self.sessions:
            self.sessions[session.session_id] = session
            return True
        return False
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return self.list_sessions()

# Global session manager instance
session_manager = SessionManager()