<?php
/**
 * The admin-specific functionality of the plugin.
 *
 * @link       https://themehigh.com
 *
 * @package    woo-checkout-field-editor-pro
 * @subpackage woo-checkout-field-editor-pro/admin
 */

if(!defined('WPINC')){	die; }

if(!class_exists('THWCFD_Admin')):
 
class THWCFD_Admin {
	private $plugin_name;
	private $version;

	/**
	 * Initialize the class and set its properties.
	 *
	 * @since    2.9.0
	 * @param    string    $plugin_name       The name of this plugin.
	 * @param    string    $version    The version of this plugin.
	 */
	public function __construct( $plugin_name, $version ) {
		$this->plugin_name = $plugin_name;
		$this->version = $version;
	}
	
	public function enqueue_styles_and_scripts($hook) {
		if(strpos($hook, 'page_checkout_form_designer') !== false) {
			$debug_mode = apply_filters('thwcfd_debug_mode', false);
			$suffix = $debug_mode ? '' : '.min';
			
			$this->enqueue_styles($suffix);
			$this->enqueue_scripts($suffix);
		}
	}
	
	private function enqueue_styles($suffix) {
		wp_enqueue_style('woocommerce_admin_styles');
		wp_enqueue_style('thwcfd-admin-style', THWCFD_ASSETS_URL_ADMIN . 'css/thwcfd-admin'. $suffix .'.css', $this->version);
	}

	private function enqueue_scripts($suffix) {
		$deps = array('jquery', 'jquery-ui-dialog', 'jquery-ui-sortable', 'jquery-tiptip', 'woocommerce_admin', 'selectWoo', 'wp-color-picker', 'wp-i18n');
			
		wp_enqueue_script('thwcfd-admin-script', THWCFD_ASSETS_URL_ADMIN . 'js/thwcfd-admin'. $suffix .'.js', $deps, $this->version, false);
    	wp_set_script_translations('thwcfd-admin-script', 'woo-checkout-field-editor-pro', dirname(THWCFD_BASE_NAME) . '/languages/');
	}
	
	public function admin_menu() {
		$capability = THWCFD_Utils::wcfd_capability();
		$this->screen_id = add_submenu_page('woocommerce', __('WooCommerce Checkout Field Editor', 'woo-checkout-field-editor-pro'), __('Checkout Form', 'woo-checkout-field-editor-pro'), $capability, 'checkout_form_designer', array($this, 'output_settings'));
	}
	
	public function add_screen_id($ids) {
		$ids[] = 'woocommerce_page_checkout_form_designer';
		$ids[] = strtolower(__('WooCommerce', 'woo-checkout-field-editor-pro')) .'_page_checkout_form_designer';

		return $ids;
	}

	public function plugin_action_links($links) {
		$settings_link = '<a href="'.esc_url(admin_url('admin.php?page=checkout_form_designer')).'">'. __('Settings', 'woo-checkout-field-editor-pro') .'</a>';
		array_unshift($links, $settings_link);
		$pro_link = '<a style="color:green; font-weight:bold" target="_blank" href="https://www.themehigh.com/product/woocommerce-checkout-field-editor-pro/?utm_source=free&utm_medium=plugin_action_link&utm_campaign=wcfe_upgrade_link">'. __('Get Pro', 'woo-checkout-field-editor-pro') .'</a>';
		array_push($links,$pro_link);
		return $links;
	}

	public function get_current_tab(){
		return isset( $_GET['tab'] ) ? sanitize_key( $_GET['tab'] ) : 'fields';
	}
	
	public function output_settings(){
		echo '<div class="wrap">';
		echo '<h2></h2>';

		$tab = $this->get_current_tab();

		echo '<div class="thwcfd-wrap">';
		if($tab === 'advanced_settings'){			
			$advanced_settings = THWCFD_Admin_Settings_Advanced::instance();	
			$advanced_settings->render_page();
		}elseif($tab === 'pro'){
			$pro_details = THWCFD_Admin_Settings_Pro::instance();	
			$pro_details->render_page();
		}elseif($tab === 'themehigh_plugins'){
			$themehigh_plugins = THWCFD_Admin_Settings_Themehigh_Plugins::instance();	
			$themehigh_plugins->render_page();
		}else{
			$general_settings = THWCFD_Admin_Settings_General::instance();	
			$general_settings->init();
		}
		echo '</div>';
		echo '</div>';
	}

	public function hide_thwcfd_admin_notice(){
		$nonse = isset($_REQUEST['thwcfd_notice_security']) ? $_REQUEST['thwcfd_notice_security'] : false;
		$capability = THWCFD_Utils::wcfd_capability();
		if(!wp_verify_nonce($nonse, 'thwcfd_notice_security') || !current_user_can($capability)){
			die();
		}
		set_transient('thwcfd_hide_admin_notice', true, apply_filters('thwcfd_hide_admin_notice_lifespan', 3 * MONTH_IN_SECONDS));
	}

