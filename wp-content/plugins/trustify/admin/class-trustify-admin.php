<?php

/**
 * The admin-specific functionality of the plugin.
 *
 * @link       http://responsive-pixel.com/
 * @since      1.0.0
 *
 * @package    Trustify
 * @subpackage Trustify/admin
 */

/**
 * The admin-specific functionality of the plugin.
 *
 * Defines the plugin name, version, and two examples hooks for how to
 * enqueue the admin-specific stylesheet and JavaScript.
 *
 * @package    Trustify
 * @subpackage Trustify/admin
 * @author     Responsive-pixel <rajendrarijal@responsive-pixel.com>
 */
class Trustify_Admin {

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
	 * @param      string    $plugin_name       The name of this plugin.
	 * @param      string    $version    The version of this plugin.
	 */

	public $report_details_table = NULL;

	public function __construct( $plugin_name, $version ) {

		$this->plugin_name = $plugin_name;
		$this->version = $version;

	}

	/**
	 * Register the stylesheets for the admin area.
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

		wp_enqueue_style( $this->plugin_name, plugin_dir_url( __FILE__ ) . 'css/trustify-admin.css', array(), $this->version, 'all' );

		wp_enqueue_style(  'jquery-ui', WP_PLUGIN_URL . '/trustify/admin/css/jquery-ui.min.css' );

		wp_enqueue_style( 'animate', WP_PLUGIN_URL . '/trustify/admin/css/animate.css' );
		// Add the color picker css file       
		wp_enqueue_style( 'wp-color-picker' );       
	}

	/**
	 * Register the JavaScript for the admin area.
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
        wp_enqueue_media();
		wp_enqueue_script( $this->plugin_name, plugin_dir_url( __FILE__ ) . 'js/trustify-admin.js', array( 'jquery' ), $this->version, false );

		wp_enqueue_script( 'trustify-custom', WP_PLUGIN_URL . '/trustify/admin/js/custom.js', array('jquery-ui-core', 'jquery-ui-datepicker', 'wp-color-picker' ), '1.0', true );

	}

	/**
	* Plugin admin  success/failure Notices.
	*/
	public function trustify_admin_notice_success(){
		 ?>
	    <div class="notice notice-success is-dismissible">
	        <p><strong><?php esc_html_e( 'Settings Saved!', 'trustify' ); ?></strong></p>
	    </div>
    <?php
	}

	public function trustify_admin_notice_error(){
		$class = 'notice notice-error is-dismissible';
		$message = esc_html__( 'Opps! An error has occurred.', 'trustify' );
		printf( '<div class="%1$s"> <p> %2$s </p> </div>', esc_attr($class), esc_html($message) );
	}

	/**
	* Register Custom Post Type mifi.
	*/
	public function create_mifi_notice(){

		$labels = array(
			'name'               => esc_attr__( 'Notifications', 'trustify' ),
			'singular_name'      => esc_attr__( 'Notification', 'trustify' ),
			'menu_name'          => esc_attr__( 'Trustify', 'trustify' ),
			'name_admin_bar'     => esc_attr__( 'Trustify', 'trustify' ),
			'add_new'            => esc_attr__( 'Add New', 'trustify' ),
			'add_new_item'       => esc_attr__( 'Add New Notification', 'trustify' ),
			'new_item'           => esc_attr__( 'New Notification', 'trustify' ),
			'edit_item'          => esc_attr__( 'Edit Notification', 'trustify' ),
			'view_item'          => esc_attr__( 'View Notification', 'trustify' ),
			'all_items'          => esc_attr__( 'Mannual Notifications', 'trustify' ),
			'search_items'       => esc_attr__( 'Search Notifications', 'trustify' ),
			'parent_item_colon'  => esc_attr__( 'Parent Notifications:', 'trustify' ),
			'not_found'          => esc_attr__( 'No Notifications found.', 'trustify' ),
			'not_found_in_trash' => esc_attr__( 'No Notifications found in Trash.', 'trustify' )
			);

		$args = array(
			'labels'             => $labels,
			'description'        => esc_attr__( 'Description.', 'trustify' ),
			'public'             => true,
			'publicly_queryable' => true,
			'show_ui'            => true,
			'show_in_menu'       => true,
			'query_var'          => true,
			'rewrite'            => array( 'slug' => 'mifi' ),
			'capability_type'    => 'post',
			'has_archive'        => true,
			'hierarchical'       => false,
			'menu_position'      => 15,
			'menu_icon'			=> 'dashicons-megaphone',
			'supports'           => array( 'title', 'thumbnail')
			);

		register_post_type( 'mifi', $args );
	}

	/**
	 * Adds meta boxes to the post editing screen
	 */
	public function mifi_time_metabox(){
		add_meta_box( 
			'mifi_time_meta', 
			esc_attr__('Set Notification Contents','trustify'), 
			array($this,'display_mifi_time_meta'), 
			'mifi', 
			'normal', 
			'high' 
			);
	}

	/**
	 * Outputs the content of the meta box
	*/
	public function display_mifi_time_meta($post){
		wp_nonce_field( basename( __FILE__ ), 'mifi_nonce'  );
		$mifi_stored_time_meta = get_post_meta($post->ID );
		?>
		<table class="form-table">
		    <tr>
			<td><label><h4><?php echo esc_html__('Text Field','trustify'); ?></h4></label></td>
			<td><input type="text" name="mifi-time-text" placeholder="<?php echo esc_html__('Someone Purchased','trustify'); ?>" id="mifi-time-text" value="<?php if( isset($mifi_stored_time_meta['mifi-time-text'])) echo $mifi_stored_time_meta['mifi-time-text'][0]; ?>"> </td>
			</tr>
			<tr>
			<td><label><h4><?php echo esc_html__('Heading Field','trustify'); ?></h4></label></td>
			<td><input type="text" name="mifi-heading" id="mifi-heading" placeholder="<?php echo esc_html__('Product Name','trustify'); ?>" value="<?php if( isset($mifi_stored_time_meta['mifi-heading'])) echo $mifi_stored_time_meta['mifi-heading'][0]; ?>"></td>
            </tr>
            <tr>
			<td><label><h4><?php echo esc_html__('Set Notification Time','trustify'); ?> </h4> </label></td>
			<td><input type="number" min="0" placeholder="<?php echo esc_html__('e.g: 10 min','trustify'); ?>" name="mifi-time" class="" id="mifi-time"  value="<?php if( isset($mifi_stored_time_meta['mifi-time'])) echo $mifi_stored_time_meta['mifi-time'][0]; ?>"/>
			<input type="text" placeholder="<?php echo esc_html__('min or hour','trustify'); ?>" name="mifi-min-hr" id="mifi-min-hr"  value="<?php if( isset($mifi_stored_time_meta['mifi-min-hr'])) echo $mifi_stored_time_meta['mifi-min-hr'][0]; ?>"/><?php echo esc_html__('Ago','trustify'); ?></td>
            </tr>
            <tr>
			<td><label><h4><?php echo esc_html__('Set Date','trustify'); ?></h4></label> </td>
			<td><input type="text" placeholder="Start date" name="mifi-from-date" class="mifi_pick" id="mifi-from-date"  value="<?php if( isset($mifi_stored_time_meta['mifi-from-date'])) echo $mifi_stored_time_meta['mifi-from-date'][0]; ?>"/>
			<?php echo esc_html__('To','trustify'); ?>
			<input type="text" placeholder="<?php echo esc_html__('End date','trustify'); ?>" name="mifi-to-date" class="mifi_pick" id="mifi-to-date"  value="<?php if( isset($mifi_stored_time_meta['mifi-to-date'])) echo $mifi_stored_time_meta['mifi-to-date'][0]; ?>"/></td>		
		   </tr>
		</table>
		<?php
	}

