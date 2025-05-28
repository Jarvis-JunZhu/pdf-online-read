import pytest
import sqlite3
import time # For varying timestamps
import os

# Add project root to sys.path for imports if tests are run directly
# This is already handled by conftest.py's sys.path.insert for pytest runs
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import (
    add_pdf_metadata,
    get_pdfs_list,
    get_pdf_details,
    init_db # init_db is called by the app fixture in conftest
)

# Test data
PDF_RECORDS_DATA = [
    {"filename": "test1.pdf", "original_filename": "Alpha.pdf", "filepath": "/uploads/test1.pdf", "filesize": 1000, "mime_type": "application/pdf"},
    {"filename": "test2.pdf", "original_filename": "Beta.pdf", "filepath": "/uploads/test2.pdf", "filesize": 2000, "mime_type": "application/pdf"},
    {"filename": "test3.pdf", "original_filename": "Gamma.pdf", "filepath": "/uploads/test3.pdf", "filesize": 500, "mime_type": "application/pdf"},
]

@pytest.fixture(autouse=True)
def ensure_schema(app):
    """
    This fixture ensures that for every test in this module,
    the database schema is initialized. It relies on the 'app' fixture
    from conftest.py which handles the db initialization with a temp db.
    """
    pass # The 'app' fixture already calls init_db()

def test_init_db_creates_table(db_conn):
    """Test if the 'pdfs' table is created by init_db."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pdfs';")
    table = cursor.fetchone()
    assert table is not None, "The 'pdfs' table should exist after init_db."
    assert table['name'] == 'pdfs', "Table name should be 'pdfs'."

def test_add_pdf_metadata_success(db_conn):
    """Test successful addition of PDF metadata."""
    pdf_id = add_pdf_metadata(
        filename="unique_file.pdf",
        original_filename="My Document.pdf",
        filepath="/path/to/unique_file.pdf",
        filesize=12345
    )
    assert pdf_id is not None
    assert isinstance(pdf_id, int)

    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM pdfs WHERE id = ?", (pdf_id,))
    record = cursor.fetchone()
    assert record is not None
    assert record["filename"] == "unique_file.pdf"
    assert record["original_filename"] == "My Document.pdf"
    assert record["filepath"] == "/path/to/unique_file.pdf"
    assert record["filesize"] == 12345

def test_add_pdf_metadata_uniqueness_constraint(db_conn):
    """Test filename and filepath uniqueness constraints."""
    # Add initial record
    add_pdf_metadata(
        filename="duplicate_test.pdf",
        original_filename="Original.pdf",
        filepath="/path/to/duplicate_test.pdf",
        filesize=100
    )
    
    # Attempt to add with same filename (should fail, or return None as per current error handling)
    second_id_same_filename = add_pdf_metadata(
        filename="duplicate_test.pdf", # Same filename
        original_filename="Another.pdf",
        filepath="/path/to/another.pdf", # Different filepath
        filesize=200
    )
    assert second_id_same_filename is None, "Adding metadata with duplicate filename should fail."

    # Attempt to add with same filepath (should fail)
    third_id_same_filepath = add_pdf_metadata(
        filename="another2.pdf", # Different filename
        original_filename="Another2.pdf",
        filepath="/path/to/duplicate_test.pdf", # Same filepath
        filesize=300
    )
    assert third_id_same_filepath is None, "Adding metadata with duplicate filepath should fail."


def test_get_pdfs_list_empty(db_conn):
    """Test getting PDFs from an empty database."""
    pdfs, total_pdfs = get_pdfs_list()
    assert pdfs == []
    assert total_pdfs == 0

def test_get_pdfs_list_with_data_pagination_and_sorting(db_conn):
    """Test pagination, sorting, and data retrieval."""
    # Add initial data with slight time differences for timestamp sorting
    for i, record_data in enumerate(PDF_RECORDS_DATA):
        add_pdf_metadata(**record_data)
        time.sleep(0.01) # Ensure upload_timestamp is different for sorting tests

    # 1. Test fetching all (default limit is 10, we have 3)
    pdfs, total_pdfs = get_pdfs_list()
    assert total_pdfs == 3
    assert len(pdfs) == 3
    # Default sort is upload_timestamp_desc
    assert pdfs[0]['original_filename'] == "Gamma.pdf" 
    assert pdfs[1]['original_filename'] == "Beta.pdf"
    assert pdfs[2]['original_filename'] == "Alpha.pdf"

    # 2. Test pagination (limit 1, page 1)
    pdfs, total_pdfs = get_pdfs_list(page=1, limit=1)
    assert total_pdfs == 3
    assert len(pdfs) == 1
    assert pdfs[0]['original_filename'] == "Gamma.pdf"

    # 3. Test pagination (limit 1, page 2)
    pdfs, total_pdfs = get_pdfs_list(page=2, limit=1)
    assert len(pdfs) == 1
    assert pdfs[0]['original_filename'] == "Beta.pdf"
    
    # 4. Test sorting by filename_asc
    pdfs, _ = get_pdfs_list(sort_by='filename_asc')
    assert pdfs[0]['original_filename'] == "Alpha.pdf"
    assert pdfs[1]['original_filename'] == "Beta.pdf"
    assert pdfs[2]['original_filename'] == "Gamma.pdf"

    # 5. Test sorting by filename_desc
    pdfs, _ = get_pdfs_list(sort_by='filename_desc')
    assert pdfs[0]['original_filename'] == "Gamma.pdf"
    assert pdfs[1]['original_filename'] == "Beta.pdf"
    assert pdfs[2]['original_filename'] == "Alpha.pdf"

    # 6. Test sorting by filesize_asc
    pdfs, _ = get_pdfs_list(sort_by='filesize_asc')
    assert pdfs[0]['filesize'] == 500  # Gamma.pdf
    assert pdfs[1]['filesize'] == 1000 # Alpha.pdf
    assert pdfs[2]['filesize'] == 2000 # Beta.pdf

    # 7. Test sorting by filesize_desc
    pdfs, _ = get_pdfs_list(sort_by='filesize_desc')
    assert pdfs[0]['filesize'] == 2000 # Beta.pdf
    assert pdfs[1]['filesize'] == 1000 # Alpha.pdf
    assert pdfs[2]['filesize'] == 500  # Gamma.pdf
    
    # 8. Test sorting by upload_timestamp_asc (oldest first)
    pdfs, _ = get_pdfs_list(sort_by='upload_timestamp_asc')
    assert pdfs[0]['original_filename'] == "Alpha.pdf"
    assert pdfs[1]['original_filename'] == "Beta.pdf"
    assert pdfs[2]['original_filename'] == "Gamma.pdf"

def test_get_pdf_details_exists(db_conn):
    """Test retrieving an existing PDF's details."""
    pdf_id = add_pdf_metadata(
        filename="details_test.pdf",
        original_filename="Details Doc.pdf",
        filepath="/path/to/details_test.pdf",
        filesize=123
    )
    details = get_pdf_details(pdf_id)
    assert details is not None
    assert details['filepath'] == "/path/to/details_test.pdf"
    assert details['original_filename'] == "Details Doc.pdf"

def test_get_pdf_details_not_exists(db_conn):
    """Test retrieving a non-existent PDF's details."""
    details = get_pdf_details(99999) # Assuming this ID won't exist
    assert details is None
