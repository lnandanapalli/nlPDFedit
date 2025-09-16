"""
AI Prompt Template for PDF Editor - Clean Architecture
This module defines simplified prompt templates that generate structured commands only.
The LLM should not know about PDF implementation details.
"""

def get_simple_command_prompt(available_files_count=0, chat_history=None):
    """
    Generate a clean system prompt for command generation only.
    This replaces the complex PDF-aware prompt with a simple command generator.
    """
    
    prompt = """You are a Document Operation Command Generator. Generate structured commands only.

AVAILABLE OPERATIONS:
1. extract_pages - Extract specific pages
2. merge_pdfs - Combine multiple documents  
3. split_pdf - Split document into parts
4. rotate_pages - Rotate pages by degrees
5. compress_pdf - Reduce file size
6. add_watermark - Add text overlay
7. extract_text - Get text content

RESPONSE FORMAT (EXACT):

<method_call_start>
<method_name>OPERATION_NAME</method_name>
<parameters>
{
    "parameter": "value"
}
</parameters>
<method_call_end>

PARAMETERS:

extract_pages:
- pages: [1, 2, 3] (required)
- output_name: "name.pdf" (optional)

merge_pdfs:
- merge_all: true (optional)
- output_name: "name.pdf" (optional)

split_pdf:
- split_type: "pages" (optional)

rotate_pages:
- pages: [1, 2] (required)
- rotation: 90/180/270 (required)

compress_pdf:
- output_name: "name.pdf" (optional)

add_watermark:
- watermark_text: "text" (required)
- output_name: "name.pdf" (optional)

extract_text:
- output_name: "name.txt" (optional)

EXAMPLES:

"Extract pages 1 and 2" →
<method_call_start>
<method_name>extract_pages</method_name>
<parameters>
{
    "pages": [1, 2]
}
</parameters>
<method_call_end>

"Merge all documents" →
<method_call_start>
<method_name>merge_pdfs</method_name>
<parameters>
{
    "merge_all": true
}
</parameters>
<method_call_end>

RULES:
- ONLY respond with method call format
- NO explanations or conversational text
- Use double quotes in JSON
- No comments in JSON
- No trailing commas
"""

    # Add context
    if available_files_count > 0:
        prompt += f"\n\nCONTEXT: {available_files_count} document(s) available.\n"
    else:
        prompt += "\n\nCONTEXT: No documents uploaded.\n"

    # Add recent history
    if chat_history and len(chat_history) > 2:
        prompt += "\nRECENT:\n"
        recent = chat_history[-3:]
        for msg in recent:
            role = "User" if msg.message_type.value == "user" else "AI"
            content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
            prompt += f"{role}: {content}\n"

    prompt += "\nGenerate command:"
    return prompt


# Legacy functions - kept for backwards compatibility but simplified

def get_pdf_editor_system_prompt(pdf_files=None, chat_history=None):
    """Legacy function - redirects to clean prompt"""
    files_count = len(pdf_files) if pdf_files else 0
    return get_simple_command_prompt(files_count, chat_history)


def parse_method_call(ai_response: str) -> dict:
    """
    Simplified parser for method calls.
    This is now just a compatibility layer - the real parsing is in CommandParserService.
    """
    import re
    import json
    
    try:
        # Extract method name
        method_match = re.search(r'<method_name>(.*?)</method_name>', ai_response, re.DOTALL)
        if not method_match:
            return {'success': False, 'error': 'No method name found'}
        
        method_name = method_match.group(1).strip()
        
        # Extract parameters
        params_match = re.search(r'<parameters>(.*?)</parameters>', ai_response, re.DOTALL)
        if not params_match:
            return {'success': False, 'error': 'No parameters found'}
        
        params_str = params_match.group(1).strip()
        
        # Clean JSON
        params_str = re.sub(r'//.*$', '', params_str, flags=re.MULTILINE)
        params_str = re.sub(r'/\*.*?\*/', '', params_str, flags=re.DOTALL)
        params_str = re.sub(r"'([^']*)':", r'"\1":', params_str)
        params_str = re.sub(r": '([^']*)'", r': "\1"', params_str)
        
        parameters = json.loads(params_str)
        
        return {
            'success': True,
            'method_name': method_name,
            'parameters': parameters
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Parse error: {str(e)}'
        }


def validate_method_call(method_name: str, parameters: dict) -> tuple[bool, str]:
    """
    Simplified validation - real validation is in CommandParserService.
    This is kept for backwards compatibility.
    """
    valid_methods = [
        'extract_pages', 'merge_pdfs', 'split_pdf', 'rotate_pages',
        'compress_pdf', 'add_watermark', 'extract_text'
    ]
    
    if method_name not in valid_methods:
        return False, f"Unknown method: {method_name}"
    
    # Basic validation - detailed validation is in CommandParserService
    if method_name in ['extract_pages', 'rotate_pages']:
        if 'pages' not in parameters:
            return False, "pages parameter required"
    
    if method_name == 'add_watermark':
        if 'watermark_text' not in parameters:
            return False, "watermark_text parameter required"
    
    if method_name == 'rotate_pages':
        if 'rotation' not in parameters or parameters['rotation'] not in [90, 180, 270]:
            return False, "rotation must be 90, 180, or 270"
    
    return True, ""