	/**
	 * Store the meta boxes input
	 */
	public function mifi_stored_time_meta($post_id){
		 	//check saved status
		$is_autosave = wp_is_post_autosave ($post_id);
		$is_revision = wp_is_post_revision ($post_id);
		$is_valid_nonce = ( isset($_POST[ 'mifi_nonce' ]) && wp_verify_nonce( $_POST['mifi_nonce'], basename( __FILE__ )))? 'true': 'false';

	 	//Exit script depending on save status
		if( $is_autosave || $is_revision || !$is_valid_nonce ){
			return;
		} 

	 	//check for input and sanitize/save if needed
		if( isset( $_POST['mifi-time'])){

			update_post_meta( $post_id, 'mifi-time-text', sanitize_text_field( $_POST['mifi-time-text'] ) );

			update_post_meta( $post_id, 'mifi-heading', sanitize_text_field( $_POST['mifi-heading'] ));

			update_post_meta( $post_id, 'mifi-time', sanitize_text_field( $_POST['mifi-time']) );	
			update_post_meta( $post_id, 'mifi-min-hr', sanitize_text_field( $_POST['mifi-min-hr']) ); 	

			update_post_meta( $post_id, 'mifi-from-date', sanitize_text_field( $_POST['mifi-from-date']) );	 	

			update_post_meta( $post_id, 'mifi-to-date', sanitize_text_field( $_POST['mifi-to-date']) );
		}
	}

	/**
	 * Adds admin side-option for Page list with checkbox.
	 */
 	public function myplugin_add_custom_box() {
 		add_meta_box( 
 			'post_sectionid',
 			esc_attr__( 'Exclude Trustify From', 'trustify' ),
 			array($this,'display_pages_metabox') ,
 			'mifi',
 			'side',
 			'low'
 			);
 	}
 	
    public function display_pages_metabox($post){

		$checkfield = maybe_unserialize( get_post_meta($post->ID, "checkfield", true) );
	    $var= $checkfield;
	    $str_arr = explode(',', $var);
        wp_nonce_field( basename( __FILE__ ), 'mifi_nonce'  );
        ?>
		<div class="mifi-postbox-fields">
			<div class="mifi-toggle-tab-header mifi-toggle-active"><h4><?php _e('Default WordPress Pages','trustify');?><span class="toggle-indicator" aria-hidden="true"></span></h4></div>
			<div class="mifi-postbox-fields mifi-toggle-tab-body">
				<p><input type="checkbox" name="checkfield[]" id="mifi_front_pages" value="front_page" <?php if( in_array('front_page',$str_arr)) echo 'checked';?>><label for="mifi_front_pages"><?php _e('Front Page','trustify');?></label></p>
				<p><input type="checkbox" name="checkfield[]" id="mifi_archive_pages" value="archive_page" <?php if( in_array('archive_page',$str_arr)) echo 'checked';?>/><label for="mifi_archive_pages"><?php _e('Archive Page','trustify');?></label></p>
				<p><input type="checkbox" name="checkfield[]"  id="mifi_404_pages" value="404_page" <?php if( in_array('404_page',$str_arr)) echo 'checked';?>/><label for="mifi_404_pages"><?php _e('404 Page','trustify');?></label></p>
				<p><input type="checkbox" name="checkfield[]"  id="mifi_search_pages" value="search_page" <?php if( in_array('search_page',$str_arr)) echo 'checked';?>/><label for="mifi_search_pages"><?php _e('Search Page','trustify');?></label></p>
				<p><input type="checkbox" name="checkfield[]" id="mifi_single_pages" value="single_page" <?php if( in_array('single_page',$str_arr)) echo 'checked';?>/><label for="mifi_single_pages"><?php _e('All Single Post/Page','trustify');?></label></p>
			</div>
		</div>        
        <?php
		$post_types = get_post_types(array('public'=>'true'));
		unset( $post_types['mifi'] );
		sort($post_types);
		foreach($post_types as $post_type){
			if(!($post_type == 'attachment')){
				$loop = get_posts( array( 'post_type' => $post_type, 'posts_per_page' => -1, 'post_status'=>'publish' ) );
				if(!empty($loop)):
					?>
					<div class="mifi-postbox-fields mifi-hide-singular" >
						<div class="mifi-toggle-tab-header">
							<h4>
								<?php esc_html_e('Specific ','trustify'); _e(ucwords($post_type));?>
								<span class="toggle-indicator" aria-hidden="true">
								</span>
							</h4>
						</div>
						<div class="mifi-postbox-fields mifi-toggle-tab-body" style="display:none;">
							<?php
							foreach($loop as $postloop): 
								$post_id = $postloop->ID;
							    $title = get_the_title( $post_id );
								?>
								<p>
									<input type="checkbox" name="checkfield[]" id="mifi-post-<?php echo esc_attr($post_id);?>" value="<?php echo esc_attr($post_id);?>" <?php if( in_array($post_id,$str_arr)) echo 'checked';?>	/>
									<label for="mifi-post-<?php echo esc_attr($post_id);?>"><?php echo esc_html( $title );?></label>
								</p>
								<?php
							endforeach; 
							?>
						</div>
					</div>
					<?php
				endif;
			}	
		}
		
	}

	public function save_checkfield( $post_id ){
		$is_valid_nonce = ( isset($_POST[ 'mifi_nonce' ]) && wp_verify_nonce( $_POST['mifi_nonce'], basename( __FILE__ )))? 'true': 'false';
		if(!$is_valid_nonce){
			return;
		}
	 	if( isset($_POST['checkfield']) ) {
	 		$var = implode( ",", $_POST['checkfield'] ) ;
        	update_post_meta( $post_id, "checkfield", $var);

        }else{
        	$var = '';
        	delete_post_meta($post_id,'checkfield', $var);
        }
    }

