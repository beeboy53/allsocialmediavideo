async function downloadInstagram(rawInput) {
    const resultsContainer = document.getElementById("sc-insta-results");
    
    if (!rawInput || rawInput.trim() === '') {
        alert("Please paste an Instagram link.");
        return;
    }

    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const foundUrls = rawInput.match(urlRegex);
    
    if (!foundUrls) {
        alert("No valid URL found. Please paste a direct link to the Instagram post.");
        return;
    }
    const url = foundUrls[0];
    
    resultsContainer.innerHTML = `
        <div class="sc-loader">
            <div class="spinner"></div>
            <p>Fetching Instagram post...</p>
        </div>
    `;

    try {
        const apiUrl = `https://allvideodownloader-production-26b1.up.railway.app/instagram_info?url=${encodeURIComponent(url)}`;
        const response = await fetch(apiUrl);
        const data = await response.json();

        if (data.error || !data.media) {
            resultsContainer.innerHTML = `<p style="color:red; text-align:center;">Error: ${data.error || 'Could not fetch post details.'}</p>`;
            return;
        }

        const uploader = data.uploader || 'instagram_post';
        
        let resultsHtml = `
            <div class="insta-results-header">
                <h2>${data.title || 'Download Results'}</h2>
            </div>
            <div class="insta-results-grid">
        `;
        
        data.media.forEach((item, index) => {
            const fileExtension = item.type === 'video' ? 'mp4' : 'jpg';
            const safeFilename = `${uploader}_${index + 1}.${fileExtension}`;
            const downloadAttribute = `download="${safeFilename}"`;

            resultsHtml += `
                <div class="insta-result-item">
                    <img src="${item.thumbnail}" alt="Instagram media thumbnail" loading="lazy" />
                    <a href="${item.url}" class="insta-download-button" ${downloadAttribute} target="_blank">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        <span>Download ${item.type.charAt(0).toUpperCase() + item.type.slice(1)}</span>
                    </a>
                </div>
            `;
        });

        resultsHtml += '</div>'; // Close grid
        resultsContainer.innerHTML = resultsHtml;

    } catch (e) {
        resultsContainer.innerHTML = "<p style='color:red; text-align:center;'>An error occurred. Please try again.</p>";
        console.error(e);
    }
}