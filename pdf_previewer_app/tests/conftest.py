import os
import tempfile
import pytest
import sqlite3
import shutil

# To make sure the app and database modules are found
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app # The Flask app instance from app.py
from database import init_db as initialize_db_schema, DATABASE_PATH as APP_DB_PATH
# Import the actual database module to patch its DATABASE_PATH
import database as app_database_module


@pytest.fixture(scope='function') # Use 'function' scope for isolation
def app(monkeypatch):
    """Create and configure a new app instance for each test."""
    
    # Create a temporary directory for uploads
    temp_upload_dir = tempfile.mkdtemp()
    
    # Create a temporary database file
    db_fd, temp_db_path = tempfile.mkstemp(suffix='.sqlite3')
    os.close(db_fd) # Close the file descriptor

    # --- Patching ---
    # Patch the DATABASE_PATH in the 'database' module
    monkeypatch.setattr(app_database_module, 'DATABASE_PATH', temp_db_path)
    # Patch the UPLOAD_FOLDER in the 'app' module (flask_app instance)
    flask_app.config['UPLOAD_FOLDER'] = temp_upload_dir
    # Patch the DATABASE path in the app's config as well
    flask_app.config['DATABASE'] = temp_db_path
    # Set app to testing mode
    flask_app.config['TESTING'] = True
    # Optional: Lower MAX_CONTENT_LENGTH for specific tests, but can be default
    # flask_app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 # 1 MB for testing

    # Initialize the temporary database with the schema
    # Ensure this init_db uses the patched DATABASE_PATH
    initialize_db_schema()

    yield flask_app

    # --- Teardown ---
    # Remove the temporary database file
    os.unlink(temp_db_path)
    # Remove the temporary upload directory and its contents
    shutil.rmtree(temp_upload_dir)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def db_conn(app):
    """A direct database connection to the test database."""
    # The DATABASE_PATH in app_database_module is already patched by the 'app' fixture
    conn = sqlite3.connect(app_database_module.DATABASE_PATH)
    conn.row_factory = sqlite3.Row # Optional: for accessing columns by name
    yield conn
    conn.close()