 	/**
	 * Add admin menu page to the custom post type
	 */
 	public function trustify_add_admin_menu(  ) {

        add_submenu_page(
            'edit.php?post_type=mifi',
            'Trustify', 'Settings',
            'manage_options',
            esc_html__('Trustify Notification Global Setting', 'trustify'),
            array($this,'trustify_options_page')
        );


        $trustify_report_page_hook_view = add_submenu_page( 'edit.php?post_type=mifi', __( 'Trustify', 'trustify' ), __( 'Report', 'trustify' ), 'manage_options', 'trustify-click-report', array( $this, 'trustify_report_page' ) );

        add_action( "load-$trustify_report_page_hook_view", array( $this, 'add_trustify_report_details_option' ) );

 	}
 	/**
	 * Trustify Click Reports Callback
	 */
    public function trustify_report_page() {
        $from = ( isset( $_GET['DateFrom'] ) && $_GET['DateFrom'] ) ? $_GET['DateFrom'] : '';
        $to = ( isset( $_GET['DateTo'] ) && $_GET['DateTo'] ) ? $_GET['DateTo'] : '';
        ?>
        <div class="wrap">
            <h2><?php _e( 'Trustify Report', 'trustify' ); ?> <a style="text-decoration: none;" href="<?php echo add_query_arg( array( 'page' => 'Trustify Notification Global Setting' ), admin_url( 'edit.php?post_type=mifi' ) ); ?>"><span class="dashicons dashicons-editor-break" style="vertical-align: middle;"></span></a></h2>

            	<div class="click-stat-view">
            		<h5><?php echo esc_html__('Click Statistics','trustify');?></h5>
            		<p><?php echo esc_html__('See how many store visitors clicked your sales popup.','trustify');?></p>
            		<ul>
            			<?php
            			global $wpdb;
            			$table_name = $wpdb->base_prefix."trustify_report";
            			$total_clicks = $wpdb->get_var("SELECT COUNT(report_id) from $table_name");
            			$today_clicks = $wpdb->get_var("SELECT COUNT(report_id) from $table_name WHERE cast(CURDATE() as DATE) = cast(`date` as DATE)");
            			$yes_clicks = $wpdb->get_var("SELECT COUNT(report_id) from $table_name WHERE cast(CURDATE()-1 as DATE) = cast(`date` as DATE)");
            			$last_clicks = $wpdb->get_var("SELECT COUNT(report_id) from $table_name WHERE `date` BETWEEN CURDATE()-7 AND CURDATE()");
            			?>
            			<li>
            				<span class="click-number"><?php echo esc_html($total_clicks);?></span>
            				<span class="click-label"><?php echo esc_html__('Total','trustify');?></span>
            			</li>
            			<li>
            				<span class="click-number"><?php echo esc_html($today_clicks);?></span>
            				<span class="click-label"><?php echo esc_html__('Today','trustify');?></span>
            			</li>
            			<li>
            				<span class="click-number"><?php echo esc_html($yes_clicks);?></span>
            				<span class="click-label"><?php echo esc_html__('Yesterday','trustify');?></span>
            			</li>
            			<li>
            				<span class="click-number"><?php echo esc_html($last_clicks);?></span>
            				<span class="click-label"><?php echo esc_html__('Last 7 days','trustify');?></span>
            			</li>
            		</ul>
            	</div>
                <div class="trustify-date-filter">
                    <strong><?php echo esc_html__('Filter by date: ','trustify')?></strong>
                    <div class="from">
                        <input type="text" name="DateFrom" placeholder="<?php echo esc_attr__('From Date','trustify')?>" value="<?php echo esc_attr($from);?>" autocomplete="off" />
                    </div>
                    <div class="to">
                        <input type="text" name="DateTo" placeholder="<?php echo esc_attr__('To Date','trustify')?>" value="<?php echo esc_attr($to);?>" autocomplete="off" />
                    </div>
                    <?php submit_button('Filter');?>
                </div>
            <form id="posts-filter" method="get">
                <?php $this->report_details_table->display(); ?>
            </form>
            <div id="ajax-response"></div>
            <br class="clear"/>
        </div>
        <?php
    }

 	public function add_trustify_report_details_option() {

        $option = 'per_page';
        $args = array(
            'label' => 'Number of items per page:',
            'default' => 10,
            'option' => 'reports_per_page'
        );
        add_screen_option( $option, $args );
        include_once( TRUSTIFY_ABSPATH . 'admin/class-trustify-report.php' );
        $this->report_details_table = new Trustify_Clicks_Report();
        $this->report_details_table->prepare_items();
 	}

    public function set_report_screen_options( $screen_option, $option, $value ) {
        if ( 'reports_per_page' === $option) {
            $screen_option = $value;
        }
        return $screen_option;
    }


 	/**
	 * Trustify Global Settings fields
	 */
 	public function trustify_settings_init(  ) {
        /*
        *=================================================================
        ** Auto Settings Starts.....
        *=================================================================
        */		
 		register_setting('pluginPage_auto','trustify_auto_settings');

 		add_settings_section(
            'trustify_auto_notice_section',
            esc_attr__( '', 'trustify' ),
            array($this,'trustify_autonotice_section_callback'),
            'pluginPage_auto'
 			);

 		add_settings_field(
 			'trustify_autonotice_enable',
 			esc_attr__( 'Check to enable Auto Notification', 'trustify' ),
 			array($this,'trustify_auto_notice_enable'),
 			'pluginPage_auto',
 			'trustify_auto_notice_section'
 			);

 		add_settings_field(
 			'trustify_autonotice_title',
 			esc_attr__( 'Add name of person', 'trustify' ).'<br><span class="auto-ttl">For eg:john,albert,mohomad</span>',
 			array($this,'trustify_auto_notice_title'),
 			'pluginPage_auto',
 			'trustify_auto_notice_section',
 			array('class'=>'trustify-auto')
 			); 	

 		add_settings_field(
 			'trustify_autonotice_country',
 			esc_attr__( 'Add name of Country', 'trustify' ).'<br><span class="auto-ttl">For eg:nepal,australia,korea</span>',
 			array($this,'trustify_auto_notice_country'),
 			'pluginPage_auto',
 			'trustify_auto_notice_section',
 			array('class'=>'trustify-auto')
 			); 	 

 		add_settings_field(
 			'trustify_autonotice_product',
 			esc_attr__( 'Add Products', 'trustify' ),
 			array($this,'trustify_auto_notice_product'),
 			'pluginPage_auto',
 			'trustify_auto_notice_section',
 			array('class'=>'trustify-auto')
 			);

/* 		add_settings_field(
 			'trustify_autonotice_static_texts',
 			esc_attr__( 'Configure Static Texts', 'trustify' ),
 			array($this,'trustify_auto_notice_statictext'),
 			'pluginPage_auto',
 			'trustify_auto_notice_section',
 			array('class'=>'trustify-auto')
 			); */
 		add_settings_field(
 			'trustify_autonotice_contents',
 			esc_attr__( 'Display Content', 'trustify' ),
 			array($this,'trustify_auto_notice_content'),
 			'pluginPage_auto',
 			'trustify_auto_notice_section',
 			array('class'=>'trustify-auto')
 			); 
 					

        /*
        *=================================================================
        ** Global Settings Starts.....
        *=================================================================
        */
        register_setting( 'pluginPage', 'trustify_settings' );   

 		add_settings_section(
 			'trustify_pluginPage_section',
 			 esc_attr__( '', 'trustify' ),
 			array($this,'trustify_settings_section_callback'),
 			'pluginPage'
 			);

 		add_settings_field(
 			'trustify_popup_time',
 			esc_attr__( 'Popup Time Settings', 'trustify' ),
 			array($this,'trustify_popup_time_section'),
 			'pluginPage',
 			'trustify_pluginPage_section'
 			);

 		add_settings_field(
 			'trustify_popup_design',
 			esc_attr__( 'Design Settings', 'trustify' ),
 			array($this,'trustify_popup_design_section'),
 			'pluginPage',
 			'trustify_pluginPage_section'
 			); 

 		add_settings_field(
 			'trustify_popup_typography',
 			esc_attr__( 'Typography Settings', 'trustify' ),
 			array($this,'trustify_popup_typo_section'),
 			'pluginPage',
 			'trustify_pluginPage_section'
 			);  

 		add_settings_field(
 			'trustify_popup_additional',
 			esc_attr__( 'Additional Settings', 'trustify' ),
 			array($this,'trustify_popup_add_section'),
 			'pluginPage',
 			'trustify_pluginPage_section'
 			); 

        /*
        *=================================================================
        ** Woo Notice Starts.....
        *=================================================================
        */		
 		register_setting('pluginPage_woo','trustify_woo_settings');

 		add_settings_section(
            'trustify_woo_notice_section',
            esc_attr__( '', 'trustify' ),
            array($this,'trustify_woonotice_section_callback'),
            'pluginPage_woo'
 			);

 		add_settings_field(
 			'trustify_woonotice_enable',
 			esc_attr__( 'Check to enable Wocommerce Notification', 'trustify' ),
 			array($this,'trustify_woo_notice_enable'),
 			'pluginPage_woo',
 			'trustify_woo_notice_section'
 			); 

 		add_settings_field(
 			'trustify_woonotice_timeperiod',
 			esc_attr__( 'Show orders within', 'trustify' ).'<br><span class="auto-ttl">in days</span>',
 			array($this,'trustify_woo_notice_timeperiod'),
 			'pluginPage_woo',
 			'trustify_woo_notice_section'
 			); 

 		add_settings_field(
 			'trustify_woonotice_content',
 			esc_attr__( 'Popup Display Contents', 'trustify' ),
 			array($this,'trustify_woo_notice_content'),
 			'pluginPage_woo',
 			'trustify_woo_notice_section'
 			);  

        /*
        *=================================================================
        ** EDD Notice Starts.....
        *=================================================================
        */		
 		register_setting('pluginPage_edd','trustify_edd_settings');

 		add_settings_section(
            'trustify_edd_notice_section',
            esc_attr__( '', 'trustify' ),
            array($this,'trustify_eddnotice_section_callback'),
            'pluginPage_edd'
 			);

 		add_settings_field(
 			'trustify_eddnotice_enable',
 			esc_attr__( 'Check to enable EDD Notification', 'trustify' ),
 			array($this,'trustify_edd_notice_enable'),
 			'pluginPage_edd',
 			'trustify_edd_notice_section'
 			); 

 		add_settings_field(
 			'trustify_eddnotice_timeperiod',
 			esc_attr__( 'Show orders within', 'trustify' ).'<br><span class="auto-ttl">in days</span>',
 			array($this,'trustify_edd_notice_timeperiod'),
 			'pluginPage_edd',
 			'trustify_edd_notice_section'
 			); 

 		add_settings_field(
 			'trustify_eddnotice_content',
 			esc_attr__( 'Popup Display Contents', 'trustify' ),
 			array($this,'trustify_edd_notice_content'),
 			'pluginPage_edd',
 			'trustify_edd_notice_section'
 			);  								


 	}