	public function skip_thwcfd_admin_notice(){
		$nonse = isset($_REQUEST['thwcfd_notice_security']) ? $_REQUEST['thwcfd_notice_security'] : false;
		$capability = THWCFD_Utils::wcfd_capability();
		if(!wp_verify_nonce($nonse, 'thwcfd_notice_security') || !current_user_can($capability)){
			die();
		}
		set_transient('thwcfd_skip_admin_notice', true, apply_filters('thwcfd_skip_admin_notice_lifespan', 7 * DAY_IN_SECONDS));
	}

	public function dismissable_admin_notice(){

		$thwcfd_since = get_option('thwcfd_since');
		if(!$thwcfd_since){
			$now = time();
			update_option('thwcfd_since', $now, 'no');
		}

		if(!apply_filters('thwcfd_show_dismissable_admin_notice', true)){
			return;
		}

		$is_hidden = get_transient('thwcfd_hide_admin_notice');
		if($is_hidden){
			return;
		}

		$is_skipped = get_transient('thwcfd_skip_admin_notice');
		if($is_skipped){
			return;
		}

		// $now = time();
		// $diff_seconds = $now - $thwcfd_since;

		// if($diff_seconds < apply_filters('thwcfd_show_admin_notice_after', 10 * DAY_IN_SECONDS)){
		// 	return;
		// }

	    ?>
	    <div class="notice notice-info thpladmin-notice is-dismissible" data-nonce="<?php echo wp_create_nonce( 'thwcfd_notice_security'); ?>">
			<h3><?php _e('We heard you!', 'woo-checkout-field-editor-pro'); ?></h3>
			<p><?php _e('The free version of Checkout Field Editor for WooCommerce plugin is now loaded with more field types and we would love to know how you feel about the improvements we made just for you. Help us to serve you and others best by simply leaving a genuine review.', 'woo-checkout-field-editor-pro'); ?></p>
			<p class="action-row">
		        <a href="#" onclick="window.open('https://wordpress.org/support/plugin/woo-checkout-field-editor-pro/reviews?rate=5#new-post', '_blank')" style="margin-right:16px; text-decoration: none"><span class="dashicons dashicons-external"></span> <?php _e("Yes, today", 'woo-checkout-field-editor-pro'); ?></a>

		        <a href="#" onclick="thwcfdSkipAdminNotice(event, this)" style="margin-right:16px; text-decoration: none"><span class="dashicons dashicons-calendar-alt"></span> <?php _e('Maybe later', 'woo-checkout-field-editor-pro'); ?></a>

		        <a href="#" onclick="thwcfdHideAdminNotice(event, this)" style="margin-right:16px; text-decoration: none"><span class="dashicons dashicons-no"></span> <?php _e("Nah, Never", 'woo-checkout-field-editor-pro'); ?></a>

            	<span class="logo" style="float: right"><a target="_blank" href="https://www.themehigh.com">
                	<img src="<?php echo esc_url(THWCFD_ASSETS_URL_ADMIN .'css/logo.svg'); ?>" style="height:18px;margin-top:4px;"/>
                </a></span>
			</p>
	    </div>
	    <?php		
	}

	function admin_notice_js_snippet(){
		if(!apply_filters('thwcfd_dismissable_admin_notice_javascript', true)){
			return;
		}		
		?>
	    <script>
			var thwcfd_dismissable_notice = (function($, window, document) {
				'use strict';

			$( document ).on( 'click', '.thpladmin-notice .notice-dismiss', function() {
				var wrapper = $(this).closest('div.thpladmin-notice');
				var nonce = wrapper.data("nonce");
				var data = {
					thwcfd_notice_security: nonce,
					action: 'hide_thwcfd_admin_notice',
				};
				$.post( ajaxurl, data, function() {

				});
			});				

				function skip_admin_notice(e, elm){
					e.preventDefault();
					var wrapper = $(elm).closest('div.thpladmin-notice');
					var nonce = wrapper.data("nonce");
					var data = {
						thwcfd_notice_security: nonce,
						action: 'skip_thwcfd_admin_notice',
					};
					$.post( ajaxurl, data, function() {

					});
					$(wrapper).hide(20);
				}

				function hide_admin_notice(e, elm){
					e.preventDefault();
					var wrapper = $(elm).closest('div.thpladmin-notice');
					var nonce = wrapper.data("nonce");
					var data = {
						thwcfd_notice_security: nonce,
						action: 'hide_thwcfd_admin_notice',
					};
					$.post( ajaxurl, data, function() {

					});
					$(wrapper).hide(20);
				}
				   				
				return {
					skipAdminNotice : skip_admin_notice,
					hideAdminNotice : hide_admin_notice,
			   	};
			}(window.jQuery, window, document));	

			function thwcfdSkipAdminNotice(e, elm){
				thwcfd_dismissable_notice.skipAdminNotice(e, elm);
			}

			function thwcfdHideAdminNotice(e, elm){
				thwcfd_dismissable_notice.hideAdminNotice(e, elm);
			}	
	    </script>
	    <?php
	}

	public function update_dismissable_notice_status(){
		$is_hidden = get_transient('thwcfd_hide_admin_notice');
		if($is_hidden){
			$data = array('1.5.2');
			update_option('thwcfd_notice_status', $data, 'no');
			delete_transient('thwcfd_hide_admin_notice');
		}
	}

}

endif;