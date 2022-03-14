<?php 
/*
Plugin Name: Clear Cache For Me
Plugin URI: https://webheadcoder.com/clear-cache-for-me/
Description: Purges all cache on WPEngine, W3 Total Cache, WP Super Cache, WP Fastest Cache when updating widgets, menus, settings.  Forces a browser to reload a theme's CSS and JS files.
Author: Webhead LLC
Author URI: https://webheadcoder.com 
Version: 1.7
*/


define( 'CCFM_VERSION', '1.7' );
define( 'CCFM_PLUGIN', __FILE__ );

require_once( 'clear-cache-for-action.php' );
require_once( 'options-page.php' );

// locale
function ccfm_plugins_loaded() {
    load_plugin_textdomain( 'ccfm', false, dirname( plugin_basename( __FILE__ ) ) . '/lang/' );

    $old_permissions = get_option( 'ccfm_permission' );
    if ( !empty( $old_permissions ) ) {
        // migrate it to the new options
        $options = get_option( 'ccfm_options', array() );
        $options['btn_cap'] = $old_permissions;
        update_option( 'ccfm_options', $options );
        delete_option( 'ccfm_permission' );
    }

    $old_infotext = get_option( 'ccfm_infotext' );
    if ( !empty( $old_infotext ) ) {
        // migrate it to the new options
        $options = get_option( 'ccfm_options', array() );
        $options['btn_instructions'] = $old_infotext;
        update_option( 'ccfm_options', $options );
        delete_option( 'ccfm_infotext' );
    }

    if ( apply_filters( 'ccfm_clear_cache_on_wp_activity', is_user_logged_in() ) ) {
        add_action( 'activated_plugin', 'ccfm_clear_cache_for_wp_activity' );
        add_action( 'deactivated_plugin', 'ccfm_clear_cache_for_wp_activity' );
        add_action( 'upgrader_process_complete', 'ccfm_clear_cache_for_wp_activity' );

        add_action( '_core_updated_successfully', 'ccfm_clear_cache_for_wp_activity' );
    }
}
add_action( 'plugins_loaded', 'ccfm_plugins_loaded' );


/**
 * Add widget save, reorder and delete detection.  Thanks to Ov3rfly.
 */
function ccfm_admin_init() {
    global $pagenow;

    ccfm_handle_requests();

    add_action( 'wp_dashboard_setup', 'ccfm_dashboard_widget' );
    
    //add styles for dashboard
    add_action( 'admin_head', 'ccfm_admin_head' );

    if ( ccfm_supported_caching_exists() ) {

        if ( defined( 'QODE_ROOT' ) ) {
            if ( 'options.php' == $pagenow ) {
                //detect when qode options saved.
                add_action( 'updated_option', 'ccfm_save_clear_cache_for_qode', 10, 3 );   
            }
        }

        //detect widget save, reorder and delete detection.  Thanks to Ov3rfly.
        add_action( 'wp_ajax_save-widget', 'ccfm_clear_cache_for_widgets_wp_ajax_action', 1 );
        add_action( 'wp_ajax_widgets-order', 'ccfm_clear_cache_for_widgets_wp_ajax_action', 1 );
        add_action( 'sidebar_admin_setup', 'ccfm_clear_cache_for_widgets_sidebar_admin_setup' );
        //detect customize theme actions.
        add_action( 'customize_save_after', 'ccfm_clear_cache_for_customized_theme' );

        //detect nav menu changes
        add_action( 'wp_update_nav_menu', 'ccfm_clear_cache_for_menus' );

        //detect settings page changes
        add_filter( 'pre_set_transient_settings_errors', 'ccfm_clear_cache_for_settings' );

        //detect ContactForm7 changes
        add_action( 'wpcf7_save_contact_form', 'ccfm_clear_cache_for_cf7' );

        //detect WooThemes settings changes
        add_action( 'update_option_woo_options', 'ccfm_clear_cache_for_woo_options' );

        if ( class_exists( 'ACF' ) ) {
            add_action( 'save_post', 'ccfm_acf_update_fields', 10, 2 );
        }

        //try detect NextGen Gallery changes
        add_action( 'ngg_update_gallery', 'ccfm_clear_cache_for_ngg' );
        add_action( 'ngg_delete_gallery', 'ccfm_clear_cache_for_ngg' );
        add_action( 'ngg_update_album', 'ccfm_clear_cache_for_ngg' );
        add_action( 'ngg_update_album_sortorder', 'ccfm_clear_cache_for_ngg' );
        add_action( 'ngg_delete_album', 'ccfm_clear_cache_for_ngg' );

        //detect Formidable changes
        add_action( 'frm_update_form', 'ccfm_clear_cache_for_formidable' );

        //detect Contact Form by WP Forms changes
        add_action( 'wpforms_builder_save_form', 'ccfm_clear_cache_for_wpforms' );

        // detect Insert Headers and Footers by WPBeginner changes
        add_action( 'update_option_ihaf_insert_header', 'ccfm_insert_headers_and_footers' );
        add_action( 'update_option_ihaf_insert_footer', 'ccfm_insert_headers_and_footers' );
        add_action( 'update_option_ihaf_insert_body', 'ccfm_insert_headers_and_footers' );

        do_action( 'ccfm_admin_init' );
    }
}
add_action( 'admin_init', 'ccfm_admin_init' ); // not 'init'