	/**
	 * Trustify Woo Notice Settings fields settings public function callback.
	 */

	public function trustify_woonotice_section_callback(){
		echo '';
	}

	public function trustify_woo_notice_enable(){ 
		$options = get_option( 'trustify_woo_settings' );
		$key = 'trustify_woonotice_enable';
		$value = ( isset( $options[$key] ) ) ? $options[$key] : '';    
		if($value == 1){
			$class='chkd';
		}else{
			$class='';
		} 
		?>
		<div class="woo-en-wrap clearfix">
	 	<input class="chk-en woo-edd <?php echo esc_attr($class);?>" type="checkbox" name="trustify_woo_settings[trustify_woonotice_enable]" value="1" <?php checked( $value, '1', true ); ?>>
	 	<div class="notice" style="display:none">
	 		<span><?php echo esc_html__('NOTE: Real Woocommerce Order Notifications will be shown.','trustify');?></span>
	 	</div>
		</div>
		<?php
	}

	public function trustify_woo_notice_timeperiod(){
		$options = get_option( 'trustify_woo_settings' );
		$key = 'trustify_woonotice_timeperiod';
		$value = ( isset( $options[$key] ) ) ? $options[$key] : '60'; 
		?>
		<input type="number" name="trustify_woo_settings[trustify_woonotice_timeperiod]" value="<?php echo esc_attr( $value ); ?>" /><span><?php echo esc_html__('days','trustify');?></span>
		<?php	
	}

	public function trustify_woo_notice_content(){ 
		$options = get_option( 'trustify_woo_settings' );
		$key = 'trustify_woonotice_content';
		$value = ( isset( $options[$key] ) ) ? $options[$key] : '[name] from [country] has purchased [product]';    	
		?>
		<textarea rows="5" cols="60" name="trustify_woo_settings[trustify_woonotice_content]"><?php echo esc_attr($value);?></textarea>
		<br><span class="auto-ttl"><?php echo esc_html__('Note:[name],[country],[city],[product] can be used in the field.','trustify'); ?></span>&nbsp;
		<span class="auto-ttl"><?php echo esc_html__('HTML tags like <br>,<strong>,<small> etc are supported.','trustify'); ?></span>
		<?php
	}

	/**
	 * Trustify EDD Notice Settings fields settings public function callback.
	 */

	public function trustify_eddnotice_section_callback(){
		echo '';
	}

	public function trustify_edd_notice_enable(){ 
		$options = get_option( 'trustify_edd_settings' );
		$key = 'trustify_eddnotice_enable';
		$value = ( isset( $options[$key] ) ) ? $options[$key] : '';   
		if($value == 1){
			$class='chkd';
		}else{
			$class='';
		} 	
		?>
		<div class="edd-en-wrap clearfix">
	 	<input class="chk-en woo-edd <?php echo esc_attr($class);?>" type="checkbox" name="trustify_edd_settings[trustify_eddnotice_enable]" value="1" <?php checked( $value, '1', true ); ?>>
	 	<div class="notice" style="display:none">
	 		<span><?php echo esc_html__('NOTE: Real EDD Order Notifications will be shown.','trustify');?><br><em><?php echo esc_html__('Uncheck WOO checkbox if enabled.','trustify');?></em></span>
	 	</div>
		</div>
		<?php
	}

	public function trustify_edd_notice_timeperiod(){
		$options = get_option( 'trustify_edd_settings' );
		$key = 'trustify_eddnotice_timeperiod';
		$value = ( isset( $options[$key] ) ) ? $options[$key] : '60'; 
		?>
		<input type="number" name="trustify_edd_settings[trustify_eddnotice_timeperiod]" value="<?php echo esc_attr( $value ); ?>" /><span><?php echo esc_html__('days','trustify');?></span>
		<?php	
	}

