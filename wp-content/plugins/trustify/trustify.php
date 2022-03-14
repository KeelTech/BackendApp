<?php

/**
 * The plugin bootstrap file
 *
 * This file is read by WordPress to generate the plugin information in the plugin
 * admin area. This file also includes all of the dependencies used by the plugin,
 * registers the activation and deactivation functions, and defines a function
 * that starts the plugin.
 *
 * @link              http://kaththemes.com/
 * @since             1.0.0
 * @package           Trustify
 *
 * @wordpress-plugin
 * Plugin Name:       Trustify
 * Plugin URI:        http://demo.kaththemes.com/plugins/trustify/
 * Description:       Help to create fake sales or real time WooCommerce sales notification as popup which will display in a certain time interval on the screen in all pages or selected pages from backend.
 * Version:           2.2
 * Author:            Kaththemes
 * Author URI:        http://kaththemes.com/
 * License:           GPL-2.0+
 * License URI:       http://www.gnu.org/licenses/gpl-2.0.txt
 * Text Domain:       trustify
 * Domain Path:       /languages
 */

// If this file is called directly, abort.
if ( ! defined( 'WPINC' ) ) {
	die;
}

// Define Plugin Path.
if ( ! defined( 'TRUSTIFY_PLUGIN_FILE' ) ) {
    define( 'TRUSTIFY_PLUGIN_FILE', __FILE__);
}

//Define Plugin Version
if ( ! defined( 'TRUSTIFY_PLUGIN_VERSION' ) ) {
    define( 'TRUSTIFY_PLUGIN_VERSION', '2.2');
}

//Define Plugin Dir
if ( ! defined( 'TRUSTIFY_ABSPATH' ) ) {
	define( 'TRUSTIFY_ABSPATH', dirname(TRUSTIFY_PLUGIN_FILE) . '/' );
}

define( 'TRUSTIFY_REMOVE_ALL_DATA', false );


/**
 * The code that runs during plugin activation.
 * This action is documented in includes/class-trustify-activator.php
 */
function activate_trustify() {
	require_once plugin_dir_path( __FILE__ ) . 'includes/class-trustify-activator.php';
	Trustify_Activator::activate();
}

/**
 * The code that runs during plugin deactivation.
 * This action is documented in includes/class-trustify-deactivator.php
 */
function deactivate_trustify() {
	require_once plugin_dir_path( __FILE__ ) . 'includes/class-trustify-deactivator.php';
	Trustify_Deactivator::deactivate();
}

register_activation_hook( __FILE__, 'activate_trustify' );
register_deactivation_hook( __FILE__, 'deactivate_trustify' );

/**
 * The core plugin class that is used to define internationalization,
 * admin-specific hooks, and public-facing site hooks.
 */
require plugin_dir_path( __FILE__ ) . 'includes/class-trustify.php';

/**
 * Begins execution of the plugin.
 *
 * Since everything within the plugin is registered via hooks,
 * then kicking off the plugin from this point in the file does
 * not affect the page life cycle.
 *
 * @since    1.0.0
 */
function run_trustify() {

	$plugin = new Trustify();
	$plugin->run();

}
run_trustify();
