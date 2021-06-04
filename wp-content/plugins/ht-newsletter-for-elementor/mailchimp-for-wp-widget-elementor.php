<?php
/**
 * Plugin Name: HT Newsletter for Elementor
 * Description: The HT Newsletter for Elementor is a elementor addons for WordPress.
 * Plugin URI:  https://htplugins.com/
 * Author:      HT Plugins
 * Author URI:  https://profiles.wordpress.org/htplugins/
 * Version:     1.0.6
 * License:     GPL2
 * License URI:  https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: ht-mailchimpform
 * Domain Path: /languages
*/

if( ! defined( 'ABSPATH' ) ) exit(); // Exit if accessed directly

if ( ! function_exists('is_plugin_active')) { include_once( ABSPATH . 'wp-admin/includes/plugin.php' ); }

define( 'HTMAILCHIMP_VERSION', '1.0.6' );
define( 'HTMAILCHIMP_PL_URL', plugins_url( '/', __FILE__ ) );
define( 'HTMAILCHIMP_PL_PATH', plugin_dir_path( __FILE__ ) );

//Enqueue style
function htmailchimp_assests_enqueue() {
    wp_enqueue_style('htmailchimp-widgets', HTMAILCHIMP_PL_URL . 'assests/css/ht-mailchimpform.css', '', HTMAILCHIMP_VERSION );
}
add_action( 'wp_enqueue_scripts', 'htmailchimp_assests_enqueue' );

if( is_plugin_active( 'mailchimp-for-wp/mailchimp-for-wp.php' ) ){
    
    // Elementor Widgets File Call
    function htmailchimp_elementor_widgets(){
        include( HTMAILCHIMP_PL_PATH.'include/elementor_widgets.php' );
    }
    add_action('elementor/widgets/widgets_registered','htmailchimp_elementor_widgets');

}

// Check Plugins is Installed or not
if( !function_exists( 'htmailchimp_is_plugins_active' ) ){
    function htmailchimp_is_plugins_active( $pl_file_path = NULL ){
        $installed_plugins_list = get_plugins();
        return isset( $installed_plugins_list[$pl_file_path] );
    }
}

// Load Plugins
function htmailchimp_load_plugin() {
    load_plugin_textdomain( 'ht-mailchimpform' );
    if ( ! did_action( 'elementor/loaded' ) ) {
        add_action( 'admin_notices', 'htmailchimp_check_elementor_status' );
        return;
    }

    if( !is_plugin_active( 'mailchimp-for-wp/mailchimp-for-wp.php' ) ){
        add_action( 'admin_notices', 'htmailchimp_check_mailchimp_status' );
        return;
    }
}
add_action( 'plugins_loaded', 'htmailchimp_load_plugin' );

// Check Elementor install or not.
function htmailchimp_check_elementor_status(){
    $elementor = 'elementor/elementor.php';
    if( htmailchimp_is_plugins_active( $elementor ) ) {
        if( ! current_user_can( 'activate_plugins' ) ) {
            return;
        }
        $activation_url = wp_nonce_url( 'plugins.php?action=activate&amp;plugin=' . $elementor . '&amp;plugin_status=all&amp;paged=1&amp;s', 'activate-plugin_' . $elementor );

        $message = '<p>' . __( 'HT MailChimp Form Addons not working because you need to activate the Elementor plugin.', 'ht-mailchimpform' ) . '</p>';
        $message .= '<p>' . sprintf( '<a href="%s" class="button-primary">%s</a>', $activation_url, __( 'Activate Elementor Now', 'ht-mailchimpform' ) ) . '</p>';
    } else {
        if ( ! current_user_can( 'install_plugins' ) ) {
            return;
        }
        $install_url = wp_nonce_url( self_admin_url( 'update.php?action=install-plugin&plugin=elementor' ), 'install-plugin_elementor' );
        $message = '<p>' . __( 'HT MailChimp Form Addons not working because you need to install the Elementor plugin', 'ht-mailchimpform' ) . '</p>';
        $message .= '<p>' . sprintf( '<a href="%s" class="button-primary">%s</a>', $install_url, __( 'Install Elementor Now', 'ht-mailchimpform' ) ) . '</p>';
    }
    echo '<div class="error"><p>' . $message . '</p></div>';
}

// Check Elementor install or not.
function htmailchimp_check_mailchimp_status(){
    $mailchimpform = 'mailchimp-for-wp/mailchimp-for-wp.php';
    if( htmailchimp_is_plugins_active( $mailchimpform ) ) {
        if( ! current_user_can( 'activate_plugins' ) ) {
            return;
        }
        $activation_url = wp_nonce_url( 'plugins.php?action=activate&amp;plugin=' . $mailchimpform . '&amp;plugin_status=all&amp;paged=1&amp;s', 'activate-plugin_' . $mailchimpform );

        $message = '<p>' . __( 'HT MailChimp Form Addons not working because you need to activate the Mailchimp for WordPress plugin.', 'ht-mailchimpform' ) . '</p>';
        $message .= '<p>' . sprintf( '<a href="%s" class="button-primary">%s</a>', $activation_url, __( 'Activate Now', 'ht-mailchimpform' ) ) . '</p>';
    } else {
        if ( ! current_user_can( 'install_plugins' ) ) {
            return;
        }
        $install_url = wp_nonce_url( self_admin_url( 'update.php?action=install-plugin&plugin=mailchimp-for-wp' ), 'install-plugin_mailchimp-for-wp' );
        $message = '<p>' . __( 'HT MailChimp Form Addons not working because you need to install the Mailchimp for WordPress plugin', 'ht-mailchimpform' ) . '</p>';
        $message .= '<p>' . sprintf( '<a href="%s" class="button-primary">%s</a>', $install_url, __( 'Install Now', 'ht-mailchimpform' ) ) . '</p>';
    }
    echo '<div class="error"><p>' . $message . '</p></div>';
}



?>