	public function trustify_edd_notice_content(){ 
		$options = get_option( 'trustify_edd_settings' );
		$key = 'trustify_eddnotice_content';
		$value = ( isset( $options[$key] ) ) ? $options[$key] : '[name] from [country] has purchased [product]';    	
		?>
		<textarea rows="5" cols="60" name="trustify_edd_settings[trustify_eddnotice_content]"><?php echo esc_attr($value);?></textarea>
		<br><span class="auto-ttl"><?php echo esc_html__('Note:[name],[country],[city],[product] can be used in the field.','trustify'); ?></span>&nbsp;
		<span class="auto-ttl"><?php echo esc_html__('HTML tags like <br>,<strong>,<small> etc are supported.','trustify'); ?></span>
		<?php
	}

	/**
	 * Trustify Auto Notice Settings fields settings public function callback.
	 */
	 public function trustify_autonotice_section_callback(){
	 	echo '';
	 }
     
     public function trustify_auto_notice_enable(){ 
 		$options = get_option( 'trustify_auto_settings' );
 		$key = 'trustify_autonotice_enable';
 		$value = ( isset( $options[$key] ) ) ? $options[$key] : '';    	
     	?>
     	<div class="auto-en-wrap clearfix">
	     	<input class="chk-en" type="checkbox" name="trustify_auto_settings[trustify_autonotice_enable]" value="1" <?php checked( $value, '1', true ); ?>>
	     	<div class="notice" style="display:none">
	     		<span><?php echo esc_html__('NOTE: Your mannually created notifications will be disabled.','trustify');?></span>
	     	</div>
     	</div>
     	<?php
     }

     public function trustify_auto_notice_title(){
 		$options = get_option( 'trustify_auto_settings' );
 		$key = 'trustify_autonotice_title';
 		$value = ( isset( $options[$key] ) ) ? $options[$key] : '';     	
     	?> 
         <textarea rows="10" cols="50" name="trustify_auto_settings[trustify_autonotice_title]"><?php echo esc_attr($value);?></textarea>
     	<?php    	
     }

     public function trustify_auto_notice_country(){
 		$options = get_option( 'trustify_auto_settings' );
 		$key = 'trustify_autonotice_country';
 		$value = ( isset( $options[$key] ) ) ? $options[$key] : '';      	
     	?> 
         <textarea rows="10" cols="50" name="trustify_auto_settings[trustify_autonotice_country]"><?php echo esc_attr($value);?></textarea>
     	<?php      	
     }

     public function trustify_auto_notice_product(){
     	?>
    <div class="products-meta-section-wrapper">
        <div class="table-products-wrapper">
            <?php
		 		$options = get_option( 'trustify_auto_settings' );
		 		$key = 'trustify_autonotice_product';
		 		$key_count = 'table_product_count';
                $table_product = ( isset( $options[$key] ) ) ? $options[$key] : '';  

                $table_product_count = ( isset( $options[$key_count] ) ) ? $options[$key_count] : ''; 
                $t_count = 0;
                if(!empty($table_product)){
                foreach ($table_product['title'] as $product => $val) {
                  $t_count++;
                $product_image = $table_product['url'][$product]; 


            ?>

                <div class="single-product">
                    <div class="single-section-title clearfix">
                        <h4 class="product-title"><?php esc_html_e( "Procuct ", 'trustify' ); echo $t_count.' :';?></h4>
                       
                        <div class="product-inputfield">
                            <input type="text" name="trustify_auto_settings[trustify_autonotice_product][title][<?php echo $t_count ;?>]" value="<?php echo esc_attr( $table_product['title'][$product] ); ?>" required/>
                        </div>
                        <div class="product-imagefield clearfix">
		                    <input type="text" name="trustify_auto_settings[trustify_autonotice_product][url][<?php echo $t_count ;?>]" placeholder="http://path/to/image.png" value="<?php echo esc_url( $product_image ); ?>">
		                    <span class="sme_galimg_ctrl">
		                        <a class="sme_add_galimg" href="#"><?php esc_html_e('Upload','trustify'); ?></a> 
		                    </span>
		                    <?php if($product_image!=''){?>
		                    <span class="prd-image"><img style="height:60px; width:60px;" src="<?php echo esc_url( $product_image ); ?>"></span>
                            <?php }?>
                        </div>
                        <div class="delete-table-product"><a href="javascript:void(0)" class="delete-product button"><?php esc_html_e('Delete Product','trustify'); ?></a></div>
                    </div>
                </div>
            <?php } }  ?>
        </div>
        <input id="table_products_count" type="hidden" name="trustify_auto_settings[table_product_count]" value="<?php echo $t_count; ?>" />
        <span class="delete-button table-products"><a href="javascript:void(0)" class="docopy-table-product button"><?php esc_html_e('Add Product','trustify'); ?></a></span>
    </div>
    <?php   	
     }

     public function trustify_auto_notice_statictext(){
 		$options = get_option( 'trustify_auto_settings' );
 		$key = 'trustify_autonotice_static_texts';
 		$value1 = ( isset( $options[$key]['has'] ) ) ? $options[$key]['has'] : 'has purchased'; 
 		$value2 = ( isset( $options[$key]['from'] ) ) ? $options[$key]['from'] : 'from';  
 		$value =  ( isset( $options['trustify_auto_contents'] ) ) ? $options['trustify_auto_contents'] : '';
     	?>
     	 <div class="static-texts">
         <span><em><?php esc_html_e('[name]','trustify'); ?></em></span>
	     	    <input type='text' id="trusify-notice-onscreen" name='trustify_auto_settings[trustify_autonotice_static_texts][from]' value='<?php echo $value2; ?>'>
         <span><em><?php esc_html_e('[country]','trustify'); ?></em></span>
	            <input type='text' id="trusify-notice-onscreen" name='trustify_auto_settings[trustify_autonotice_static_texts][has]' value='<?php echo $value1; ?>'>
         <span><em><?php esc_html_e('[product name]','trustify'); ?></em></span>
     	 </div>
     	<?php
     }

     public function trustify_auto_notice_content(){
 		$options = get_option( 'trustify_auto_settings' );
 		$key = 'trustify_autonotice_content'; 
 		$value =  ( isset( $options[$key] ) ) ? $options[$key] : '[name] from [country] has purchased [product]';
     	?>
		<textarea rows="10" cols="50" name="trustify_auto_settings[trustify_autonotice_content]"><?php echo esc_attr($value);?></textarea>
		<br><span class="auto-ttl">
			<?php echo esc_html__('Note:[name],[country],[product] can be used in the field.','trustify'); ?>
		</span>&nbsp;
		<span class="auto-ttl"><?php echo esc_html__('HTML tags like <br>,<strong>,<small> etc are supported.','trustify'); ?></span>
     	<?php
     }


	/**
	 * Trustify Global Settings fields settings public function callback.
	 */
	
