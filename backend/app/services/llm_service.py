from openai import OpenAI
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from ..models import ChatMessageResponse, MessageType, PDFFileInfo


class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """Get list of available PDF operations for function calling"""
        return [
            {
                "name": "extract_pages",
                "description": "Extract specific pages from a PDF",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pdf_id": {"type": "string", "description": "ID of the PDF to extract from"},
                        "pages": {"type": "array", "items": {"type": "integer"}, "description": "Page numbers to extract (1-based)"},
                        "output_name": {"type": "string", "description": "Name for the output file"}
                    },
                    "required": ["pdf_id", "pages"]
                }
            },
            {
                "name": "merge_pdfs",
                "description": "Merge multiple PDF files",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pdf_ids": {"type": "array", "items": {"type": "string"}, "description": "IDs of PDFs to merge"},
                        "output_name": {"type": "string", "description": "Name for the merged file"}
                    },
                    "required": ["pdf_ids"]
                }
            },
            {
                "name": "split_pdf",
                "description": "Split a PDF into separate files",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pdf_id": {"type": "string", "description": "ID of the PDF to split"},
                        "split_type": {"type": "string", "enum": ["pages", "range"], "description": "How to split the PDF"}
                    },
                    "required": ["pdf_id"]
                }
            },
            {
                "name": "rotate_pages",
                "description": "Rotate specific pages in a PDF",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pdf_id": {"type": "string", "description": "ID of the PDF"},
                        "pages": {"type": "array", "items": {"type": "integer"}, "description": "Page numbers to rotate"},
                        "rotation": {"type": "integer", "enum": [90, 180, 270], "description": "Rotation angle"}
                    },
                    "required": ["pdf_id", "pages", "rotation"]
                }
            },
            {
                "name": "compress_pdf",
                "description": "Compress a PDF to reduce file size",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pdf_id": {"type": "string", "description": "ID of the PDF to compress"},
                        "output_name": {"type": "string", "description": "Name for the compressed file"}
                    },
                    "required": ["pdf_id"]
                }
            },
            {
                "name": "add_watermark",
                "description": "Add a watermark to PDF pages",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pdf_id": {"type": "string", "description": "ID of the PDF"},
                        "watermark_text": {"type": "string", "description": "Text for the watermark"},
                        "output_name": {"type": "string", "description": "Name for the watermarked file"}
                    },
                    "required": ["pdf_id", "watermark_text"]
                }
            },
            {
                "name": "extract_text",
                "description": "Extract text content from a PDF",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pdf_id": {"type": "string", "description": "ID of the PDF"},
                        "output_name": {"type": "string", "description": "Name for the text file"}
                    },
                    "required": ["pdf_id"]
                }
            }
        ]
    
    async def process_message(
        self,
        message: str,
        session_id: str,
        pdf_files: List[PDFFileInfo],
        chat_history: List[ChatMessageResponse]
    ) -> ChatMessageResponse:
        """Process user message with LLM"""
        
        try:
            # Prepare context
            system_message = self._create_system_message(pdf_files, chat_history)
            
            # Get available functions
            functions = self.get_available_functions()
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                tools=[{"type": "function", "function": f} for f in functions],
                tool_choice="auto",
                temperature=0.1,
                max_tokens=1000
            )
            
            message_response = response.choices[0].message
            
            # Check if LLM wants to call a function
            if message_response.tool_calls:
                return await self._handle_tool_calls(message_response, session_id)
            else:
                # Regular conversational response
                return ChatMessageResponse(
                    id=str(uuid.uuid4()),
                    content=message_response.content,
                    message_type=MessageType.ASSISTANT,
                    timestamp=datetime.now(),
                    session_id=session_id
                )
                
        except Exception as e:
            return ChatMessageResponse(
                id=str(uuid.uuid4()),
                content=f"I encountered an error: {str(e)}",
                message_type=MessageType.ERROR,
                timestamp=datetime.now(),
                session_id=session_id,
                operation_result={
                    "error": str(e),
                    "show_retry": True
                }
            )
    
    def _create_system_message(
        self,
        pdf_files: List[PDFFileInfo],
        chat_history: List[ChatMessageResponse]
    ) -> str:
        """Create system message with context"""
        
        system_msg = """You are a PDF manipulation assistant. You help users perform operations on PDF files using natural language commands.

Available PDF operations:
- Extract specific pages from PDFs
- Merge multiple PDFs together
- Split PDFs into separate files
- Rotate pages
- Compress PDFs to reduce file size
- Add watermarks
- Extract text content

Current session context:"""
        
        if pdf_files:
            system_msg += f"\n\nAvailable PDFs ({len(pdf_files)}):"
            for pdf in pdf_files:
                system_msg += f"\n- ID: {pdf.id}, Name: {pdf.name}, Pages: {pdf.page_count}"
        else:
            system_msg += "\n\nNo PDFs currently uploaded."
        
        # Add recent chat context
        if chat_history:
            recent_messages = chat_history[-3:]  # Last 3 messages
            system_msg += "\n\nRecent conversation:"
            for msg in recent_messages:
                if msg.message_type == MessageType.USER:
                    system_msg += f"\nUser: {msg.content}"
                elif msg.message_type == MessageType.ASSISTANT:
                    system_msg += f"\nAssistant: {msg.content[:100]}..."
        
        system_msg += """

Instructions:
1. When users request PDF operations, call the appropriate function with the correct parameters
2. Use PDF IDs when referring to specific files
3. For page numbers, users typically use 1-based numbering
4. Generate appropriate output filenames if not specified
5. Be conversational and helpful in your responses
6. If you need clarification about which PDF to use or specific parameters, ask the user

Always be helpful and provide clear feedback about the operations performed."""
        
        return system_msg
    
    async def _handle_tool_calls(
        self,
        message_response,
        session_id: str
    ) -> ChatMessageResponse:
        """Handle LLM tool calls"""
        
        tool_call = message_response.tool_calls[0]
        function_call = tool_call.function
        function_name = function_call.name
        
        try:
            function_args = json.loads(function_call.arguments)
            
            # Return a message indicating the operation will be performed
            return ChatMessageResponse(
                id=str(uuid.uuid4()),
                content=f"I'll perform the {function_name} operation for you.",
                message_type=MessageType.ASSISTANT,
                timestamp=datetime.now(),
                session_id=session_id,
                operation_result={
                    "operation": function_name,
                    "parameters": function_args,
                    "status": "pending"
                }
            )
            
        except Exception as e:
            return ChatMessageResponse(
                id=str(uuid.uuid4()),
                content=f"Error processing operation: {str(e)}",
                message_type=MessageType.ERROR,
                timestamp=datetime.now(),
                session_id=session_id,
                operation_result={
                    "error": str(e),
                    "show_retry": True
                }
            )