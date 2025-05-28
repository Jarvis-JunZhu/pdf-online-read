# PDF Online Previewer

## Description
PDF Online Previewer is a web application that allows users to upload, list, and view PDF files directly in their browser. It provides a simple interface for managing PDF documents online without requiring any desktop software.

## Features
*   **PDF File Upload:** Securely upload PDF files with server-side validation for file type (only `.pdf` allowed) and size (up to 50MB).
*   **PDF Listing:** View a paginated and sortable list of all uploaded PDF files. Sorting options include filename, upload date, and file size.
*   **Online PDF Viewer:** Read PDF content directly in the browser using the integrated PDF.js library, which offers controls for navigation and zoom.
*   **Backend Unit Tests:** Comprehensive unit tests for backend logic (database operations and API endpoints) using pytest.

## Technology Stack
*   **Backend:**
    *   Language: Python 3.8+
    *   Framework: Flask
    *   Database: SQLite
*   **Frontend:**
    *   Markup/Styling: HTML5, CSS3
    *   JavaScript: Plain JavaScript (ES6+)
    *   PDF Viewing: PDF.js (by Mozilla)
*   **Testing:**
    *   pytest

## Prerequisites
*   Python 3.8 or newer.
*   `pip` (Python package installer), which usually comes with Python.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd pdf-online-read 
    ```
    (Replace `<repository_url>` with the actual URL of your repository, e.g., the one you are currently working in.)

2.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.

    *   Create the environment (e.g., named `venv`):
        ```bash
        python -m venv venv
        ```
    *   Activate the environment:
        *   On Linux/macOS:
            ```bash
            source venv/bin/activate
            ```
        *   On Windows:
            ```bash
            venv\Scripts\activate
            ```

3.  **Install Dependencies:**
    Navigate to the application directory and install all required Python packages.
    ```bash
    pip install -r pdf_previewer_app/requirements.txt
    ```

4.  **Initialize the Database:**
    The application uses an SQLite database. To set it up for the first time, run the following commands from the project root directory (`pdf-online-read`):
    ```bash
    cd pdf_previewer_app
    flask init-db
    cd .. 
    ```
    (This creates the `pdf_metadata.sqlite3` file within the `pdf_previewer_app` directory.)

## Running the Application

1.  **Navigate to the Application Directory:**
    Ensure your terminal is in the `pdf_previewer_app` directory (if you are in the project root `pdf-online-read`, `cd pdf_previewer_app`):
    ```bash
    cd pdf_previewer_app
    ```

2.  **Start the Flask Development Server:**
    ```bash
    flask run
    ```

3.  **Access the Application:**
    Open your web browser and go to:
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

    You should see the PDF uploader page.

## Running Tests
The project includes a suite of backend unit tests using `pytest`.

*   **From the `pdf_previewer_app` directory:**
    Ensure your virtual environment is activated and you are in the `pdf_previewer_app` directory.
    ```bash
    python -m pytest
    ```
    or simply:
    ```bash
    pytest
    ```

*   **From the project root directory (`pdf-online-read`):**
    ```bash
    pytest pdf_previewer_app/tests/
    ```

## API Endpoints (Brief Summary)

The application exposes the following RESTful API endpoints:

*   `POST /api/upload`
    *   Uploads a PDF file.
    *   Expects `multipart/form-data` with a file part named `pdf_file`.
*   `GET /api/pdfs`
    *   Lists uploaded PDF files.
    *   Supports query parameters for pagination (`page`, `limit`) and sorting (`sort_by`).
*   `GET /api/pdfs/<id>`
    *   Serves a specific PDF file for viewing or download.
    *   Replace `<id>` with the numerical ID of the PDF.

## Project Structure

```
pdf-online-read/
├── pdf_previewer_app/
│   ├── static/             # Frontend assets (HTML, CSS, JS, PDF.js library)
│   │   ├── css/            # Stylesheets (style.css)
│   │   ├── js/             # JavaScript files (upload.js, list.js, viewer.js)
│   │   └── lib/pdfjs/      # PDF.js library files (gitignored)
│   ├── templates/          # (Currently not used for pages, static serving instead)
│   ├── tests/              # Backend unit tests
│   │   ├── conftest.py     # Pytest fixtures and configuration
│   │   ├── test_app.py     # Tests for Flask app routes
│   │   └── test_database.py# Tests for database functions
│   ├── uploads/pdfs/       # Storage for uploaded PDF files (gitignored)
│   ├── app.py              # Main Flask application logic and routes
│   ├── database.py         # Database interaction logic (SQLite)
│   ├── requirements.txt    # Python dependencies for the backend
│   └── pdf_metadata.sqlite3 # SQLite database file (gitignored)
├── .gitignore              # Specifies intentionally untracked files
├── README.md               # This file: project overview and instructions
├── requirements_document.md # Detailed project requirements
└── system_design_document.md  # System architecture and design details
```

This structure separates the backend Flask application (`pdf_previewer_app`) from project-level documentation files. Static frontend assets are served from the `static` directory, and uploaded PDFs are stored in `uploads/pdfs`. The PDF.js library, database file, and uploads directory are gitignored.
