<?php
defined( 'ABSPATH' ) or exit( 'restricted access' );
/*
Plugin Name: LeadSquared Suite
Plugin URI: http://www.leadsquared.com/
Description: LeadSquared Suite allows you to capture your leads from web forms and visitor comments seamlessly  and track their online behavior.
Version: 0.7.4
Author: LeadSquared, Inc
Author URI: http://www.leadsquared.com/
License: GPL v2

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License, version 2, as
    published by the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/
 /**
  * Define useful comments
  */
define('LSQFORM_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('LSQFORM_PLUGIN_FILE_PATH', LSQFORM_PLUGIN_PATH.'leadsquared-form.php');
define('LSQFORM_PLUGIN_URL', plugin_dir_url(__FILE__));
define('LSQFORM_PLUGIN_ICON', plugin_dir_url(__FILE__).'images/icon.png');
//--------------------------------------------------------------------------------//
if ( ! defined( 'LSQFORM_PLUGIN_SLUG' ) ) define( 'LSQFORM_PLUGIN_SLUG', 'leadsquared-wordpress-suit' );
if ( ! defined( 'LSQFORM_SETTING_SLUG' ) ) define('LSQFORM_SETTING_SLUG', 'settings-api');
if ( ! defined( 'LSQFORM_REST_API_OPTION' ) ) define('LSQFORM_REST_API_OPTION', '_leadsquared_rest_api');
if ( ! defined( 'LSQFORM_COMMENT_FORM_OPTION' ) ) define('LSQFORM_COMMENT_FORM_OPTION', '_comments2lead_form_fields');
if ( ! defined( 'LSQFORM_OPTION' ) ) define('LSQFORM_OPTION', 'leadsquared_modules');
if ( ! defined( 'LSQFORM_REST_CREATE_LEADS_URL' ) ) define('LSQFORM_REST_CREATE_LEADS_URL', 'https://'.get_option("leadsquared_api").'/v2/LeadManagement.svc/Lead.Capture?');
if ( ! defined( 'LSQFORM_REST_FIELD_META_URL' ) ) define('LSQFORM_REST_FIELD_META_URL', 'https://'.get_option("leadsquared_api").'/v2/LeadManagement.svc/LeadsMetaData.Get?');
if ( ! defined( 'LSQFORM_REST_PROSPECT_ACTIVITY_TYPE' ) ) define('LSQFORM_REST_PROSPECT_ACTIVITY_TYPE', 'https://'.get_option("leadsquared_api").'/v2/ProspectActivity.svc/ActivityTypes.Get?');
if ( ! defined( 'LSQFORM_REST_PROSPECT_ACTIVITY_CREATE' ) ) define('LSQFORM_REST_PROSPECT_ACTIVITY_CREATE', 'https://'.get_option("leadsquared_api").'/v2/ProspectActivity.svc/Create?');
if ( ! defined( 'LSQFORM_PROSPECT_ACTIVITY_OPTION' ) ) define('LSQFORM_PROSPECT_ACTIVITY_OPTION', '_comments2lead_prospect_activity');
if ( ! defined( 'LSQFORM_AUTH' ) ) define('LSQFORM_AUTH', 'https://api.leadsquared.com/v2/Authentication.svc/UserByAccessKey.Get?');
/**
*   Check the class is existing
*/


if(!class_exists('WP_leadsquared_form'))  {
class WP_leadsquared_form {
    var $plugin_url;
	var $parent_menu_slug;
	var $submenu_slug;
	var $restkeys;
	var $rest_create_leads; 
	var $leadsquare_prospect_activity;
	var $comment_form_lead;
    /**
	 * Standard Constructor to initialize hooks and options 
	 */
    public function __construct() {
	    // assign default menu slug value
		$this->plugin_url        = LSQFORM_PLUGIN_URL;
		$this->parent_menu_slug  = LSQFORM_PLUGIN_SLUG;
		$this->submenu_slug      = LSQFORM_SETTING_SLUG;
		$this->restkeys          = get_option(LSQFORM_REST_API_OPTION);
		$this->lsqoption         = get_option(LSQFORM_OPTION);
		$this->rest_create_leads = LSQFORM_REST_CREATE_LEADS_URL;
		$this->leadsquare_prospect_activity   = get_option(LSQFORM_PROSPECT_ACTIVITY_OPTION);
		$this->comment_form_lead              = get_option(LSQFORM_COMMENT_FORM_OPTION);
		$this->prospect_activity_type_url     = LSQFORM_REST_PROSPECT_ACTIVITY_TYPE;
		//
		add_action('init', array($this, 'leadsquared_form_init'));
		add_action( 'init', array($this,'leadsquared_form_post_type') );
		add_action( 'init', array($this,'leadsquared_cf7_logs_post_type') );
		add_action('plugins_loaded', array($this, 'prospectID'), 11);
		/**
		 * Register hooks that are fired when the plugin is activated, deactivated and uninstalled respectively.
		 */
		register_activation_hook( __FILE__, array( $this, 'LSQFORM_activate') );
	}
	
	/**
	 * Activate the Plugin and set up options
	 */
	public function LSQFORM_activate() {
	    add_option( LSQFORM_REST_API_OPTION, '' );
		$lsq_mod_array = array("lsqform"=>"0", "lsqts"=>"0", "cf72lsq"=>"0", "lsqc2l"=>"0");
		add_option( "leadsquared_modules", $lsq_mod_array );
		
	} // END public function install
		 
	/**
	 * init callback to include js files
	 * 
	 */

	
	public function leadsquared_form_init() {
		add_action( 'admin_menu', array($this, 'register_leadsquared_form_menu_page' ));
		add_action( 'admin_enqueue_scripts', array($this, 'load_wp_lsq_admin_style' ));
		add_action( 'add_meta_boxes', array($this, 'leadsquared_meta') );
		add_action( 'wp_ajax_leadsquared_form_get_form', array($this, 'leadsquared_form_get_form') );
		add_action( 'wp_ajax_nopriv_leadsquared_form_get_form', array($this, 'leadsquared_form_get_form') );
		add_action( 'save_post', array( $this, 'save_leadsquared_form' ) );
		add_action( 'save_post', array( $this, 'save_leadsquared_tracking' ) );
		add_action( 'wp_footer', array( $this, 'leadsquared_tracking_script' ) );
		add_action('manage_leadsquared_form_posts_custom_column', array( $this,'leadsquared_form_columns_content'), 10, 2);
		add_filter( 'post_row_actions', array( $this,'remove_row_actions'), 10, 1 );
		add_filter('manage_leadsquared_form_posts_columns', array( $this,'leadsquared_form_columns_head'), 10);	
		add_filter( 'hidden_meta_boxes', array( $this,'hidden_meta_boxes') , 10, 3 );
		add_filter('manage_edit-leadsquared_cf7_logs_columns', array( $this,'add_new_logs_columns'));
		add_action( 'manage_leadsquared_cf7_logs_posts_custom_column', array( $this,'logs_columns'), 10, 2 );
		add_filter( 'manage_edit-leadsquared_cf7_logs_sortable_columns', array( $this,'logs_sortable_columns') );
		add_shortcode('leadsquared-form', array( $this, 'leadsquared_shortcode'));	
		add_filter('widget_text','do_shortcode');		
		if($this->lsqoption['cf72lsq'] == '1' )
		 {
			add_action( 'wpcf7_before_send_mail', array($this, 'contact2leads' ));
			add_action( 'admin_init',  array($this,'cf7_leadsquared_add_tag_generator'), 20 );
			add_action('init', array($this, 'contacts_lead_init'));
		 }
		 if($this->lsqoption['lsqc2l'] == '1' )
		 {
			add_action('transition_comment_status', array( &$this, 'approve_comment_callback'), 10, 3);
			add_action('wp_insert_comment', array( &$this, 'approve_comment_posted'), 10, 2 );
			add_action( 'wp_ajax_load_prospect_activity_request', array(&$this, 'load_prospect_activity_ajax_request' ));
		 }
	}

	/**
	 * admin_enqueue_scripts callback function
	 */
	public function load_wp_lsq_admin_style($hook) { 	
	$admin_path = admin_url();
			$js_object = array('plugin_url' => $admin_path);
		wp_register_style('lead-squared-home-style', plugins_url( '/css/leadsquared-home-style.css' , __FILE__ ), array(), '1.1', 'all' );
		wp_enqueue_style( 'lead-squared-home-style' );
		
		//		
			if( 'leadsquared_page_comments-to-lead' != $hook )
				return;		
			//modal lightboxes
			add_thickbox();
			wp_enqueue_script('leads2comment-tablednd', plugins_url( '/js/comments-to-lead-tablednd.js' , __FILE__ ) , array( 'jquery' ));	
			wp_localize_script( 'leads2comment-tablednd', 'object_name', $js_object );
			wp_enqueue_script('leads2comment-admin', plugins_url( '/js/comments-to-lead-admin.js' , __FILE__ ) , array( 'jquery' ));	
			wp_localize_script( 'leads2comment-admin', 'object_name', $js_object );

	}
	
	/**
	 * Add admin menu
	 */
	public function register_leadsquared_form_menu_page() {
	// Add a page to manage this plugin's settings
		global $menu, $submenu;
		$menu_exist = false;
		if(is_array($menu)) { 
			foreach($menu as $item) {
			  if(strtolower($item[2]) == strtolower($this->parent_menu_slug)) {
				  $menu_exist = true;
			  }
			}
		}
        if(!$menu_exist) {
		 /* Register sub-menu for LeadSquared security credential and Comments2Lead page */
					add_menu_page(
								  __('LeadSquared'),                                    // Parent Page Title
								  __('LeadSquared'),                                    // Parent Menu Title
								  'manage_options',                                     // Capability
								  $this->parent_menu_slug,                              // Parent Menu slug 
								  array($this, 'leadsquared'),                         // Callback function  
								  $this->plugin_url.'images/icon.png'                   // Parent Menu icon
								  );
					add_submenu_page(
					              $this->parent_menu_slug,
								  '',
								  '',
								  'manage_options',
								  $this->parent_menu_slug
								  );
					if($this->lsqoption['lsqform'] == '1' or $this->lsqoption['cf72lsq'] =='1' or $this->lsqoption['lsqts'] == '1'or $this->lsqoption['lsqc2l'] == '1')	
					{
						add_submenu_page(
					              $this->parent_menu_slug,                                // Parent slug 
								  __('Leadsquared API Setting'),                          // Sub Page title
								  __('Security Credentials'),                             // Sub Menu title
								  'manage_options',                                       // Sub Capability
								  'settings-api',                                         // Sub Menu slug 
								  array($this, 'setting_api_form')                       // Sub Callback function
 								  );
						add_submenu_page(
					              'wpcf7',                                            // Parent slug 
								  __('Leadsquared CF7 logs'),                          // Sub Page title
								  __('LeadSquared Logs'),                             // Sub Menu title
								  'manage_options',                                       // Sub Capability
								  'edit.php?post_type=leadsquared_cf7_logs'                       // Sub Callback function
 								  );	
					}
					if($this->lsqoption['lsqform'] == '1' )
					{						
						add_submenu_page(
									  $this->parent_menu_slug,                                // Parent slug 
									  __('Leadsquared Form'),                                 // Sub Page title
									  __('Forms'),                                            // Sub Menu title
									  'manage_options',                                       // Sub Capability
									 'edit.php?post_type=leadsquared_form'                       // Sub Callback function
									  );
					}
					if($this->lsqoption['lsqc2l'] == '1' )
					{						
						add_submenu_page(
								  $this->parent_menu_slug,                                // Parent slug 
							 	  __('Comments to LeadSquared Form'),                     // Sub Page title
								  __('Comments to LeadSquared'),                          // Sub Menu title
								  'manage_options',                                       // Sub Capability
								  'comments-to-lead',                                     // Sub Menu slug 
								  array(&$this, 'leadsquared_comment_form_configuration') // Sub Callback function
								  );
					}
								  }

				}				
	
	/**
	 *  Home page function
	 */
	 public function leadsquared() {
	         include_once(LSQFORM_PLUGIN_PATH.'inc/lsqadmin.php');
	 }
	/**
	 * Rest API settings function
	 */
	 public function setting_api_form() {
	  	    include_once(LSQFORM_PLUGIN_PATH.'inc/settingsapi.php');
	 }
	 
	 /**
		 * Callback function for load ajax prospect type
		 */
		 public function load_prospect_activity_ajax_request() {
		    if(isset($_POST['status']) == 1) {
			if($this->leadsquare_prospect_activity) {
			$prospect_activity_option = "";
			if($this->leadsquare_prospect_activity[0] != '' && $this->leadsquare_prospect_activity[1] != '')  {
				$prospect_status_option     = $this->leadsquare_prospect_activity[0]; 
				$prospect_activity_option   = $this->leadsquare_prospect_activity[1];
			} }
		   	$activity_url = $this->prospect_activity_type_url.'accessKey='.$this->restkeys["access_key"].'&secretKey='.$this->restkeys["secret_key"];
			$activity_json = $this->getRestdata($activity_url);
			$decode_activity_json = json_decode($activity_json, TRUE);
			if($decode_activity_json) {
					$activity_type = array();
					foreach($decode_activity_json as $key => $value) {
						   $activity_type[$value['ActivityEvent']] = $value['DisplayName'];
			  	    }
			$prospect_activity_type = array_unique($activity_type);
			//}
            $output = 'Activity Type: <select name="select_activity_type" id="select_activity_type">
                       <option value="" selected="selected">-- SELECT --</option>';
            if(!empty($prospect_activity_type)) {
			asort($prospect_activity_type);
            foreach($prospect_activity_type as $activity_key => $activity_values) {
			$select = (isset($prospect_activity_option) == $activity_key) ? 'selected="selected"' : '';
			$output .= '<option '.$select.' value="'.$activity_key.'">'.$activity_values.'</option>'; 
			} 
			}
            $output .= '</select>';
			print $output;
			die;
			}
			else {
			print "You must configure Security Credentials before you can use Comments-to-Lead plugin";
			die;
			}
			}
		 }
	 
	 /**
	 * Registering Post Type
	 */
	
	public function leadsquared_form_post_type() {
		$labels = array(
			"name" => "Forms",
			"singular_name" => "Forms",
			"menu_name" => "Forms",
			"all_items" => "Leadsquared Forms",
			"add_new" => "Add New",
			"add_new_item" => "Add New Form",
			"edit" => "Edit",
			"edit_item" => "Edit  Form",
			"new_item" => "New Form",
			"view" => "View",
			"view_item" => "View Form",
			"search_items" => "Search Form",
			);

		$args = array(
			"labels" => $labels,
			"description" => "",
			"public" => false,
			"show_ui" => true,
			"has_archive" => false,
			"show_in_menu" => 'edit.php?post_type=leadsquared_form',
			"exclude_from_search" => true,
			"capability_type" => "post",
			"map_meta_cap" => true,
			"hierarchical" => false,
			"rewrite" => array( "slug" => "leadsquared_form", "with_front" => true ),
			"query_var" => true,
			"menu_position" => 5,
			"menu_icon" => LSQFORM_PLUGIN_ICON,		
			"supports" => array( "title" ),		
		);
		register_post_type( "leadsquared_form", $args );

	// End of cptui_register_my_cpts()
	}
	
	public function leadsquared_cf7_logs_post_type() {
		$labels = array(
			"name" => "Logs",
			"singular_name" => "Logs",
			"menu_name" => "Logs",
			"all_items" => "Leadsquared CF7 Logs",
			"view" => "View",
			"view_item" => "View Logs",
			"edit" => "View",
			"edit_item" => "Log",
			"search_items" => "Search Logs",
			);

		$args = array(
			"labels" => $labels,
			"description" => "",
			"public" => false,
			"show_ui" => true,
			"has_archive" => false,
			"show_in_menu" => 'edit.php?post_type=leadsquared_cf7_logs',
			"exclude_from_search" => true,
			"capability_type" => "post",
			'capabilities' => array(
				'create_posts' => 'do_not_allow'
			  ),
			"map_meta_cap" => true,
			"hierarchical" => false,
			"rewrite" => array( "slug" => "leadsquared_cf7_logs", "with_front" => true ),
			"query_var" => true,
			"menu_position" => 5,
			"menu_icon" => LSQFORM_PLUGIN_ICON,		
			"supports" => array(''),		
		);
		register_post_type( "leadsquared_cf7_logs", $args );

	// End of cptui_register_my_cpts()
	}
	
	/*
	* Meta Box for LeadSquared Form
	*/
	
	public function leadsquared_meta() {
		if($this->lsqoption['lsqts'] == '1' )
		 {
			add_meta_box( 'leadsquared_tracking', __( 'LeadSquared Tracking Script', 'leadsquared' ), array($this, 'leadsquared_tracking_meta_box' ), null ,'side');
		
		 }
		 add_meta_box( 'leadsquared_meta', __( 'LeadSquared Form', 'leadsquared' ), array($this, 'leadsquared_form_meta_box' ), 'leadsquared_form' ,'side');
		add_meta_box( 'leadsquared_meta_display', __( 'LeadSquared Form', 'leadsquared' ), array($this, 'leadsquared_form_meta_box_display' ), 'leadsquared_form' ,'normal');
		
		add_meta_box( 'leadsquared_cf7_log_data', __( 'Data Sent', 'leadsquared' ), array($this, 'leadsquared_cf7log_data_meta_box_display' ), 'leadsquared_cf7_logs' ,'normal');
		
		add_meta_box( 'leadsquared_cf7_log_res', __( 'Response', 'leadsquared' ), array($this, 'leadsquared_cf7log_res_meta_box_display' ), 'leadsquared_cf7_logs' ,'normal');
		
	}
	
	public function leadsquared_tracking_meta_box() {
		include_once(LSQFORM_PLUGIN_PATH.'inc/metabox-tracking.php');
	}
	
	public function leadsquared_form_meta_box() {
		include_once(LSQFORM_PLUGIN_PATH.'inc/metabox.php');
	}
	
	public function leadsquared_form_meta_box_display() {
		include_once(LSQFORM_PLUGIN_PATH.'inc/metabox-display.php');
	}
	
	public function leadsquared_cf7log_data_meta_box_display() {
		include_once(LSQFORM_PLUGIN_PATH.'inc/metabox-cf7-log-data.php');
	}
	
	public function leadsquared_cf7log_res_meta_box_display() {
		include_once(LSQFORM_PLUGIN_PATH.'inc/metabox-cf7-log-res.php');
	}
	
	public function leadsquared_tracking_script(){
		if($this->lsqoption['lsqts'] == '1' )
		{
			include_once(LSQFORM_PLUGIN_PATH.'inc/tracking-script.php');
		}
		include_once(LSQFORM_PLUGIN_PATH.'inc/lsq-script.php');
	}
	
	public function leadsquared_form_get_form(){
		$landing_page_id = $_POST['landing_pid'];
		$landing_page_style = $_POST['landing_pstyle'];
		$api_url_base = 'https://'.get_option("leadsquared_api").'/v2/LandingPage.svc';
		$url = $api_url_base . '/ExportFormHtml?accessKey=' . $this->restkeys["access_key"]. '&secretKey=' . $this->restkeys["secret_key"].'&landingPageId='. $landing_page_id .'&exportWithStyle='.$landing_page_style;
		$request = wp_remote_get($url);
		$response = wp_remote_retrieve_body( $request );
		$json_decode = json_decode($response, true);
		$form = $json_decode['Content'];
		echo '<div id="showresults">'.$form.'</div>';
		die();
	}
	
	public function save_leadsquared_form($post_id) {
		
		/*
		 * We need to verify this came from the our screen and with proper authorization,
		 * because save_post can be triggered at other times.
		 */

		// Check if our nonce is set.
		if ( ! isset( $_POST['leadsquared_form_box_nonce'] ) )
			return $post_id;

		$nonce = $_POST['leadsquared_form_box_nonce'];

		// Verify that the nonce is valid.
		if ( ! wp_verify_nonce( $nonce, 'leadsquared_form_box' ) )
			return $post_id;

		// If this is an autosave, our form has not been submitted,
                //     so we don't want to do anything.
		if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) 
			return $post_id;

		// Check the user's permissions.
		if ( 'page' == $_POST['post_type'] ) {

			if ( ! current_user_can( 'edit_page', $post_id ) )
				return $post_id;
	
		} else {

			if ( ! current_user_can( 'edit_post', $post_id ) )
				return $post_id;
		}

		/* OK, its safe for us to save the data now. */

		// Sanitize the user input.
		
		$landing_page_id = sanitize_text_field( $_POST['lp-select'] );
		$landing_page_style = sanitize_text_field( $_POST['lpstyle'] );
		$landing_page_code =  htmlspecialchars($_POST['formcode']);
		$landing_page_settings = array(
			"landing_page_id"=>$landing_page_id,
			"landing_page_style"=>$landing_page_style
		);
		update_post_meta( $post_id, 'leadsquared-form-settings', $landing_page_settings );
		update_post_meta( $post_id, 'leadsquared-form-code', $landing_page_code );
	}
	
	public function save_leadsquared_tracking($post_id) {
		/*
		 * We need to verify this came from the our screen and with proper authorization,
		 * because save_post can be triggered at other times.
		 */

		// Check if our nonce is set.
		if ( ! isset( $_POST['leadsquared_tracking_nonce'] ) )
			return $post_id;

		$nonce = $_POST['leadsquared_tracking_nonce'];

		// Verify that the nonce is valid.
		if ( ! wp_verify_nonce( $nonce, 'leadsquared_tracking' ) )
			return $post_id;

		// If this is an autosave, our form has not been submitted,
                //     so we don't want to do anything.
		if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) 
			return $post_id;

		// Check the user's permissions.
		if ( 'page' == $_POST['post_type'] ) {

			if ( ! current_user_can( 'edit_page', $post_id ) )
				return $post_id;
	
		} else {

			if ( ! current_user_can( 'edit_post', $post_id ) )
				return $post_id;
		}

		/* OK, its safe for us to save the data now. */

		// Sanitize the user input.
		if(isset($_POST['tracking_status'])){
			$tracking_status = sanitize_text_field( $_POST['tracking_status'] );
		} else {
			$tracking_status = '';
		}
		
		if(isset($_POST['lsq_score'])){
				$lsq_score = sanitize_text_field( $_POST['lsq_score'] );
		} else {
				$lsq_score = '';
		}
		
		$lsq_tracking = array(
			"tracking"=>$tracking_status,
			"score"=>$lsq_score
		);
		update_post_meta( $post_id, 'lsq_tracking', $lsq_tracking );
	}

	public function remove_row_actions( $actions )
	{
		if( get_post_type() === 'leadsquared_form' )
			unset( $actions['view'] );
		if( get_post_type() === 'leadsquared_cf7_logs' )
			unset( $actions['edit'] );
			unset( $actions['view'] );
			unset( $actions['trash'] );
			unset( $actions['inline hide-if-no-js'] );
		return $actions;
	}
	
	public function leadsquared_shortcode($params = array()) {
			// default parameters
		extract(shortcode_atts(array(
			'id' => '1',
		), $params));
		$pid = $id;
		$lpc = get_post_meta( $pid, 'leadsquared-form-code', true );
		return htmlspecialchars_decode($lpc);
	}
	
	public function leadsquared_form_columns_head($columns) {
	  $leadsquared_columns = array();
	  $date = 'date'; 
	  foreach($columns as $key => $value) {
		if ($key==$date){
		  $leadsquared_columns['short_code'] = 'Shortcode';   
		  $leadsquared_columns['author'] = 'Author'; 
		}
		  $leadsquared_columns[$key] = $value;
	  }
	  return $leadsquared_columns;
	}
	public function cf7_leadsquared_add_tag_generator() {
		 if($this->lsqoption['cf72lsq'] == '1' )
		 {
			include_once(LSQFORM_PLUGIN_PATH.'inc/lscf7-modul.php');
		 }
	}
	
	/**
		 * LeadSquared comment form configuration function
		 */
		public function leadsquared_comment_form_configuration() {
		    $url          = LSQFORM_REST_FIELD_META_URL.'accessKey='.$this->restkeys["access_key"].'&secretKey='.$this->restkeys["secret_key"];
			$activity_url = LSQFORM_REST_PROSPECT_ACTIVITY_TYPE.'accessKey='.$this->restkeys["access_key"].'&secretKey='.$this->restkeys["secret_key"];
		    $json = $this->getRestdata($url);
			$activity_json = $this->getRestdata($activity_url);
			include_once(LSQFORM_PLUGIN_PATH.'inc/comment-form-configuration.php');
		}
	/**
          * Get REST data from a given URL
          */
		 public function getRestdata($url) {
		    $request = wp_remote_get($url);
			$response = wp_remote_retrieve_body( $request );
			$result = $response;
			return $result; 
		 }
	
	public function leadsquared_form_columns_content($column_name, $post_ID) {
		if ($column_name == 'short_code') {
				echo '<strong>[leadsquared-form id="'. $post_ID .'"]</strong></br>Copy this shortcode and paste it into your post, page, or text widget content';
		}
	}
	public function ProspectIDScript() {
		?><script>
		function SetProspectID(){
				  if (typeof(MXCProspectId) !== "undefined")
				  jQuery('input[name="ProspectID"]').attr('value',MXCProspectId);
				 }
				  window.onload = function()  
				 {
				  setTimeout (SetProspectID , 2000);
				  };				
		</script><?php
	
	}

		/**
	 * before send mail callback
	 */
	public function contact2leads( $cf7 ) {
		if (!isset($cf7->posted_data) && class_exists('WPCF7_Submission')) {
			$submission = WPCF7_Submission::get_instance();
			if ( $submission ) {
				$posted_data = $submission->get_posted_data();
			}
			}
			else
			{
				$posted_data = $cf7->posted_data;
			}

			if( !empty($posted_data['ProspectID']) ){
				$url = $this->rest_create_leads.'accessKey='.$this->restkeys["access_key"].'&secretKey='.$this->restkeys["secret_key"];	
				$data_string_value[] = array("Attribute"=>"Origin", "Value"=>"Contact Form 7");
				$data_string_value[] = array("Attribute"=>"ProspectID", "Value"=> $posted_data['ProspectID']);
			} else {
				$url = $this->rest_create_leads.'accessKey='.$this->restkeys["access_key"].'&secretKey='.$this->restkeys["secret_key"];	
				if(empty($posted_data['leadsquared-Source']))
				{
					$data_string_value[] = array("Attribute"=>"Source", "Value"=>"Contact Form 7");
				}
				if(empty($posted_data['leadsquared-Origin']))
				{
					$data_string_value[] = array("Attribute"=>"Origin", "Value"=>"Contact Form 7");
				}
			}	
			
			$phone_number = null;
			$country_code = null;
			$mobile_number = null;
			
			if (array_key_exists("leadsquared-Phone-cf7it-national",$posted_data)){
				$phone_number = $posted_data['leadsquared-Phone-cf7it-national'];
				unset($posted_data['leadsquared-Phone-cf7it-national']);
			}

			if (array_key_exists("leadsquared-Phone-cf7it-country-name",$posted_data)){
				unset($posted_data['leadsquared-Phone-cf7it-country-name']);
			}			
			
			if (array_key_exists("leadsquared-Phone-cf7it-country-code",$posted_data)){
				$country_code = $posted_data['leadsquared-Phone-cf7it-country-code'];
				unset($posted_data['leadsquared-Phone-cf7it-country-code']);
			}
			
			if (array_key_exists("leadsquared-Phone-cf7it-country-iso2",$posted_data)){
				unset($posted_data['leadsquared-Phone-cf7it-country-iso2']);
			}			
			
			if (array_key_exists("leadsquared-Mobile-cf7it-national",$posted_data)){
				$mobile_number = $posted_data['leadsquared-Mobile-cf7it-national'];
				unset($posted_data['leadsquared-Mobile-cf7it-national']);
			}

			if (array_key_exists("leadsquared-Mobile-cf7it-country-name",$posted_data)){
				unset($posted_data['leadsquared-Mobile-cf7it-country-name']);
			}			
			
			if (array_key_exists("leadsquared-Mobile-cf7it-national",$posted_data)){
				$country_code = $posted_data['leadsquared-Mobile-cf7it-national'];
				unset($posted_data['leadsquared-Mobile-cf7it-country-code']);
			}
			if (array_key_exists("leadsquared-Mobile-cf7it-country-iso2",$posted_data)){
				unset($posted_data['leadsquared-Mobile-cf7it-country-iso2']);
			}
			
			if(!is_null($phone_number)){
				$posted_data['leadsquared-Phone'] = '+'.$country_code.'-'.$phone_number;
			}
			
			if(!is_null($mobile_number)){
				$posted_data['leadsquared-Mobile'] = '+'.$country_code.'-'.$mobile_number;
			}
			
		foreach($posted_data as $key => $value){
				$exp_key = explode('-', $key);
				if($exp_key[0] == 'leadsquared'){
					if($exp_key[1] == 'multi'){
						$arr_value = $exp_key[2];
						if(is_array($value)){
							$arr_result[$arr_value] = implode(";",$value);
						} else {
							$arr_result[$arr_value] = $value;
						}
					}else{
						$arr_value = $exp_key[1];
						if(is_array($value)){
							$arr_result[$arr_value] = $value[0];
						} else {
							$arr_result[$arr_value] = $value;
						}
					}
				}
			}
		if($arr_result == null)
		  {
			return true;
		  } else {
		foreach($arr_result as $key => $value) {
			$value_esc_attr = stripslashes_deep(esc_attr($value));
			$value  = trim(preg_replace('/\s+/',' ', $value_esc_attr));
			$data_string_value[] = array("Attribute"=>$key, "Value"=>$value);
			
		}
		
		$post_string = json_encode($data_string_value);

		$response = wp_remote_request( $url, array( 
				'method'  => 'POST',
				'headers' => array('Content-Type' => 'application/json','Content-Length' => strlen($post_string)),
				'body'    => $post_string,
				'timeout' => 20
			) );

		if ( is_wp_error( $response ) ) {	
				$result =  false;
				
			} else {
				if($response['response']['code']  == '200'){
					$response_body = json_decode( $response['body'], true );
					$result = true; 
				} else {
					$response_body = json_decode( $response['body'], true );
					$result =  false;
				}
			}
			
			if(isset($posted_data['leadsquared-EmailAddress'])){
				$cf7t = $posted_data['leadsquared-EmailAddress'];
			}elseif(isset($posted_data['leadsquared-Phone'])){
				$cf7t = $posted_data['leadsquared-Phone'];
			}elseif(isset($posted_data['leadsquared-Mobile'])){
				$cf7t = $posted_data['leadsquared-Mobile'];
			}else{
				$cf7t = $posted_data['leadsquared-FirstName'];
			}
				$my_post = array(
					'post_title'    => $cf7t,
					'post_status'   => 'publish',
					'post_type' => 'leadsquared_cf7_logs',
					'meta_input' => array(
						'leadsquared-cf7-log-data' => $post_string,
						'leadsquared-cf7-log-response' => $response['body']
					)
				);
				 
				// Insert the post into the database.
				wp_insert_post( $my_post );
				return (int)$result;
		  }
	}
	
	public function approve_comment_callback($new_status, $old_status, $comment) {
	
			$comment_id = $comment->comment_ID;
			if($old_status != $new_status) {
			
				if($new_status == 'approved') {
					$this->activityOrLeadCreation($comment_id);
				}
				
			}
			
		}
	public function approve_comment_posted( $comment_id, $comment_object ) {
						
			$comment_approved = $comment_object->comment_approved;
			
			if( $comment_approved == 1 ) {

				$this->activityOrLeadCreation($comment_id);
				
			}			
		}
	public function activityOrLeadCreation($comment_id)
		{
			$activity = get_option(LSQFORM_PROSPECT_ACTIVITY_OPTION);
			if($activity) {
				 if(isset($activity[1]) && $activity[1] != '') {
						$prospect_req_url = LSQFORM_REST_PROSPECT_ACTIVITY_CREATE.'accessKey='.$this->restkeys["access_key"].'&secretKey='.$this->restkeys["secret_key"];
						$comment_wp       = get_comment($comment_id); 
						$FirstName        = $comment_wp->comment_author;
						$EmailAddress     = $comment_wp->comment_author_email;
						$Website          = $comment_wp->comment_author_url;
						$ActivityNote     = $comment_wp->comment_content;
						$ActivityEvent    = $activity[1];
						$ActivityDateTime = date("Y-m-d H:i:s");
						//Remove message spaces
						$ActivityNote   = trim(preg_replace('/\s+/',' ', $ActivityNote));
						/***
						 * create JSON formatted data with comment value.
						 */
						$prospect_post_string = '{"FirstName":"'.$FirstName.'", "EmailAddress":"'.$EmailAddress.'", "ActivityEvent": "'.$ActivityEvent.'", "ActivityNote": "'.$ActivityNote.'", "ActivityDateTime": "'.$ActivityDateTime.'", "Website": "'.$Website.'", "Source": "Website Comments"}';
						//Request to post activity in LeadSquared
						 $this->curlUsingPost($prospect_req_url, $prospect_post_string);
					}
			}
			else {
					      $this->lsq_curl($comment_id);
					}
		}
		
		 		//Function to post value in LeadSquared
		public function curlUsingPost($url = NULL, $data = NULL) {
			if(empty($url) || empty($data))
			{
			  return 'Error: invalid Url or Data';
			}
			
			$post_string = $data;

			
			$response = wp_remote_request( $url, array( 
				'method'  => 'POST',
				'headers' => array('Content-Type' => 'application/json','Content-Length' => strlen($post_string)),
				'body'    => $post_string,
				'timeout' => 45
			) );

			if ( is_wp_error( $response ) ) {
			   $result =  false;
			} else {
				$result = true; 
			}			
				return (int)$result;
		}
		
		/**
		 * REST api request function
		 */
		public function lsq_curl($comment_id) {
			/*** 
			 * Create Rest API keys with value to save data in LeadSquared
			 */
			$lsqc2l = $this->comment_form_lead;
			$url = $this->rest_create_leads.'accessKey='.$this->restkeys["access_key"].'&secretKey='.$this->restkeys["secret_key"];
			$lsqc2l = $this->comment_form_lead;
			foreach($lsqc2l as $value){
					$leads_schemaname[] = $value['leads_schemaname'];
				}
				$comment_wp = get_comment($comment_id); 
				$name    = $comment_wp->comment_author;
				$email   = $comment_wp->comment_author_email;
				$website = $comment_wp->comment_author_url;
				$notes   = $comment_wp->comment_content;
				$comment_default_values = array($name,$email,$website,$notes);
				$c=array_combine($leads_schemaname,$comment_default_values);
				$i=0;
				foreach($c as $key => $value) {
					 $data_key_value[$i] = '{"Attribute":"'.$key.'", "Value": "'.$value.'"},';
					 $i++;
				}
				foreach($data_key_value as $value) {
							$data_string_value .= $value;
						}
				$additnional_av =  '{"Attribute":"Source" ,"Value": "Website Comments"},{"Attribute": "SearchBy","Value": "EmailAddress"},';
				$post_string = '[
                         '.$data_string_value.$additnional_av.'		
						]';
				$this->curlUsingPost($url,$post_string);

		}
		
	public function prospectID() {
		
		if( class_exists('WPCF7_Shortcode') ) {
			wpcf7_add_form_tag( array( 'tracking', 'tracking*' ), array($this,'wpcf7_ProspectID'), true );
		} 
	}
	
	public function wpcf7_ProspectID( $tag ) {

		add_action( 'wp_footer', array($this, 'ProspectIDScript') );

		$html = '<input type="hidden" name="ProspectID" id="ProspectID" class="ProspectID" value="" >';

		return $html;
	}
		
	public function hidden_meta_boxes( $hidden, $screen, $use_defaults )
	{
		global $wp_meta_boxes;
		$cpt = 'leadsquared_cf7_logs'; // Modify this to your needs!

		if( $cpt === $screen->id && isset( $wp_meta_boxes[$cpt] ) )
		{
			
			$tmp = array();
			foreach( (array) $wp_meta_boxes[$cpt] as $context_key => $context_item )
			{
				foreach( $context_item as $priority_key => $priority_item )
				{
					foreach( $priority_item as $metabox_key => $metabox_item )
						
						if(!in_array($metabox_key,array('leadsquared_cf7_log_data','leadsquared_cf7_log_res'))){
							$tmp[] = $metabox_key;
						}
				}
			}
			$hidden = $tmp;  // Override the current user option here.
		}
		return $hidden;
	}
	
	public function add_new_logs_columns($gallery_columns) {    

		$new_columns['title'] = _x('EmailAddress', 'column name'); 
		$new_columns['phone'] = _x('Phone', 'column name');
		$new_columns['mobile'] = _x('Mobile', 'column name');
		$new_columns['status'] = _x('Status', 'column name');
		$new_columns['date'] = _x('Date', 'column name');
	 
		return $new_columns;
	}

	public function logs_columns( $column, $post_id ) {
		
		global $post;
		
		$meta = get_post_meta( $post_id, 'leadsquared-cf7-log-data', true );
		$meta_ara = json_decode($meta,true);
		
		$res = get_post_meta( $post_id, 'leadsquared-cf7-log-response', true );
		$res_ara = json_decode($res,true);
		
		$Phone = '';
		$Mobile = '';
		
		$res_msg = "<p style='color:red'>Error</p>";
		
		if($res_ara['Status'] == 'Success' ){
			$res_msg = "<p style='color:green'>Success</p>";
		}
		
		foreach($meta_ara as $key=>$value){
			if($value['Attribute'] == 'Phone'){
				$Phone = $value['Value'];
			}elseif($value['Attribute'] == 'Mobile'){
				$Mobile = $value['Value'];
			}
		}
		
		switch( $column ) {

			case 'phone' :

				if ( empty( $Phone ) )
					echo __( '' );

				else
					printf( __( '%s' ), $Phone );

				break;


			case 'mobile' :


				if ( empty( $Mobile ) )
					echo __( '' );

				else
					printf( __( '%s' ), $Mobile );

				break;
			
			case 'status' :


				if ( empty( $res_msg ) )
					echo __( '' );

				else
					printf( __( '%s' ), $res_msg );

				break;

			default :
				break;
		}
	}
	
	public function logs_sortable_columns( $columns ) {

		$columns['status'] = 'status';

		return $columns;
	}
   //end class
   }
}
// Instantiate our class
$WP_leadsquared_form = new WP_leadsquared_form;