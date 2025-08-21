from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Document, Text
from ai_service import ai_assistant
from document_processor import document_processor
from subscription_middleware import subscription_required, api_subscription_required
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
@subscription_required
def dashboard():
    # Get user's documents and texts
    user_documents = Document.query.filter_by(user_id=current_user.id).all()
    user_texts = Text.query.filter_by(user_id=current_user.id).order_by(Text.updated_at.desc()).all()
    return render_template('dashboard.html', user=current_user, documents=user_documents, texts=user_texts)

@main_bp.route('/api/ai-assist', methods=['POST'])
@login_required
@api_subscription_required
def ai_assist():
    """Generate AI writing suggestions"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        text = data.get('text', '').strip()
        current_text_id = data.get('current_text_id', None)  # Optional: current active text ID
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Get document context based on current text
        document_context = ""
        if current_text_id:
            # Get documents associated with current text
            current_text = Text.query.filter_by(
                id=current_text_id,
                user_id=current_user.id
            ).first()
            
            if current_text:
                associated_documents = current_text.documents.all()
                document_context = document_processor.get_document_context(associated_documents)
        
        # Generate suggestions
        suggestions = ai_assistant.get_suggestions(title, text, document_context)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        print(f"Error in ai_assist: {str(e)}")
        return jsonify({'error': 'Failed to generate suggestions'}), 500

@main_bp.route('/api/upload', methods=['POST'])
@login_required
@api_subscription_required
def upload_document():
    """Handle document upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        result = document_processor.process_uploaded_file(file, current_user.id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Save document info to database
        document = Document(
            user_id=current_user.id,
            filename=result['filename'],
            original_filename=result['original_filename'],
            file_type=result['file_type'],
            file_size=result['file_size'],
            content_text=result['extracted_text'],
            upload_path=result.get('file_path'),  # May be None for Cloudinary uploads
            cloudinary_public_id=result.get('cloudinary_public_id'),
            cloudinary_url=result.get('cloudinary_url'),
            cloudinary_secure_url=result.get('cloudinary_secure_url')
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'document': {
                'id': document.id,
                'filename': document.original_filename,
                'file_type': document.file_type,
                'file_size': document.file_size
            }
        })
        
    except Exception as e:
        print(f"Error in upload_document: {str(e)}")
        return jsonify({'error': 'Failed to upload document'}), 500

@main_bp.route('/api/documents/<int:document_id>', methods=['DELETE'])
@login_required
def delete_document(document_id):
    """Delete a document"""
    try:
        document = Document.query.filter_by(
            id=document_id, 
            user_id=current_user.id
        ).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Delete file from Cloudinary or disk
        document_processor.delete_file(document)
        
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error in delete_document: {str(e)}")
        return jsonify({'error': 'Failed to delete document'}), 500

# Text CRUD Routes
@main_bp.route('/api/texts', methods=['GET'])
@login_required
def get_texts():
    """Get all texts for the current user"""
    try:
        texts = Text.query.filter_by(user_id=current_user.id).order_by(Text.updated_at.desc()).all()
        
        texts_data = []
        for text in texts:
            texts_data.append({
                'id': text.id,
                'title': text.title,
                'content': text.content,
                'created_at': text.created_at.isoformat(),
                'updated_at': text.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'texts': texts_data
        })
        
    except Exception as e:
        print(f"Error in get_texts: {str(e)}")
        return jsonify({'error': 'Failed to fetch texts'}), 500

