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
 * SINGLETON: Class used to render plugin settings fields.
 **/
final class SettingsFields {

	/**
	 * The one true SettingsFields.
	 *
	 * @var SettingsFields
	 **/
	private static $instance;

	/**
	 * Settings prefix
	 * @var string
	 */
	private $prefix = 'mdp_lottier_elementor_settings';

	/**
	 * Tabs list
	 * 'general' => [ 'icon' => 'cloud', 'name' => 'General' ]
	 *
	 * @var array
	 */
	public $tabs = [];

	/**
	 * Default settings
	 * @var string[]
	 */
	public $defaults = [

		'api_key' => '',

	];

	/**
	 * Set tabs and settings groups
	 */
	public function tabs() {

		if ( count( self::$instance->tabs ) < 1 ) {
			return;
		}

		/** General tab */
		$this->tab_general();

	}

	/**
	 * Add Tabs setting
	 * @param $tab - Tab Slug
	 */
	public function tab_content( $tab ) {

		if ( count( self::$instance->tabs ) < 1 ) {
			return;
		}

		if ( 'general' === $tab ) {
			echo '<h3>' . esc_html__( 'New Tab', 'lottier-elementor' ) . '</h3>';
			settings_fields( 'LottierElementorOptionsGroup' );
			do_settings_sections( 'LottierElementorOptionsGroup' );}

	}

	/**
	 * Create General Tab.
	 *
	 * @access public
	 **/
	public function tab_general() {

		/** General Tab. */
		$group_name = 'LottierElementorOptionsGroup';
		$section_id = 'mdp_lottier_elementor_settings_page_general_section';
		$option_name = 'mdp_lottier_elementor_settings';

		/** Create settings section. */
		register_setting( $group_name, $option_name );
		add_settings_section( $section_id, '', null, $group_name );

		/** Render Settings fields. */
		add_settings_field( 'api_key', esc_html__( 'Setting:', 'lottier-elementor' ), ['\Merkulove\LottierElementor\SettingsFields', 'api_key' ], $group_name, $section_id );

	}

	/**
	 * Render UI box
	 *
	 * @access public
	 * @return void
	 **/
	public static function api_key() {

		UI::get_instance()->render_input(
			Settings::get_instance()->options[ 'api_key' ], // Selected option.
			esc_html__( 'Setting ', 'lottier-elementor' ),
			'',
			[
				'name' => self::get_instance()->prefix . '[api_key]',
				'id' => 'mdp-lottier-elementor-settings-api-key'
			]
		);

	}

	/**
	 * Main SettingsFields Instance.
	 *
	 * Insures that only one instance of SettingsFields exists in memory at any one time.
	 *
	 * @static
	 * @return SettingsFields
	 * @since 1.0.0
	 **/
    public static function get_instance() {

        if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

            self::$instance = new self;

        }

        return self::$instance;

    }

} // End Class SettingsFields.
