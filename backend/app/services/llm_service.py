from openai import OpenAI
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from ..models import ChatMessageResponse, MessageType, PDFFileInfo


class LLMService:
    """
    Clean LLM Service - Only responsible for generating structured commands
    
    This service focuses solely on:
    1. Communicating with the LLM API
    2. Generating structured command output
    3. No PDF-specific knowledge or operations
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    async def generate_command(
        self,
        user_message: str,
        available_files_count: int = 0,
        chat_history: List[ChatMessageResponse] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured command based on user input.
        
        Args:
            user_message: User's request
            available_files_count: Number of PDF files available (for context only)
            chat_history: Recent conversation history
            
        Returns:
            dict: LLM response with structured command or error
        """
        try:
            system_prompt = self._create_system_prompt(available_files_count, chat_history)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            llm_response = response.choices[0].message.content
            
            return {
                'success': True,
                'response': llm_response,
                'model': self.model,
                'tokens_used': response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"LLM API error: {str(e)}",
                'response': None
            }
    
    def _create_system_prompt(
        self, 
        available_files_count: int, 
        chat_history: List[ChatMessageResponse] = None
    ) -> str:
        """Create system prompt for structured command generation"""
        
        prompt = """You are a PDF Operation Command Generator. You MUST respond with structured commands only.

AVAILABLE OPERATIONS:
1. extract_pages - Extract specific pages from a PDF
2. merge_pdfs - Merge multiple PDF files
3. split_pdf - Split a PDF into separate files  
4. rotate_pages - Rotate pages by degrees
5. compress_pdf - Reduce PDF file size
6. add_watermark - Add text watermarks
7. extract_text - Extract text content

RESPONSE FORMAT - Use this EXACT structure:

<method_call_start>
<method_name>OPERATION_NAME</method_name>
<parameters>
{
    "parameter_name": "value"
}
</parameters>
<method_call_end>

PARAMETER RULES:

extract_pages:
- pages: [1, 2, 3] (required) - Page numbers to extract
- output_name: "filename.pdf" (optional)

merge_pdfs:
- merge_all: true/false (optional)
- output_name: "filename.pdf" (optional)

split_pdf:
- split_type: "pages" (optional)

rotate_pages:
- pages: [1, 2] (required) - Pages to rotate
- rotation: 90/180/270 (required) - Degrees

compress_pdf:
- output_name: "filename.pdf" (optional)

add_watermark:
- watermark_text: "text" (required)
- output_name: "filename.pdf" (optional)

extract_text:
- output_name: "filename.txt" (optional)

JSON RULES:
- Use double quotes only
- No comments allowed
- No trailing commas
- Valid JSON format

EXAMPLES:

User: "Extract pages 1 to 3"
Response:
<method_call_start>
<method_name>extract_pages</method_name>
<parameters>
{
    "pages": [1, 2, 3]
}
</parameters>
<method_call_end>

User: "Merge all my PDFs"
Response:
<method_call_start>
<method_name>merge_pdfs</method_name>
<parameters>
{
    "merge_all": true
}
</parameters>
<method_call_end>

CRITICAL:
- ONLY respond with the method call format
- NO conversational text
- Focus on WHAT operation, not HOW to do it
- You don't need to know about specific PDF files
"""

        # Add context about available files
        if available_files_count > 0:
            prompt += f"\n\nCONTEXT: {available_files_count} PDF file(s) available for operations.\n"
        else:
            prompt += "\n\nCONTEXT: No PDF files uploaded. User must upload files first.\n"

        # Add recent conversation history if available
        if chat_history and len(chat_history) > 2:
            prompt += "\nRECENT CONVERSATION:\n"
            recent = chat_history[-4:]
            for msg in recent:
                role = "User" if msg.message_type.value == "user" else "Assistant"
                content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                prompt += f"{role}: {content}\n"

        prompt += "\nGenerate the appropriate command for the user's request:"
        
        return prompt