<?php

/**
 * The file that defines the core plugin class
 *
 * A class definition that includes attributes and functions used across both the
 * public-facing side of the site and the admin area.
 *
 * @link       http://responsive-pixel.com/
 * @since      1.0.0
 *
 * @package    Trustify
 * @subpackage Trustify/includes
 */

/**
 * The core plugin class.
 *
 * This is used to define internationalization, admin-specific hooks, and
 * public-facing site hooks.
 *
 * Also maintains the unique identifier of this plugin as well as the current
 * version of the plugin.
 *
 * @since      1.0.0
 * @package    Trustify
 * @subpackage Trustify/includes
 * @author     Responsive-pixel <rajendrarijal@responsive-pixel.com>
 */
class Trustify {

	/**
	 * The loader that's responsible for maintaining and registering all hooks that power
	 * the plugin.
	 *
	 * @since    1.0.0
	 * @access   protected
	 * @var      Trustify_Loader    $loader    Maintains and registers all hooks for the plugin.
	 */
	protected $loader;

	/**
	 * The unique identifier of this plugin.
	 *
	 * @since    1.0.0
	 * @access   protected
	 * @var      string    $plugin_name    The string used to uniquely identify this plugin.
	 */
	protected $plugin_name;

	/**
	 * The current version of the plugin.
	 *
	 * @since    1.0.0
	 * @access   protected
	 * @var      string    $version    The current version of the plugin.
	 */
	protected $version;

	/**
	 * Define the core functionality of the plugin.
	 *
	 * Set the plugin name and the plugin version that can be used throughout the plugin.
	 * Load the dependencies, define the locale, and set the hooks for the admin area and
	 * the public-facing side of the site.
	 *
	 * @since    1.0.0
	 */
	public function __construct() {

		$this->plugin_name = 'trustify';
		$this->version = '1.0.0';
		$this->load_dependencies();
		$this->set_locale();
		$this->define_admin_hooks();
		$this->define_public_hooks();

	}

	/**
	 * Load the required dependencies for this plugin.
	 *
	 * Include the following files that make up the plugin:
	 *
	 * - Trustify_Loader. Orchestrates the hooks of the plugin.
	 * - Trustify_i18n. Defines internationalization functionality.
	 * - Trustify_Admin. Defines all hooks for the admin area.
	 * - Trustify_Public. Defines all hooks for the public side of the site.
	 *
	 * Create an instance of the loader which will be used to register the hooks
	 * with WordPress.
	 *
	 * @since    1.0.0
	 * @access   private
	 */
	private function load_dependencies() {

		/**
		 * The class responsible for orchestrating the actions and filters of the
		 * core plugin.
		 */
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/class-trustify-loader.php';

		/**
		 * The class responsible for defining internationalization functionality
		 * of the plugin.
		 */
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/class-trustify-i18n.php';

		/**
		 * The class responsible for defining all actions that occur in the admin area.
		 */
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'admin/class-trustify-admin.php';

		/**
		 * The class responsible for defining all actions that occur in the public-facing
		 * side of the site.
		 */
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'public/class-trustify-public.php';

		$this->loader = new Trustify_Loader();

	}

	/**
	 * Define the locale for this plugin for internationalization.
	 *
	 * Uses the Trustify_i18n class in order to set the domain and to register the hook
	 * with WordPress.
	 *
	 * @since    1.0.0
	 * @access   private
	 */
	private function set_locale() {

		$plugin_i18n = new Trustify_i18n();

		$this->loader->add_action( 'plugins_loaded', $plugin_i18n, 'load_plugin_textdomain' );

	}

