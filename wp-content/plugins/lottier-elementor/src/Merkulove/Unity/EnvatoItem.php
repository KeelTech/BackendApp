<?php
/**
 * Lottier for Elementor
 * Lottie animations in just a few clicks without writing a single line of code.
 * Exclusively on https://1.envato.market/lottier-elementor
 *
 * @encoding        UTF-8
 * @version         1.0.4
 * @copyright       (C) 2018 - 2021 Merkulove ( https://merkulov.design/ ). All rights reserved.
 * @license         Envato License https://1.envato.market/KYbje
 * @contributors    Vitaliy Nemirovskiy (nemirovskiyvitaliy@gmail.com), Cherviakov Vlad (vladchervjakov@gmail.com), Dmitry Merkulov (dmitry@merkulov.design)
 * @support         help@merkulov.design
 **/

namespace Merkulove\LottierElementor\Unity;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
    header( 'Status: 403 Forbidden' );
    header( 'HTTP/1.1 403 Forbidden' );
    exit;
}

/**
 * SINGLETON: Class contain information about the envato item.
 *
 * @since 1.0.0
 *
 **/
final class EnvatoItem {

	/**
	 * The one true EnvatoItem.
	 *
	 * @var EnvatoItem
	 **/
	private static $instance;

	/**
	 * Return CodeCanyon Item ID.
	 *
     * @since 1.0.0
	 * @access public
     *
	 * @return int
	 **/
	public function get_id() {

	    return 26261526;

		/** Do we have Envato item id in cache? */
		$cache = new Cache();

        /** In this option we store Envato Item ID. */
        $key = 'mdp_' . Plugin::get_slug() . '_envato_id';
		$cached_item_id = $cache->get( $key, false );

		/** If cache exist */
		if ( ! empty( $cached_item_id ) ) {

			/** Extract item_id from cache record */
			$cached_item_id = json_decode( $cached_item_id, true );
			$item_id = (int)$cached_item_id[ $key ];

			/** ID out of the range of valid ID's */
			if ( $item_id <= 0 || $item_id > 99999999 ) {

				$item_id = 0;

				/** New request for outdated cache. */
				if ( ! $cache->get( $key, true ) ) {

					$item_id = $this->get_remote_plugin_id();
					$cache->set( $key, [ $key => $item_id ], false );

				}

			}

		/** If cache not exist */
		} else {

            $item_id = $this->get_remote_plugin_id();
            $cache->set( $key, [$key => $item_id], false );

		}

		return $item_id;

	}

	/**
	 * Return CodeCanyon Plugin ID from out server.
	 *
	 * @since 1.0.0
	 * @access private
     *
     * @return int
     **/
	private function get_remote_plugin_id() {

		/** Get url to request item id. */
		$url = $this->prepare_url();

		/** Get Envato item ID. */
		$item_id = wp_remote_get( $url, [
            'sslverify'  => Settings::get_instance()->options[ 'check_ssl' ] === 'on'
        ] );

		/** Check for errors. */
		if ( is_wp_error( $item_id ) || empty( $item_id['body'] ) ) { return 0; }

		/** Now in $item_id we have item id. */
		$item_id = json_decode( $item_id['body'], true );

		return (int) $item_id;

	}

	/**
	 * Build url to request item id.
	 *
	 * @access private
     * @since 1.0.0
     *
	 * @return int
	 **/
	private function prepare_url() {

		/** Build URL. */
		$url = 'https://merkulove.host/wp-content/plugins/mdp-purchase-validator/src/Merkulove/PurchaseValidator/GetMyId.php';
		$url .= '?plugin_name=' . urlencode( Plugin::get_name() );

		return $url;

	}

	/**
	 * Main EnvatoItem Instance.
	 * Insures that only one instance of EnvatoItem exists in memory at any one time.
	 *
	 * @static
     * @since 1.0.0
     * @access public
     *
	 * @return EnvatoItem
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

}
