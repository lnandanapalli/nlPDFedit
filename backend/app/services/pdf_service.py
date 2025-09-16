from typing import List, Dict, Any
import os
import uuid
from datetime import datetime
from pathlib import Path
import shutil
import asyncio
from ..models import PDFFileInfo
import logging

# Import pdfly modules
from pdfly import cat, compress, extract_images, metadata
import pypdf

logger = logging.getLogger(__name__)

class PDFService:
    def __init__(self):
        self.upload_dir = "uploads"
        self.temp_dir = "temp"
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def perform_operation(
        self, 
        operation_type: str, 
        input_files: List[PDFFileInfo], 
        parameters: Dict[str, Any],
        session_id: str
    ) -> PDFFileInfo:
        """
        Perform a PDF operation and return the result file info.
        """
        try:
            if operation_type == "extract_text":
                return await self._extract_text(input_files, parameters, session_id)
            elif operation_type == "extract_pages":
                return await self._extract_pages(input_files, parameters, session_id)
            elif operation_type == "merge_pdfs":
                return await self._merge_pdfs(input_files, parameters, session_id)
            elif operation_type == "split_pdf":
                return await self._split_pdf(input_files, parameters, session_id)
            elif operation_type == "rotate_pages":
                return await self._rotate_pages(input_files, parameters, session_id)
            elif operation_type == "add_watermark":
                return await self._add_watermark(input_files, parameters, session_id)
            elif operation_type == "compress_pdf":
                return await self._compress_pdf(input_files, parameters, session_id)
            else:
                raise ValueError(f"Unsupported operation: {operation_type}")
        
        except Exception as e:
            logger.error(f"Error performing PDF operation {operation_type}: {str(e)}")
            raise
    
    async def _extract_text(self, input_files: List[PDFFileInfo], parameters: Dict[str, Any], session_id: str) -> PDFFileInfo:
        """Extract text from PDF pages using PyPDF2."""
        if not input_files:
            raise ValueError("No input files provided")
        
        input_file = input_files[0]
        output_name = parameters.get('output_name', f"extracted_text_{input_file.name.replace('.pdf', '.txt')}")
        
        if not output_name.endswith('.txt'):
            output_name += '.txt'
        
        # Generate unique file ID first
        file_id = str(uuid.uuid4())
        
        input_path = Path(input_file.file_path)
        # Use file_id for the actual file name to make downloads work
        file_extension = Path(output_name).suffix
        output_path = Path(self.temp_dir) / f"{file_id}{file_extension}"
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._extract_text_sync,
                input_path,
                output_path
            )
            
            file_size = output_path.stat().st_size if output_path.exists() else 0
            
            result_file = PDFFileInfo(
                id=file_id,
                name=output_name,  # Keep the user-friendly name for display
                original_filename=output_name,
                file_path=str(output_path),
                file_size=file_size,
                page_count=1,  # Text files have 1 "page"
                created_at=datetime.now().isoformat(),
                is_temporary=True
            )
            
            logger.info(f"Successfully extracted text from {input_file.name}")
            return result_file
            
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            raise Exception(f"Failed to extract text: {str(e)}")
    
    def _extract_text_sync(self, input_path: Path, output_path: Path):
        """Synchronous text extraction using PyPDF2"""
        from pypdf import PdfReader
        
        reader = PdfReader(str(input_path))
        text_content = []
        
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                text_content.append(f"--- Page {i+1} ---\n{page_text}\n\n")
            except Exception as e:
                text_content.append(f"--- Page {i+1} ---\n[Error extracting text: {str(e)}]\n\n")
        
        # Write text to file
        with open(output_path, 'w', encoding='utf-8') as text_file:
            text_file.writelines(text_content)
    
    async def _extract_pages(self, input_files: List[PDFFileInfo], parameters: Dict[str, Any], session_id: str) -> PDFFileInfo:
        """Extract specific pages from PDF using PyPDF2 (simpler than pdfly cat)."""
        if not input_files:
            raise ValueError("No input files provided")
        
        input_file = input_files[0]
        pages = parameters.get('pages', [1])
        output_name = parameters.get('output_name', f"extracted_pages_{len(pages)}.pdf")
        
        # Ensure output name ends with .pdf
        if not output_name.endswith('.pdf'):
            output_name += '.pdf'
        
        # Generate unique file ID first
        file_id = str(uuid.uuid4())
        
        # Create output path using file_id for the actual filename
        output_path = Path(self.temp_dir) / f"{file_id}.pdf"
        input_path = Path(input_file.file_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._extract_pages_sync,
                input_path,
                output_path,
                pages
            )
            
            # Get file size
            file_size = output_path.stat().st_size if output_path.exists() else 0
            
            # Create result file info
            result_file = PDFFileInfo(
                id=file_id,
                name=output_name,  # Keep user-friendly name for display
                original_filename=output_name,
                file_path=str(output_path),
                file_size=file_size,
                page_count=len(pages),
                created_at=datetime.now().isoformat(),
                is_temporary=True
            )
            
            logger.info(f"Successfully extracted {len(pages)} pages from {input_file.name}")
            return result_file
            
        except Exception as e:
            logger.error(f"Error extracting pages: {str(e)}")
            raise Exception(f"Failed to extract pages: {str(e)}")
    
    def _extract_pages_sync(self, input_path: Path, output_path: Path, pages: List[int]):
        """Synchronous page extraction using PyPDF2"""
        from pypdf import PdfReader, PdfWriter
        
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        
        for page_num in pages:
            if 1 <= page_num <= len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])  # Convert to 0-based
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
    
    async def _merge_pdfs(self, input_files: List[PDFFileInfo], parameters: Dict[str, Any], session_id: str) -> PDFFileInfo:
        """Merge multiple PDFs into one using pdfly."""
        if len(input_files) < 2:
            raise ValueError("At least 2 PDF files are required for merging")
        
        output_name = parameters.get('output_name', f"merged_{len(input_files)}_files.pdf")
        if not output_name.endswith('.pdf'):
            output_name += '.pdf'
        
        output_path = Path(self.temp_dir) / f"{session_id}_{output_name}"
        
        try:
            # Prepare file paths for pdfly cat
            input_paths = []
            total_pages = 0
            total_size = 0
            
            for file_info in input_files:
                input_path = Path(file_info.file_path)
                if not input_path.exists():
                    raise FileNotFoundError(f"Input file not found: {input_path}")
                input_paths.append(input_path)
                total_pages += file_info.page_count
                total_size += file_info.file_size
            
            # Use pdfly cat to merge all files (no page ranges = all pages)
            fn_pgrgs = []  # Empty page ranges means all pages for each file
            
            # Call pdfly cat with first file and empty page ranges for others
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._merge_pdfs_sync,
                input_paths,
                output_path
            )
            
            # Get actual file size
            file_size = output_path.stat().st_size if output_path.exists() else total_size
            
            result_file = PDFFileInfo(
                id=str(uuid.uuid4()),
                name=output_name,
                original_filename=output_name,
                file_path=str(output_path),
                file_size=file_size,
                page_count=total_pages,
                created_at=datetime.now().isoformat(),
                is_temporary=True
            )
            
            logger.info(f"Successfully merged {len(input_files)} PDFs into {output_name}")
            return result_file
            
        except Exception as e:
            logger.error(f"Error merging PDFs: {str(e)}")
            raise Exception(f"Failed to merge PDFs: {str(e)}")
    
    def _merge_pdfs_sync(self, input_paths: List[Path], output_path: Path):
        """Synchronous PDF merge using PyPDF2 (since pdfly cat is complex for multiple files)"""
        from pypdf import PdfWriter, PdfReader
        
        writer = PdfWriter()
        
        for input_path in input_paths:
            reader = PdfReader(str(input_path))
            for page in reader.pages:
                writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
    
    async def _split_pdf(self, input_files: List[PDFFileInfo], parameters: Dict[str, Any], session_id: str) -> PDFFileInfo:
        """Split PDF into multiple files using PyPDF2."""
        if not input_files:
            raise ValueError("No input files provided")
        
        input_file = input_files[0]
        split_type = parameters.get('split_type', 'pages')  # 'pages' or 'range'
        
        input_path = Path(input_file.file_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        try:
            # For now, split each page into separate files
            output_files = await asyncio.get_event_loop().run_in_executor(
                None,
                self._split_pdf_sync,
                input_path,
                session_id,
                input_file
            )
            
            # Return info about the first split file (in a real app, you might return all files)
            if output_files:
                result_file = output_files[0]
                logger.info(f"Successfully split {input_file.name} into {len(output_files)} files")
                return result_file
            else:
                raise Exception("No files were created during split operation")
            
        except Exception as e:
            logger.error(f"Error splitting PDF: {str(e)}")
            raise Exception(f"Failed to split PDF: {str(e)}")
    
    def _split_pdf_sync(self, input_path: Path, session_id: str, input_file: PDFFileInfo) -> List[PDFFileInfo]:
        """Synchronous PDF splitting using PyPDF2"""
        from pypdf import PdfReader, PdfWriter
        
        reader = PdfReader(str(input_path))
        output_files = []
        
        for i, page in enumerate(reader.pages):
            output_name = f"split_page_{i+1}_{input_file.name}"
            output_path = Path(self.temp_dir) / f"{session_id}_{output_name}"
            
            writer = PdfWriter()
            writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            file_size = output_path.stat().st_size if output_path.exists() else 0
            
            file_info = PDFFileInfo(
                id=str(uuid.uuid4()),
                name=output_name,
                original_filename=output_name,
                file_path=str(output_path),
                file_size=file_size,
                page_count=1,
                created_at=datetime.now().isoformat(),
                is_temporary=True
            )
            output_files.append(file_info)
        
        return output_files
    
    async def _rotate_pages(self, input_files: List[PDFFileInfo], parameters: Dict[str, Any], session_id: str) -> PDFFileInfo:
        """Rotate pages in PDF using PyPDF2 (pdfly doesn't have rotation)."""
        if not input_files:
            raise ValueError("No input files provided")
        
        input_file = input_files[0]
        pages = parameters.get('pages', [1])
        rotation = parameters.get('rotation', 90)
        output_name = parameters.get('output_name', f"rotated_{input_file.name}")
        
        if not output_name.endswith('.pdf'):
            output_name += '.pdf'
        
        input_path = Path(input_file.file_path)
        output_path = Path(self.temp_dir) / f"{session_id}_{output_name}"
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if rotation not in [90, 180, 270]:
            raise ValueError("Rotation must be 90, 180, or 270 degrees")
        
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._rotate_pages_sync,
                input_path,
                output_path,
                pages,
                rotation
            )
            
            file_size = output_path.stat().st_size if output_path.exists() else input_file.file_size
            
            result_file = PDFFileInfo(
                id=str(uuid.uuid4()),
                name=output_name,
                original_filename=output_name,
                file_path=str(output_path),
                file_size=file_size,
                page_count=input_file.page_count,
                created_at=datetime.now().isoformat(),
                is_temporary=True
            )
            
            logger.info(f"Successfully rotated pages {pages} by {rotation}° in {input_file.name}")
            return result_file
            
        except Exception as e:
            logger.error(f"Error rotating pages: {str(e)}")
            raise Exception(f"Failed to rotate pages: {str(e)}")
    
    def _rotate_pages_sync(self, input_path: Path, output_path: Path, pages: List[int], rotation: int):
        """Synchronous page rotation using PyPDF2"""
        from pypdf import PdfReader, PdfWriter
        
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        
        for i, page in enumerate(reader.pages):
            page_num = i + 1  # Convert to 1-based
            if page_num in pages:
                page.rotate(rotation)
            writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
    
    async def _add_watermark(self, input_files: List[PDFFileInfo], parameters: Dict[str, Any], session_id: str) -> PDFFileInfo:
        """Add watermark to PDF using reportlab and PyPDF2."""
        if not input_files:
            raise ValueError("No input files provided")
        
        input_file = input_files[0]
        watermark_text = parameters.get('watermark_text', 'WATERMARK')
        output_name = parameters.get('output_name', f"watermarked_{input_file.name}")
        
        if not output_name.endswith('.pdf'):
            output_name += '.pdf'
        
        input_path = Path(input_file.file_path)
        output_path = Path(self.temp_dir) / f"{session_id}_{output_name}"
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._add_watermark_sync,
                input_path,
                output_path,
                watermark_text
            )
            
            file_size = output_path.stat().st_size if output_path.exists() else input_file.file_size
            
            result_file = PDFFileInfo(
                id=str(uuid.uuid4()),
                name=output_name,
                original_filename=output_name,
                file_path=str(output_path),
                file_size=file_size,
                page_count=input_file.page_count,
                created_at=datetime.now().isoformat(),
                is_temporary=True
            )
            
            logger.info(f"Successfully added watermark '{watermark_text}' to {input_file.name}")
            return result_file
            
        except Exception as e:
            logger.error(f"Error adding watermark: {str(e)}")
            raise Exception(f"Failed to add watermark: {str(e)}")
    
    def _add_watermark_sync(self, input_path: Path, output_path: Path, watermark_text: str):
        """Synchronous watermark addition using reportlab and PyPDF2"""
        from pypdf import PdfReader, PdfWriter
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        # Create watermark PDF in memory
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 50)
        can.setFillAlpha(0.3)  # Make it semi-transparent
        can.rotate(45)  # Diagonal watermark
        can.drawString(100, 100, watermark_text)
        can.save()
        
        # Move to the beginning of the StringIO buffer
        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        watermark_page = watermark_pdf.pages[0]
        
        # Read the input PDF
        reader = PdfReader(str(input_path))
        writer = PdfWriter()
        
        # Add watermark to each page
        for page in reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        # Write the output PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
    
    async def _compress_pdf(self, input_files: List[PDFFileInfo], parameters: Dict[str, Any], session_id: str) -> PDFFileInfo:
        """Compress PDF file using pdfly."""
        if not input_files:
            raise ValueError("No input files provided")
        
        input_file = input_files[0]
        output_name = parameters.get('output_name', f"compressed_{input_file.name}")
        if not output_name.endswith('.pdf'):
            output_name += '.pdf'
        
        input_path = Path(input_file.file_path)
        output_path = Path(self.temp_dir) / f"{session_id}_{output_name}"
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        try:
            # Use pdfly compress
            await asyncio.get_event_loop().run_in_executor(
                None,
                compress.main,
                input_path,
                output_path
            )
            
            # Get file sizes for comparison
            original_size = input_file.file_size
            compressed_size = output_path.stat().st_size if output_path.exists() else original_size
            
            result_file = PDFFileInfo(
                id=str(uuid.uuid4()),
                name=output_name,
                original_filename=output_name,
                file_path=str(output_path),
                file_size=compressed_size,
                page_count=input_file.page_count,
                created_at=datetime.now().isoformat(),
                is_temporary=True
            )
            
            # Calculate compression ratio
            compression_ratio = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0
            logger.info(f"Successfully compressed {input_file.name}, reduced by {compression_ratio:.1f}%")
            
            return result_file
            
        except Exception as e:
            logger.error(f"Error compressing PDF: {str(e)}")
            raise Exception(f"Failed to compress PDF: {str(e)}")