<?php

/**
 * Fired during plugin deactivation
 *
 * @link       http://responsive-pixel.com/
 * @since      1.0.0
 *
 * @package    Trustify
 * @subpackage Trustify/includes
 */

/**
 * Fired during plugin deactivation.
 *
 * This class defines all code necessary to run during the plugin's deactivation.
 *
 * @since      1.0.0
 * @package    Trustify
 * @subpackage Trustify/includes
 * @author     Responsive-pixel <rajendrarijal@responsive-pixel.com>
 */
class Trustify_Deactivator {

	/**
	 * Short Description. (use period)
	 *
	 * Long Description.
	 *
	 * @since    1.0.0
	 */
	public static function deactivate() {
		if ( defined( 'TRUSTIFY_REMOVE_ALL_DATA' ) && true === TRUSTIFY_REMOVE_ALL_DATA ) {
			global $wpdb;
		    // Tables.
		    $wpdb->query( "DROP TABLE IF EXISTS {$wpdb->base_prefix}trustify_report" );

		    // Delete options.
		    $wpdb->query( "DELETE FROM $wpdb->options WHERE option_name LIKE 'trustify\_%';" );
		    $wpdb->query( "DELETE FROM $wpdb->options WHERE option_name LIKE 'trustify\_%';" );

		    // Clear any cached data that has been removed
		    wp_cache_flush();
		}
	}

}