	public function trustify_popup_time_section(){

 		$options = get_option( 'trustify_settings' );
 		$key = 'trustify_popup_time';
 		$popup_start = ( isset( $options[$key]['start_time'] ) ? $options[$key]['start_time'] : '');
 		$popup_onscreen = ( isset( $options[$key]['onscreen_time'] ) ? $options[$key]['onscreen_time'] : '');
 		$popup_range_from = ( isset( $options[$key]['start_from'] ) ? $options[$key]['start_from'] : '');
 		$popup_range_to = ( isset( $options[$key]['start_to'] ) ? $options[$key]['start_to'] : '');
 		?>
 		<div class="popup-time-section">
	        <div class="trustify-settings-tabs toggle-active" data-id="time">
	        	<?php esc_html_e('Popup Time Settings','trustify');?>
	        	<span class="toggle-indicator" aria-hidden="true"></span>
	        </div>
	        <div class="trustify-settings-wrap time"> 
	 		    <ul class="option-wrap">
		 		    <li>
		 		        <!--Popup Start Time -->
		 		    	<label><?php esc_html_e('Popup Start Time','trustify');?></label>
		 				<input type='number' min="0" id="trusify-notice-start-from"  name='trustify_settings[trustify_popup_time][start_time]' value='<?php echo $popup_start; ?>'><?php echo esc_attr__('Sec','trustify');?>
		 			</li>

                    <li>
			 			<!--Popup Stay Time -->
			 			<label><?php esc_html_e('Popup Stay Time','trustify');?></label>
			 			<input type='number' min="0" id="trusify-notice-onscreen" name='trustify_settings[trustify_popup_time][onscreen_time]' value='<?php echo $popup_onscreen; ?>'> <?php echo esc_attr__('Sec','trustify');?> 
		 			</li>

		 			<li>
			 			<!--Popup Range-->
			 			<label><?php esc_html_e('Popup Frequency','trustify');?></label>
			 			<input type='number' min="0" id="trusify-notice-start-from"  name='trustify_settings[trustify_popup_time][start_from]' value='<?php echo $popup_range_from; ?>'> <?php echo esc_attr__('to','trustify');?>
			 			<input type='number' min="0" id="trusify-notice-start-to" name='trustify_settings[trustify_popup_time][start_to]' value='<?php echo $popup_range_to; ?>'><?php esc_html_e('Sec','trustify'); ?>
	 		       </li>
	 		    </ul>   
	 		</div>
 		</div>
 		<?php		
	}

	public function trustify_popup_design_section(){

 		$options = get_option( 'trustify_settings' );
 		$key = 'trustify_popup_design';
 		$popup_position = ( isset ( $options[$key]['position'] ) ? $options[$key]['position'] : '');
 		$popup_animation = ( isset ( $options[$key]['animation'] ) ? $options[$key]['animation'] : '');
 		$popup_imgposition = ( isset ( $options[$key]['imgposition'] ) ? $options[$key]['imgposition'] : '');
 		$popup_imageview = ( isset ( $options[$key]['imageview'] ) ? $options[$key]['imageview'] : 'square');
 		$popup_bgcolor = ( isset ( $options[$key]['bg_color'] ) ? $options[$key]['bg_color'] : '');
 		$popup_bgimage = ( isset ( $options[$key]['bg_image'] ) ? $options[$key]['bg_image'] : '');
 		$popup_innerpadding = ( isset ( $options[$key]['inner_padding'] ) ? $options[$key]['inner_padding'] : array());
 		if(is_array($popup_innerpadding)){
 			$top = $popup_innerpadding['top'];
 			$bottom = $popup_innerpadding['bottom'];
 			$left = $popup_innerpadding['left'];
 			$right = $popup_innerpadding['right'];
 		}else{
 			$top = $bottom = $left = $right = $popup_innerpadding;
 		}
 		$border_enable = ( isset ( $options[$key]['border'] ) ? $options[$key]['border'] : '');
 		$border_color = ( isset ( $options[$key]['border_color'] ) ? $options[$key]['border_color'] : '');
 		$border_width = ( isset ( $options[$key]['border_width'] ) ? $options[$key]['border_width'] : '');
 		$border_radius = ( isset ( $options[$key]['border_radius'] ) ? $options[$key]['border_radius'] : '');
 		$popup_width = ( isset ( $options[$key]['popup_width'] ) ? $options[$key]['popup_width'] : '');
 		?>
        <div class="popup-design-section">
	        <div class="trustify-settings-tabs" data-id="position">
	        	<?php esc_html_e('Design Settings','trustify');?>
	        	<span class="toggle-indicator" aria-hidden="true"></span>
	        </div>
	        <div class="trustify-settings-wrap position" style="display:none"> 
	        <ul class="option-wrap">
	            <li>    
	            <!--Popup Position -->
	            <label><?php esc_html_e('Popup Position','trustify');?></label>
		 		<select id="template_position" name='trustify_settings[trustify_popup_design][position]'>
		 			<option value='bottomLeft' <?php selected( $popup_position, 'bottomLeft', true ); ?>><?php esc_html_e('Bottom Left','trustify'); ?></option>
		 			<option value='bottomRight' <?php selected( $popup_position, 'bottomRight', true ); ?>><?php esc_html_e('Bottom Right','trustify'); ?></option>
		 			<option value='topLeft' <?php selected( $popup_position, 'topLeft', true ); ?>><?php esc_html_e('Top Left','trustify'); ?></option>
		 			<option value='topRight' <?php selected( $popup_position, 'topRight', true ); ?>><?php esc_html_e('Top Right','trustify'); ?></option>
		 		</select> 
	            </li>

	            <li>
	            <!--Animation Style -->
	            <label><?php esc_html_e('Animation Style','trustify');?></label>
		 		<select id="transition_style" name='trustify_settings[trustify_popup_design][animation]'>
		 			<option value='fadeInLeft' <?php selected($popup_animation, 'fadeInLeft', true ); ?>><?php esc_html_e('Fade in Left','trustify'); ?></option>
		 			<option value='fadeInUp' <?php selected($popup_animation, 'fadeInUp', true ); ?>><?php esc_html_e('Fade in Up','trustify'); ?></option>
		 			<option value='fadeInRight' <?php selected($popup_animation, 'fadeInRight', true ); ?>><?php esc_html_e('Fade in Right','trustify'); ?></option>
		 			<option value='bounceInRight' <?php selected($popup_animation, 'bounceInRight', true ); ?>><?php esc_html_e('Bounce in Right','trustify'); ?></option>
		 			<option value='bounceInLeft' <?php selected($popup_animation, 'bounceInLeft', true ); ?>><?php esc_html_e('Bounce in Left','trustify'); ?></option>
		 			<option value='bounceInUp' <?php selected($popup_animation, 'bounceInUp', true ); ?>><?php esc_html_e('Bounce in Up','trustify'); ?></option>
		 			<option value='flipInX' <?php selected($popup_animation, 'flipInX', true ); ?>><?php esc_html_e('Flip in X','trustify'); ?></option>
		 			<option value='zoomIn' <?php selected($popup_animation, 'zoomIn', true ); ?>><?php esc_html_e('ZoomIn','trustify'); ?></option>
		 			<option value='shake' <?php selected($popup_animation, 'shake', true ); ?>><?php esc_html_e('Shake','trustify'); ?></option>
		 			<option value='swing' <?php selected($popup_animation, 'swing', true ); ?>><?php esc_html_e('Swing','trustify'); ?></option>
		 			<option value='rollIn' <?php selected($popup_animation, 'rollIn', true ); ?>><?php esc_html_e('RollIn','trustify'); ?></option>

		 		</select> 
	            </li>

	            <li>
	            <!--Image Position -->
	            <label><?php esc_html_e('Image Position','trustify');?></label>
		 		<select id="template_layout" name='trustify_settings[trustify_popup_design][imgposition]'>
		 			<option value='imageOnLeft' <?php selected($popup_imgposition, 'imageOnLeft',true ); ?>><?php esc_html_e('Image on left','trustify'); ?></option>
		 			<option value='imageOnRight' <?php selected($popup_imgposition, 'imageOnRight', true ); ?>><?php esc_html_e('Image on right','trustify'); ?></option>
		 			<option value='textOnly' <?php selected($popup_imgposition, 'textOnly', true ); ?>><?php esc_html_e('Text only','trustify'); ?></option>
		 		</select> 
                </li>

	            <li>
	            <!--Image Position -->
	            <label><?php esc_html_e('Image View','trustify');?></label>
		 		<select id="image-view" name='trustify_settings[trustify_popup_design][imageview]'>
		 			<option value='square' <?php selected($popup_imageview, 'square',true ); ?>><?php esc_html_e('Square','trustify'); ?></option>
		 			<option value='circle' <?php selected($popup_imageview, 'circle', true ); ?>><?php esc_html_e('Circle','trustify'); ?></option>
		 		</select> 
                </li>

                <li>
		 		<!--Popup Width -->
		 		<label><?php esc_html_e('Popup Width','trustify');?></label>
		 		<input type='number' min="0" id="trusify-popup-width"  name='trustify_settings[trustify_popup_design][popup_width]' value='<?php echo esc_attr($popup_width); ?>'><?php esc_html_e('px','trustify'); ?>		 		
                </li> 

                <li>
	            <!--Background Color -->
	            <label><?php esc_html_e('Background Color','trustify');?></label>
		 		<input type="text" class="color-picker" id="popup_bgcolor" name="trustify_settings[trustify_popup_design][bg_color]" value='<?php echo $popup_bgcolor; ?>'><br>
                </li>

                <li>
	            <!--Background Image -->
	            <label><?php esc_html_e('Background Image','trustify');?></label>
	            <div class="bg-image">
		 		<input type="text" class="upload-field" id="popup_bgimage" name="trustify_settings[trustify_popup_design][bg_image]" value='<?php echo esc_url($popup_bgimage); ?>' placeholder="https://image-path">
				<span class="sme_galimg_ctrl">
                    <a class="sme_add_galimg" href="#"><?php esc_html_e('Upload','trustify'); ?></a> 
                </span>
            	</div>
		 		<br>
                </li>

                <li>
		 		<!--Inner padding -->
		 		<label><?php esc_html_e('Inner Padding','trustify');?></label>
		 		<span class="padding-wrap">
		 		<input type='number' min="0" class="trusify-inner-padding" data-place="top"  name='trustify_settings[trustify_popup_design][inner_padding][top]' value='<?php echo esc_attr($top); ?>'>
		 		<input type='number' min="0" class="trusify-inner-padding" data-place="right"  name='trustify_settings[trustify_popup_design][inner_padding][right]' value='<?php echo esc_attr($right); ?>'>
		 		<input type='number' min="0" class="trusify-inner-padding" data-place="bottom" name='trustify_settings[trustify_popup_design][inner_padding][bottom]' value='<?php echo esc_attr($bottom); ?>'>
		 		<input type='number' min="0" class="trusify-inner-padding" data-place="left" name='trustify_settings[trustify_popup_design][inner_padding][left]' value='<?php echo esc_attr($left); ?>'>
		 		<?php esc_html_e('px','trustify'); ?>	
		 		</span>	 		
                </li>

                <li>
 		        <!--Border Options -->
 		        <label><?php esc_html_e('Check to Enable Border','trustify');?></label>
                <div class="auto-en-wrap clearfix">
	     	        <input class="chk-border" type="checkbox" name="trustify_settings[trustify_popup_design][border]" value="1" <?php checked( $border_enable, '1', true ); ?>>
	 	        </div>
	 	        </li>
	 	        <li>
	 	        <div class="trustify-border">
		 	        <label><?php esc_html_e('Border Color','trustify');?></label>
	 		        <input type="text" class="color-picker" id="popup_bordercolor" name="trustify_settings[trustify_popup_design][border_color]" value='<?php echo $border_color; ?>'><br>
		 		    <label><?php esc_html_e('Border Radius','trustify');?></label>
		 		    <input type='number' min="0" class="trustify-border" id="trusify-border-radius" name='trustify_settings[trustify_popup_design][border_radius]' value='<?php echo $border_radius; ?>'><?php echo esc_attr__('px','trustify');?>
                     <br>
		 		    <label><?php esc_html_e('Border Width','trustify');?></label>
		 		    <input type='number' min="0" id="trusify-border-width" name='trustify_settings[trustify_popup_design][border_width]' value='<?php echo $border_width; ?>'><?php echo esc_attr__('px','trustify');?>		
 		        </div>
 		        </li>
 		    </ul>    
 		    </div>
 		</div>

 		<?php
	}