/**
 * Special function to add actions for hooks that are triggered before admin_init.
 */
function ccfm_init_actions() {
    //detect WooCommerce settings changes
    add_action( 'woocommerce_settings_saved', 'ccfm_clear_cache_for_woocommerce');
    
    if ( ccfm_option( 'btn_admin_bar', 1 ) == 1 ) {
        $needed_cap = ccfm_option( 'btn_cap', 'manage_options' );
        if ( current_user_can( $needed_cap ) || current_user_can( 'manage_options' ) ) {
            add_action( 'admin_bar_menu', 'ccfm_toolbar_link', 99 );
        }
    }

    do_action( 'ccfm_init_actions' );
}
add_action( 'init', 'ccfm_init_actions' );

/**
 * Enqueue script for admin bar.
 */
function ccfm_enqueue_admin_bar_scripts() {
    if ( !is_user_logged_in() ) {
        return;
    }
    wp_enqueue_script( 
        'ccfm-admin-bar', 
        plugins_url( '/js/admin-bar.js', CCFM_PLUGIN ),
        array( 'jquery', 'admin-bar' ), 
        CCFM_VERSION, 
        true
    );
    wp_localize_script( 'ccfm-admin-bar', 'ccfm', array( 
        'ajax_url' => admin_url( 'admin-ajax.php' ),
        'nonce'    => wp_create_nonce( 'ccfm' ),
    ) );
}
add_action( 'wp_enqueue_scripts', 'ccfm_enqueue_admin_bar_scripts' );
add_action( 'admin_enqueue_scripts', 'ccfm_enqueue_admin_bar_scripts' );

/**
 * Return the first caching system found.
 */
function ccfm_get_caching_system_used() {
    $cache_system_key = '';
    if ( function_exists( 'w3tc_pgcache_flush' ) ) {
        $cache_system_key = 'w3tc';
    }
    else if ( function_exists( 'wp_cache_clean_cache' ) ) {
        $cache_system_key = 'wp_cache';
    }
    else if ( class_exists( 'WpeCommon' ) ) {
        $cache_system_key = 'wpengine';
    }
    else if ( method_exists( 'WpFastestCache', 'deleteCache' ) ) {
        $cache_system_key = 'wp_fastest_cache';
    }
    else if ( class_exists( '\WPaaS\Cache' ) ) {
        $cache_system_key = 'godaddy';
    }
    else if ( class_exists( 'WP_Optimize' ) && defined( 'WPO_PLUGIN_MAIN_PATH' ) ) {
        $cache_system_key = 'wp_optimize';
    }
    else if ( class_exists( '\Kinsta\Cache' ) ) {
        $cache_system_key = 'kinsta';
    }
    else if ( class_exists( 'Breeze_Admin' ) ) {
        $cache_system_key = 'breeze';
    }
    else if ( class_exists( 'LiteSpeed_Cache_Purge' ) ) {
        $cache_system_key = 'litespeed';
    }
    else if ( function_exists( 'sg_cachepress_purge_cache' ) ) {
        $cache_system_key = 'siteground';
    }
    else if ( class_exists( 'autoptimizeCache' ) ) {
        $cache_system_key = 'autooptimize';
    }
    else if ( class_exists( 'Cache_Enabler' ) ) {
        $cache_system_key = 'cacheenabler';
    }
    return $cache_system_key;
}

