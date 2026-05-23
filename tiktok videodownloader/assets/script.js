document.addEventListener('DOMContentLoaded', () => {
    const downloadForm = document.getElementById('sc-download-form');
    if (!downloadForm) {
        return;
    }

    const urlInput = document.getElementById('sc-url-input');
    const resultsDiv = document.getElementById('sc-results');
    
    const API_BASE_URL = 'https://saveclips-api.onrender.com';

    downloadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const videoUrl = urlInput.value.trim();
        if (!videoUrl) {
            alert('Please paste a TikTok video URL.');
            return;
        }
        showLoader();
        try {
            const { endpoint, payload } = getApiDetails(videoUrl);
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'An unknown error occurred.');
            }
            displayResults(data);
        } catch (error) {
            displayError(error.message);
        }
    });
    
    // NEW FUNCTION TO FORCE DOWNLOAD
    async function forceDownload(url, title) {
        const downloadButton = document.getElementById('final-download-btn');
        const originalText = downloadButton.textContent;
        downloadButton.textContent = 'Downloading...';
        downloadButton.disabled = true;

        try {
            // Fetch the video data
            const response = await fetch(url);
            const blob = await response.blob();

            // Create a temporary link and click it
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            // Sanitize title for the filename
            const fileName = title.replace(/[^a-z0-9_.-]/gi, '_') + '.mp4';
            link.download = fileName;
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // Clean up the blob URL
            URL.revokeObjectURL(link.href);

        } catch (error) {
            console.error('Download failed:', error);
            alert('Could not download the file.');
        } finally {
            // Restore button text
            downloadButton.textContent = originalText;
            downloadButton.disabled = false;
        }
    }
    
    function getApiDetails(url) {
        if (url.includes('tiktok.com')) {
            return {
                endpoint: '/tiktok/download',
                payload: { url }
            };
        } else {
            throw new Error('Invalid URL. This downloader only supports TikTok videos.');
        }
    }

    function showLoader() {
        resultsDiv.innerHTML = `
            <div class="sc-loader">
                <div class="spinner"></div>
                <p>Fetching video, please wait...</p>
            </div>
        `;
    }

    function displayError(message) {
        const sanitizedMessage = message.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        resultsDiv.innerHTML = `<p style="color: var(--primary-color-magenta);">${sanitizedMessage}</p>`;
    }

    function displayResults(data) {
        if (!data.title || !data.download_url) {
            displayError('Could not retrieve video information. The link may be private or invalid.');
            return;
        }

        // UPDATED: Now creates a button that will trigger the download script
        resultsDiv.innerHTML = `
            <div class="video-card">
                ${data.thumbnail ? `<img src="${data.thumbnail}" alt="Video Thumbnail">` : ''}
                <h2>${data.title}</h2>
                <div class="download-links">
                    <button id="final-download-btn" class="download-btn-small">Download Video</button>
                </div>
            </div>
        `;

        // Add an event listener to the new button
        const finalDownloadBtn = document.getElementById('final-download-btn');
        if (finalDownloadBtn) {
            finalDownloadBtn.addEventListener('click', () => {
                forceDownload(data.download_url, data.title);
            });
        }
    }
});