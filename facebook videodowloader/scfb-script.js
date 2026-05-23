document.addEventListener('DOMContentLoaded', () => {
    const downloadForm = document.getElementById('scfb-download-form');
    if (!downloadForm) {
        return;
    }

    const urlInput = document.getElementById('scfb-url-input');
    const resultsDiv = document.getElementById('scfb-results');
    
    downloadForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const videoUrl = urlInput.value.trim();
        if (!videoUrl) {
            alert('Please paste a Facebook video URL.');
            return;
        }
        showLoader();

        // Get the security nonce value from the hidden field
        const nonce = document.querySelector('#scfb_nonce_field').value;

        // Prepare data to send to our own server (PHP)
        const formData = new FormData();
        formData.append('action', 'scfb_download_action');
        formData.append('nonce', nonce);
        formData.append('url', videoUrl);

        try {
            // Send the request to our secure PHP handler
            const response = await fetch(scfb_ajax_object.ajax_url, {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            // WordPress AJAX returns a 'success' property
            if (!data.success) {
                // 'data.data' contains the error payload from our PHP
                throw new Error(data.data.detail || 'An unknown error occurred.');
            }
            
            // 'data.data' contains the success payload from our PHP
            displayResults(data.data);

        } catch (error) {
            displayError(error.message);
        }
    });
    
    async function forceDownload(url, title) {
        // This function remains the same
        const downloadButton = resultsDiv.querySelector('.scfb-download-btn-small');
        if (!downloadButton) return;
        downloadButton.textContent = 'Downloading...';
        downloadButton.disabled = true;
        try {
            const response = await fetch(url);
            const blob = await response.blob();
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = (title || 'facebook-video').replace(/[^a-z0-9_.-]/gi, '_') + '.mp4';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);
        } catch (error) {
            alert('Could not download file.');
        } finally {
            downloadButton.textContent = 'Download Video';
            downloadButton.disabled = false;
        }
    }
    
    function showLoader() {
        resultsDiv.innerHTML = `<div class="scfb-loader"><div class="scfb-spinner"></div><p>Fetching video...</p></div>`;
    }

    function displayError(message) {
        const sanitized = message.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        resultsDiv.innerHTML = `<p style="color: #d93025; font-weight: bold;">${sanitized}</p>`;
    }

    function displayResults(data) {
        if (!data.title || !data.download_url) {
            displayError('Could not get video info. It may be private or the link is invalid.');
            return;
        }
        resultsDiv.innerHTML = `
            <div class="scfb-video-card">
                ${data.thumbnail ? `<img src="${data.thumbnail}" alt="Thumbnail">` : ''}
                <h2>${data.title}</h2>
                <div class="scfb-download-links">
                    <button class="scfb-download-btn-small">Download Video</button>
                </div>
            </div>`;
        resultsDiv.querySelector('.scfb-download-btn-small').addEventListener('click', () => {
            forceDownload(data.download_url, data.title);
        });
    }
});