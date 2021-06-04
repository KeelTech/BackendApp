<?php
/**
 * Lottier for Elementor
 * Lottie animations in just a few clicks without writing a single line of code.
 * Exclusively on https://1.envato.market/lottier-elementor
 *
 * @encoding        UTF-8
 * @version         1.0.3
 * @copyright       (C) 2018 - 2020 Merkulove ( https://merkulov.design/ ). All rights reserved.
 * @license         Envato License https://1.envato.market/KYbje
 * @contributors    Vitaliy Nemirovskiy (nemirovskiyvitaliy@gmail.com), Dmitry Merkulov (dmitry@merkulov.design)
 * @support         help@merkulov.design
 * @license         Envato License https://1.envato.market/KYbje
 **/


namespace Merkulove;

/** Include plugin autoloader for additional classes. */
require __DIR__ . '/src/autoload.php';

use Merkulove\LottierElementor\Cache;
use Merkulove\LottierElementor\Helper;
use Merkulove\LottierElementor\EnvatoItem;

/** Exit if uninstall.php is not called by WordPress. */
if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
	header( 'Status: 403 Forbidden' );
	header( 'HTTP/1.1 403 Forbidden' );
	exit;
}

/**
 * Class used to implement Uninstall of plugin.
 **/
final class Uninstall {

	/**
	 * The one true Uninstall.
	 *
	 * @var Uninstall
	 **/
	private static $instance;

	/**
	 * Sets up a new Uninstall instance.
	 *
	 * @access public
	 **/
	private function __construct() {

		/** Get Uninstall mode. */
		$uninstall_mode = $this->get_uninstall_mode();

		/** Send uninstall Action to our host. */
		Helper::get_instance()->send_action( 'uninstall', 'lottier-elementor', '1.0.3' );

		/** Remove Plugin and Settings. */
		if ( 'plugin+settings' === $uninstall_mode ) {

			/** Remove Plugin Settings. */
			$this->remove_settings();

		}

	}

	/**
	 * Return uninstall mode.
	 * plugin - Will remove the plugin only. Settings and Audio files will be saved. Used when updating the plugin.
	 * plugin+settings - Will remove the plugin and settings. Audio files will be saved. As a result, all settings will be set to default values. Like after the first installation.
	 *
	 * @access public
	 **/
	public function get_uninstall_mode() {

		$uninstall_settings = get_option( 'mdp_lottier_elementor_uninstall_settings' );

		if( isset( $uninstall_settings['mdp_lottier_elementor_uninstall_settings'] ) AND $uninstall_settings['mdp_lottier_elementor_uninstall_settings'] ) { // Default value.
			$uninstall_settings = [
				'delete_plugin' => 'plugin'
			];
		}

		return $uninstall_settings['delete_plugin'];

	}

	/**
	 * Delete Plugin Options.
	 *
	 * @access public
	 **/
	public function remove_settings() {

		$settings = [
			'mdp_lottier_elementor_envato_id',
			'mdp_lottier_elementor_settings',
			'mdp_lottier_elementor_uninstall_settings',
			'mdp_lottier_elementor_send_action_install',
			'envato_purchase_code_' . EnvatoItem::get_instance()->get_id() // Envato item ID.
		];

		/** Remove settings */
		foreach ( $settings as $key ) {

			if ( is_multisite() ) { // For Multisite.
				if ( get_site_option( $key ) ) {
					delete_site_option( $key );
				}
			} else {
				if ( get_option( $key ) ) {
					delete_option( $key );
				}
			}
		}

		/** Remove cache table */
		$cache = new Cache();
		$cache->drop_cache_table();

	}

	/**
	 * Main Uninstall Instance.
	 * Insures that only one instance of Uninstall exists in memory at any one time.
	 *
	 * @static
	 * @return Uninstall
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

}

/** Runs on Uninstall of plugin. */
Uninstall::get_instance();
