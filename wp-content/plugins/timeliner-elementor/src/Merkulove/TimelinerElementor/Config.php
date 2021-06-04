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

use Merkulove\TimelinerElementor\Unity\Plugin;
use Merkulove\TimelinerElementor\Unity\Settings;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
	header( 'Status: 403 Forbidden' );
	header( 'HTTP/1.1 403 Forbidden' );
	exit;
}

/**
 * SINGLETON: Settings class used to modify default plugin settings.
 *
 * @since 1.0.0
 *
 **/
final class Config {

	/**
	 * The one true Settings.
	 *
     * @since 1.0.0
     * @access private
	 * @var Config
	 **/
	private static $instance;

    /**
     * Prepare plugin settings by modifying the default one.
     *
     * @since 1.0.0
     * @access public
     *
     * @return void
     **/
    public function prepare_settings() {

        /** Get default plugin settings. */
        $tabs = Plugin::get_tabs();

        /** Short hand access to plugin settings. */
        $options = Settings::get_instance()->options;

        // Change General tab label.
        // $tabs['general']['label'] = esc_html__( 'Ave General', 'timeliner-elementor' );
        // $tabs['general']['title'] = esc_html__( 'Awesome General', 'timeliner-elementor' );

        // Remove 'Delete plugin, settings and data' option from Uninstall tab.
        // unset( $tabs['uninstall']['fields']['delete_plugin']['options']['plugin+settings+data'] );

        // Add Text control
        $tabs['general']['fields']['test_text'] = [
            'type'              => 'text',
            'label'             => esc_html__( 'Text field', 'timeliner-elementor' ),
            'show_label'        => true,
            'placeholder'       => esc_html__( 'Enter Text value', 'timeliner-elementor' ),
            'description'       => esc_html__( 'Some text field description.', 'timeliner-elementor' ),
            'show_description'  => true,
            'default'           => '',
            'attr'              => [
                'class'     => 'mdp-test-class',
                'maxlength' => '4500'
            ]
        ];

        // Add Divider control
        $tabs['general']['fields']['divider_test'] = [
            'type'              => 'divider',
            'label'             => '',
            'show_label'        => false,
            'default'           => '',
        ];

        // Add Select control
        $tabs['general']['fields']['test_select'] = [
            'type'              => 'select',
            'label'             => esc_html__( 'Select field', 'timeliner-elementor' ),
            'show_label'        => true,
            'placeholder'       => esc_html__( 'Top Label', 'timeliner-elementor' ),
            'description'       => esc_html__( 'Some select field description.', 'timeliner-elementor' ),
            'show_description'  => true,
            'default'           => 'small-bluetooth-class-device',
            'options'           => [
                'wearable-class-device'                 => esc_html__( 'Smart watches and other wearables', 'timeliner-elementor' ),
                'handset-class-device'                  => esc_html__( 'Smartphones', 'timeliner-elementor' ),
                'headphone-class-device'                => esc_html__( 'Earbuds or headphones', 'timeliner-elementor' ),
                'small-bluetooth-class-device'  => esc_html__( 'Small home', 'timeliner-elementor' ),
                'medium-bluetooth-class-device' => esc_html__( 'Smart home', 'timeliner-elementor' ),
                'large-home-entertainment-class-device' => esc_html__( 'Home entertainment systems', 'timeliner-elementor' ),
                'large-automotive-class-device'         => esc_html__( 'Car', 'timeliner-elementor' ),
                'telephony-class-application'           => esc_html__( 'Interactive Voice Response', 'timeliner-elementor' ),
            ]
        ];

        // Add Switcher control
        $tabs['general']['fields']['test_switcher'] = [
            'type'              => 'switcher',
            'label'             => esc_html__( 'Dictation', 'timeliner-elementor' ),
            'show_label'        => true,
            'placeholder'       => esc_html__( 'Option Dictation', 'timeliner-elementor' ),
            'description'       => esc_html__( 'Some Switcher field description.', 'timeliner-elementor' ),
            'show_description'  => true,
            'default'           => 'off',
        ];

        // Add Slider control
        $key = 'test_slider';
        $default = 2;
        $tabs['general']['fields'][$key] = [
            'type'              => 'slider',
            'label'             => esc_html__( 'Offset:', 'timeliner-elementor' ),
            'show_label'        => true,
            'description'       => esc_html__( 'Current Offset:', 'timeliner-elementor' ) .
                ' <strong>' .
                esc_html( ( isset( $options[$key] ) ) ? $options[$key] : $default ) .
                '</strong>' .
                esc_html__( ' px', 'timeliner-elementor' ),
            'show_description'  => true,
            'min'               => 0,
            'max'               => 50,
            'step'              => 1,
            'default'           => $default,
            'discrete'          => true,
        ];

        // Header control
        $tabs['general']['fields']['test_header'] = [
            'type'              => 'header',
            'label'             => esc_html__( 'Popup', 'timeliner-elementor' ),
            'show_label'        => true,
            'description'       => esc_html__( 'Customize the Look & Feel of the Popup Box.', 'timeliner-elementor' ),
            'show_description'  => true,
            'default'           => ''
        ];

        // Textarea control
        $tabs['general']['fields']['test_textarea'] = [
            'type'              => 'textarea',
            'label'             => esc_html__( 'Textarea', 'timeliner-elementor' ),
            'show_label'        => true,
            'placeholder'       => esc_html__( 'Placeholder Option', 'timeliner-elementor' ),
            'description'       => esc_html__( 'Customize the Look & Feel of the Popup Box.', 'timeliner-elementor' ),
            'show_description'  => true,
            'default'           => ''
        ];

        // Add colorpicker
        $tabs['general']['fields']['test_color'] = [
            'type'              => 'colorpicker',
            'label'             => esc_html__( 'Select color', 'timeliner-elementor' ),
            'show_label'        => true,
            'placeholder'       => esc_html__( 'Enter color res value', 'timeliner-elementor' ),
            'description'       => esc_html__( 'Some color field description.', 'timeliner-elementor' ),
            'show_description'  => true,
            'default'           => '#0274e6',
            'attr'              => [
                'readonly'      => 'readonly',
            ]
        ];

        // Add icon
        // Add to package.json to dependencies "mdc-icon-library": "git+https://bitbucket.org/wpelements/mdc-icon-library.git",
        // and place 'mdc-icons' folder to /images
//        $tabs['general']['fields']['test_icon'] = [
//            'type'              => 'icon',
//            'label'             => esc_html__( 'Select icon', 'timeliner-elementor' ),
//            'show_label'        => true,
//            'placeholder'       => '',
//            'description'       => esc_html__( 'Some icon field description.', 'timeliner-elementor' ),
//            'show_description'  => true,
//            'default'           => 'material/add-comment-button.svg',
//            'meta'              => [
//                '_listener.json',
//                'font-awesome.json',
//                'material.json'
//            ]
//        ];

        // WP Editor
        $tabs['general']['fields']['editor_test'] = [
            'type'              => 'editor',
            'label'             => esc_html__( 'WP Editor:', 'timeliner-elementor' ),
            'show_label'        => true,
            'description'       => '',
            'show_description'  => false,
            'default'           => '<p>' . esc_html__( 'Some content goes here!', 'timeliner-elementor' ) . '</p>',
            'attr'              => [
                'textarea_rows' => '3',
            ]
        ];

//        // Custom Control with custom handler
//        $tabs['general']['fields']['custom_test'] = [
//            'type'              => 'custom_type',
//            'render'            => [ TabGeneral::get_instance(), 'render_custom_type' ],
//            'label'             => esc_html__( 'Custom field:', 'timeliner-elementor' ),
//            'show_label'        => true,
//            'description'       => '',
//            'show_description'  => false,
//            'default'           => 'Default value',
//        ];

        // Add Chosen control
        $tabs['general']['fields']['test_chosen'] = [
            'type'              => 'chosen',
            'label'             => esc_html__( 'Chosen field:', 'timeliner-elementor' ),
            'show_label'        => true,
            'description'       => esc_html__( 'Some chosen field description.', 'timeliner-elementor' ),
            'show_description'  => true,
            'default'           => [ 'default', 'value-2' ],
            'options'           => [
                'default'   => esc_html__( 'Default', 'timeliner-elementor' ),
                'value-1'   => esc_html__( 'Value 1', 'timeliner-elementor' ),
                'value-2'   => esc_html__( 'Value 2', 'timeliner-elementor' ),
                'value-3'   => esc_html__( 'Value 3', 'timeliner-elementor' ),
                'value-4'   => esc_html__( 'value 4', 'timeliner-elementor' ),
            ],
            'attr'              => [
                'multiple' => 'multiple',
            ]

        ];

        // Add Button control
        $tabs['general']['fields']['test_button'] = [
            'type'              => 'button',
            'label'             => esc_html__( 'Button field', 'timeliner-elementor' ),
            'show_label'        => true,
            'placeholder'       => esc_html__( 'Enter Button value', 'timeliner-elementor' ),
            'description'       => esc_html__( 'Some text field description.', 'timeliner-elementor' ),
            'show_description'  => true,
            'default'           => '',
            'icon'              => 'close',
            'attr'              => [
                'class'     => 'mdc-button--unelevated', // Filled button
                //'class'     => 'mdc-button--outlined', // Outlined button
            ]
        ];

        /** Special config for Elementor plugins. */
        if ( 'elementor' === Plugin::get_type() ) {
            unset( $tabs['general'] );
        }

        /** Set updated tabs. */
        Plugin::set_tabs( $tabs );

        /** Refresh settings. */
        Settings::get_instance()->get_options();

    }

	/**
	 * Main Settings Instance.
	 * Insures that only one instance of Settings exists in memory at any one time.
	 *
	 * @static
     * @since 1.0.0
     * @access public
     *
	 * @return Config
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

}
