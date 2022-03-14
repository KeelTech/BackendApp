<?php
/*********************************
 * Options page
 *********************************/


/**
 *  Add menu page
 */
function ccfm_options_add_page() {
    $ccfm_hook = add_options_page( 'Clear Cache for Me Settings', // Page title
                      'Clear Cache for Me', // Label in sub-menu
                      'manage_options', // capability
                      'ccfm-options', // page identifier 
                      'ccfm_options_do_page' ); // call back function name
                      
    // add_action( 'load-' . $ccfm_hook, 'ccfm_load_admin_js' );
}
add_action( 'admin_menu', 'ccfm_options_add_page' );

/**
 * Init plugin options to white list our options
 */
function ccfm_options_init(){
    register_setting( 'ccfm_options_options', 'ccfm_options', 'ccfm_options_validate' );
}
add_action( 'admin_init', 'ccfm_options_init' );

/**
 * Remember user closed the hosting notice 
 */
function ccfm_hosting_notice_response() {
    if ( !check_ajax_referer( 'ccfm-admin-nonce', 'nonce', false ) ){
        wp_send_json( 0 );
    }
    $stats = get_option( '_ccfm_stats', array() );

    if ( !is_array( $stats ) ) {
        $stats = array();
    }

    set_transient( 'ccfm_hosting_notice', 1, YEAR_IN_SECONDS / 2 );
    // $stats['hosting_notice'] = 1;
    // update_option( '_ccfm_stats', $stats );
    wp_send_json( 1 );
}
add_action('wp_ajax_ccfm-notice-response', 'ccfm_hosting_notice_response');


/**
 * Draw the menu page itself
 */
function ccfm_options_do_page() {
    global $wp_roles;

    if ( !current_user_can( 'manage_options' ) ) { 
     wp_die( __( 'You do not have sufficient permissions to access this page.' ) ); 
    } 

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
    <style>
        .api-table th {
            text-align: left;
        }
        .api-table th.api-col1 {
            width:400px;
        }
        .form-table input[type="text"],
        .form-table textarea,
        .form-table select  {
            width:400px;
        }
        .ccfm-hidden {
            display: none;
        }
        .field-checkboxes {
            -webkit-columns: 300px 2; /* Chrome, Safari, Opera */
            -moz-columns: 300px 2; /* Firefox */
            columns: 300px 2;
        }
        .ccfm-settings h3 {
            margin-bottom: 0;
        }

        .ccfm-settings a .dashicons {
            text-decoration: none;
        }
        .ccfm-notice-hosting {
            position: relative;
        }
        .notice-dismiss:before {
            display: none;
        }


    </style>
    <div class="ccfm-settings wrap">
        <h2><?php _e( 'Clear Cache for Me Settings', 'ccfm' ); ?></h2>
        <?php if ( ccfm_show_hosting_notice() ) : ?>
        <div class="notice notice-info ccfm-notice-hosting"> 
            <p>If you're looking for a fast webhost, you may want to consider <a href="https://webheadcoder.com/cloud-web-hosts/" target="_blank">managed hosts using cloud services</a>.</p>
            <a href="#" class="notice-dismiss">Dismiss for 6 months</a>
        </div>
        <?php endif; ?>


        <form id="cchim" method="post" action="options.php">
            <?php settings_fields( 'ccfm_options_options' ); ?>
            <?php $options = get_option( 'ccfm_options' );?>
            <h3>Status</h3>
            <p>
            <?php 
                $cache_name = ccfm_get_cache_system_name();
                if ( !empty( $cache_name ) ) :
                    $timestamp = get_option( '_ccfm_style_timestamp_theme', 0 );

            ?>
                <?php _e( 'Cache will be cleared for:', 'ccfm' ); ?> <strong><?php echo $cache_name; ?></strong>
                <br>
                <?php if ( !empty( $timestamp ) ) : 
                    $date_string = get_date_from_gmt( date( 'Y-m-d H:i:s', $timestamp ), get_option( 'date_format' ) . ' ' . get_option( 'time_format' ) );
                ?>
                <?php _e( 'Last cleared by this plugin:', 'ccfm' ); ?> <strong><?php echo $date_string; ?></strong>
                <?php else: ?>
                <?php _e( 'This plugin has not cleared the cache for you yet!', 'ccfm' ); ?>
                <?php endif; ?>
            <?php else : ?>
                <?php echo sprintf( __( 'No supported caching systems found.  <a href="%s" target="_blank">Click here to learn more</a>.', 'ccfm' ), 'https://webheadcoder.com/clear-cache-for-me/' ); ?>
            <?php endif; ?>
            </p>
            <br>
            <h3>Button Settings</h3>
            <table class="form-table">
                <tr valign="top"><th scope="row"><?php _e( 'Required capability to see the button (on dashboard and top admin bar).', 'ccfm' ); ?></th>
                    <td>
                        <select name="ccfm_options[btn_cap]" id="btn_cap">
                            <?php foreach ( $caps as $cap ) : ?>
                                <option value="<?php echo esc_attr($cap); ?>" <?php selected( ccfm_option( 'btn_cap', 'manage_options' ), $cap );?>><?php echo $cap; ?></option>
                            <?php endforeach; ?>
                        </select>
                        <br><i><?php _e( 'Users with this capability will be able to see the \'Clear Cache Now!\' button on the dashboard', 'ccfm' ); ?></i>
                    </td>
                </tr>
                <tr valign="top"><th scope="row"><?php _e( 'Instructions to show above button (optional):', 'ccfm' ); ?></th>
                    <td>
                        <textarea rows="10" name="ccfm_options[btn_instructions]"><?php echo esc_textarea( isset( $options['btn_instructions'] ) ? $options['btn_instructions'] : __( 'If you\'re not seeing your changes on your public pages, it might be cached.  Click the button below to see a fresh version of your pages.', 'ccfm' ) ); ?></textarea>
                        <br><i><?php _e( 'These instructions will appear on the dashboard above the Clear Cache button.', 'ccfm' ); ?></i>
                    </td>
                </tr>
                <tr valign="top"><th scope="row"><?php _e( 'Show \'Clear Cache For Me\' button in admin bar.', 'ccfm' ); ?></th>
                    <td>
                        <input type="checkbox" name="ccfm_options[btn_admin_bar]" value="1" <?php checked( 1, isset( $options['btn_admin_bar'] ) ? $options['btn_admin_bar'] : 1 ); ?>> Yes
                        <?php if ( empty( $cache_name ) ) : ?>
                        <br><i style="color: #dc3232;"><?php _e( 'The button will not show due to the status shown above.', 'ccfm' ); ?></i>
                        <?php endif; ?>
                    </td>
                </tr>


            </table>

            <br>
            <h3>Development Mode</h3>

            <table class="form-table">
                <tr valign="top"><th scope="row"><?php _e( 'Force browser to fetch a fresh copy of CSS and JS files on each page load.', 'ccfm' ); ?> <?php echo sprintf( __( '<a href="%s" target="_blank"><span class="dashicons dashicons-editor-help"></span></a>', 'ccfm' ), 'https://webheadcoder.com/clear-cache-for-me/#dev-mode' ); ?></th>
                    <td>
                        <input type="checkbox" name="ccfm_options[dev_mode_assets]" value="1" <?php checked( 1, isset( $options['dev_mode_assets'] ) ? $options['dev_mode_assets'] : 0 ); ?>> Yes
                    </td>
                </tr>


            </table>
            <br>
            <p class="submit">
            <input type="submit" class="button-primary" value="<?php _e( 'Save Changes' ) ?>" />
            </p>
        </form>
    </div>
    <?php   
}

