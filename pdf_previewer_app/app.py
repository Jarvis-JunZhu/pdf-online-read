import os
import uuid
import math
from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from database import init_db, add_pdf_metadata, get_pdfs_list, get_pdf_details, DATABASE_PATH

# --- Configuration ---
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads', 'pdfs')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

# --- App Initialization ---
app = Flask(__name__, static_folder='static') # Ensure static_folder is set if not default
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['DATABASE'] = DATABASE_PATH # For reference, though database.py handles its own path

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Helper Functions ---
def allowed_file(filename):
    """Checks if the filename has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- API Endpoints ---
@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    """
    Handles PDF file uploads. Validates the file, saves it, 
    and records its metadata in the database.
    """
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['pdf_file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file: # Check if the file object itself is valid
        return jsonify({"error": "Invalid file object"}), 400

    original_filename_secured = secure_filename(file.filename)

    if not allowed_file(original_filename_secured):
        return jsonify({"error": "Invalid file type. Only PDF files are allowed."}), 400
    
    # Further MIME type check (more reliable than extension alone)
    if file.mimetype != 'application/pdf':
         # Allow if extension is .pdf but mimetype is application/octet-stream as some browsers/systems might set it this way
        if not (original_filename_secured.lower().endswith('.pdf') and file.mimetype == 'application/octet-stream'):
            return jsonify({"error": f"Invalid MIME type: {file.mimetype}. Expected 'application/pdf'."}), 415


    try:
        # Generate a unique filename for storage
        unique_filename = uuid.uuid4().hex + ".pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the file
        file.seek(0) # Ensure we are at the beginning of the file stream
        file.save(filepath)
        
        # Get file size
        filesize = os.path.getsize(filepath)

        # Add metadata to database
        pdf_id = add_pdf_metadata(
            filename=unique_filename,
            original_filename=original_filename_secured,
            filepath=filepath, # Storing absolute path for now, can be made relative
            filesize=filesize,
            mime_type=file.mimetype
        )

        if pdf_id:
            return jsonify({
                "message": "File uploaded successfully",
                "pdf_id": pdf_id,
                "filename": original_filename_secured,
                "stored_filename": unique_filename,
                "filesize_bytes": filesize
            }), 201
        else:
            # Attempt to clean up the saved file if DB insert failed
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": "Failed to save file metadata to database."}), 500

    except Exception as e:
        # Also attempt to clean up if any other error occurs during save/db interaction
        # filepath might not be defined if error is before that point
        current_filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename if 'unique_filename' in locals() else '')
        if 'unique_filename' in locals() and os.path.exists(current_filepath):
             os.remove(current_filepath)
        app.logger.error(f"Error during file upload: {e}")
        return jsonify({"error": f"An unexpected error occurred during file upload: {str(e)}"}), 500


@app.route('/api/pdfs', methods=['GET'])
def list_pdfs():
    """
    Retrieves a paginated and sorted list of uploaded PDF files.
    """
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        sort_by = request.args.get('sort_by', 'upload_timestamp_desc', type=str)
    except ValueError:
        return jsonify({"error": "Invalid query parameter type. 'page' and 'limit' must be integers."}), 400

    if page < 1:
        page = 1
    if limit < 1:
        limit = 1
    # Max limit to prevent abuse
    if limit > 100:
        limit = 100 

    valid_sort_options = [
        'filename_asc', 'filename_desc',
        'upload_timestamp_asc', 'upload_timestamp_desc',
        'filesize_asc', 'filesize_desc'
    ]
    if sort_by not in valid_sort_options:
        return jsonify({"error": f"Invalid sort_by parameter. Allowed values: {', '.join(valid_sort_options)}"}), 400

    try:
        pdfs_list, total_pdfs = get_pdfs_list(page=page, limit=limit, sort_by=sort_by)
        
        if total_pdfs == 0:
            total_pages = 0
        else:
            total_pages = math.ceil(total_pdfs / limit)

        return jsonify({
            "pdfs": pdfs_list,
            "total_pdfs": total_pdfs,
            "current_page": page,
            "total_pages": total_pages,
            "limit": limit
        }), 200
    except Exception as e:
        app.logger.error(f"Error fetching PDF list: {e}")
        return jsonify({"error": "An unexpected error occurred while fetching PDF list."}), 500


@app.route('/api/pdfs/<int:pdf_id>', methods=['GET'])
def get_pdf_file(pdf_id):
    """
    Serves a specific PDF file for viewing or downloading.
    """
    pdf_info = get_pdf_details(pdf_id)

    if not pdf_info:
        return jsonify({"error": "PDF not found in database."}), 404

    filepath = pdf_info["filepath"]
    original_filename = pdf_info["original_filename"]

    if not os.path.exists(filepath):
        app.logger.error(f"File not found on disk: {filepath} for PDF ID: {pdf_id}")
        return jsonify({"error": "PDF file not found on server."}), 404

    try:
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=False, # Opens in browser's PDF viewer if supported
            download_name=original_filename # Suggests original filename if user chooses to save
        )
    except Exception as e:
        app.logger.error(f"Error serving PDF file (ID: {pdf_id}): {e}")
        return jsonify({"error": "An error occurred while serving the PDF file."}), 500

# --- Static File Serving ---
@app.route('/')
def serve_index():
    """Serves the main HTML page for uploading files."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serves other static files like CSS, JS, other HTML pages."""
    return send_from_directory(app.static_folder, filename)


# --- CLI Commands for DB ---
@app.cli.command('init-db')
def init_db_command():
    """Initializes the database."""
    # Ensure the directory for the database exists
    db_dir = os.path.dirname(DATABASE_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created database directory: {db_dir}")
        
    init_db()
    print("Database initialized from CLI.")

if __name__ == '__main__':
    # For development:
    # 1. Run `flask init-db` in the terminal from the `pdf_previewer_app` directory.
    # 2. Then run `flask run` to start the development server.
    app.run(debug=True)
