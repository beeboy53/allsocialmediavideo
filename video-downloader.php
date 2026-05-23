<?php
/*
Plugin Name: Video Downloader
Description: All-in-one video downloader connected to your FastAPI service.
Version: 1.1
Author: You
*/

// Shortcode output
function vd_form() {
    return '
    <div class="sc-video-downloader">
        <h1>SaveClips – All-in-One Video Downloader</h1>
        <p class="subtitle">Paste a link and download from anywhere.</p>

        <div class="input-group">
            <input type="text" id="sc-url-input" placeholder="Paste video link here...">
            
            <button id="sc-download-btn" onclick="downloadVideo(document.getElementById(\'sc-url-input\').value)">Download Now</button>
        </div>

        <div id="sc-results"></div>
    </div>
    ';
}
add_shortcode("video_downloader", "vd_form");