/**
 * Return the caching system name for the key.
 */
function ccfm_get_cache_system_name( $cache_system_key = '' ) {
    if ( empty( $cache_system_key ) ) {
        $cache_system_key = ccfm_get_caching_system_used();
    }
    $cache_name = '';
    switch( $cache_system_key ) {
        case 'w3tc':
            $cache_name = 'W3 Total Cache';
            break;
        case 'wp_cache':
            $cache_name = 'WP Super Cache';
            break;
        case 'wpengine':
            $cache_name = 'WPEngine Cache';
            break;
        case 'wp_fastest_cache':
            $cache_name = 'WP Fastest Cache';
            break;
        case 'godaddy':
            $cache_name = 'GoDaddy Cache';
            break;
        case 'wp_optimize':
            $cache_name = 'WP Optimize';
            break;
        case 'kinsta':
            $cache_name = 'Kinsta Cache';
            break;
        case 'breeze':
            $cache_name = 'Breeze';
            break;
        case 'litespeed':
            $cache_name = 'LiteSpeed Cache';
            break;
        case 'siteground':
            $cache_name = 'SiteGround SuperCacher';
            break;
        case 'autooptimize':
            $cache_name = 'Autoptimize';
            break;
        case 'cacheenabler':
            $cache_name = 'Cache Enabler';
            break;
        default:
            break;
    }
    return $cache_name;
}

/**
 * Return true if known caching systems exists.
 */
function ccfm_supported_caching_exists() {
    $cache_system_key = ccfm_get_caching_system_used();
    $supported = !empty( $cache_system_key );
    return apply_filters( 'ccfm_supported_caching_exists', $supported );
}

/**
 * Set up the cache to be cleared
 */
function ccfm_clear_cache_for_me( $source ) {
    global $ccfm_source;
    if ( isset( $ccfm_source ) ) {
        return;
    }

    $ccfm_source = $source;
    add_action( 'shutdown', 'ccfm_clear_cache_for_all' );
}

/**
 * Clear the caches!
 */
function ccfm_clear_cache_for_all() {
    global $wp_fastest_cache, $kinsta_cache, $admin, $ccfm_source;

    if ( empty( $ccfm_source ) ) {
        $ccfm_source = '';
    }

    do_action( 'ccfm_clear_cache_for_me_before', $ccfm_source );

    // if W3 Total Cache is being used, clear the cache
    if ( function_exists( 'w3tc_pgcache_flush' ) ) { 
        w3tc_pgcache_flush(); 
    }
    // if WP Super Cache is being used, clear the cache
    else if ( function_exists( 'wp_cache_clean_cache' ) ) {
        global $file_prefix, $supercachedir;
        if ( empty( $supercachedir ) && function_exists( 'get_supercache_dir' ) ) {
            $supercachedir = get_supercache_dir();
        }
        wp_cache_clean_cache( $file_prefix );
    }
    else if ( class_exists( 'WpeCommon' ) ) {
        //be extra careful, just in case 3rd party changes things on us
        if ( method_exists( 'WpeCommon', 'purge_memcached' ) ) {
            WpeCommon::purge_memcached();
        }
        if ( method_exists( 'WpeCommon', 'clear_maxcdn_cache' ) ) {  
            WpeCommon::clear_maxcdn_cache();
        }
        if ( method_exists( 'WpeCommon', 'purge_varnish_cache' ) ) {
            WpeCommon::purge_varnish_cache();   
        }
    }
    else if ( method_exists( 'WpFastestCache', 'deleteCache' ) && !empty( $wp_fastest_cache ) ) {
        $wp_fastest_cache->deleteCache( true );
    }
    else if ( class_exists( '\Kinsta\Cache' ) && !empty( $kinsta_cache ) ) {
        $kinsta_cache->kinsta_cache_purge->purge_complete_caches();
    }
    else if ( class_exists( '\WPaaS\Cache' ) ) {
        ccfm_godaddy_purge();
    }
    else if ( class_exists( 'WP_Optimize' ) && defined( 'WPO_PLUGIN_MAIN_PATH' ) ) {
        if (!class_exists('WP_Optimize_Cache_Commands')) include_once(WPO_PLUGIN_MAIN_PATH . 'cache/class-cache-commands.php');

        if ( class_exists( 'WP_Optimize_Cache_Commands' ) ) {
            $wpoptimize_cache_commands = new WP_Optimize_Cache_Commands();
            $wpoptimize_cache_commands->purge_page_cache();
        }
    }
    else if ( class_exists( 'Breeze_Admin' ) ) {
        do_action('breeze_clear_all_cache');
    }
    else if ( class_exists( 'LiteSpeed_Cache_Purge' ) ) {
        LiteSpeed_Cache_Purge::purge_all( 'Clear Cache For Me' );
    }
    else if ( function_exists( 'sg_cachepress_purge_cache' ) ) {
        sg_cachepress_purge_cache();
    }
    else if ( class_exists( 'autoptimizeCache' ) ) {
        autoptimizeCache::clearall();
    }
    else if ( class_exists( 'Cache_Enabler' ) ) {
        Cache_Enabler::clear_total_cache();
    }
    do_action( 'ccfm_clear_cache_for_me', $ccfm_source );

    $time = time();
    update_option( '_ccfm_style_timestamp_theme', $time );

    do_action( 'ccfm_clear_cache_for_css_js', $time );
}

