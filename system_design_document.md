# System Design Document: PDF File Upload and Online Preview Website

## 1. Introduction

### Purpose of the document
This document outlines the system architecture, technology stack, data model, API design, and other technical aspects for the PDF File Upload and Online Preview Website. It is intended for developers, system administrators, and other technical stakeholders. It builds upon the functional and non-functional requirements specified in the `requirements_document.md`.

### System Overview
The system will allow users to upload PDF files, view a list of uploaded PDFs, and preview them directly in their web browser. The initial version will be open-access, with no user registration required. Key features include PDF upload with size and type restrictions, a sortable and paginated list of PDFs, and an embedded PDF viewer.

## 2. System Architecture

### Architectural Style
A **Client-Server architecture** will be adopted.
*   **Client (Frontend):** A web browser rendering the user interface using HTML, CSS, and JavaScript. It will interact with the backend via HTTP requests.
*   **Server (Backend):** A Python Flask application responsible for handling business logic, API requests, file operations, and database interactions.

### Components
The system will comprise the following high-level components:
*   **Frontend (Web UI):**
    *   Provides the user interface for file uploading, listing PDFs, and viewing PDFs.
    *   Built with HTML, CSS, and plain JavaScript.
    *   Integrates a PDF viewer library (PDF.js) for rendering PDFs.
*   **Backend (API Server):**
    *   A RESTful API built with Python (Flask).
    *   Handles file uploads, validation, and storage.
    *   Manages PDF metadata in the database.
    *   Serves PDF files and metadata to the frontend.
*   **File Storage:**
    *   Initially, the local file system on the server will be used to store uploaded PDF files in a designated directory.
*   **Database:**
    *   An SQLite database will store metadata about the uploaded PDF files (e.g., filename, size, upload date).

## 3. Technology Stack

### Frontend
*   **Core Technologies:** HTML5, CSS3, JavaScript (ES6+).
*   **JavaScript Framework/Library:** Plain JavaScript will be used for the initial version to maintain simplicity and minimize dependencies. For more complex UIs in the future, a framework like Vue.js or React could be considered.
*   **PDF Viewer Library:** **PDF.js** (by Mozilla) will be used for embedding the PDF viewer and rendering PDF documents in the browser.

### Backend
*   **Programming Language:** Python (version 3.8+).
*   **Framework:** **Flask**. Flask is a lightweight WSGI web application framework in Python, suitable for this project's scale and I/O-bound nature.
*   **Web Server (for deployment):** Gunicorn (or similar WSGI server) in conjunction with Nginx as a reverse proxy.

### Database
*   **Database System:** **SQLite**. It's serverless, self-contained, and easy to set up, making it ideal for this application's initial scope. For larger-scale deployments, PostgreSQL or MySQL could be considered.

### File Storage
*   **Initial Storage:** Local server file system (e.g., in a directory like `/app/uploads/`).
*   **Future Scalable Option:** Cloud storage services like AWS S3 or Google Cloud Storage could be integrated for better scalability, durability, and management of PDF files.

## 4. Data Model / Database Design

The database will be SQLite. The primary table will store metadata for the PDF files.

*   **Table: `pdfs`**

    | Column             | Data Type                     | Constraints                       | Description                                         |
    | ------------------ | ----------------------------- | --------------------------------- | --------------------------------------------------- |
    | `id`               | INTEGER                       | PRIMARY KEY AUTOINCREMENT         | Unique identifier for the PDF record.               |
    | `filename`         | TEXT                          | NOT NULL                          | Sanitized or uniquely generated name for storage.   |
    | `original_filename`| TEXT                          | NOT NULL                          | The original filename as uploaded by the user.      |
    | `filepath`         | TEXT                          | NOT NULL                          | Relative or absolute path to the stored PDF file.   |
    | `filesize`         | INTEGER                       | NOT NULL                          | File size in bytes.                                 |
    | `upload_timestamp` | DATETIME                      | DEFAULT CURRENT_TIMESTAMP         | Timestamp of when the file was uploaded.            |
    | `mime_type`        | TEXT                          | DEFAULT 'application/pdf'         | MIME type of the file.                              |

    *Example SQL for table creation:*
    ```sql
    CREATE TABLE IF NOT EXISTS pdfs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        filesize INTEGER NOT NULL,
        upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        mime_type TEXT DEFAULT 'application/pdf'
    );
    ```

## 5. API Design (RESTful)

All API endpoints will be prefixed with `/api`.

### 5.1. File Upload
*   **Endpoint:** `POST /api/upload`
*   **Description:** Uploads a new PDF file.
*   **Request:**
    *   Method: `POST`
    *   Content-Type: `multipart/form-data`
    *   Body: Contains a single file part, typically named `pdf_file`.
*   **Response (Success):**
    *   Status Code: `201 Created`
    *   Content-Type: `application/json`
    *   Body:
        ```json
        {
          "message": "File uploaded successfully",
          "pdf_id": 123,
          "filename": "MyDocument.pdf"
        }
        ```
*   **Response (Error - Invalid Input/Type/Size):**
    *   Status Code: `400 Bad Request`
    *   Content-Type: `application/json`
    *   Body:
        ```json
        {
          "error": "Invalid file type. Only PDF files are allowed."
        }
        ```
        or
        ```json
        {
          "error": "File size exceeds the 50MB limit."
        }
        ```
*   **Response (Error - Server Side):**
    *   Status Code: `500 Internal Server Error`
    *   Content-Type: `application/json`
    *   Body:
        ```json
        {
          "error": "An unexpected error occurred during file upload."
        }
        ```

