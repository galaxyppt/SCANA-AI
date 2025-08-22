"""PDF processing module for extracting text from contract documents."""

from typing import Optional, Dict, Any
import tempfile
import os

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

class PDFProcessor:
    """Handles PDF document processing and text extraction."""
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.last_processed_file = None
        self.extracted_text = None
        if not HAS_PDFPLUMBER:
            print("Warning: pdfplumber not installed. PDF processing will be disabled.")
    
    def validate_pdf(self, file_path: str) -> bool:
        """
        Validate if the file is a valid PDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            bool: True if valid PDF, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                # Check PDF signature
                signature = f.read(4)
                return signature == b'%PDF'
        except Exception:
            return False
    
    def extract_text(self, pdf_file: Any) -> Optional[str]:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_file: File object or path to PDF file
            
        Returns:
            str: Extracted text from PDF or None if extraction fails
        """
        if not HAS_PDFPLUMBER:
            print("Error: pdfplumber not installed. Cannot process PDF files.")
            return None
            
        try:
            # If input is a file object, save it temporarily
            if hasattr(pdf_file, 'read'):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(pdf_file.read())
                    tmp_file_path = tmp_file.name
            else:
                tmp_file_path = pdf_file
            
            # Validate PDF first
            if not self.validate_pdf(tmp_file_path):
                print("Error: Invalid PDF file")
                return None
            
            text = []
            with pdfplumber.open(tmp_file_path) as pdf:
                if len(pdf.pages) == 0:
                    print("Warning: PDF has no pages")
                    return None
                    
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text.append(extracted)
            
            # Clean up temporary file if created
            if hasattr(pdf_file, 'read'):
                os.unlink(tmp_file_path)
            
            if not text:
                print("Warning: No text extracted from PDF")
                return None
                
            self.extracted_text = '\n\n'.join(text)
            return self.extracted_text
            
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return None
    
    def get_document_metadata(self, pdf_file: Any) -> Dict[str, Any]:
        """
        Extract metadata from PDF file.
        
        Args:
            pdf_file: File object or path to PDF file
            
        Returns:
            dict: Document metadata
        """
        if not HAS_PDFPLUMBER:
            print("Error: pdfplumber not installed. Cannot process PDF files.")
            return {}
            
        try:
            # If input is a file object, save it temporarily
            if hasattr(pdf_file, 'read'):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(pdf_file.read())
                    tmp_file_path = tmp_file.name
            else:
                tmp_file_path = pdf_file
            
            # Validate PDF first
            if not self.validate_pdf(tmp_file_path):
                print("Error: Invalid PDF file")
                return {}
            
            with pdfplumber.open(tmp_file_path) as pdf:
                metadata = {
                    'pages': len(pdf.pages),
                    'metadata': pdf.metadata or {}
                }
            
            # Clean up temporary file if created
            if hasattr(pdf_file, 'read'):
                os.unlink(tmp_file_path)
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting metadata from PDF: {str(e)}")
            return {} 