from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Document, Text
from ai_service import ai_assistant
from document_processor import document_processor
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's documents and texts
    user_documents = Document.query.filter_by(user_id=current_user.id).all()
    user_texts = Text.query.filter_by(user_id=current_user.id).order_by(Text.updated_at.desc()).all()
    return render_template('dashboard.html', user=current_user, documents=user_documents, texts=user_texts)

@main_bp.route('/api/ai-assist', methods=['POST'])
@login_required
def ai_assist():
    """Generate AI writing suggestions"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        text = data.get('text', '').strip()
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Get user's documents for context
        user_documents = Document.query.filter_by(user_id=current_user.id).all()
        document_context = document_processor.get_document_context(user_documents)
        
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
            upload_path=result['file_path']
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
        
        # Delete file from disk
        document_processor.delete_file(document.upload_path)
        
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