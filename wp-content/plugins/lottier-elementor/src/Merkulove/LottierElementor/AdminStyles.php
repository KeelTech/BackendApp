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
 * SINGLETON: Class adds admin styles.
 **/
final class AdminStyles {

	/**
	 * The one true AdminStyles.
	 *
	 * @var AdminStyles
	 **/
	private static $instance;

	/**
	 * Sets up a new AdminStyles instance.
	 *
	 * @access public
	 **/
	private function __construct() {

		add_action( 'admin_enqueue_scripts', [ $this, 'admin_styles' ] );

	}

	/**
	 * Add CSS for admin area.
	 *
	 * @return void
	 **/
	public function admin_styles() {

		/** Plugin Settings Page. */
		$this->settings_styles();

		/** Plugins page. Styles for "View version details" popup. */
		$this->plugin_update_styles();

	}

	/**
	 * Styles for plugin setting page.
	 *
	 * @return void
	 **/
	private function settings_styles() {

		/** Add styles only on setting page */
		$screen = get_current_screen();
		if ( null === $screen ) { return; }

		/** Settings Page. */
		$bases = [
			'elementor_page_mdp_lottier_elementor_settings',
			'settings_page_mdp_lottier_elementor_settings'
		];

		/** Add styles only on plugin settings page */
		if ( in_array( $screen->base, $bases ) ) {

			wp_enqueue_style( 'mdp-ui', LottierElementor::$url . 'css/merkulov-ui.min.css', [], LottierElementor::$version );
			wp_enqueue_style( 'mdp-admin', LottierElementor::$url . 'css/admin' . LottierElementor::$suffix . '.css', [], LottierElementor::$version );

		}

	}

	/**
	 * Styles for plugins page. "View version details" popup.
	 *
	 * @return void
	 **/
	private function plugin_update_styles() {

		/** Plugin install page, for style "View version details" popup. */
		$screen = get_current_screen();
		if ( null === $screen || $screen->base !== 'plugin-install' ) { return; }

		/** Styles only for our plugin. */
		if ( isset( $_GET['plugin'] ) && $_GET['plugin'] === 'lottier-elementor' ) {

			wp_enqueue_style( 'mdp-lottier-elementor-plugin-install', LottierElementor::$url . 'css/plugin-install' . LottierElementor::$suffix . '.css', [], LottierElementor::$version );

		}

	}

	/**
	 * Main AdminStyles Instance.
	 *
	 * Insures that only one instance of AdminStyles exists in memory at any one time.
	 *
	 * @static
	 * @return AdminStyles
	 **/
	public static function get_instance() {

        /** @noinspection SelfClassReferencingInspection */
        if ( ! isset( self::$instance ) && ! ( self::$instance instanceof AdminStyles ) ) {

			self::$instance = new AdminStyles;

		}

		return self::$instance;

	}

}
