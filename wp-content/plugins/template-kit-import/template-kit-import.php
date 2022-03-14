<?php
/**
 * Plugin Name: Template Kit Import
 * Description: Import Template Kits to WordPress
 * Author: Envato
 * Author URI: https://envato.com
 * Version: 1.0.14
 * License: GPLv3 or later
 * License URI: https://www.gnu.org/licenses/gpl-3.0.html
 * Elementor tested up to: 3.5.0
 * Elementor Pro tested up to: 3.5.0
 *
 * Text Domain: template-kit-import
 *
 * @package Envato/Template_Kit_Import
 *
 * Template Kit Import is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * any later version.
 *
 * Template Kit Import is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'ENVATO_TEMPLATE_KIT_IMPORT_SLUG', 'template-kit-import' );
define( 'ENVATO_TEMPLATE_KIT_IMPORT_VER', '1.0.14' );
define( 'ENVATO_TEMPLATE_KIT_IMPORT_FILE', __FILE__ );
define( 'ENVATO_TEMPLATE_KIT_IMPORT_DIR', plugin_dir_path( ENVATO_TEMPLATE_KIT_IMPORT_FILE ) );
define( 'ENVATO_TEMPLATE_KIT_IMPORT_URI', plugins_url( '/', ENVATO_TEMPLATE_KIT_IMPORT_FILE ) );
define( 'ENVATO_TEMPLATE_KIT_IMPORT_PHP_VERSION', '5.6' );
define( 'ENVATO_TEMPLATE_KIT_IMPORT_API_NAMESPACE', ENVATO_TEMPLATE_KIT_IMPORT_SLUG . '/v2' );


/**
 * Our supported import types
 */
if( ! defined( 'ENVATO_TEMPLATE_KIT_IMPORT_TYPE_ENVATO' ) ) {
	define( 'ENVATO_TEMPLATE_KIT_IMPORT_TYPE_ENVATO', 'template-kit' );
}
if ( ! defined( 'ENVATO_TEMPLATE_KIT_IMPORT_TYPE_ELEMENTOR' ) ) {
	define( 'ENVATO_TEMPLATE_KIT_IMPORT_TYPE_ELEMENTOR', 'elementor-kit' );
}

add_action( 'plugins_loaded', 'template_kit_import_load_plugin_textdomain' );

if ( ! version_compare( PHP_VERSION, ENVATO_TEMPLATE_KIT_IMPORT_PHP_VERSION, '>=' ) ) {
	add_action( 'admin_notices', 'template_kit_import_fail_php_version' );
} elseif ( ! version_compare( get_bloginfo( 'version' ), '4.6', '>=' ) ) {
	add_action( 'admin_notices', 'template_kit_import_fail_wp_version' );
} else {
	require ENVATO_TEMPLATE_KIT_IMPORT_DIR . 'inc/bootstrap.php';
}


/**
 * Load Envato Elements textdomain.
 *
 * Load gettext translate for Envato Elements text domain.
 *
 * @since 0.0.2
 *
 * @return void
 */
function template_kit_import_load_plugin_textdomain() {
	load_plugin_textdomain( 'template-kit-import' );
}


/**
 * Envato Elements admin notice for minimum PHP version.
 *
 * Warning when the site doesn't have the minimum required PHP version.
 *
 * @since 0.0.2
 *
 * @return void
 */
function template_kit_import_fail_php_version() {
	$message = sprintf(
		/* translators: %s: PHP version */
		esc_html__( 'Template Kit Import plugin requires PHP version %1$s+, plugin is currently NOT ACTIVE. Please contact the hosting provider. WordPress recommends version %2$s.', 'template-kit-import' ),
		ENVATO_TEMPLATE_KIT_IMPORT_PHP_VERSION,
		sprintf(
			'<a href="%s" target="_blank">%s</a>',
			esc_url( 'https://wordpress.org/about/requirements/' ),
			esc_html__( '7.2 or above', 'template-kit-import' )
		)
	);

	$html_message = sprintf( '<div class="error">%s</div> ', wpautop( $message ) );
	echo wp_kses_post( $html_message );
}

/**
 * Envato Elements admin notice for minimum WordPress version.
 *
 * Warning when the site doesn't have the minimum required WordPress version .
 *
 * @since 0.0.2
 *
 * @return void
 */
function template_kit_import_fail_wp_version() {
	/* translators: %s: WordPress version */
	$message      = sprintf( esc_html__( 'Envato Elements requires WordPress version %s+. Because you are using an earlier version, the plugin is currently NOT ACTIVE.', 'template-kit-import' ), '4.6' );
	$html_message = sprintf( '<div class="error">%s</div>', wpautop( $message ) );
	echo wp_kses_post( $html_message );
}
