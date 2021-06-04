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

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
	header( 'Status: 403 Forbidden' );
	header( 'HTTP/1.1 403 Forbidden' );
	exit;
}

/**
 * Class used to implement UninstallTab tab on plugin settings page.
 **/
final class UninstallTab {

	/**
	 * The one true UninstallTab.
	 *
	 * @var UninstallTab
	 **/
	private static $instance;

	/**
	 * Sets up a new UninstallTab instance.
	 *
	 * @access public
	 **/
	private function __construct() {}

	/**
	 * Render form with all settings fields.
	 *
	 * @access public
	 **/
	public function render_form() {

		settings_fields( 'LottierElementorUninstallOptionsGroup' );
		do_settings_sections( 'LottierElementorUninstallOptionsGroup' );

	}

	/**
	 * Generate Uninstall Tab.
	 *
	 * @access public
	 **/
	public function add_settings() {

		/** Uninstall Tab. */
		register_setting( 'LottierElementorUninstallOptionsGroup', 'mdp_lottier_elementor_uninstall_settings' );
		add_settings_section( 'mdp_lottier_elementor_settings_page_uninstall_section', '', null, 'LottierElementorUninstallOptionsGroup' );

		/** Delete plugin. */
		add_settings_field( 'delete_plugin', esc_html__( 'Removal settings:', 'lottier-elementor' ), [$this, 'render_delete_plugin'], 'LottierElementorUninstallOptionsGroup', 'mdp_lottier_elementor_settings_page_uninstall_section' );

	}

	/**
	 * Render "Delete Plugin" field.
	 *
	 * @access public
	 **/
	public function render_delete_plugin() {

		/** Get uninstall settings. */
		$uninstall_settings = get_option( 'mdp_lottier_elementor_uninstall_settings' );

		/** Set Default value 'plugin'. */
		if ( ! isset( $uninstall_settings[ 'delete_plugin' ] ) ) {
			$uninstall_settings = [
				'delete_plugin' => 'plugin'
			];
		}

		$options = [
			'plugin' => esc_html__( 'Delete plugin only', 'lottier-elementor' ),
			'plugin+settings' => esc_html__( 'Delete plugin and settings', 'lottier-elementor' ),
		];

		/** Prepare description. */
		$helper_text = esc_html__( 'Choose which data to delete upon using the "Delete" action in the "Plugins" admin page.', 'lottier-elementor' );

		/** Render select. */
		UI::get_instance()->render_select(
			$options,
			$uninstall_settings[ 'delete_plugin' ], // Selected option.
			esc_html__( 'Delete plugin', 'lottier-elementor' ),
			$helper_text,
			[ 'name' => 'mdp_lottier_elementor_uninstall_settings[delete_plugin]' ]
		);

	}

	/**
	 * Main UninstallTab Instance.
	 * Insures that only one instance of UninstallTab exists in memory at any one time.
	 *
	 * @static
	 * @return UninstallTab
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

}
