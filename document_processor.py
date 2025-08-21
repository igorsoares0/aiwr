import os
import PyPDF2
from docx import Document as DocxDocument
from typing import Optional
import tempfile
import uuid
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader

class DocumentProcessor:
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, upload_folder: str = 'uploads'):
        self.upload_folder = upload_folder
        # Create upload folder if it doesn't exist (for temp files)
        os.makedirs(upload_folder, exist_ok=True)
        
    def _configure_cloudinary(self):
        """Configure Cloudinary with app settings"""
        try:
            from flask import current_app
            if hasattr(current_app, 'config'):
                cloud_name = current_app.config.get('CLOUDINARY_CLOUD_NAME')
                api_key = current_app.config.get('CLOUDINARY_API_KEY')
                api_secret = current_app.config.get('CLOUDINARY_API_SECRET')
                
                if not all([cloud_name, api_key, api_secret]):
                    return False
                
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret
                )
                return True
        except RuntimeError:
            # Outside application context, skip configuration
            pass
        return False
    
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
        Process uploaded file, extract text content, and upload to Cloudinary
        
        Args:
            file: Flask uploaded file object
            user_id: ID of the user uploading the file
            
        Returns:
            Dictionary with file info, extracted text, and Cloudinary URLs
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
        
        temp_file_path = None
        
        try:
            # Configure Cloudinary
            cloudinary_configured = self._configure_cloudinary()
            
            # Secure filename
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            # Create unique filename
            unique_filename = f"{user_id}_{uuid.uuid4().hex}_{filename}"
            
            # Save to temporary file for text extraction
            temp_file_path = os.path.join(self.upload_folder, f"temp_{unique_filename}")
            file.save(temp_file_path)
            
            # Extract text based on file type
            if file_extension == 'pdf':
                extracted_text = self.extract_text_from_pdf(temp_file_path)
            elif file_extension == 'docx':
                extracted_text = self.extract_text_from_docx(temp_file_path)
            else:
                return {'error': 'Unsupported file type'}
            
            if not extracted_text:
                return {'error': 'Could not extract text from file'}
            
            
            # Upload to Cloudinary only if configured
            if cloudinary_configured:
                cloudinary_result = self._upload_to_cloudinary(
                    temp_file_path, 
                    user_id, 
                    unique_filename, 
                    file_extension
                )
                
                if 'error' in cloudinary_result:
                    # Fallback to local storage
                    local_file_path = os.path.join(self.upload_folder, unique_filename)
                    os.rename(temp_file_path, local_file_path)
                    temp_file_path = None  # Don't delete in finally block
                    
                    return {
                        'success': True,
                        'filename': unique_filename,
                        'original_filename': file.filename,
                        'file_type': file_extension,
                        'file_size': file_size,
                        'file_path': local_file_path,
                        'extracted_text': extracted_text
                    }
            else:
                # Use local storage
                local_file_path = os.path.join(self.upload_folder, unique_filename)
                os.rename(temp_file_path, local_file_path)
                temp_file_path = None  # Don't delete in finally block
                
                return {
                    'success': True,
                    'filename': unique_filename,
                    'original_filename': file.filename,
                    'file_type': file_extension,
                    'file_size': file_size,
                    'file_path': local_file_path,
                    'extracted_text': extracted_text
                }
            
            return {
                'success': True,
                'filename': unique_filename,
                'original_filename': file.filename,
                'file_type': file_extension,
                'file_size': file_size,
                'file_path': None,  # No local path anymore
                'extracted_text': extracted_text,
                'cloudinary_public_id': cloudinary_result['public_id'],
                'cloudinary_url': cloudinary_result['url'],
                'cloudinary_secure_url': cloudinary_result['secure_url']
            }
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return {'error': 'Error processing file. Please try again.'}
        
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    print(f"Warning: Could not delete temp file {temp_file_path}: {str(e)}")
    
    def get_document_context(self, documents, max_length: int = 5000) -> str:
        """
        Get combined context from multiple documents, with intelligent extraction
        
        Args:
            documents: List of Document model instances
            max_length: Maximum length of combined context (default 5000 for better AI context)
            
        Returns:
            Combined text context from all documents
        """
        if not documents:
            return ""
        
        combined_text = ""
        
        # Intelligent distribution based on number of documents
        num_docs = len(documents)
        if num_docs == 1:
            chars_per_doc = min(4500, max_length - 500)  # Reserve space for headers
        elif num_docs == 2:
            chars_per_doc = min(2200, (max_length - 200) // 2)  # Split between 2 docs
        else:
            chars_per_doc = min(1500, (max_length - 300) // num_docs)  # Distribute among all
        
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
    
    def _upload_to_cloudinary(self, file_path: str, user_id: int, filename: str, file_extension: str) -> dict:
        """
        Upload file to Cloudinary
        
        Args:
            file_path: Local file path
            user_id: User ID for folder organization
            filename: Unique filename
            file_extension: File extension
            
        Returns:
            Dictionary with Cloudinary upload result or error
        """
        try:
            # Generate public_id without extension (Cloudinary adds it)
            public_id = f"documents/{user_id}/{filename.rsplit('.', 1)[0]}"
            
            upload_result = cloudinary.uploader.upload(
                file_path,
                resource_type="raw",  # For non-image files
                public_id=public_id,
                tags=[f"user:{user_id}", f"type:{file_extension}"],
                overwrite=False
            )
            
            
            return {
                'public_id': upload_result['public_id'],
                'url': upload_result['url'],
                'secure_url': upload_result['secure_url']
            }
            
        except Exception as e:
            print(f"Error uploading to Cloudinary: {str(e)}")
            return {'error': 'Failed to upload file to cloud storage'}
    
    def delete_file(self, document_model) -> bool:
        """
        Delete file from Cloudinary or local storage
        
        Args:
            document_model: Document model instance with file info
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # If stored in Cloudinary, delete from there
            if hasattr(document_model, 'is_cloudinary_stored') and document_model.is_cloudinary_stored:
                self._configure_cloudinary()
                result = cloudinary.uploader.destroy(
                    document_model.cloudinary_public_id,
                    resource_type="raw"
                )
                return result.get('result') == 'ok'
            
            # Fallback: delete local file
            elif document_model.upload_path and os.path.exists(document_model.upload_path):
                os.remove(document_model.upload_path)
                return True
                
            return False
            
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False

# Global instance
document_processor = DocumentProcessor()