    public function trustify_popup_typo_section(){

 		$options = get_option( 'trustify_settings' );
 		$key = 'trustify_popup_typography';
 		$text_color = ( isset( $options[$key]['text_color'] ) ? $options[$key]['text_color'] : '');
 		$font_size = ( isset( $options[$key]['font_size'] ) ? $options[$key]['font_size'] : '');
 		$line_height = ( isset( $options[$key]['line_height'] ) ? $options[$key]['line_height'] : '');
 		$text_transform = ( isset( $options[$key]['text_transform'] ) ? $options[$key]['text_transform'] : '');
 		?>
 		<div class="popup-typo-section">
	        <div class="trustify-settings-tabs" data-id="typo">
	        	<?php esc_html_e('Typography Settings','trustify');?>
	        	<span class="toggle-indicator" aria-hidden="true"></span>
	        </div>
	        <div class="trustify-settings-wrap typo" style="display:none"> 
		        <ul class="option-wrap">
		            <li>		    
			 		    <label><?php esc_html_e('Text Color','trustify');?></label>
			 			<input type='text' class="color-picker" id="popup_textcolor" name='trustify_settings[trustify_popup_typography][text_color]' value='<?php echo $text_color; ?>'>
	 	            </li>

	 	            <li>
		 		    <label><?php esc_html_e('Font Size','trustify');?></label>
		 			<input type='number' min="0" id="popup_font_size" name='trustify_settings[trustify_popup_typography][font_size]' value='<?php echo $font_size; ?>'><?php echo esc_attr__('px','trustify');?>			    
		            </li>

		            <li>
		            <label><?php esc_html_e('Text Transform','trustify');?></label>
			 		<select id="popup_text_tnsfrm" name='trustify_settings[trustify_popup_typography][text_transform]'>
			 		    <option value='none' <?php selected($text_transform, 'none',true ); ?>><?php esc_html_e('Default','trustify'); ?></option>
			 			<option value='uppercase' <?php selected($text_transform, 'uppercase',true ); ?>><?php esc_html_e('Uppercase','trustify'); ?></option>
			 			<option value='lowercase' <?php selected($text_transform, 'lowercase', true ); ?>><?php esc_html_e('Lowercase','trustify'); ?></option>
			 			<option value='capitalize' <?php selected($text_transform, 'capitalize', true ); ?>><?php esc_html_e('Capitalize','trustify'); ?></option>
			 		</select>
			 		</li>
	 	            <li>
		 		    <label><?php esc_html_e('Line Height','trustify');?></label>
		 			<input type='number' min="0" step="0.1" id="popup_line_height" name='trustify_settings[trustify_popup_typography][line_height]' value='<?php echo $line_height; ?>'>			    
		            </li>
			 	</ul>			    
 		    </div>
 		</div>
 		<?php    	
    }

