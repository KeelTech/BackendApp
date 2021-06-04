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
 * Class used to implement base plugin features.
 */
final class PluginHelper {

	/**
	 * The one true Helper.
	 *
	 * @var PluginHelper
	 **/
	private static $instance;

	/**
	 * Sets up a new Helper instance.
	 *
	 * @access public
	 **/
	private function __construct() {

		/** Add plugin links. */
		add_filter( 'plugin_action_links_' . LottierElementor::$basename, [ $this, 'add_links' ] );

		/** Add plugin meta. */
		add_filter( 'plugin_row_meta', [ $this, 'add_row_meta' ], 10, 2 );

		/** Load JS and CSS for Backend Area. */
		$this->enqueue_backend();

	}

	/**
	 * Load JS and CSS for Backend Area.
	 *
	 * @access public
	 **/
	public function enqueue_backend() {

		/** Add admin styles. */
		add_action( 'admin_enqueue_scripts', [ $this, 'admin_styles' ] );

		/** Add admin javascript. */
		add_action( 'admin_enqueue_scripts', [ $this, 'admin_scripts' ] );

	}

	/**
	 * Add CSS for admin area.
	 *
	 * @return void
	 **/
	public function admin_styles() {

		$screen = get_current_screen();
		if ( null === $screen ) { return; }

		/** Add styles only on WP Plugins page. */
		if ( $screen->base === 'plugins' ) {

			wp_enqueue_style( 'mdp-plugins', LottierElementor::$url . 'css/plugins' . LottierElementor::$suffix . '.css', [], LottierElementor::$version );

		}

	}

	/**
	 * Add JS for admin area.
	 *
	 * @return void
	 **/
	public function admin_scripts() {

		$screen = get_current_screen();
		if ( null === $screen ) { return; }

		/** Add scripts only on WP Plugins page. */
		if ( $screen->base === 'plugins' ) {
			wp_enqueue_script( 'mdp-plugins', LottierElementor::$url . 'js/plugins' . LottierElementor::$suffix . '.js', [ 'jquery' ], LottierElementor::$version, true );
		}

	}

	/**
	 * Add "merkulov.design" and  "Envato Profile" links on plugin page.
	 *
	 * @param array $links Current links: Deactivate | Edit
	 * @return array
	 * @access public
	 */
	public function add_links( $links ) {

		array_unshift( $links, '<a title="' . esc_html__( 'Settings', 'lottier-elementor' ) . '" href="' . admin_url( 'admin.php?page=mdp_lottier_elementor_settings' ) . '">' . esc_html__( 'Settings', 'lottier-elementor' ) . '</a>' );
		$links[] = '<a title="' . esc_html__( 'Documentation', 'lottier-elementor' ) . '" href="https://docs.merkulov.design/tag/lottier" target="_blank">' . esc_html__( 'Documentation', 'lottier-elementor' ) . '</a>';
		$links[] = '<a href="https://1.envato.market/cc-merkulove" target="_blank" class="cc-merkulove"><img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB2aWV3Qm94PSIwIDAgMTE3Ljk5IDY3LjUxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8ZGVmcz4KPHN0eWxlPi5jbHMtMSwuY2xzLTJ7ZmlsbDojMDA5ZWQ1O30uY2xzLTIsLmNscy0ze2ZpbGwtcnVsZTpldmVub2RkO30uY2xzLTN7ZmlsbDojMDA5ZWUyO308L3N0eWxlPgo8L2RlZnM+CjxjaXJjbGUgY2xhc3M9ImNscy0xIiBjeD0iMTUiIGN5PSI1Mi41MSIgcj0iMTUiLz4KPHBhdGggY2xhc3M9ImNscy0yIiBkPSJNMzAsMmgwQTE1LDE1LDAsMCwxLDUwLjQ4LDcuNUw3Miw0NC43NGExNSwxNSwwLDEsMS0yNiwxNUwyNC41LDIyLjVBMTUsMTUsMCwwLDEsMzAsMloiLz4KPHBhdGggY2xhc3M9ImNscy0zIiBkPSJNNzQsMmgwQTE1LDE1LDAsMCwxLDk0LjQ4LDcuNUwxMTYsNDQuNzRhMTUsMTUsMCwxLDEtMjYsMTVMNjguNSwyMi41QTE1LDE1LDAsMCwxLDc0LDJaIi8+Cjwvc3ZnPgo=" alt="' . esc_html__( 'Plugins', 'lottier-elementor' ) . '">' . esc_html__( 'Plugins', 'lottier-elementor' ) . '</a>';

		return $links;

	}

	/**
	 * Add "Rate us" link on plugin page.
	 *
	 * @param array $links Current links: Deactivate | Edit
	 * @param $file - Path to the plugin file relative to the plugins directory.
	 * @return array
	 * @access public
	 */
	public function add_row_meta( $links, $file ) {

		if ( LottierElementor::$basename !== $file ) {
			return $links;
		}

		$stars = esc_html__( 'Rate this plugin:', 'lottier-elementor' );
		$stars .= "<span class='mdp-rating-stars'>";
		for ( $i = 1; $i <= 5; $i++) {
			$stars .= "<a href='https://1.envato.market/cc-downloads' target='_blank'><span class='dashicons dashicons-star-filled'></span></a>";
		}
		$stars .= "<span>";

		$links[] = $stars;
		return $links;

	}

	/**
	 * Remove unnecessary WordPress branding and messages
	 */
	public function remove_unnecessary() {

		/** Remove all "third-party" notices from plugin settings page. */
		add_action( 'in_admin_header', [ $this, 'remove_all_notices' ], 1000 );

		/** Remove "Thank you for creating with WordPress" and WP version only from plugin settings page. */
		add_action( 'admin_enqueue_scripts', [ $this, 'remove_wp_copyrights' ] );

	}

	/**
	 * Remove "Thank you for creating with WordPress" and WP version only from plugin settings page.
	 *
	 * @access private
	 * @return void
	 **/
	public function remove_wp_copyrights() {

		/** Remove "Thank you for creating with WordPress" and WP version from plugin settings page. */
		$screen = get_current_screen(); // Get current screen.
		if ( null === $screen ) { return; }

		/** Plugin Settings Page. */
		$bases = [
			'elementor_page_mdp_lottier_elementor_settings',
			'settings_page_mdp_lottier_elementor_settings'
		];

		/** Plugin Settings Page. */
		if ( in_array( $screen->base, $bases ) ) {
			add_filter( 'admin_footer_text', '__return_empty_string', 11 );
			add_filter( 'update_footer', '__return_empty_string', 11 );
		}

	}

	/**
	 * Remove all other notices.
	 *
	 * @access public
	 **/
	public function remove_all_notices() {

		/** Work only on plugin settings page. */
		$screen = get_current_screen();
		if ( null === $screen ) { return; }

		$bases = [
			'elementor_page_mdp_lottier_elementor_settings',
			'settings_page_mdp_lottier_elementor_settings'
		];

		/** Remove other notices. */
		if ( in_array( $screen->base, $bases ) ) {

			remove_all_actions( 'admin_notices' );
			remove_all_actions( 'all_admin_notices' );

		}

	}

	/**
	 * Main Helper Instance.
	 * Insures that only one instance of Helper exists in memory at any one time.
	 *
	 * @static
	 * @return PluginHelper
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

}

