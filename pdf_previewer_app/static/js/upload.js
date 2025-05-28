document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const pdfFileInput = document.getElementById('pdf-file-input');
    const messageArea = document.getElementById('message-area');
    const uploadProgress = document.getElementById('upload-progress');
    const uploadButton = document.getElementById('upload-button');

    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        messageArea.textContent = '';
        messageArea.className = 'message-area'; // Reset classes
        uploadProgress.style.display = 'none';
        uploadProgress.value = 0;

        const file = pdfFileInput.files[0];

        if (!file) {
            displayMessage('Please select a file to upload.', 'error');
            return;
        }

        // Basic client-side check for PDF extension
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            displayMessage('Invalid file type. Only PDF files are allowed.', 'error');
            return;
        }
        
        // Client-side check for file size (50MB limit)
        const maxSize = 50 * 1024 * 1024; // 50 MB in bytes
        if (file.size > maxSize) {
            displayMessage(`File is too large. Maximum size is ${maxSize / (1024*1024)}MB.`, 'error');
            return;
        }

        const formData = new FormData();
        formData.append('pdf_file', file);

        displayMessage('Uploading...', 'info');
        uploadProgress.style.display = 'block'; // Show progress bar (indeterminate for now)
        uploadButton.disabled = true;

        try {
            // Using XHR for progress tracking
            const xhr = new XMLHttpRequest();

            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 100;
                    uploadProgress.value = percentComplete;
                    // displayMessage(`Uploading: ${Math.round(percentComplete)}%`, 'info');
                } else {
                    // Fallback for non-computable progress
                    uploadProgress.removeAttribute('value'); // Indeterminate state
                }
            };

            xhr.onload = () => {
                uploadButton.disabled = false;
                uploadProgress.style.display = 'none';
                uploadProgress.value = 0;

                if (xhr.status === 201) {
                    const response = JSON.parse(xhr.responseText);
                    displayMessage(`Success! File "${response.filename}" uploaded. PDF ID: ${response.pdf_id}`, 'success');
                    uploadForm.reset(); // Clear the file input
                } else {
                    let errorMsg = 'An unknown error occurred.';
                    try {
                        const response = JSON.parse(xhr.responseText);
                        errorMsg = response.error || `Error ${xhr.status}: ${xhr.statusText}`;
                    } catch (e) {
                        errorMsg = `Error ${xhr.status}: ${xhr.statusText}`;
                    }
                    displayMessage(errorMsg, 'error');
                }
            };

            xhr.onerror = () => {
                uploadButton.disabled = false;
                uploadProgress.style.display = 'none';
                uploadProgress.value = 0;
                displayMessage('Upload failed. Network error or server unreachable.', 'error');
            };
            
            xhr.open('POST', '/api/upload', true);
            xhr.send(formData);

        } catch (error) {
            console.error('Upload error:', error);
            uploadButton.disabled = false;
            uploadProgress.style.display = 'none';
            uploadProgress.value = 0;
            displayMessage('An unexpected error occurred during upload. Check console for details.', 'error');
        }
    });

    function displayMessage(message, type) {
        messageArea.textContent = message;
        messageArea.className = 'message-area'; // Reset classes
        if (type === 'success') {
            messageArea.classList.add('message-success');
        } else if (type === 'error') {
            messageArea.classList.add('message-error');
        } else if (type === 'info') {
            messageArea.classList.add('message-info');
        }
    }
});
