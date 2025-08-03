from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Document
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
    # Get user's documents
    user_documents = Document.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', user=current_user, documents=user_documents)

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