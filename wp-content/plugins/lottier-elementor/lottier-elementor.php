<?php

/**
 * Lottier for Elementor
 *
 * @encoding        UTF-8
 * @version         1.0.3
 * @copyright       (C) 2018 - 2020 Merkulove ( https://merkulov.design/ ). All rights reserved.
 * @license         Envato License https://1.envato.market/KYbje
 * @contributors    Vitaliy Nemirovskiy (nemirovskiyvitaliy@gmail.com), Dmitry Merkulov (dmitry@merkulov.design)
 * @support         help@merkulov.design
 * @license         Envato License https://1.envato.market/KYbje
 *
 * @wordpress-plugin
 * Plugin Name: Lottier for Elementor
 * Plugin URI: https://1.envato.market/lottier-elementor
 * Description: Lottie animations in just a few clicks without writing a single line of code.
 * Version: 1.0.3
 * Requires at least: 3.0
 * Requires PHP: 5.6
 * Author: Merkulove
 * Author URI: https://1.envato.market/cc-merkulove
 * License: Envato License https://1.envato.market/KYbje
 * License URI: https://1.envato.market/KYbje
 * Text Domain: lottier-elementor
 * Domain Path: /languages
 * Tested up to: 5.5
 **/


namespace Merkulove;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
    header( 'Status: 403 Forbidden' );
    header( 'HTTP/1.1 403 Forbidden' );
    exit;
}

/** Include plugin autoloader for additional classes. */
require __DIR__ . '/src/autoload.php';

use Merkulove\LottierElementor\CheckCompatibility;
use Merkulove\LottierElementor\Helper;
use Merkulove\LottierElementor\PluginHelper;
use Merkulove\LottierElementor\PluginUpdater;
use Merkulove\LottierElementor\Settings;
use Merkulove\LottierElementor\AdminScripts;
use Merkulove\LottierElementor\AdminStyles;
use Merkulove\LottierElementor\TabUpdates;
use Merkulove\LottierElementor\Elementor;

/**
 * SINGLETON: Core class used to implement a plugin.
 *
 * This is used to define internationalization, admin-specific hooks, and
 * public-facing site hooks.
 *
 **/
final class LottierElementor {

	/**
	 * Plugin version.
	 *
	 * @string version
	 **/
	public static $version = '';

	/**
	 * Plugin name.
	 *
	 * @string version
	 **/
	public static $name;

	/**
	 * Use minified libraries if SCRIPT_DEBUG is turned off.
	 **/
	public static $suffix = '';

	/**
	 * URL (with trailing slash) to plugin folder.
	 *
	 * @var string
	 **/
	public static $url = '';

	/**
	 * PATH to plugin folder.
	 *
	 * @var string
	 **/
	public static $path = '';

	/**
	 * Plugin base name.
	 *
	 * @var string
	 **/
	public static $basename = '';

	/**
	 * Plugin admin menu base.
	 *
	 * @var string
	 **/
	public static $menu_base;

	/**
	 * Full path to main plugin file.
	 *
	 * @var string
	 **/
	public static $plugin_file;

	/**
	 * Plugin slug base.
	 *
	 * @var string
	 **/
	public static $slug;

    /**
     * The one true Plugin.
     *
     * @var LottierElementor
     **/
    private static $instance;

    /**
     * Sets up a new plugin instance.
     *
     * @access public
     **/
    private function __construct() {

	    /** Initialize main variables. */
	    $this->initialization();

    }

	/**
	 * Initialize main variables.
	 *
	 * @access public
	 **/
	public function initialization() {

		/** Get Plugin version. */
		self::$version = $this->get_plugin_data( 'Version' );

		/** Plugin slug. */
		self::$slug = $this->get_plugin_data( 'TextDomain' );

		/** Get Plugin name. */
		self::$name = $this->get_plugin_data( 'Name' );

		/** Gets the plugin URL (with trailing slash). */
		self::$url = plugin_dir_url( __FILE__ );

		/** Gets the plugin PATH. */
		self::$path = plugin_dir_path( __FILE__ );

		/** Use minified libraries if SCRIPT_DEBUG is turned off. */
		self::$suffix = ( defined( 'SCRIPT_DEBUG' ) && SCRIPT_DEBUG ) ? '' : '.min';

		/** Set plugin basename. */
		self::$basename = plugin_basename( __FILE__ );

		/** Plugin settings page base. */
		self::$menu_base = 'toplevel_page_mdp_lottier_elementor_settings';

		/** Full path to main plugin file. */
		self::$plugin_file = __FILE__;

	}

	/**
	 * Return current plugin metadata.
	 *
	 * @access public
	 * @return array {
	 *     Plugin data. Values will be empty if not supplied by the plugin.
	 *
	 *     @type string $Name        Name of the plugin. Should be unique.
	 *     @type string $Title       Title of the plugin and link to the plugin's site (if set).
	 *     @type string $Description Plugin description.
	 *     @type string $Author      Author's name.
	 *     @type string $AuthorURI   Author's website address (if set).
	 *     @type string $Version     Plugin version.
	 *     @type string $TextDomain  Plugin textdomain.
	 *     @type string $DomainPath  Plugins relative directory path to .mo files.
	 *     @type bool   $Network     Whether the plugin can only be activated network-wide.
	 *     @type string $RequiresWP  Minimum required version of WordPress.
	 *     @type string $RequiresPHP Minimum required version of PHP.
	 * }
	 **/
	public function get_plugin_data( $field ) {

		static $plugin_data;

		/** We already have $plugin_data. */
		if ( $plugin_data !== null ) {
			return $plugin_data[$field];
		}

		/** This is first time call of method, so prepare $plugin_data. */
		if ( ! function_exists( 'get_plugin_data' ) ) {
			require_once( ABSPATH . 'wp-admin/includes/plugin.php' );
		}

		$plugin_data = get_plugin_data( __FILE__ );

		return $plugin_data[$field];

	}