/**
 * Add a button to clear the cache on the dashboard.
 */
function ccfm_dashboard_widget() {
    $needed_cap = ccfm_option( 'btn_cap', 'manage_options' );
    if ( current_user_can( $needed_cap ) || current_user_can( 'manage_options' ) ) {
        wp_add_dashboard_widget('dashboard_ccfm_widget', 'Clear Cache for Me', 'ccfm_dashboard_widget_output');       
    }
}

function ccfm_dashboard_widget_output() {
    $infotext = ccfm_option( 'btn_instructions', __( 'If you\'re not seeing your changes on your public pages, it might be cached.  Click the button below to see a fresh version of your pages.', 'ccfm' ) );
    ?>
<div class="ccfm_widget">
    <form method="post">
        <?php wp_nonce_field( 'ccfm' ); ?>
        <?php echo ( $infotext ) ? '<p class="info">' . $infotext . '</p>' : ''; ?><div class="ccfm-button">
            <input type="submit" name="ccfm" class="button button-primary button-large" value="<?php _e( 'Clear Cache Now!', 'ccfm' ); ?>">
        </div>
    </form>
</div>
    <?php
        if ( current_user_can( 'manage_options' ) ) {
            global $wp_roles;
            $roles = $wp_roles->roles;
            $caps = array();
            foreach( $roles as $role ) {
                if ( !empty( $role['capabilities'] ) ) {
                    foreach ( $role['capabilities'] as $capability => $val ) {
                        $caps[ $capability ] = $capability;
                    }   
                }
            }
            asort( $caps );
    ?>
    <?php
    }
}

/**
 * Add some CSS.
 */
function ccfm_admin_head() {
?>
<style type="text/css">
#dashboard_ccfm_widget .inside {
    margin: 0;
    padding: 0;
}
#dashboard_ccfm_widget .ccfm_widget {
    border-top: 1px solid #eee;
    font-size: 13px;
    padding: 12px;
}
#dashboard_ccfm_widget .ccfm_widget:first-child {
    border-top: none;
}
#dashboard_ccfm_widget h4 {
    margin-bottom: 4px;
}
#dashboard_ccfm_widget p {
    margin: 0 0 8px 0;
}
#dashboard_ccfm_widget label {
    display: block;
    margin: 0 0 4px 0;
    color: #777;
}
#dashboard_ccfm_widget .info {
    display: block;
    width: 100%;
    margin-bottom: 15px;
}

#dashboard_ccfm_widget .ccfm-button {
    display: block;
    width: 100%;
    text-align: left;
}


</style>
<?php
}


/**
 * Clear the cache if requested.
 */
function ccfm_handle_requests() {
    if ( isset( $_REQUEST['ccfm'] ) ) {
        check_admin_referer( 'ccfm' );
        $needed_cap = ccfm_option( 'btn_cap', 'manage_options' );
        $is_success = 0;
        if ( current_user_can( $needed_cap ) ) {
            ccfm_clear_cache_for_me( 'button' );
            $is_success = 1;
            add_action( 'admin_notices', 'ccfm_success' );
        }
        else {
            add_action( 'admin_notices', 'ccfm_error' );   
        }
        wp_safe_redirect( admin_url() . '?ccfm_success=' . $is_success );
        exit;
    }

    if ( isset( $_GET['ccfm_success'] ) ) {
        if ( !empty( $_GET['ccfm_success'] ) ) {
            add_action( 'admin_notices', 'ccfm_success' );
        }
        else {
            add_action( 'admin_notices', 'ccfm_error' );   
        }
    }
}

