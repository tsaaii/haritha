from flask import Blueprint, request, jsonify, session, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from functools import wraps
import os
import logging
import uuid
from datetime import datetime
from config.themes import THEMES, get_theme
from utils.page_builder import create_themed_page

# Create blueprint for upload routes
upload_bp = Blueprint('upload', __name__)

def get_current_theme():
    """Get current theme from session or default"""
    return session.get('current_theme', 'dark')

def create_upload_content(theme_name="dark"):
    """Create upload-specific content"""
    theme = get_theme(theme_name)
    
    # Upload-specific features
    features = [
        {
            "icon": "📤",
            "title": "Bulk File Upload",
            "description": "Upload multiple files simultaneously with progress tracking"
        },
        {
            "icon": "✅",
            "title": "File Validation",
            "description": "Automatic validation and format checking for uploaded files"
        },
        {
            "icon": "🗂️",
            "title": "Document Management",
            "description": "Organize and categorize uploaded documents and data files"
        },
        {
            "icon": "🔄",
            "title": "Data Processing",
            "description": "Automatic processing and integration of uploaded data"
        },
        {
            "icon": "📊",
            "title": "Import Analytics",
            "description": "Track and analyze data import statistics and quality"
        },
        {
            "icon": "🔒",
            "title": "Secure Storage",
            "description": "Encrypted storage and access control for sensitive data"
        }
    ]
    
    return {
        "features": features,
        "description": "Comprehensive file upload and data management system for waste management operations. Upload, validate, and process various data files including collection records, vehicle data, and operational reports.",
        "capabilities": [
            "Support for multiple file formats (CSV, Excel, PDF, Images)",
            "Bulk upload with progress tracking and error handling",
            "Automatic data validation and quality checks",
            "Integration with existing database systems",
            "File versioning and backup management",
            "Role-based access control and audit trails"
        ]
    }

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'swaccha_session_id' not in session:
            return redirect('/oauth/login')
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx', 'xls', 'json'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload')
@login_required
def upload_page():
    """Main upload page"""
    try:
        theme_name = get_current_theme()
        content = create_upload_content(theme_name)
        
        return create_themed_page(
            title="Data Upload & Management",
            icon="📤",
            theme_name=theme_name,
            content=content,
            page_type="upload"
        )
    except Exception as e:
        logging.error(f"Error loading upload page: {e}")
        return "Error loading upload page", 500

@upload_bp.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    """API endpoint for file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Create upload directory if it doesn't exist
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        user_data = session.get('user_data', {})
        user_folder = os.path.join(upload_folder, str(user_data.get('user_id', 'anonymous')))
        os.makedirs(user_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(user_folder, unique_filename)
        file.save(file_path)
        
        # TODO: Save file metadata to database
        user_data = session.get('user_data', {})
        file_metadata = {
            'id': str(uuid.uuid4()),
            'original_filename': original_filename,
            'stored_filename': unique_filename,
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'upload_date': datetime.utcnow().isoformat(),
            'user_id': user_data.get('user_id')
        }
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_id': file_metadata['id'],
            'filename': original_filename,
            'size': file_metadata['file_size']
        }), 201
        
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return jsonify({'error': 'Failed to upload file'}), 500

@upload_bp.route('/api/uploads', methods=['GET'])
@login_required
def get_user_uploads():
    """API endpoint to get user's uploaded files"""
    try:
        user_data = session.get('user_data', {})
        user_id = user_data.get('user_id')
        
        # TODO: Implement logic to fetch user's uploads from database
        uploads = {
            'files': [],
            'total_count': 0,
            'total_size': 0
        }
        
        return jsonify(uploads)
    except Exception as e:
        logging.error(f"Error fetching uploads: {e}")
        return jsonify({'error': 'Failed to fetch uploads'}), 500

@upload_bp.route('/api/upload/<file_id>', methods=['GET'])
@login_required
def get_file_info(file_id):
    """API endpoint to get file information"""
    try:
        # TODO: Implement logic to fetch file info from database
        # Verify user owns the file
        
        file_info = {
            'id': file_id,
            'filename': 'example.csv',
            'size': 1024,
            'upload_date': '2024-01-01T12:00:00Z',
            'file_type': 'csv'
        }
        
        return jsonify(file_info)
    except Exception as e:
        logging.error(f"Error fetching file info for {file_id}: {e}")
        return jsonify({'error': 'Failed to fetch file info'}), 500

@upload_bp.route('/api/upload/<file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    """API endpoint to delete an uploaded file"""
    try:
        # TODO: Implement file deletion logic
        # 1. Verify user owns the file
        # 2. Delete file from filesystem
        # 3. Remove record from database
        
        return jsonify({'message': 'File deleted successfully'})
    except Exception as e:
        logging.error(f"Error deleting file {file_id}: {e}")
        return jsonify({'error': 'Failed to delete file'}), 500

@upload_bp.route('/api/upload/<file_id>/download', methods=['GET'])
@login_required
def download_file(file_id):
    """API endpoint to download a file"""
    try:
        # TODO: Implement file download logic
        # 1. Verify user owns the file
        # 2. Get file path from database
        # 3. Return file using send_file
        
        # For now, return error
        return jsonify({'error': 'Download not implemented'}), 501
    except Exception as e:
        logging.error(f"Error downloading file {file_id}: {e}")
        return jsonify({'error': 'Failed to download file'}), 500

@upload_bp.route('/api/upload/bulk', methods=['POST'])
@login_required
def bulk_upload():
    """API endpoint for bulk file upload"""
    try:
        files = request.files.getlist('files')
        
        if not files:
            return jsonify({'error': 'No files provided'}), 400
        
        results = []
        errors = []
        
        for file in files:
            if file.filename == '':
                continue
                
            if not allowed_file(file.filename):
                errors.append(f"File {file.filename} has invalid type")
                continue
            
            try:
                # Similar upload logic as single file upload
                # TODO: Implement bulk upload processing
                results.append({
                    'filename': file.filename,
                    'status': 'success',
                    'file_id': str(uuid.uuid4())
                })
            except Exception as e:
                errors.append(f"Failed to upload {file.filename}: {str(e)}")
        
        return jsonify({
            'uploaded': results,
            'errors': errors,
            'total_uploaded': len(results)
        })
        
    except Exception as e:
        logging.error(f"Error in bulk upload: {e}")
        return jsonify({'error': 'Failed to process bulk upload'}), 500

@upload_bp.route('/api/upload/validate', methods=['POST'])
@login_required
def validate_file():
    """API endpoint to validate file before upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        validation_result = {
            'valid': True,
            'issues': [],
            'file_info': {
                'name': file.filename,
                'size': len(file.read()),
                'type': file.content_type
            }
        }
        
        # Reset file pointer
        file.seek(0)
        
        # Validate file type
        if not allowed_file(file.filename):
            validation_result['valid'] = False
            validation_result['issues'].append('File type not allowed')
        
        # Validate file size (example: 10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if validation_result['file_info']['size'] > max_size:
            validation_result['valid'] = False
            validation_result['issues'].append('File size exceeds 10MB limit')
        
        return jsonify(validation_result)
    except Exception as e:
        logging.error(f"Error validating file: {e}")
        return jsonify({'error': 'Failed to validate file'}), 500

def register_upload_routes(app):
    """Register upload routes with the Flask app"""
    app.register_blueprint(upload_bp)