<?php

/**
 * Fired during plugin activation
 *
 * @link       http://responsive-pixel.com/
 * @since      1.0.0
 *
 * @package    Trustify
 * @subpackage Trustify/includes
 */

/**
 * Fired during plugin activation.
 *
 * This class defines all code necessary to run during the plugin's activation.
 *
 * @since      1.0.0
 * @package    Trustify
 * @subpackage Trustify/includes
 * @author     Responsive-pixel <rajendrarijal@responsive-pixel.com>
 */
class Trustify_Activator {

    private static $db_updates = array(
        '2.0' => array(
            'trustify_update_20_db_column'
        ),
    );
    
    public function __construct() {
        self::update();
    }

	/**
	 * Short Description. (use period)
	 *
	 * Long Description.
	 *
	 * @since    1.0.0
	 */
	public static function activate() {
        if ( ! is_blog_installed() ) {
            return;
        }
        self::create_tables();
	}

    /**
     * plugins table creation
     * @global object $wpdb
     */
    private static function create_tables() {
        global $wpdb;
        $wpdb->hide_errors();
        require_once( ABSPATH . 'wp-admin/includes/upgrade.php' );

        dbDelta( self::get_schema() );
    }

    /**
     * Plugin table schema
     * @global object $wpdb
     * @return string
     */
    private static function get_schema() {
        global $wpdb;
        $collate = '';

        if ( $wpdb->has_cap( 'collation' ) ) {
            $collate = $wpdb->get_charset_collate();
        }
        $tables = "CREATE TABLE IF NOT EXISTS {$wpdb->base_prefix}trustify_report (
            report_id BIGINT UNSIGNED NOT NULL auto_increment,
            product_id BIGINT UNSIGNED NOT NULL DEFAULT 1,
            date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY  (report_id ),
            KEY product_id (product_id )
        ) $collate;";
        return $tables;
    }

    /**
     * Get list of DB update callbacks.
     *
     * @since  1.0.8
     * @return array
     */
    public static function get_db_update_callbacks() {
        return self::$db_updates;
    }
    
    /**
     * Update plugin
     */
    private static function update() {
        $current_db_version = get_option( 'trustify_db_version' );
        if (version_compare(TRUSTIFY_PLUGIN_VERSION, $current_db_version, '=' ) ){
            return;
        }
        foreach ( self::get_db_update_callbacks() as $version => $update_callbacks) {
            if (version_compare( $current_db_version, $version, '<' ) ) {
                foreach ( $update_callbacks as $update_callback) {
                    call_user_func( $update_callback);
                }
            }
        }
        self::update_db_version();
    }

    /**
     * Update DB version to current.
     *
     * @param string|null $version New WooCommerce DB version or null.
     */
    public static function update_db_version( $version = null) {
        delete_option( 'trustify_db_version' );
        add_option( 'trustify_db_version', is_null( $version) ? TRUSTIFY_PLUGIN_VERSION : $version );
    }

}