@main_bp.route('/api/texts', methods=['POST'])
@login_required
@api_subscription_required
def create_text():
    """Create a new text"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Create new text
        text = Text(
            user_id=current_user.id,
            title=title,
            content=content
        )
        
        db.session.add(text)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'text': {
                'id': text.id,
                'title': text.title,
                'content': text.content,
                'created_at': text.created_at.isoformat(),
                'updated_at': text.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"Error in create_text: {str(e)}")
        return jsonify({'error': 'Failed to create text'}), 500

@main_bp.route('/api/texts/<int:text_id>', methods=['GET'])
@login_required
def get_text(text_id):
    """Get a specific text"""
    try:
        text = Text.query.filter_by(
            id=text_id,
            user_id=current_user.id
        ).first()
        
        if not text:
            return jsonify({'error': 'Text not found'}), 404
        
        return jsonify({
            'success': True,
            'text': {
                'id': text.id,
                'title': text.title,
                'content': text.content,
                'created_at': text.created_at.isoformat(),
                'updated_at': text.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"Error in get_text: {str(e)}")
        return jsonify({'error': 'Failed to fetch text'}), 500

@main_bp.route('/api/texts/<int:text_id>', methods=['PUT'])
@login_required
def update_text(text_id):
    """Update a text"""
    try:
        text = Text.query.filter_by(
            id=text_id,
            user_id=current_user.id
        ).first()
        
        if not text:
            return jsonify({'error': 'Text not found'}), 404
        
        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Update text
        text.title = title
        text.content = content
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'text': {
                'id': text.id,
                'title': text.title,
                'content': text.content,
                'created_at': text.created_at.isoformat(),
                'updated_at': text.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        print(f"Error in update_text: {str(e)}")
        return jsonify({'error': 'Failed to update text'}), 500

@main_bp.route('/api/texts/<int:text_id>', methods=['DELETE'])
@login_required
def delete_text(text_id):
    """Delete a text"""
    try:
        text = Text.query.filter_by(
            id=text_id,
            user_id=current_user.id
        ).first()
        
        if not text:
            return jsonify({'error': 'Text not found'}), 404
        
        db.session.delete(text)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error in delete_text: {str(e)}")
        return jsonify({'error': 'Failed to delete text'}), 500

# Text-Document Association Routes
@main_bp.route('/api/texts/<int:text_id>/documents', methods=['GET'])
@login_required
def get_text_documents(text_id):
    """Get all documents associated with a specific text"""
    try:
        # Verify text belongs to current user
        text = Text.query.filter_by(
            id=text_id,
            user_id=current_user.id
        ).first()
        
        if not text:
            return jsonify({'error': 'Text not found'}), 404
        
        # Get associated documents
        documents = text.documents.all()
        
        documents_data = []
        for doc in documents:
            documents_data.append({
                'id': doc.id,
                'filename': doc.original_filename,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'created_at': doc.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'documents': documents_data
        })
        
    except Exception as e:
        print(f"Error in get_text_documents: {str(e)}")
        return jsonify({'error': 'Failed to fetch text documents'}), 500

@main_bp.route('/api/texts/<int:text_id>/documents/<int:document_id>', methods=['POST'])
@login_required
def associate_document_to_text(text_id, document_id):
    """Associate a document with a text"""
    try:
        # Verify text belongs to current user
        text = Text.query.filter_by(
            id=text_id,
            user_id=current_user.id
        ).first()
        
        if not text:
            return jsonify({'error': 'Text not found'}), 404
        
        # Verify document belongs to current user
        document = Document.query.filter_by(
            id=document_id,
            user_id=current_user.id
        ).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Check if already associated
        if document in text.documents:
            return jsonify({'error': 'Document already associated with this text'}), 400
        
        # Associate document with text
        text.documents.append(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document associated successfully'
        })
        
    except Exception as e:
        print(f"Error in associate_document_to_text: {str(e)}")
        return jsonify({'error': 'Failed to associate document'}), 500

@main_bp.route('/api/texts/<int:text_id>/documents/<int:document_id>', methods=['DELETE'])
@login_required
def disassociate_document_from_text(text_id, document_id):
    """Remove association between a document and a text"""
    try:
        # Verify text belongs to current user
        text = Text.query.filter_by(
            id=text_id,
            user_id=current_user.id
        ).first()
        
        if not text:
            return jsonify({'error': 'Text not found'}), 404
        
        # Verify document belongs to current user
        document = Document.query.filter_by(
            id=document_id,
            user_id=current_user.id
        ).first()
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        # Check if document is associated
        if document not in text.documents:
            return jsonify({'error': 'Document not associated with this text'}), 400
        
        # Remove association
        text.documents.remove(document)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Document disassociated successfully'
        })
        
    except Exception as e:
        print(f"Error in disassociate_document_from_text: {str(e)}")
        return jsonify({'error': 'Failed to disassociate document'}), 500

@main_bp.route('/api/texts/<int:text_id>/available-documents', methods=['GET'])
@login_required
def get_available_documents_for_text(text_id):
    """Get all user's documents that are not yet associated with the text"""
    try:
        # Verify text belongs to current user
        text = Text.query.filter_by(
            id=text_id,
            user_id=current_user.id
        ).first()
        
        if not text:
            return jsonify({'error': 'Text not found'}), 404
        
        # Get all user's documents
        all_documents = Document.query.filter_by(user_id=current_user.id).all()
        
        # Get documents already associated with this text
        associated_document_ids = [doc.id for doc in text.documents.all()]
        
        # Filter out already associated documents
        available_documents = [doc for doc in all_documents if doc.id not in associated_document_ids]
        
        documents_data = []
        for doc in available_documents:
            documents_data.append({
                'id': doc.id,
                'filename': doc.original_filename,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'created_at': doc.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'documents': documents_data
        })
        
    except Exception as e:
        print(f"Error in get_available_documents_for_text: {str(e)}")
        return jsonify({'error': 'Failed to fetch available documents'}), 500