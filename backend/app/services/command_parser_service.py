"""
Command Parser Service - Clean Architecture Layer

This service acts as a bridge between the LLM's structured output and the PDF operations.
It translates high-level commands into specific PDF library operations.
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
import uuid
from datetime import datetime

from ..models import PDFFileInfo, ChatMessageResponse, MessageType


class CommandType(Enum):
    """Available PDF command types"""
    EXTRACT_PAGES = "extract_pages"
    MERGE_PDFS = "merge_pdfs"
    SPLIT_PDF = "split_pdf"
    ROTATE_PAGES = "rotate_pages"
    COMPRESS_PDF = "compress_pdf"
    ADD_WATERMARK = "add_watermark"
    EXTRACT_TEXT = "extract_text"


class CommandParserService:
    """
    Parses structured LLM output and validates commands before execution.
    This service ensures clean separation between AI logic and PDF operations.
    """
    
    def __init__(self):
        self.supported_commands = {cmd.value for cmd in CommandType}
    
    def parse_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """
        Parse structured LLM response into command format.
        
        Args:
            llm_response: Raw response from LLM service
            
        Returns:
            dict: Parsed command with validation status
        """
        try:
            # Extract command structure from LLM response
            command_data = self._extract_command_structure(llm_response)
            
            if not command_data['success']:
                return command_data
            
            # Validate command
            validation_result = self._validate_command(
                command_data['command_type'], 
                command_data['parameters']
            )
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f"Command validation failed: {validation_result['error']}",
                    'command_type': command_data['command_type'],
                    'parameters': command_data['parameters']
                }
            
            return {
                'success': True,
                'command_type': command_data['command_type'],
                'parameters': command_data['parameters'],
                'execution_plan': self._create_execution_plan(
                    command_data['command_type'], 
                    command_data['parameters']
                )
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to parse LLM response: {str(e)}",
                'raw_response': llm_response
            }
    
    def _extract_command_structure(self, llm_response: str) -> Dict[str, Any]:
        """Extract command structure from LLM response"""
        import re
        
        try:
            # Extract method name
            method_match = re.search(r'<method_name>(.*?)</method_name>', llm_response, re.DOTALL)
            if not method_match:
                return {
                    'success': False,
                    'error': 'No command type found in LLM response'
                }
            
            command_type = method_match.group(1).strip()
            
            # Extract parameters
            params_match = re.search(r'<parameters>(.*?)</parameters>', llm_response, re.DOTALL)
            if not params_match:
                return {
                    'success': False,
                    'error': 'No parameters found in LLM response'
                }
            
            params_str = params_match.group(1).strip()
            
            # Clean and parse JSON
            cleaned_params = self._clean_json_string(params_str)
            parameters = json.loads(cleaned_params)
            
            return {
                'success': True,
                'command_type': command_type,
                'parameters': parameters
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Invalid JSON in parameters: {str(e)}',
                'raw_params': params_str
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error extracting command structure: {str(e)}'
            }
    
    def _clean_json_string(self, json_str: str) -> str:
        """Clean JSON string from common LLM formatting issues"""
        import re
        
        # Remove comments
        json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        # Fix single quotes to double quotes for property names and values
        json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
        json_str = re.sub(r": '([^']*)'", r': "\1"', json_str)
        
        return json_str.strip()
    
    def _validate_command(self, command_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate command type and parameters"""
        
        if command_type not in self.supported_commands:
            return {
                'valid': False,
                'error': f"Unsupported command type: {command_type}"
            }
        
        # Command-specific validation
        validation_functions = {
            CommandType.EXTRACT_PAGES.value: self._validate_extract_pages,
            CommandType.MERGE_PDFS.value: self._validate_merge_pdfs,
            CommandType.SPLIT_PDF.value: self._validate_split_pdf,
            CommandType.ROTATE_PAGES.value: self._validate_rotate_pages,
            CommandType.COMPRESS_PDF.value: self._validate_compress_pdf,
            CommandType.ADD_WATERMARK.value: self._validate_add_watermark,
            CommandType.EXTRACT_TEXT.value: self._validate_extract_text
        }
        
        validator = validation_functions.get(command_type)
        if validator:
            return validator(parameters)
        
        return {'valid': True}
    
    def _validate_extract_pages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extract_pages parameters"""
        if 'pages' not in params:
            return {'valid': False, 'error': 'pages parameter is required'}
        
        if not isinstance(params['pages'], list) or not params['pages']:
            return {'valid': False, 'error': 'pages must be a non-empty list of integers'}
        
        if not all(isinstance(p, int) and p > 0 for p in params['pages']):
            return {'valid': False, 'error': 'All page numbers must be positive integers'}
        
        return {'valid': True}
    
    def _validate_merge_pdfs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate merge_pdfs parameters"""
        return {'valid': True}  # No required parameters
    
    def _validate_split_pdf(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate split_pdf parameters"""
        return {'valid': True}  # No required parameters
    
    def _validate_rotate_pages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate rotate_pages parameters"""
        if 'pages' not in params:
            return {'valid': False, 'error': 'pages parameter is required'}
        
        if not isinstance(params['pages'], list) or not params['pages']:
            return {'valid': False, 'error': 'pages must be a non-empty list of integers'}
        
        if not all(isinstance(p, int) and p > 0 for p in params['pages']):
            return {'valid': False, 'error': 'All page numbers must be positive integers'}
        
        if 'rotation' not in params or params['rotation'] not in [90, 180, 270]:
            return {'valid': False, 'error': 'rotation must be 90, 180, or 270 degrees'}
        
        return {'valid': True}
    
    def _validate_compress_pdf(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate compress_pdf parameters"""
        return {'valid': True}  # No required parameters
    
    def _validate_add_watermark(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate add_watermark parameters"""
        if 'watermark_text' not in params:
            return {'valid': False, 'error': 'watermark_text parameter is required'}
        
        if not isinstance(params['watermark_text'], str) or not params['watermark_text'].strip():
            return {'valid': False, 'error': 'watermark_text must be a non-empty string'}
        
        return {'valid': True}
    
    def _validate_extract_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extract_text parameters"""
        return {'valid': True}  # No required parameters
    
    def _create_execution_plan(self, command_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution plan for the command"""
        
        return {
            'operation': command_type,
            'parameters': parameters,
            'requires_pdf_selection': self._requires_pdf_selection(command_type),
            'output_type': self._get_output_type(command_type),
            'estimated_complexity': self._estimate_complexity(command_type, parameters)
        }
    
    def _requires_pdf_selection(self, command_type: str) -> str:
        """Determine PDF selection strategy for command"""
        selection_strategy = {
            CommandType.EXTRACT_PAGES.value: "single",
            CommandType.MERGE_PDFS.value: "multiple",
            CommandType.SPLIT_PDF.value: "single",
            CommandType.ROTATE_PAGES.value: "single",
            CommandType.COMPRESS_PDF.value: "single",
            CommandType.ADD_WATERMARK.value: "single",
            CommandType.EXTRACT_TEXT.value: "single"
        }
        return selection_strategy.get(command_type, "single")
    
    def _get_output_type(self, command_type: str) -> str:
        """Get expected output type for command"""
        output_types = {
            CommandType.EXTRACT_PAGES.value: "pdf",
            CommandType.MERGE_PDFS.value: "pdf",
            CommandType.SPLIT_PDF.value: "multiple_pdf",
            CommandType.ROTATE_PAGES.value: "pdf",
            CommandType.COMPRESS_PDF.value: "pdf",
            CommandType.ADD_WATERMARK.value: "pdf",
            CommandType.EXTRACT_TEXT.value: "text"
        }
        return output_types.get(command_type, "pdf")
    
    def _estimate_complexity(self, command_type: str, parameters: Dict[str, Any]) -> str:
        """Estimate operation complexity for progress tracking"""
        if command_type == CommandType.MERGE_PDFS.value:
            return "medium"
        elif command_type == CommandType.SPLIT_PDF.value:
            return "medium"
        elif command_type == CommandType.COMPRESS_PDF.value:
            return "high"
        else:
            return "low"
    
    def select_input_files(
        self, 
        execution_plan: Dict[str, Any], 
        available_files: List[PDFFileInfo]
    ) -> List[PDFFileInfo]:
        """
        Select appropriate input files based on execution plan
        """
        if not available_files:
            return []
        
        selection_strategy = execution_plan['requires_pdf_selection']
        
        if selection_strategy == "multiple":
            # Return all available files for merge operations
            return available_files
        elif selection_strategy == "single":
            # Return the most recent or first available file
            return [available_files[0]]
        
        return available_files