	/**
	 * Setup the plugin.
	 *
	 * @access public
	 * @return void
	 **/
	public function setup() {

		/** Do critical initial checks. */
		if ( ! CheckCompatibility::get_instance()->do_initial_checks( true ) ) { return; }

		/** Send install Action to our host. */
		self::send_install_action();

		/** Define admin hooks. */
		$this->admin_hooks();

		/** Define hooks that runs on both the front-end as well as the dashboard. */
		$this->both_hooks();

	}

	/**
	 * Define hooks that runs on both the front-end as well as the dashboard.
	 *
	 * @access private
	 * @return void
	 **/
	private function both_hooks() {

		/** Load the plugin text domain for translation. */
		add_action( 'plugins_loaded', [ $this, 'load_textdomain' ] );

		/** Register Elementor Widgets. */
		$this->register_elementor_widgets();

    }

	/**
	 * Register all of the hooks related to the admin area functionality.
	 *
	 * @access private
	 * @return void
	 **/
	private function admin_hooks() {

		if ( ! is_admin() ) { return; }

		/** Remove unnecessary WordPress branding and messages */
		PluginHelper::get_instance()->remove_unnecessary();

		/** Initialize plugin settings. */
		Settings::get_instance();

		/** Initialize PluginHelper. */
		PluginHelper::get_instance();

		/** Plugin update mechanism enable only if plugin have Envato ID. */
		PluginUpdater::get_instance();

		/** Add plugin settings page. */
		Settings::get_instance()->add_settings_page();

		/** Add admin CSS */
		AdminStyles::get_instance();

		/** Add admin JS */
		AdminScripts::get_instance();

		/** Add Ajax handlers for Updates Tab. */
		TabUpdates::add_ajax();

		/** Allow SVG files in the media library. */
		add_filter( 'upload_mimes', [ $this, 'allow_svg_uploads' ], 1, 1 );

    }

	/**
	 * Return plugin version.
	 *
	 * @return string
	 * @access public
	 **/
	public function get_version() {

		return self::$version;

	}

    /**
     * Loads the plugin translated strings.
     *
     * @access public
     **/
    public function load_textdomain() {

        load_plugin_textdomain( 'lottier-elementor', false, self::$path . '/languages/' );

    }

	/**
	 * Run when the plugin is activated.
	 *
	 * @static
	 **/
	public static function on_activation() {

		/** Security checks. */
		if ( ! current_user_can( 'activate_plugins' ) ) { return; }

		/** We need to know plugin to activate it. */
		if ( ! isset( $_REQUEST[ 'plugin' ] ) ) { return; }

		/** Get plugin. */
		$plugin = filter_var( $_REQUEST[ 'plugin' ], FILTER_SANITIZE_STRING );

		/** Checks that a user was referred from admin page with the correct security nonce. */
		check_admin_referer( "activate-plugin_{$plugin}" );

		/** Do critical initial checks. */
		if ( ! CheckCompatibility::get_instance()->do_initial_checks( false ) ) { return; }

		/** Send install Action to our host. */
		self::send_install_action();

	}

	/**
	 * Send install Action to our host.
	 *
	 * @static
	 **/
	private static function send_install_action() {

		/** Plugin version. */
		$ver = self::get_instance()->get_version();

		/** Have we already sent 'install' for this version? */
		$opt_name = 'mdp_lottier_elementor_send_action_install';
		$ver_installed = get_option( $opt_name );

		/** Send install Action to our host. */
		if ( ! $ver_installed || $ver !== $ver_installed ) {

			/** Send install Action to our host. */
			Helper::get_instance()->send_action( 'install', 'lottier-elementor', $ver );
			update_option( $opt_name, $ver );

		}

	}

	/**
	 * Allow SVG files in the media library.
	 *
	 * @param $mime_types - Current array of mime types.
	 * @return array - Updated array of mime types.
	 * @access public
	 */
	public function allow_svg_uploads( $mime_types ) {

		/** Adding .svg extension. */
		$mime_types['svg']  = 'image/svg+xml';
		$mime_types['svgz'] = 'image/svg+xml';

		return $mime_types;

	}

	/**
	 * Registers a Elementor Widget.
	 *
	 * @return void
	 * @access public
	 **/
	public function register_elementor_widgets() {

		Elementor::get_instance();

	}

	/**
	 * Main Instance.
	 *
	 * Insures that only one instance of plugin exists in memory at any one time.
	 *
	 * @static
	 * @return LottierElementor
	 * @since 1.0.0
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

}

/** Run when the plugin is activated. */
register_activation_hook( __FILE__, [ LottierElementor::class, 'on_activation' ] );

/** Run the plugin class once after activated plugins have loaded. */
add_action( 'plugins_loaded', [ LottierElementor::get_instance(), 'setup' ] );
