<?php
/**
 * Template Kit Import:
 *
 * This starts things up. Registers the SPL and starts up some classes.
 *
 * @package Envato/Template_Kit_Import
 * @since 0.0.2
 */

namespace Template_Kit_Import;

use Template_Kit_Import\Backend\Welcome;
use Template_Kit_Import\Utils\Base;

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly.
}


/**
 * Envato Elements plugin.
 *
 * The main plugin handler class is responsible for initializing Envato Elements. The
 * class registers and all the components required to run the plugin.
 *
 * @since 0.0.2
 */
class Plugin extends Base {

	/**
	 * Initializing Envato Elements plugin.
	 *
	 * @since 0.0.2
	 * @access private
	 */
	public function __construct() {
		add_action( 'admin_menu', array( $this, 'admin_menu' ) );
		add_action( 'admin_init', array( $this, 'admin_init' ) );
		add_action( 'plugins_loaded', array( $this, 'db_upgrade_check' ) );
	}

	/**
	 * Sets up the admin menu options.
	 *
	 * @since 0.0.2
	 * @access public
	 */
	public function admin_menu() {
		Welcome::get_instance()->admin_menu();
	}

	/**
	 * Sets up the admin menu options.
	 *
	 * @since 0.0.2
	 * @access public
	 */
	public function admin_init() {
	}

	public function db_upgrade_check() {
		if ( is_admin() && get_option( 'template_kit_import_version' ) !== ENVATO_TEMPLATE_KIT_IMPORT_VER ) {
			$this->activation();
		}
	}

	public function activation() {
		update_option( 'template_kit_import_version', ENVATO_TEMPLATE_KIT_IMPORT_VER );
		if ( ! get_option( 'template_kit_import_install_time' ) ) {
			update_option( 'template_kit_import_install_time', time() );
		}
	}

}
