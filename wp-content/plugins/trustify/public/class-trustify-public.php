<?php

/**
 * The public-facing functionality of the plugin.
 *
 * @link       http://responsive-pixel.com/
 * @since      1.0.0
 *
 * @package    Trustify
 * @subpackage Trustify/public
 */

/**
 * The public-facing functionality of the plugin.
 *
 * Defines the plugin name, version, and two examples hooks for how to
 * enqueue the admin-specific stylesheet and JavaScript.
 *
 * @package    Trustify
 * @subpackage Trustify/public
 * @author     Responsive-pixel <rajendrarijal@responsive-pixel.com>
 */
class Trustify_Public {

	/**
	 * The ID of this plugin.
	 *
	 * @since    1.0.0
	 * @access   private
	 * @var      string    $plugin_name    The ID of this plugin.
	 */
	private $plugin_name;

	/**
	 * The version of this plugin.
	 *
	 * @since    1.0.0
	 * @access   private
	 * @var      string    $version    The current version of this plugin.
	 */
	private $version;

	/**
	 * Initialize the class and set its properties.
	 *
	 * @since    1.0.0
	 * @param      string    $plugin_name       The name of the plugin.
	 * @param      string    $version    The version of this plugin.
	 */
	public function __construct( $plugin_name, $version ) {

		$this->plugin_name = $plugin_name;
		$this->version = $version;

	}

