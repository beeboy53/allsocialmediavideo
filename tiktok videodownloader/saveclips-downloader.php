<?php
/**
 * Plugin Name:       SaveClips TikTok Downloader
 * Description:       A simple TikTok video downloader. Use the [saveclips_downloader] shortcode.
 * Version:           1.2.0
 * Author:           MK Tech
 * Author URI:       https://mk-tech.in
 * License:           GPL-2.0+
 */

if (!defined('ABSPATH')) {
    exit;
}

function scd_enqueue_assets() {
    wp_enqueue_style(
        'scd-styles',
        plugin_dir_url(__FILE__) . 'assets/style.css',
        array(),
        '1.2.0'
    );
    wp_enqueue_script(
        'scd-script',
        plugin_dir_url(__FILE__) . 'assets/script.js',
        array(),
        '1.2.0',
        true
    );
}
add_action('wp_enqueue_scripts', 'scd_enqueue_assets');

function scd_display_downloader() {
    ob_start();
    ?>
    <div class="sc-tiktok-downloader">
        <h1>TikTok Video Downloader</h1>
        <p class="subtitle">Download TikTok videos without a watermark for free.</p>
        
        <form id="sc-download-form">
            <div class="input-group">
                <input type="url" id="sc-url-input" placeholder="Paste TikTok video link here..." required>
                <button type="submit" id="sc-download-btn">Download</button>
            </div>
        </form>

        <div id="sc-results">
            </div>
    </div>
    <?php
    return ob_get_clean();
}

add_shortcode('saveclips_downloader', 'scd_display_downloader');