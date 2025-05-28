import sqlite3
import os

DATABASE_NAME = 'pdf_metadata.sqlite3'
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATABASE_NAME)

def init_db():
    """Initializes the database and creates the 'pdfs' table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pdfs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,
                original_filename TEXT NOT NULL,
                filepath TEXT NOT NULL UNIQUE,
                filesize INTEGER NOT NULL,
                upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                mime_type TEXT DEFAULT 'application/pdf'
            )
        ''')
        conn.commit()
        print(f"Database initialized successfully at {DATABASE_PATH}")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

def get_pdf_details(pdf_id):
    """
    Retrieves the filepath and original_filename of a PDF by its ID.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT filepath, original_filename FROM pdfs WHERE id = ?", (pdf_id,))
        pdf_record = cursor.fetchone()
        if pdf_record:
            return {"filepath": pdf_record["filepath"], "original_filename": pdf_record["original_filename"]}
        else:
            return None
    except sqlite3.Error as e:
        print(f"Error fetching PDF details for id {pdf_id}: {e}")
        return None
    finally:
        if conn:
            conn.close()

def add_pdf_metadata(filename, original_filename, filepath, filesize, mime_type='application/pdf'):
    """Adds metadata of a newly uploaded PDF to the database."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pdfs (filename, original_filename, filepath, filesize, mime_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, original_filename, filepath, filesize, mime_type))
        conn.commit()
        return cursor.lastrowid 
    except sqlite3.Error as e:
        print(f"Error adding PDF metadata: {e}")
        return None
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # This allows initializing the DB from the command line
    print(f"Attempting to initialize database at {DATABASE_PATH}...")
    # Ensure the directory for the database exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    init_db()

def get_pdfs_list(page=1, limit=10, sort_by='upload_timestamp_desc'):
    """
    Retrieves a paginated and sorted list of PDF metadata from the database.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    # Makes the cursor return rows as dictionaries (or sqlite3.Row objects that behave like dicts)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    # Validate and map sort_by parameter to SQL
    valid_sort_options = {
        'filename_asc': 'original_filename ASC',
        'filename_desc': 'original_filename DESC',
        'upload_timestamp_asc': 'upload_timestamp ASC',
        'upload_timestamp_desc': 'upload_timestamp DESC',
        'filesize_asc': 'filesize ASC',
        'filesize_desc': 'filesize DESC',
    }
    order_by_clause = valid_sort_options.get(sort_by, 'upload_timestamp DESC') # Default sort

    offset = (page - 1) * limit

    try:
        # Query to get the list of PDFs for the current page
        query = f'''
            SELECT id, original_filename, filesize, upload_timestamp, mime_type
            FROM pdfs
            ORDER BY {order_by_clause}
            LIMIT ? OFFSET ?
        '''
        cursor.execute(query, (limit, offset))
        pdf_rows = cursor.fetchall()
        
        # Convert rows to simple dictionaries
        pdfs_list = [dict(row) for row in pdf_rows]

        # Query to get the total count of PDFs
        cursor.execute("SELECT COUNT(id) FROM pdfs")
        total_pdfs = cursor.fetchone()[0]
        
        return pdfs_list, total_pdfs
    except sqlite3.Error as e:
        print(f"Error fetching PDF list: {e}")
        return [], 0
    finally:
        if conn:
            conn.close()
