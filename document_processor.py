import os
import PyPDF2
from docx import Document as DocxDocument
from typing import Optional
import tempfile
from werkzeug.utils import secure_filename

class DocumentProcessor:
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, upload_folder: str = 'uploads'):
        self.upload_folder = upload_folder
        # Create upload folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text content from DOCX file"""
        try:
            doc = DocxDocument(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting DOCX text: {str(e)}")
            return ""
    
    def process_uploaded_file(self, file, user_id: int) -> dict:
        """
        Process uploaded file and extract text content
        
        Args:
            file: Flask uploaded file object
            user_id: ID of the user uploading the file
            
        Returns:
            Dictionary with file info and extracted text
        """
        if not file or file.filename == '':
            return {'error': 'No file selected'}
        
        if not self.is_allowed_file(file.filename):
            return {'error': 'File type not allowed. Please upload PDF or DOCX files.'}
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > self.MAX_FILE_SIZE:
            return {'error': 'File too large. Maximum size is 10MB.'}
        
        try:
            # Secure filename
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            # Create unique filename
            import uuid
            unique_filename = f"{user_id}_{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(self.upload_folder, unique_filename)
            
            # Save file
            file.save(file_path)
            
            # Extract text based on file type
            if file_extension == 'pdf':
                extracted_text = self.extract_text_from_pdf(file_path)
            elif file_extension == 'docx':
                extracted_text = self.extract_text_from_docx(file_path)
            else:
                return {'error': 'Unsupported file type'}
            
            if not extracted_text:
                # Clean up file if no text extracted
                os.remove(file_path)
                return {'error': 'Could not extract text from file'}
            
            return {
                'success': True,
                'filename': unique_filename,
                'original_filename': file.filename,
                'file_type': file_extension,
                'file_size': file_size,
                'file_path': file_path,
                'extracted_text': extracted_text
            }
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return {'error': 'Error processing file. Please try again.'}
    
    def get_document_context(self, documents, max_length: int = 8000) -> str:
        """
        Get combined context from multiple documents, with intelligent extraction
        
        Args:
            documents: List of Document model instances
            max_length: Maximum length of combined context
            
        Returns:
            Combined text context from all documents
        """
        if not documents:
            return ""
        
        combined_text = ""
        chars_per_doc = 2000  # Increased from 500 to 2000 chars per document
        
        for doc in documents:
            if doc.content_text:
                combined_text += f"\n--- From {doc.original_filename} ---\n"
                
                # Extract intelligently: beginning + end for better context
                doc_text = doc.content_text.strip()
                if len(doc_text) <= chars_per_doc:
                    # Document is small enough, use all of it
                    combined_text += doc_text + "\n"
                else:
                    # Document is large, extract beginning and end
                    half_chars = chars_per_doc // 2
                    beginning = self._extract_complete_sentences(doc_text[:half_chars])
                    ending = self._extract_complete_sentences(doc_text[-half_chars:], from_end=True)
                    
                    combined_text += beginning
                    if beginning and ending:
                        combined_text += "\n[...document continues...]\n"
                    combined_text += ending + "\n"
        
        # Truncate to max_length if needed
        if len(combined_text) > max_length:
            combined_text = combined_text[:max_length] + "..."
        
        return combined_text.strip()
    
    def _extract_complete_sentences(self, text: str, from_end: bool = False) -> str:
        """
        Extract text while preserving complete sentences/paragraphs
        
        Args:
            text: Text to extract from
            from_end: If True, extract from the end of text
            
        Returns:
            Text with complete sentences
        """
        if not text:
            return ""
        
        # Find sentence boundaries (. ! ? followed by space/newline)
        import re
        sentence_endings = re.finditer(r'[.!?]\s+', text)
        positions = [match.end() for match in sentence_endings]
        
        if not positions:
            # No clear sentence boundaries, return as-is
            return text
        
        if from_end:
            # Find the first complete sentence from the end
            for pos in reversed(positions):
                if len(text) - pos <= len(text) * 0.8:  # Don't cut too much
                    return text[pos:].strip()
            return text  # Fallback
        else:
            # Find the last complete sentence from the beginning
            for pos in reversed(positions):
                if pos <= len(text) * 0.8:  # Don't cut too much
                    return text[:pos].strip()
            return text  # Fallback
    
    def delete_file(self, file_path: str) -> bool:
        """Delete uploaded file from disk"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

# Global instance
document_processor = DocumentProcessor()