    public function trustify_popup_add_section(){

 		$options = get_option( 'trustify_settings' );
 		$key = 'trustify_popup_additional';
 		$resp_enable = ( isset( $options[$key]['resp_enable'] ) ? $options[$key]['resp_enable'] : '');
 		$dis_loggedin = ( isset( $options[$key]['disable_loggedin'] ) ? $options[$key]['disable_loggedin'] : '');
 		?> 
 		<div class="popup-add-section">  
	        <div class="trustify-settings-tabs" data-id="add">
	        	<?php esc_html_e('Additional Settings','trustify');?>
	        	<span class="toggle-indicator" aria-hidden="true"></span>
	        </div>
	        <div class="trustify-settings-wrap add" style="display:none"> 		 	
		 		<!--Responsive Options -->
		 		<input class="chk-responsive" type="checkbox" name="trustify_settings[trustify_popup_additional][resp_enable]" value="1" <?php checked( $resp_enable, '1', true ); ?>>   
		 		<label><?php esc_html_e('Check to enable on mobile','trustify');?></label>
            </div>
	        <div class="trustify-settings-wrap add" style="display:none"> 		 	
		 		<!--Responsive Options -->
		 		<input class="chk-responsive" type="checkbox" name="trustify_settings[trustify_popup_additional][disable_loggedin]" value="1" <?php checked( $dis_loggedin, '1', true ); ?>>   
		 		<label><?php esc_html_e('Check to Disable For Logged In User','trustify');?></label>
            </div>
        </div>
        <?php
    }

 	public function trustify_settings_section_callback(  ) {

 		echo '';

 	}

 	public function trustify_options_page(  ) {

 		?>
 		<div class="settings-wrap" id="trustify-settings">
 		    <div class="trustify-settings-tab clearfix">
 		    	<ul class="tab-wrap clearfix">
 		    		<li class="tab active" data-id="global-settings-wrap">
 		    			<?php echo esc_attr__('Global Notification Settings',"trustify");?>
 		    		</li>
 		    		<li class="tab" data-id="trustify-auto-settings">
 		    			<?php echo esc_attr__('Auto Notification Settings',"trustify");?>
 		    		</li>
 		    		<li class="tab" data-id="trustify-woo-settings">
 		    			<?php echo esc_attr__('Woocommerce Notification',"trustify");?>
 		    		</li>
 		    		<li class="tab" data-id="trustify-edd-settings">
 		    			<?php echo esc_attr__('Easy Digital Notification',"trustify");?>
 		    		</li>
 		    	</ul>
 		    </div>
	 		<div class="tab-pane global-settings-wrap clearfix">
        <div class="trustify-title">
          <h2><?php echo esc_attr__('Trustify Global Settings',"trustify");?>
                   <span><?php echo esc_attr__('Set Trustify Notice Global Variables',"trustify");?></span>
          </h2>         
        </div> 
	 			<div class="trustify-main-settings" >
	 				<form action='options.php' method='post'>
	 					<?php
	 					settings_fields( 'pluginPage' );
	 					do_settings_sections( 'pluginPage' );
	 					submit_button();
	 					?>
	 				</form>		
	 			</div>
	 			<div class="trustify-backend-preview">
	 				<div class="plug_header">
	 					<h3><?php esc_html_e('Preview Section','trustify'); ?></h3>
	 				</div>

	 				<div class="popup_position bottomRight" >
	 					<div class="popup_template clearfix animated border radius" id="popup_template">
	 					   <div class="popup-item clearfix">
	 					   		<div class="popup_close">X</div>
		 						<img src="<?php echo plugin_dir_url( __FILE__ ).'/css/images/placeholder.png';?>">
		 						<p>
		 							<?php esc_html_e('Someone Purchased an Item','trustify'); ?> <br>
		 							<?php esc_html_e('From Nepal','trustify'); ?><br>
		 							<small class="time"><?php esc_html_e('16 min ago','trustify'); ?></small>
		 						</p>
	 						</div>
	 					</div>
	 				</div>
	 			</div>
	 		</div>
 			<div class="tab-pane trustify-auto-settings" style="display:none">
		        <div class="trustify-title">
		          <h2><?php echo esc_attr__('Trustify Auto Notification Settings',"trustify");?>
		                   <span><?php echo esc_attr__('Set Trustify Auto Notification Variables',"trustify");?></span>
		          </h2>

		        </div>        
 				<form action='options.php' method='post'>
 					<?php
 					settings_fields( 'pluginPage_auto' );
 					do_settings_sections( 'pluginPage_auto' );
 					submit_button();
 					?>
 				</form>	 				
 			</div>
 			<div class="tab-pane trustify-woo-settings" style="display:none">
		        <div class="trustify-title">
		          <h2><?php echo esc_attr__('Woocommerce Notification',"trustify");?>
		                   <span><?php echo esc_attr__('Set Trustify Woocommerce Real Order Notifications.',"trustify");?></span>
		          </h2>

		        </div>        
 				<form action='options.php' method='post'>
 					<?php
 					settings_fields( 'pluginPage_woo' );
 					do_settings_sections( 'pluginPage_woo' );
 					submit_button();
 					?>
 				</form>	 				
 			</div>
 			<div class="tab-pane trustify-edd-settings" style="display:none">
		        <div class="trustify-title">
		          <h2><?php echo esc_attr__('Easy Digital Notification',"trustify");?>
		                   <span><?php echo esc_attr__('Set Trustify EDD Real Order Notifications.',"trustify");?></span>
		          </h2>

		        </div>        
 				<form action='options.php' method='post'>
 					<?php
 					settings_fields( 'pluginPage_edd' );
 					do_settings_sections( 'pluginPage_edd' );
 					submit_button();
 					?>
 				</form>				
 			</div>
 		</div>
 		<?php
 	}


 	/**
	 * Trustify notification custom columns. 
	 */

 	public function set_custom_edit_mifi_columns($columns) {
    unset( $columns['author'] );
    $columns['start_date'] = esc_html__( 'Start Date', 'trustify' );
    $columns['end_date'] = esc_html__( 'End Date', 'trustify' );
    //$columns['assiged_page'] = esc_html__( 'Assigned Page', 'trustify' );

    return $columns;
	}

 	public function mifi_notification_custom_column( $column, $post_id ){

 		switch ( $column) {
 			case 'start_date':

 				 echo get_post_meta( $post_id, 'mifi-from-date', TRUE );
 				break;
 			case 'end_date':
 				echo get_post_meta( $post_id, 'mifi-to-date', TRUE );
 				break;
 		}

 	}

}
