<?php
/**
 * Plugin Name:   SaveClips - Instagram Downloader
 * Description:   A dedicated shortcode for downloading Instagram photos, Reels, and videos.
 * Version:       1.1
 * Author:        MK Tech
 */

if (!defined("ABSPATH")) {
    exit; // Exit if accessed directly
}

/**
 * Enqueue scripts and styles ONLY when the shortcode is present.
 * This improves site performance by not loading assets on every page.
 */
function sc_insta_enqueue_assets() {
    global $post;
    
    // Check if the post object exists and if the shortcode is in the post content
    if (is_a($post, 'WP_Post') && has_shortcode($post->post_content, 'instagram_downloader')) {
        wp_enqueue_style(
            'sc-insta-style',
            plugin_dir_url(__FILE__) . 'style-instagram.css',
            array(),
            '1.1' // Bumped version
        );
        wp_enqueue_script(
            'sc-insta-script',
            plugin_dir_url(__FILE__) . 'script-instagram.js',
            array(),
            '1.1', // Bumped version
            true
        );
    }
}
add_action('wp_enqueue_scripts', 'sc_insta_enqueue_assets');

/**
 * Shortcode output function.
 * Uses output buffering for cleaner code and removes inline JS.
 */
function sc_insta_form() {
    ob_start(); // Start output buffering
    ?>
    <div class="sc-video-downloader sc-instagram-downloader">
        <h1>Instagram Downloader</h1>
        <p class="subtitle">Download Instagram videos, Reels, photos, and carousels for free.</p>
        
        <form id="sc-insta-download-form">
            <div class="input-group">
                <input type="url" id="sc-insta-url-input" placeholder="Paste Instagram link here..." required>
                <button type="submit" id="sc-insta-download-btn">Download</button>
            </div>
        </form>
        
        <div id="sc-insta-results"></div>
    </div>
    <?php
    return ob_get_clean(); // Return the buffered content
}
add_shortcode("instagram_downloader", "sc_insta_form");