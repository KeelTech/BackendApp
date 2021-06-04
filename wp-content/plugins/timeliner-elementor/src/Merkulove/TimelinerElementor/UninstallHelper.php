<?php
/**
 * Timeliner for Elementor
 * Beautiful graphical representation of a period of time for Elementor
 * Exclusively on https://1.envato.market/timeliner-elementor
 *
 * @encoding        UTF-8
 * @version         1.0.0
 * @copyright       (C) 2018 - 2021 Merkulove ( https://merkulov.design/ ). All rights reserved.
 * @license         Envato License https://1.envato.market/KYbje
 * @contributors    Nemirovskiy Vitaliy (nemirovskiyvitaliy@gmail.com)
 * @support         help@merkulov.design
 **/

namespace Merkulove\TimelinerElementor;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
	header( 'Status: 403 Forbidden' );
	header( 'HTTP/1.1 403 Forbidden' );
	exit;
}

/**
 * SINGLETON: UninstallHelper class run when the users deletes the plugin.
 *
 * @since 1.0.0
 *
 **/
final class UninstallHelper {

	/**
	 * The one true UninstallHelper.
	 *
     * @since 1.0.0
     * @access private
	 * @var UninstallHelper
	 **/
	private static $instance;

    /**
     * Implement plugin uninstallation.
     *
     * @param string $uninstall_mode - Uninstall mode: plugin, plugin+settings, plugin+settings+data
     *
     * @since  1.0.0
     * @access public
     *
     * @return void
     **/
    public function uninstall( $uninstall_mode ) {

        /** Remove Plugin. */
        if ( 'plugin' === $uninstall_mode ) {

        /** Remove Plugin and Settings. */
        } elseif ( 'plugin+settings' === $uninstall_mode ) {

        /** Remove Plugin, Settings and all created data. */
        } elseif ( 'plugin+settings+data' === $uninstall_mode ) {

        }

    }

	/**
	 * Main UninstallHelper Instance.
	 * Insures that only one instance of UninstallHelper exists in memory at any one time.
	 *
	 * @static
     * @since 1.0.0
     * @access public
     *
	 * @return UninstallHelper
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

}