	/**
	 * Register the stylesheets for the public-facing side of the site.
	 *
	 * @since    1.0.0
	 */
	public function enqueue_styles() {

		/**
		 * This function is provided for demonstration purposes only.
		 *
		 * An instance of this class should be passed to the run() function
		 * defined in Trustify_Loader as all of the hooks are defined
		 * in that particular class.
		 *
		 * The Trustify_Loader will then create the relationship
		 * between the defined hooks and the functions defined in this
		 * class.
		 */

		wp_enqueue_style( $this->plugin_name, plugin_dir_url( __FILE__ ) . 'css/trustify-public.css', array(), $this->version, 'all' );
		wp_enqueue_style( 'animate', WP_PLUGIN_URL . '/trustify/admin/css/animate.css' );

        //Typography option
 		$options = get_option( 'trustify_settings' );
 		$key = 'trustify_popup_typography';
 		$text_color = ( ( $options[$key]['text_color'] )!='' ? $options[$key]['text_color'] : '#000');
        $font_size = ( ( $options[$key]['font_size'] )!='' ? $options[$key]['font_size'] : '12');
        $line_height = ( isset( $options[$key]['line_height'] ) ? $options[$key]['line_height'] : '1.4');
        $text_transform = ( ( $options[$key]['text_transform'] )!='' ? $options[$key]['text_transform'] : 'none');

        //Design options        
 		$options = get_option( 'trustify_settings' );
 		$key = 'trustify_popup_design';
 		//Image Position
 		$popup_imgposition = ( isset ( $options[$key]['imgposition'] ) ? $options[$key]['imgposition'] : '');
 		switch ($popup_imgposition) {
            case 'imageOnLeft':
                $imgFloat = 'left';
                break;
            case 'imageOnRight':
                $imgFloat = 'right';
                break;
            default:
                $imgFloat = '';
        }
 		$popup_bgcolor = ( ( $options[$key]['bg_color'] )!='' ? $options[$key]['bg_color'] : '#e0e0e0');
 		$popup_bgimage = ( isset( $options[$key]['bg_image'] ) && $options[$key]['bg_image']!='' ? $options[$key]['bg_image'] : '');
 		$popup_innerpadding = ( ( $options[$key]['inner_padding'] )!='' ? $options[$key]['inner_padding'] : '10');
 		if(is_array($popup_innerpadding)){
 			$top = $popup_innerpadding['top'];
 			$bottom = $popup_innerpadding['bottom'];
 			$left = $popup_innerpadding['left'];
 			$right = $popup_innerpadding['right'];
 		}else{
 			$top = $bottom = $left = $right = $popup_innerpadding;
 		}
 		$border_enable = ( isset( $options[$key]['border'] ) ? $options[$key]['border'] : '');
 		$border_color = ( ( $options[$key]['border_color'] )!='' ? $options[$key]['border_color'] : '#c9c9c9');
 		$border_width = ( ( $options[$key]['border_width'] )!='' ? $options[$key]['border_width'] : '1');
 		$border_radius = ( ( $options[$key]['border_radius'] )!='' ? $options[$key]['border_radius'] : '0');
        $popup_width = ( ( $options[$key]['popup_width'] )!='' ? $options[$key]['popup_width'] : '250');
        //for responsive
 		$options = get_option( 'trustify_settings' );
 		$key = 'trustify_popup_additional';
        $resp_enable = ( isset( $options[$key]['resp_enable'] ) ? $options[$key]['resp_enable'] : '');
        if($resp_enable==1){
        	$display = 'block';
        }else{
        	$display = 'none';
        }

		if($border_enable==1){
		$trustify_border_css = "
                border:2px solid {$border_color};
                border-width:{$border_width}px;
                border-radius:{$border_radius}px;
            ";
		}else{
			$trustify_border_css = '';
		}

		if($popup_bgimage!=''){
		  $trustify_bg_css = "
		               background-blend-mode: overlay;
		               background-image:url('{$popup_bgimage}');
		               background-size:cover;
		               background-repeat:no-repeat;
		               background-position: center;
		               ";
		            
		}else{
		  $trustify_bg_css = '';
		}

		$trustify_popup_front_css = "
	        #trustifyWrapper .popup_template{
                background-color:{$popup_bgcolor};
                {$trustify_border_css}
                {$trustify_bg_css}
            }
            #trustifyWrapper .popup_position .trustify-content-wrap{
                color:{$text_color};
            	font-size:{$font_size}px;
            	text-transform:{$text_transform};
            	line-height:{$line_height};
            }
			@media (max-width: 767px){ 
              text-transform:{$text_transform};
            }	
			#trustifyWrapper .popup_position img{
				float: {$imgFloat};
			}
			
			#trustifyWrapper .popup-item{
				padding-top:{$top}px;
				padding-right:{$right}px;
				padding-bottom:{$bottom}px;
				padding-left:{$left}px;
			}
			#trustifyWrapper .popup_position{
				width:{$popup_width}px;
			}
			@media (max-width: 767px){ 
              #trustifyWrapper { display: {$display};} 
            }	
			";
	wp_add_inline_style( 'trustify', $trustify_popup_front_css );

}

	/**
	 * Register the JavaScript for the public-facing side of the site.
	 *
	 * @since    1.0.0
	 */
	public function enqueue_scripts() {

		/**
		 * This function is provided for demonstration purposes only.
		 *
		 * An instance of this class should be passed to the run() function
		 * defined in Trustify_Loader as all of the hooks are defined
		 * in that particular class.
		 *
		 * The Trustify_Loader will then create the relationship
		 * between the defined hooks and the functions defined in this
		 * class.
		 */

		wp_enqueue_script( 'jquery.cookie', plugin_dir_url( __FILE__ ) . 'js/jquery.cookie.js', array( 'jquery' ), $this->version, false );
		wp_enqueue_script( $this->plugin_name, plugin_dir_url( __FILE__ ) . 'js/trustify-public.js', array( 'jquery' ), $this->version, false );

		/**  
		* Popup Time
		*/
 		$options = get_option( 'trustify_settings' );
 		$key = 'trustify_popup_time';
 		$popup_start = ( ( $options[$key]['start_time']!='' ) ? $options[$key]['start_time'] : '3');
 		$popup_onscreen = ( ( $options[$key]['onscreen_time']!='' ) ? $options[$key]['onscreen_time'] : '5');
 		$popup_range_from = ( ( $options[$key]['start_from']!='' ) ? $options[$key]['start_from'] : '3');
 		$popup_range_to = ( ( $options[$key]['start_to']!='' ) ? $options[$key]['start_to'] : '20');
       
        // Popup animation/position
 		$options = get_option( 'trustify_settings' );
 		$key = 'trustify_popup_design';
 		$popup_position = ( ( $options[$key]['position'] )!='' ? $options[$key]['position'] : 'bottomLeft');
 		$popup_animation = ( ( $options[$key]['animation'] )!='' ? $options[$key]['animation'] : 'fadeInLeft');

		/* Notification type */
		$options = get_option( 'trustify_auto_settings' );
		$key =  'trustify_autonotice_enable';
		$woptions = get_option( 'trustify_woo_settings' );
		$eddoptions = get_option( 'trustify_edd_settings' );
		$wkey = 'trustify_woonotice_enable';
		$eddkey = 'trustify_eddnotice_enable';
		$n_type = ( isset( $options[$key] ) ) ? $options[$key] : '';
		$woo = ( isset( $woptions[$wkey] ) ) ? $woptions[$wkey] : '';		
        $edd = ( isset( $eddoptions[$eddkey] ) ) ? $eddoptions[$eddkey] : '';

		wp_localize_script( 'trustify', 'trustify_popup_params', array(
			'trustify_popup_position' => $popup_position,
			'trustify_popup_start_time' => $popup_start,
			'trustify_popup_transition' => $popup_animation,
			'trustify_popup_range_from' => $popup_range_from,
			'trustify_popup_range_to' => $popup_range_to,
			'trustify_popup_stay' => $popup_onscreen,
			'trustify_notification_type' => $n_type,
			'trustify_woo_notice' => $woo,
			'trustify_edd_notice' => $edd,
            'ajax_url' => admin_url( 'admin-ajax.php' )
		) );

	}

	/**  
	* Include frontend content 
	*/
	public function trustify_frontend(){
		$path = plugin_dir_path( __FILE__ ). '/partials/trustify-public-display-wrapper.php';
		require_once($path);
	}

	/**
     * Get random Trustify Notice without repeat
     */
    public function trustify_get_notice()
    {
        $trustify_ids = $this->getTrustifyDisplayedNoticeIds();
        $path = plugin_dir_path( __FILE__ ). '/partials/trustify-public-display-content.php';

        require_once($path);
        exit();
    }

    public function getTrustifyDisplayedNoticeIds()
    {
        if(isset($_COOKIE['trustify_ids'])) {
            return json_decode(stripslashes($_COOKIE['trustify_ids']));
        }

        return [];
    }

    /* For Auto Notifications */
    public function trustify_get_auto_notice()
    {
        $path = plugin_dir_path( __FILE__ ). '/partials/trustify-public-display-auto-content.php';

        require_once($path);
        exit();
    }

    /* For Woo Notifications */
    public function trustify_get_woo_notice()
    {
    	$trustify_ids = $this->getTrustifyDisplayedNoticeIds();
        $path = plugin_dir_path( __FILE__ ). '/partials/trustify-public-display-woo-content.php';

        require_once($path);
        exit();
    }

    /* For EDD Notifications */
    public function trustify_get_edd_notice()
    {
    	//$trustify_ids = $this->getTrustifyDisplayedNoticeIds();
        $path = plugin_dir_path( __FILE__ ). '/partials/trustify-public-display-edd-content.php';

        require_once($path);
        exit();
    }
    
    /* Track Click Count */
    public function trustify_click_track(){
    	global $wpdb;
    	$pid = $_POST['product_id'];
    	$table_name = $wpdb->base_prefix.'trustify_report';
        
		$success = $wpdb->insert("{$table_name}", array(
		   "product_id" => $pid,
		),array('%d'));

		if($success){
			echo 'success';
		}else{
			echo 'error';
		}
		die();
    }
}

