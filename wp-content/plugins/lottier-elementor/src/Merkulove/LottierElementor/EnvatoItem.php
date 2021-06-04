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


namespace Merkulove\LottierElementor;

use Merkulove\LottierElementor;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
	header( 'Status: 403 Forbidden' );
	header( 'HTTP/1.1 403 Forbidden' );
	exit;
}

/**
 * SINGLETON: Class contain information about the envato item.
 **/
final class EnvatoItem {

	/**
	 * Plugins slug.
	 *
	 * @var string
	 * @since 3.0.5
	 **/
	private static $slug;

	/**
	 * Plugins Name.
	 *
	 * @var string
	 **/
	private static $plugin_name;

	/**
	 * In this option we store Envato Item ID.
	 *
	 * @var integer
	 **/
	public static $opt_item_id;

	/**
	 * The one true EnvatoItem.
	 *
	 * @var EnvatoItem
	 **/
	private static $instance;

	/**
	 * Sets up a new ServerReporter instance.
	 *
	 * @access public
	 **/
	private function __construct() {

		$this->initialization();

	}

	/**
	 * Initialize variables.
	 *
	 * @access public
	 * @return void
	 **/
	public function initialization() {

		/** Plugin slug. */
		self::$slug = 'lottier-elementor';

		/** Plugin name. */
		self::$plugin_name = 'Lottier for Elementor';

		/** In this option we store Envato Item ID. */
		self::$opt_item_id = 'mdp_' . self::$slug . '_envato_id';

	}

	/**
	 * Return CodeCanyon Item ID.
	 *
	 * @access public
	 * @return string
	 **/
	public function get_id() {

		/** Do we have Envato item id in cache? */
		$cache = new Cache();
		$key = self::$opt_item_id;
		$cached_item_id = $cache->get( $key, false );

		/** If cache exist */
		if ( ! empty( $cached_item_id ) ) { // Cache exist

			/** Extract item_id from cache record */
			$cached_item_id = json_decode( $cached_item_id, true );
			$item_id = (int)$cached_item_id[ $key ];

			/** ID out of the range of valid ID's */
			if ( $item_id <= 0 || $item_id > 99999999 ) {

				$item_id = 0;

				/** New request for outdated cache */
				if ( ! $cache->get( $key, true ) ) {

					$item_id = $this->get_remote_plugin_id();
					$cache->set( $key, [ $key => $item_id ], false );

				}

			}

		/** If cache not exist */
		} else { // Cache not exist

			$item_id = $this->get_remote_plugin_id();
			$cache->set( $key, [$key => $item_id], false );

		}

		return $item_id;

	}

	/**
	 * Return CodeCanyon Plugin ID from out server.
	 *
	 * @since 1.0.0
	 * @access public
	 **/
	private function get_remote_plugin_id() {

		/** Get url to request item id. */
		$url = $this->prepare_url();

		/** Get Envato item ID. */
		$item_id = wp_remote_get( $url );

		/** Check for errors. */
		if ( is_wp_error( $item_id ) || empty( $item_id['body'] ) ) { return 0; }

		/** Now in $item_id we have item id. */
		$item_id = json_decode( $item_id['body'], true );

		return (int)$item_id;

	}

	/**
	 * Build url to request item id.
	 *
	 * @access public
	 * @return int
	 **/
	private function prepare_url() {

		/** Build URL. */
		$url = 'https://merkulove.host/wp-content/plugins/mdp-purchase-validator/src/Merkulove/PurchaseValidator/GetMyId.php';
		$url .= '?plugin_name=' . urlencode( self::$plugin_name );

		return $url;

	}

	/**
	 * Main EnvatoItem Instance.
	 * Insures that only one instance of EnvatoItem exists in memory at any one time.
	 *
	 * @static
	 * @return EnvatoItem
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

}
