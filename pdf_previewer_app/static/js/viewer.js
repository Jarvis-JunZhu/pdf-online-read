document.addEventListener('DOMContentLoaded', () => {
    const iframe = document.getElementById('pdf-iframe');
    const errorMessageDiv = document.getElementById('error-message');

    if (!iframe) {
        console.error('Error: PDF iframe element not found.');
        if(errorMessageDiv) errorMessageDiv.textContent = 'PDF viewer component is missing. Please contact support.';
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const pdfId = urlParams.get('pdf_id');

    if (!pdfId) {
        displayError('No PDF ID provided in the URL.');
        iframe.style.display = 'none'; // Hide iframe if no ID
        return;
    }

    // Validate if pdfId is a number (basic validation)
    if (isNaN(parseInt(pdfId))) {
        displayError('Invalid PDF ID format.');
        iframe.style.display = 'none';
        return;
    }

    // Construct the URL to your backend endpoint that serves the PDF file
    const pdfUrl = `/api/pdfs/${pdfId}`;

    // Encode the PDF URL to be safely passed as a query parameter to PDF.js viewer
    const encodedPdfUrl = encodeURIComponent(pdfUrl);

    // Construct the full URL for the PDF.js viewer
    // Assuming viewer.html is at /static/lib/pdfjs/web/viewer.html
    // And this viewer.js is at /static/js/viewer.js
    // So the path to PDF.js viewer is relative from the root.
    const viewerUrl = `lib/pdfjs/web/viewer.html?file=${encodedPdfUrl}`;
    
    console.log(`Attempting to load PDF.js viewer with URL: ${viewerUrl}`);
    iframe.src = viewerUrl;

    // Optional: Listen for iframe load errors (might be limited due to cross-origin policies if any)
    iframe.onerror = () => {
        displayError('Failed to load the PDF viewer. The file might be corrupted or the viewer path is incorrect.');
        iframe.style.display = 'none';
    };
    
    // Check if the PDF exists by making a HEAD request (optional, but good for UX)
    // This helps to quickly identify if the PDF is missing before loading the entire viewer.
    fetch(pdfUrl, { method: 'HEAD' })
        .then(response => {
            if (!response.ok) {
                // If HEAD request fails, the PDF is likely not available or ID is wrong
                let errorDetail = `PDF not found (ID: ${pdfId}). Status: ${response.status}.`;
                if (response.status === 404) {
                     errorDetail = `The requested PDF (ID: ${pdfId}) could not be found. It might have been deleted or the ID is incorrect.`;
                } else if (response.status === 500) {
                     errorDetail = `There was a server error trying to access PDF (ID: ${pdfId}).`;
                }
                displayError(errorDetail);
                iframe.style.display = 'none'; // Hide iframe
            } else {
                // PDF exists, viewer will proceed to load it.
                // Ensure error message is hidden if previously shown
                if(errorMessageDiv) errorMessageDiv.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error checking PDF existence:', error);
            // This could be a network error or CORS issue if backend is on a different domain
            displayError(`Network error or issue accessing PDF (ID: ${pdfId}). Please check your connection or contact support.`);
            iframe.style.display = 'none';
        });


    function displayError(message) {
        if (errorMessageDiv) {
            errorMessageDiv.textContent = message;
            errorMessageDiv.style.display = 'block';
        } else {
            console.error(message); // Fallback if error div is not present
        }
    }
});