### 5.2. List PDFs
*   **Endpoint:** `GET /api/pdfs`
*   **Description:** Retrieves a paginated and sortable list of uploaded PDF files.
*   **Request:**
    *   Method: `GET`
    *   Query Parameters:
        *   `page` (integer, optional, default: `1`): For pagination.
        *   `limit` (integer, optional, default: `10`): Number of items per page.
        *   `sort_by` (string, optional, default: `upload_timestamp_desc`): Sorting criteria. Examples:
            *   `filename_asc` (Filename A-Z)
            *   `filename_desc` (Filename Z-A)
            *   `upload_timestamp_asc` (Oldest first)
            *   `upload_timestamp_desc` (Newest first)
            *   `filesize_asc` (Smallest first)
            *   `filesize_desc` (Largest first)
*   **Response (Success):**
    *   Status Code: `200 OK`
    *   Content-Type: `application/json`
    *   Body:
        ```json
        {
          "pdfs": [
            { "id": 1, "original_filename": "doc1.pdf", "filesize": 102400, "upload_timestamp": "2023-10-26T10:30:00Z" },
            { "id": 2, "original_filename": "report.pdf", "filesize": 204800, "upload_timestamp": "2023-10-25T15:00:00Z" }
          ],
          "total_pdfs": 20,
          "current_page": 1,
          "total_pages": 2,
          "limit": 10
        }
        ```
*   **Response (Error):**
    *   Status Code: `400 Bad Request` (e.g., invalid sort_by parameter)
    *   Content-Type: `application/json`
    *   Body:
        ```json
        {
          "error": "Invalid sorting parameter."
        }
        ```

### 5.3. Get Specific PDF (for viewing/downloading)
*   **Endpoint:** `GET /api/pdfs/<id>`
*   **Description:** Retrieves the actual PDF file content by its ID. This endpoint will be used by the frontend PDF viewer.
*   **Request:**
    *   Method: `GET`
    *   Path Parameter: `<id>` (integer): The ID of the PDF file to retrieve.
*   **Response (Success):**
    *   Status Code: `200 OK`
    *   Content-Type: `application/pdf`
    *   Headers:
        *   `Content-Disposition: inline; filename="<original_filename>.pdf"` (Suggests browser to display inline)
        *   Or `Content-Disposition: attachment; filename="<original_filename>.pdf"` (If download is preferred)
    *   Body: The raw binary data of the PDF file.
*   **Response (Error - Not Found):**
    *   Status Code: `404 Not Found`
    *   Content-Type: `application/json`
    *   Body:
        ```json
        {
          "error": "PDF file not found."
        }
        ```

## 6. File Handling and Storage

*   **Storage Location:** Uploaded PDF files will be stored in a dedicated directory on the server, e.g., `./uploads/` (relative to the application root). This directory must be writable by the application process.
*   **Filename Generation:** To prevent filename collisions and potential security issues with user-supplied filenames:
    *   A unique filename will be generated for each stored file (e.g., using `uuid.uuid4().hex + ".pdf"`).
    *   The original filename provided by the user will be stored in the `original_filename` column of the `pdfs` table for display purposes.
*   **File Validation:**
    *   **Type Check:** The backend will verify that the uploaded file is actually a PDF. This can be done by checking the `Content-Type` header and/or using a library to inspect the file signature (magic numbers). Relying solely on file extension is not secure.
    *   **Size Check:** The backend will enforce the 50MB file size limit specified in FR5.
*   **Serving Files:** The `GET /api/pdfs/<id>` endpoint will retrieve the `filepath` from the database and serve the file using Flask's `send_from_directory` or a similar mechanism, ensuring correct MIME types are set.

## 7. Deployment Considerations (Brief)

*   **Web Server:** A production-grade WSGI server like Gunicorn will be used to run the Flask application.
*   **Reverse Proxy:** Nginx is recommended as a reverse proxy in front of Gunicorn. Nginx can handle serving static files (CSS, JS, images, and potentially the PDF viewer library), SSL termination, request logging, and load balancing (if scaled).
*   **Environment Variables:** Configuration parameters (e.g., database path, upload folder, secret keys) should be managed using environment variables rather than hardcoding them.
*   **File Permissions:** Ensure the `./uploads/` directory and the SQLite database file have the correct read/write permissions for the user running the application.
*   **Python Dependencies:** A `requirements.txt` file will list all Python dependencies, which can be installed using `pip`.

## 8. Security Considerations (High-Level)

Security is paramount, especially when dealing with file uploads.
*   **Input Validation:**
    *   All data received from the client (API request parameters, query strings, file metadata) must be strictly validated on the backend.
    *   Validate file types rigorously (MIME type, file signature) beyond just the extension.
    *   Enforce file size limits.
*   **File Upload Vulnerabilities:**
    *   **Path Traversal:** Ensure generated filenames and storage paths prevent directory traversal attacks (e.g., by not using user input directly in file paths and by storing files in a designated, non-executable directory).
    *   **File Content:** While PDFs are generally safer than executables, ensure that the PDF rendering library (PDF.js) is kept up-to-date to mitigate vulnerabilities in the parser. Do not allow upload of other executable file types.
    *   **Cross-Site Scripting (XSS):** Sanitize any user-provided data (like original filenames) before displaying it in HTML to prevent XSS.
*   **Serving Files:**
    *   Serve files with appropriate `Content-Type` and `Content-Disposition` headers.
    *   Do not serve files from directories that might contain sensitive application code or configuration files.
*   **General Web Vulnerabilities:**
    *   Protect against CSRF if forms are used in a way that could be targeted (though less critical for a stateless API if session cookies are not used for authentication).
    *   Keep all software dependencies (OS, Python, Flask, PDF.js, etc.) updated.
*   **HTTPS:** In a production environment, always use HTTPS to encrypt data in transit.

This document provides a foundational design. Further details will be elaborated during the development phases.
