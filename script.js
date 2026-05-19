async function downloadVideo(url) {
    const results = document.getElementById("sc-results");
    if (!url) {
        alert("Please paste a video link.");
        return;
    }

    results.innerHTML = `
        <div class="sc-loader">
            <div class="spinner"></div>
            <p>Fetching download links...</p>
        </div>
    `;

    try {
        const apiUrl = "https://allvideodownloader-production-26b1.up.railway.app/info?url=" + encodeURIComponent(url);
        const resp = await fetch(apiUrl);
        const data = await resp.json();

        if (data.error || !data.formats) {
            results.innerHTML = `<p style="color:red;">Error: ${data.detail || 'Could not fetch video details.'}</p>`;
            return;
        }

        // --- ✨ Categorize all formats ---
        let mergedFormats = [];
        let videoWithAudioFormats = [];
        let videoOnlyFormats = [];
        let audioOnlyFormats = [];

        data.formats.forEach(f => {
            const hasVideo = f.vcodec !== 'none' && f.vcodec !== null;
            const hasAudio = f.acodec !== 'none' && f.acodec !== null;

            if (f.vcodec === 'merged') {
                mergedFormats.push(f);
            } else if (hasVideo && hasAudio) {
                videoWithAudioFormats.push(f);
            } else if (hasVideo && !hasAudio) {
                videoOnlyFormats.push(f);
            } else if (hasAudio && !hasVideo) {
                audioOnlyFormats.push(f);
            }
        });

        const makeLinks = (arr) => arr.map(f => {
            const icon = (f.vcodec !== 'none' && f.acodec === 'none') ? '🔇' : ''; // Mute icon for video-only
            return `<a href="${f.url}" target="_blank" class="download-btn-small" download>${f.quality} (${f.ext}) ${icon}</a>`;
        }).join('');

        // --- ✨ Build the final HTML with all categories ---
        results.innerHTML = `
            <div class="video-card">
                <img src="${data.thumbnail}" alt="Video Thumbnail"/>
                <h2>${data.title}</h2>

                ${mergedFormats.length > 0 ? `<h3>⭐ Best Quality</h3><div class="download-links">${makeLinks(mergedFormats)}</div>` : ''}
                ${videoWithAudioFormats.length > 0 ? `<h3>🎬 Video + Audio</h3><div class="download-links">${makeLinks(videoWithAudioFormats)}</div>` : ''}
                ${videoOnlyFormats.length > 0 ? `<h3>🎥 Video Only</h3><div class="download-links">${makeLinks(videoOnlyFormats)}</div>` : ''}
                ${audioOnlyFormats.length > 0 ? `<h3>🎧 Audio Only</h3><div class="download-links">${makeLinks(audioOnlyFormats)}</div>` : ''}
            </div>
        `;
    } catch (e) {
        results.innerHTML = "<p style='color:red;'>Failed to connect to the download server.</p>";
        console.error(e);
    }
}