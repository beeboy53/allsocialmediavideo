<?php
/**
 * Plugin Name:      SaveClips FB Downloader (New)
 * Description:      A fresh downloader for Facebook videos. Use the shortcode [saveclips_fb_downloader].
 * Version:          2.0.0
 * Author:           MK Tech
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly.
}

/**
 * Enqueue assets and pass the AJAX URL to the script.
 */
function scfb_new_enqueue_assets() {
    global $post;
    
    if (is_a($post, 'WP_Post') && has_shortcode($post->post_content, 'saveclips_fb_downloader')) {
        wp_enqueue_style(
            'scfb-new-styles',
            plugin_dir_url(__FILE__) . 'assets/scfb-style.css',
            array(),
            '2.2.0' // Version bumped
        );
        wp_enqueue_script(
            'scfb-new-script',
            plugin_dir_url(__FILE__) . 'assets/scfb-script.js',
            array(),
            '2.2.0', // Version bumped
            true
        );

        wp_localize_script('scfb-new-script', 'scfb_ajax_object', array(
            'ajax_url' => admin_url('admin-ajax.php')
        ));
    }
}
add_action('wp_enqueue_scripts', 'scfb_new_enqueue_assets');

/**
 * Display function for the shortcode.
 */
function scfb_new_display_downloader() {
    ob_start();
    ?>
    <div class="scfb-downloader-container">
        <h1>Facebook Video Downloader</h1>
        <p class="scfb-subtitle">Download public videos from Facebook in HD for free.</p>
        
        <form id="scfb-download-form">
            <div class="scfb-input-group">
                <input type="url" id="scfb-url-input" placeholder="Paste Facebook video link here..." required>
                <?php wp_nonce_field('scfb_nonce_action', 'scfb_nonce_field'); ?>
                <button type="submit" id="scfb-download-btn">Download</button>
            </div>
        </form>

        <div id="scfb-results"></div>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('saveclips_fb_downloader', 'scfb_new_display_downloader');

/**
 * The secure server-side AJAX handler.
 */
function scfb_handle_download_request() {
    check_ajax_referer('scfb_nonce_action', 'nonce');

    $url = isset($_POST['url']) ? esc_url_raw($_POST['url']) : '';
    if (empty($url)) {
        wp_send_json_error(['detail' => 'URL is missing.']);
        return;
    }

    //
    // === THIS IS THE CORRECTED PART ===
    // The entire cookie file content is now stored as a multi-line string
    // in the exact Netscape format that the API requires.
    //
    $netscape_cookies = <<<'COOKIES'
# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.facebook.com	TRUE	/	TRUE	1777295348	sb	tr4nZyjyhJhRh1NYWzW89unx
.facebook.com	TRUE	/	TRUE	1792147000	datr	tr4nZ_VvjA2AqB5UOhsfAJZJ
.facebook.com	TRUE	/	TRUE	1765278080	ps_l	1
.facebook.com	TRUE	/	TRUE	1765278080	ps_n	1
.facebook.com	TRUE	/	TRUE	1789832053	c_user	100045268867467
.facebook.com	TRUE	/	TRUE	1758903659	dpr	0.800000011920929
.facebook.com	TRUE	/	TRUE	0	ar_debug	1
.facebook.com	TRUE	/	TRUE	1758903659	wd	1697x802
.facebook.com	TRUE	/	TRUE	1789832053	xs	30%3A947_zZe5K4EWMA%3A2%3A1742735338%3A-1%3A-1%3A%3AAcW136HlQW6gtnhbjxkCOs4vaMOjRdUqXw5BNsOcx-gB
.facebook.com	TRUE	/	TRUE	1789834855	i_user	61565654844679
.facebook.com	TRUE	/	TRUE	1766074857	fr	15jxyzKR6xAWa1BdY.AWckbAFmCmH6bQ-AmRUinKml12b-P7vuwI_KhBa4yMSDgn2W5hc.BozXf0..AAA.0.0.BozYLn.AWcgCTOZ8pctQKgvA42M3ORF9C8
COOKIES;


    $api_url = 'https://saveclips-api.onrender.com/facebook/download';
    $body = json_encode([
        'url' => $url,
        'cookies' => $netscape_cookies // We now send the full Netscape content
    ]);

    $response = wp_remote_post($api_url, [
        'method'    => 'POST',
        'headers'   => ['Content-Type' => 'application/json; charset=utf-8'],
        'body'      => $body,
        'timeout'   => 45
    ]);

    if (is_wp_error($response)) {
        wp_send_json_error(['detail' => 'Failed to connect to the API server.']);
        return;
    }

    $response_body = wp_remote_retrieve_body($response);
    $data = json_decode($response_body, true);

    if (wp_remote_retrieve_response_code($response) !== 200) {
        wp_send_json_error($data);
        return;
    }

    wp_send_json_success($data);
}
add_action('wp_ajax_scfb_download_action', 'scfb_handle_download_request');
add_action('wp_ajax_nopriv_scfb_download_action', 'scfb_handle_download_request');