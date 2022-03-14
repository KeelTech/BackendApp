<?php
/**
 * Plugin Name: YITH WooCommerce Affiliates
 * Plugin URI: https://yithemes.com/themes/plugins/yith-woocommerce-affiliates/
 * Description: <code><strong>YITH WooCommerce Affiliates</strong></code> allows your users to become affiliates on your site earning commissions on every sale generated through their exclusive affiliation links. Create a sales network at no cost and increase your incomes just like big stores. <a href="https://yithemes.com/" target="_blank">Get more plugins for your e-commerce on <strong>YITH</strong></a>
 * Version: 1.14.0
 * Author: YITH
 * Author URI: https://yithemes.com/
 * Text Domain: yith-woocommerce-affiliates
 * Domain Path: /languages/
 * WC requires at least: 6.0
 * WC tested up to: 6.2
 *
 * @author Your Inspiration Themes
 * @package YITH WooCommerce Affiliates
 * @version 1.0.0
 */

/*
 * This file belongs to the YIT Framework.
 *
 * This source file is subject to the GNU GENERAL PUBLIC LICENSE (GPL 3.0)
 * that is bundled with this package in the file LICENSE.txt.
 * It is also available through the world-wide-web at this URL:
 * http://www.gnu.org/licenses/gpl-3.0.txt
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
} // Exit if accessed directly

if ( ! function_exists( 'yith_plugin_registration_hook' ) ) {
	require_once 'plugin-fw/yit-plugin-registration-hook.php';
}
register_activation_hook( __FILE__, 'yith_plugin_registration_hook' );

if ( ! defined( 'YITH_WCAF' ) ) {
	define( 'YITH_WCAF', true );
}

if ( ! defined( 'YITH_WCAF_FREE' ) ) {
	define( 'YITH_WCAF_FREE', true );
}

if ( ! defined( 'YITH_WCAF_URL' ) ) {
	define( 'YITH_WCAF_URL', plugin_dir_url( __FILE__ ) );
}

if ( ! defined( 'YITH_WCAF_DIR' ) ) {
	define( 'YITH_WCAF_DIR', plugin_dir_path( __FILE__ ) );
}

if ( ! defined( 'YITH_WCAF_INC' ) ) {
	define( 'YITH_WCAF_INC', YITH_WCAF_DIR . 'includes/' );
}

if ( ! defined( 'YITH_WCAF_SLUG' ) ) {
	define( 'YITH_WCAF_SLUG', 'yith-woocommerce-affiliates' );
}

if ( ! defined( 'YITH_WCAF_INIT' ) ) {
	define( 'YITH_WCAF_INIT', plugin_basename( __FILE__ ) );
}

if ( ! defined( 'YITH_WCAF_FREE_INIT' ) ) {
	define( 'YITH_WCAF_FREE_INIT', plugin_basename( __FILE__ ) );
}

/* Plugin Framework Version Check */
if ( ! function_exists( 'yit_maybe_plugin_fw_loader' ) && file_exists( YITH_WCAF_DIR . 'plugin-fw/init.php' ) ) {
	require_once YITH_WCAF_DIR . 'plugin-fw/init.php';
}
yit_maybe_plugin_fw_loader( YITH_WCAF_DIR );

if ( ! function_exists( 'yith_affiliates_constructor' ) ) {
	function yith_affiliates_constructor() {
		load_plugin_textdomain( 'yith-woocommerce-affiliates', false, dirname( plugin_basename( __FILE__ ) ) . '/languages/' );

		require_once YITH_WCAF_INC . 'functions.yith-wcaf.php';
		require_once YITH_WCAF_INC . 'class.yith-wcaf.php';
		require_once YITH_WCAF_INC . 'class.yith-wcaf-shortcode.php';
		require_once YITH_WCAF_INC . 'class.yith-wcaf-click-handler.php';
		require_once YITH_WCAF_INC . 'class.yith-wcaf-commission-handler.php';
		require_once YITH_WCAF_INC . 'class.yith-wcaf-rate-handler.php';
		require_once YITH_WCAF_INC . 'class.yith-wcaf-affiliate-handler.php';
		require_once YITH_WCAF_INC . 'class.yith-wcaf-payment-handler.php';
		require_once YITH_WCAF_INC . 'class.yith-wcaf-affiliate.php';

		// Let's start the game
		YITH_WCAF();

		if ( is_admin() ) {
			if ( ! class_exists( 'WP_List_Table' ) ) {
				require_once ABSPATH . 'wp-admin/includes/class-wp-list-table.php';
			}
			require_once YITH_WCAF_INC . 'admin-tables/class.yith-wcaf-commissions-table.php';
			require_once YITH_WCAF_INC . 'admin-tables/class.yith-wcaf-payments-table.php';
			require_once YITH_WCAF_INC . 'admin-tables/class.yith-wcaf-affiliates-table.php';
			require_once YITH_WCAF_INC . 'admin-tables/class.yith-wcaf-product-stat-table.php';
			require_once YITH_WCAF_INC . 'class.yith-wcaf-admin.php';

			YITH_WCAF_Admin();
		}
	}
}
add_action( 'yith_wcaf_init', 'yith_affiliates_constructor' );

if ( ! function_exists( 'yith_affiliates_install' ) ) {
	function yith_affiliates_install() {

		if ( ! function_exists( 'is_plugin_active' ) ) {
			require_once ABSPATH . 'wp-admin/includes/plugin.php';
		}

		if ( ! function_exists( 'WC' ) ) {
			add_action( 'admin_notices', 'yith_wcaf_install_woocommerce_admin_notice' );
		} elseif ( defined( 'YITH_WCAF_PREMIUM_INIT' ) ) {
			add_action( 'admin_notices', 'yith_wcaf_install_free_admin_notice' );
			deactivate_plugins( plugin_basename( __FILE__ ) );
		} else {
			do_action( 'yith_wcaf_init' );
		}
	}
}
add_action( 'plugins_loaded', 'yith_affiliates_install', 11 );

if ( ! function_exists( 'yith_wcaf_install_woocommerce_admin_notice' ) ) {
	function yith_wcaf_install_woocommerce_admin_notice() {
		?>
		<div class="error">
			<p><?php echo 'YITH WooCommerce Affiliates ' . __( 'is enabled but not effective. It requires WooCommerce in order to work.', 'yith-woocommerce-affiliates' ); ?></p>
		</div>
		<?php
	}
}

if ( ! function_exists( 'yith_wcaf_install_free_admin_notice' ) ) {
	function yith_wcaf_install_free_admin_notice() {
		?>
		<div class="error">
			<p><?php echo __( 'You can\'t activate the free version of ', 'yith-woocommerce-affiliates' ) . 'YITH WooCommerce Affiliates' . __( ' while you are using the premium one.', 'yith-woocommerce-affiliates' ); ?></p>
		</div>
		<?php
	}
}