/**
 * Sanitize and validate input. Accepts an array, return a sanitized array.
 */
function ccfm_options_validate( $input ) {
    global $wp_settings_errors;

    // all checkboxes
    $setting_names = array( 
        'btn_admin_bar',
        'dev_mode_assets'
    );
    foreach( $setting_names as $name ) {
        if ( !isset( $input[$name] ) ) {
            $input[$name] = 0;
        }  
    }
      
    return $input;
}

/**
 * Enqueue scripts for the admin side.
 */
function ccfm_options_enqueue_scripts( $hook ) {
    if( 'settings_page_ccfm-options' != $hook )
        return;

    if ( ccfm_show_hosting_notice() ) {
        wp_enqueue_script( 'ccfm-admin',
            plugins_url( 'js/admin.js', __FILE__ ),
            array( 'jquery' ),
            CCFM_VERSION, true );

        wp_localize_script( 'ccfm-admin', 'ccfm_admin', array(
            'nonce'         => wp_create_nonce( 'ccfm-admin-nonce' )
        ));
    }
}
add_action( 'admin_enqueue_scripts', 'ccfm_options_enqueue_scripts' );

/**
 * Return true if hosting notice should show.
 */
function ccfm_show_hosting_notice() {
    global $kinsta_cache;
    $stats = get_option( '_ccfm_stats', 0 );

    if ( !empty( $stats['hosting_notice'] ) ) {
        return false;
    }

    if ( !empty( get_transient( 'ccfm_hosting_notice ' ) ) ) {
        return false;
    }

    $cache_system_key = ccfm_get_caching_system_used();
    if ( $cache_system_key == 'kinsta' || $cache_system_key == 'wpengine' || $cache_system_key == 'breeze' ) {
        return false;
    }

    return true;
}