	/**
	 * Register all of the hooks related to the admin area functionality
	 * of the plugin.
	 *
	 * @since    1.0.0
	 * @access   private
	 */
	private function define_admin_hooks() {

		$plugin_admin = new Trustify_Admin( $this->get_plugin_name(), $this->get_version() );

		$this->loader->add_action( 'admin_enqueue_scripts', $plugin_admin, 'enqueue_styles' );
		$this->loader->add_action( 'admin_enqueue_scripts', $plugin_admin, 'enqueue_scripts' );

		$this->loader->add_action( 'init', $plugin_admin, 'create_mifi_notice' );

		$this->loader->add_action( 'admin_init', $plugin_admin,'mifi_time_metabox' );
		$this->loader->add_action( 'save_post',$plugin_admin, 'mifi_stored_time_meta' );

		//meta box for page list
		$this->loader-> add_action( 'add_meta_boxes', $plugin_admin, 'myplugin_add_custom_box' );

		$this->loader-> add_action( 'save_post', $plugin_admin, 'save_checkfield',10, 2 );

		//Admin Global Settting
		$this->loader-> add_action( 'admin_menu',$plugin_admin, 'trustify_add_admin_menu' );

		$this->loader->add_action( 'admin_init', $plugin_admin, 'trustify_settings_init' );

		//insert custom column to mifi CPT
		$this->loader->add_filter( 'manage_mifi_posts_columns',$plugin_admin, 'set_custom_edit_mifi_columns' );
		$this->loader->add_action( 'manage_mifi_posts_custom_column' ,$plugin_admin, 'mifi_notification_custom_column', 10, 2 );

		$this->loader->add_filter( 'set-screen-option',$plugin_admin, 'set_report_screen_options',10,3 );		

	}

	/**
	 * Register all of the hooks related to the public-facing functionality
	 * of the plugin.
	 *
	 * @since    1.0.0
	 * @access   private
	 */
	private function define_public_hooks() {

		$plugin_public = new Trustify_Public( $this->get_plugin_name(), $this->get_version() );

		$this->loader->add_action( 'wp_enqueue_scripts', $plugin_public, 'enqueue_styles' );
		$this->loader->add_action( 'wp_enqueue_scripts', $plugin_public, 'enqueue_scripts' );

		//ajax
		$this->loader->add_action( 'wp_ajax_trustify_get_notice', $plugin_public, 'trustify_get_notice' );
		$this->loader->add_action( 'wp_ajax_nopriv_trustify_get_notice', $plugin_public, 'trustify_get_notice' );

		//ajax_auto
		$this->loader->add_action( 'wp_ajax_trustify_get_auto_notice', $plugin_public, 'trustify_get_auto_notice' );
		$this->loader->add_action( 'wp_ajax_nopriv_trustify_get_auto_notice', $plugin_public, 'trustify_get_auto_notice' );

		//ajax_woo
		$this->loader->add_action( 'wp_ajax_trustify_get_woo_notice', $plugin_public, 'trustify_get_woo_notice' );
		$this->loader->add_action( 'wp_ajax_nopriv_trustify_get_woo_notice', $plugin_public, 'trustify_get_woo_notice' );

		//ajax_edd
		$this->loader->add_action( 'wp_ajax_trustify_get_edd_notice', $plugin_public, 'trustify_get_edd_notice' );
		$this->loader->add_action( 'wp_ajax_nopriv_trustify_get_edd_notice', $plugin_public, 'trustify_get_edd_notice' );

		//click track
		$this->loader->add_action( 'wp_ajax_trustify_click_track', $plugin_public, 'trustify_click_track' );
		$this->loader->add_action( 'wp_ajax_nopriv_trustify_click_track', $plugin_public, 'trustify_click_track' );

		$this->loader->add_action( 'wp_footer', $plugin_public, 'trustify_frontend', 20 );

	}

	/**
	 * Run the loader to execute all of the hooks with WordPress.
	 *
	 * @since    1.0.0
	 */
	public function run() {
		$this->loader->run();
	}

	/**
	 * The name of the plugin used to uniquely identify it within the context of
	 * WordPress and to define internationalization functionality.
	 *
	 * @since     1.0.0
	 * @return    string    The name of the plugin.
	 */
	public function get_plugin_name() {
		return $this->plugin_name;
	}

	/**
	 * The reference to the class that orchestrates the hooks with the plugin.
	 *
	 * @since     1.0.0
	 * @return    Trustify_Loader    Orchestrates the hooks of the plugin.
	 */
	public function get_loader() {
		return $this->loader;
	}

	/**
	 * Retrieve the version number of the plugin.
	 *
	 * @since     1.0.0
	 * @return    string    The version number of the plugin.
	 */
	public function get_version() {
		return $this->version;
	}

}