/**
 * Show the success notice.
 */
function ccfm_success() { ?>
    <div class="updated">
        <p><?php _e( 'Cache cleared!', 'ccfm' ); ?></p>
    </div>
<?php
}

/**
 * Show the success notice for saving options.
 */
function ccfm_admin_success() { ?>
    <div class="updated">
        <p><?php _e( 'Settings Saved!', 'ccfm' ); ?></p>
    </div>
<?php
}

/**
 * Show the error notice.
 */
function ccfm_error() { ?>
    <div class="error">
        <p><?php _e( 'You do not have permission to do that.', 'ccfm' ); ?></p>
    </div>
<?php
}



/**
 * If we have urls to uncache, setup filters.
 * - must be at wp_head priority 1 for style_loader_src to work.
 */
function ccfm_clear_cache_for_custom_styles() {
    add_filter( 'style_loader_src', 'ccfm_show_src_version', 10, 2 );
    add_filter( 'script_loader_src', 'ccfm_show_src_version', 10, 2 );
}
add_action( 'wp_head', 'ccfm_clear_cache_for_custom_styles', 1 );

/**
 * Change a src to a key.
 */
function ccfm_custom_src_key( $src ) {
    $urls = apply_filters( 'ccfm_custom_src_urls', array() );
    $src_parts = explode( '?', $src );
    foreach( $urls as $url => $key ) {
        if ( $src_parts[0] === $url ) {
            return $key;
        }   
    }
    $template = get_template_directory_uri();
    $child = get_stylesheet_directory_uri();
    if ( stripos( $src, $template ) === 0 || stripos( $src, $child ) === 0 ) {
        return 'theme';
    }

    return '';
}

/**
 * Filter the version to make sure it's the latest.
 */    
function ccfm_show_src_version ( $src, $handle ) {
    $key = ccfm_custom_src_key( $src );
    $timestamp = get_option( '_ccfm_style_timestamp_' . $key, '' );
    $dev_mode_assets = ccfm_option( 'dev_mode_assets', 0 );
    if ( empty( $timestamp ) && $dev_mode_assets == 0 ) {
        return $src;
    }
    if ( $dev_mode_assets == 1 ) {
        $timestamp = time();
    }
    $src_parts = explode( '?', $src );
    if ( count( $src_parts ) > 1 ) {
        $query_string = $src_parts[1];
        parse_str( $query_string, $query );
        $query['ver'] = $timestamp;
        return add_query_arg( $query, $src_parts[0] );
    }
    return add_query_arg( 'ver', $timestamp, $src );
}




/**
 * Get option
 */
function ccfm_option($name, $default='', $options = false) {
    if (empty($options)) {
        $options = get_option( 'ccfm_options' );
    }

    if (!empty($options) && isset($options[$name])) {
        $ret = $options[$name];
    }
    else {
        $ret = $default;
    }
    return $ret;
}

/**
 * add a link to the WP Toolbar
 */
function ccfm_toolbar_link( $wp_admin_bar ) {
    $url = add_query_arg( '_wpnonce', wp_create_nonce( 'ccfm' ), admin_url() . '?ccfm=1' );
    $args = array(
        'id' => 'ccfm-link',
        'title' => _x( 'Clear Cache For Me', 'Button in admin bar', 'ccfm' ),
        'href' => $url
    );
    $wp_admin_bar->add_node( $args );
}

/**
 * Return the options for the school dropdown.
 */
function ccfm_ajax_ccfm() {
    if ( !check_ajax_referer( 'ccfm', 'nonce', false ) ){
        wp_die( 'The url you are trying to reach is no longer valid.', 401);
    }
    $needed_cap = ccfm_option( 'btn_cap', 'manage_options' );
    $is_success = false;
    if ( current_user_can( $needed_cap ) || current_user_can( 'manage_options' ) ) {
        ccfm_clear_cache_for_me( 'admin-bar-button' );
        $is_success = true;
    }

    wp_send_json( ['success' => $is_success ] );
}
add_action( 'wp_ajax_ccfm-ajax-ccfm', 'ccfm_ajax_ccfm' );


