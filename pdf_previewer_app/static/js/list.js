document.addEventListener('DOMContentLoaded', () => {
    const pdfListContainer = document.getElementById('pdf-list-container');
    const paginationControlsContainer = document.getElementById('pagination-controls');
    const sortBySelect = document.getElementById('sort-by');
    
    let currentPage = 1;
    const defaultLimit = 10; // Can be made configurable if needed
    let currentSortBy = sortBySelect.value;

    async function fetchPdfList(page = 1, limit = defaultLimit, sortBy = currentSortBy) {
        currentPage = page; // Update current page
        currentSortBy = sortBy; // Update current sort order

        pdfListContainer.innerHTML = '<p class="message-info">Loading PDF list...</p>';
        paginationControlsContainer.innerHTML = ''; // Clear old pagination

        try {
            const response = await fetch(`/api/pdfs?page=${page}&limit=${limit}&sort_by=${sortBy}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: `HTTP error! Status: ${response.status}` }));
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            renderPdfList(data.pdfs);
            renderPaginationControls(data.total_pdfs, data.current_page, data.total_pages, data.limit);
        } catch (error) {
            console.error('Error fetching PDF list:', error);
            displayMessage(pdfListContainer, `Error fetching PDFs: ${error.message}`, 'error');
        }
    }

    function renderPdfList(pdfs) {
        pdfListContainer.innerHTML = ''; // Clear previous content (like loading message)

        if (!pdfs || pdfs.length === 0) {
            displayMessage(pdfListContainer, 'No PDFs uploaded yet.', 'info');
            return;
        }

        const ul = document.createElement('ul');
        pdfs.forEach(pdf => {
            const li = document.createElement('li');

            const detailsDiv = document.createElement('div');
            detailsDiv.className = 'pdf-item-details';

            const title = document.createElement('h3');
            const link = document.createElement('a');
            link.href = `viewer.html?pdf_id=${pdf.id}`;
            // Open in new tab for convenience, can be changed
            // link.target = '_blank'; 
            link.textContent = pdf.original_filename || 'Unnamed PDF';
            title.appendChild(link);
            detailsDiv.appendChild(title);

            const metadataDiv = document.createElement('div');
            metadataDiv.className = 'pdf-metadata';

            const sizeSpan = document.createElement('span');
            sizeSpan.innerHTML = `<span class="label">Size:</span> ${formatFilesize(pdf.filesize)}`;
            metadataDiv.appendChild(sizeSpan);
            
            const uploadedSpan = document.createElement('span');
            const uploadedDate = new Date(pdf.upload_timestamp).toLocaleString();
            uploadedSpan.innerHTML = `<span class="label">Uploaded:</span> ${uploadedDate}`;
            metadataDiv.appendChild(uploadedSpan);

            detailsDiv.appendChild(metadataDiv);
            li.appendChild(detailsDiv);
            
            // Could add a direct view/download button here as well if desired
            // const viewButton = document.createElement('a');
            // viewButton.href = `/api/pdfs/${pdf.id}`;
            // viewButton.textContent = 'View Raw';
            // viewButton.className = 'button-like'; // Add some styling
            // li.appendChild(viewButton);

            ul.appendChild(li);
        });
        pdfListContainer.appendChild(ul);
    }

    function renderPaginationControls(totalPdfs, currentPageNum, totalPages, limit) {
        paginationControlsContainer.innerHTML = ''; // Clear previous controls

        if (totalPdfs === 0 || totalPages <= 1) {
            return; // No pagination needed for 0 or 1 page
        }

        const prevButton = document.createElement('button');
        prevButton.textContent = 'Previous';
        prevButton.disabled = currentPageNum === 1;
        prevButton.addEventListener('click', () => {
            if (currentPageNum > 1) {
                fetchPdfList(currentPageNum - 1, limit, currentSortBy);
            }
        });
        paginationControlsContainer.appendChild(prevButton);

        const pageInfo = document.createElement('span');
        pageInfo.textContent = `Page ${currentPageNum} of ${totalPages}`;
        pageInfo.className = 'current-page'; // For styling
        paginationControlsContainer.appendChild(pageInfo);

        const nextButton = document.createElement('button');
        nextButton.textContent = 'Next';
        nextButton.disabled = currentPageNum === totalPages;
        nextButton.addEventListener('click', () => {
            if (currentPageNum < totalPages) {
                fetchPdfList(currentPageNum + 1, limit, currentSortBy);
            }
        });
        paginationControlsContainer.appendChild(nextButton);
    }

    function formatFilesize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function displayMessage(container, message, type) {
        container.innerHTML = ''; // Clear previous content
        const p = document.createElement('p');
        p.textContent = message;
        p.className = ''; // Reset classes
        if (type === 'success') {
            p.classList.add('message-success');
        } else if (type === 'error') {
            p.classList.add('message-error');
        } else if (type === 'info') {
            p.classList.add('message-info');
        }
        container.appendChild(p);
    }

    // Event listener for sort dropdown
    sortBySelect.addEventListener('change', (event) => {
        fetchPdfList(1, defaultLimit, event.target.value); // Fetch from page 1 with new sort
    });

    // Initial fetch
    fetchPdfList(currentPage, defaultLimit, currentSortBy);
});
