<?php
/**
 * Theme functions and definitions
 *
 * @package HelloElementor
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly.
}

define( 'HELLO_ELEMENTOR_VERSION', '2.3.1' );

if ( ! isset( $content_width ) ) {
	$content_width = 800; // Pixels.
}

if ( ! function_exists( 'hello_elementor_setup' ) ) {
	/**
	 * Set up theme support.
	 *
	 * @return void
	 */
	function hello_elementor_setup() {
		$hook_result = apply_filters_deprecated( 'elementor_hello_theme_load_textdomain', [ true ], '2.0', 'hello_elementor_load_textdomain' );
		if ( apply_filters( 'hello_elementor_load_textdomain', $hook_result ) ) {
			load_theme_textdomain( 'hello-elementor', get_template_directory() . '/languages' );
		}

		$hook_result = apply_filters_deprecated( 'elementor_hello_theme_register_menus', [ true ], '2.0', 'hello_elementor_register_menus' );
		if ( apply_filters( 'hello_elementor_register_menus', $hook_result ) ) {
			register_nav_menus( array( 'menu-1' => __( 'Primary', 'hello-elementor' ) ) );
		}

		$hook_result = apply_filters_deprecated( 'elementor_hello_theme_add_theme_support', [ true ], '2.0', 'hello_elementor_add_theme_support' );
		if ( apply_filters( 'hello_elementor_add_theme_support', $hook_result ) ) {
			add_theme_support( 'post-thumbnails' );
			add_theme_support( 'automatic-feed-links' );
			add_theme_support( 'title-tag' );
			add_theme_support(
				'html5',
				array(
					'search-form',
					'comment-form',
					'comment-list',
					'gallery',
					'caption',
				)
			);
			add_theme_support(
				'custom-logo',
				array(
					'height'      => 100,
					'width'       => 350,
					'flex-height' => true,
					'flex-width'  => true,
				)
			);

			/*
			 * Editor Style.
			 */
			add_editor_style( 'editor-style.css' );
			
			/*
			 * Gutenberg wide images.
			 */
			add_theme_support( 'align-wide' );

			/*
			 * WooCommerce.
			 */
			$hook_result = apply_filters_deprecated( 'elementor_hello_theme_add_woocommerce_support', [ true ], '2.0', 'hello_elementor_add_woocommerce_support' );
			if ( apply_filters( 'hello_elementor_add_woocommerce_support', $hook_result ) ) {
				// WooCommerce in general.
				add_theme_support( 'woocommerce' );
				// Enabling WooCommerce product gallery features (are off by default since WC 3.0.0).
				// zoom.
				add_theme_support( 'wc-product-gallery-zoom' );
				// lightbox.
				add_theme_support( 'wc-product-gallery-lightbox' );
				// swipe.
				add_theme_support( 'wc-product-gallery-slider' );
			}
		}
	}
}
add_action( 'after_setup_theme', 'hello_elementor_setup' );

if ( ! function_exists( 'hello_elementor_scripts_styles' ) ) {
	/**
	 * Theme Scripts & Styles.
	 *
	 * @return void
	 */
	function hello_elementor_scripts_styles() {
		$enqueue_basic_style = apply_filters_deprecated( 'elementor_hello_theme_enqueue_style', [ true ], '2.0', 'hello_elementor_enqueue_style' );
		$min_suffix          = defined( 'SCRIPT_DEBUG' ) && SCRIPT_DEBUG ? '' : '.min';

		if ( apply_filters( 'hello_elementor_enqueue_style', $enqueue_basic_style ) ) {
			wp_enqueue_style(
				'hello-elementor',
				get_template_directory_uri() . '/style' . $min_suffix . '.css',
				[],
				HELLO_ELEMENTOR_VERSION
			);
		}

		if ( apply_filters( 'hello_elementor_enqueue_theme_style', true ) ) {
			wp_enqueue_style(
				'hello-elementor-theme-style',
				get_template_directory_uri() . '/theme' . $min_suffix . '.css',
				[],
				HELLO_ELEMENTOR_VERSION
			);
		}
	}
}
add_action( 'wp_enqueue_scripts', 'hello_elementor_scripts_styles' );

if ( ! function_exists( 'hello_elementor_register_elementor_locations' ) ) {
	/**
	 * Register Elementor Locations.
	 *
	 * @param ElementorPro\Modules\ThemeBuilder\Classes\Locations_Manager $elementor_theme_manager theme manager.
	 *
	 * @return void
	 */
	function hello_elementor_register_elementor_locations( $elementor_theme_manager ) {
		$hook_result = apply_filters_deprecated( 'elementor_hello_theme_register_elementor_locations', [ true ], '2.0', 'hello_elementor_register_elementor_locations' );
		if ( apply_filters( 'hello_elementor_register_elementor_locations', $hook_result ) ) {
			$elementor_theme_manager->register_all_core_location();
		}
	}
}
add_action( 'elementor/theme/register_locations', 'hello_elementor_register_elementor_locations' );

if ( ! function_exists( 'hello_elementor_content_width' ) ) {
	/**
	 * Set default content width.
	 *
	 * @return void
	 */
	function hello_elementor_content_width() {
		$GLOBALS['content_width'] = apply_filters( 'hello_elementor_content_width', 800 );
	}
}
add_action( 'after_setup_theme', 'hello_elementor_content_width', 0 );

if ( is_admin() ) {
	require get_template_directory() . '/includes/admin-functions.php';
}

if ( ! function_exists( 'hello_elementor_check_hide_title' ) ) {
	/**
	 * Check hide title.
	 *
	 * @param bool $val default value.
	 *
	 * @return bool
	 */
	function hello_elementor_check_hide_title( $val ) {
		if ( defined( 'ELEMENTOR_VERSION' ) ) {
			$current_doc = \Elementor\Plugin::instance()->documents->get( get_the_ID() );
			if ( $current_doc && 'yes' === $current_doc->get_settings( 'hide_title' ) ) {
				$val = false;
			}
		}
		return $val;
	}
}
add_filter( 'hello_elementor_page_title', 'hello_elementor_check_hide_title' );

/**
 * Wrapper function to deal with backwards compatibility.
 */
if ( ! function_exists( 'hello_elementor_body_open' ) ) {
	function hello_elementor_body_open() {
		if ( function_exists( 'wp_body_open' ) ) {
			wp_body_open();
		} else {
			do_action( 'wp_body_open' );
		}
	}
}
function wpb_hook_javascript() {
  if (is_page ('63')) { 
    ?>
        <script type="text/javascript" src="https://www.getkeel.com/wp-content/themes/hello-elementor/crs.js">
          // your javscript code goes here
        </script>
    <?php
  }
}


add_action('wp_footer', 'wpb_hook_javascript');
wp_enqueue_script('jquery');


// A send custom WebHook
add_action( 'elementor_pro/forms/new_record', function( $record, $handler ) {
    //make sure its our form
    $form_name = $record->get_form_settings( 'form_name' );

    // Replace MY_FORM_NAME with the name you gave your form
    if ( 'test_form' !== $form_name ) {
        return;
    }

    $raw_fields = $record->get( 'fields' );
    $fields = [];
    foreach ( $raw_fields as $id => $field ) {
        $fields[ $id ] = $field['value'];
		
    }
		
$myEmail = $fields["email"];
$myName = $fields["name"];
$myNumber = $fields["contact_number"];
$myFormData = '[{"Attribute":"EmailAddress","Value":"'.$myEmail.'"},{"Attribute":"FirstName","Value":"'.$myName.'"},{"Attribute":"Phone","Value":"'.$myNumber.'"},]';


$data_string = '[{"Attribute":"EmailAddress","Value":"test3@getkeel.com"},{"Attribute":"FirstName","Value":"Robert"},{"Attribute":"LastName","Value":"Smith"},{"Attribute":"Phone","Value":"9876243210"},]';

$curl = curl_init('https://api-in21.leadsquared.com/v2/LeadManagement.svc/Lead.Create?accessKey=u$r9538ca002d0f679810a27e8f254a2f62&secretKey=e342f6d83be820cc15fb10378cc31e6c33e66843');
curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "POST");
curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($curl, CURLOPT_HEADER, 0);
curl_setopt($curl, CURLOPT_POSTFIELDS, $myFormData);
curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curl, CURLOPT_HTTPHEADER, array(
        "Content-Type:application/json",
        "Content-Length:".strlen($myFormData)));
 curl_exec($curl);
	
// $response = curl_exec($curl);
// print_r(json_decode($response));


}, 10, 2 );



// A send custom WebHook for Homepage form
add_action( 'elementor_pro/forms/new_record', function( $record, $handler ) {
    //make sure its our form
    $form_name = $record->get_form_settings( 'form_name' );

    // Replace MY_FORM_NAME with the name you gave your form
    if ( 'homepage_form' !== $form_name ) {
        return;
    }

    $raw_fields = $record->get( 'fields' );
    $fields = [];
    foreach ( $raw_fields as $id => $field ) {
        $fields[ $id ] = $field['value'];
		
    }
		
$myEmail = $fields["email"];
$myNumber = $fields["contact_number"];
$myFormData = '[{"Attribute":"EmailAddress","Value":"'.$myEmail.'"},{"Attribute":"Phone","Value":"'.$myNumber.'"},]';

$curl = curl_init('https://api-in21.leadsquared.com/v2/LeadManagement.svc/Lead.Create?accessKey=u$r9538ca002d0f679810a27e8f254a2f62&secretKey=e342f6d83be820cc15fb10378cc31e6c33e66843');
curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "POST");
curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($curl, CURLOPT_HEADER, 0);
curl_setopt($curl, CURLOPT_POSTFIELDS, $myFormData);
curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curl, CURLOPT_HTTPHEADER, array(
        "Content-Type:application/json",
        "Content-Length:".strlen($myFormData)));
 curl_exec($curl);
	
// $response = curl_exec($curl);
// print_r(json_decode($response));


}, 10, 2 );



// A send custom WebHook for Contact form
add_action( 'elementor_pro/forms/new_record', function( $record, $handler ) {
    //make sure its our form
    $form_name = $record->get_form_settings( 'form_name' );

    // Replace MY_FORM_NAME with the name you gave your form
    if ( 'contact_form' !== $form_name ) {
        return;
    }

    $raw_fields = $record->get( 'fields' );
    $fields = [];
    foreach ( $raw_fields as $id => $field ) {
        $fields[ $id ] = $field['value'];
		
    }

$myName = $fields["myName"];		
$myEmail = $fields["myEmail"];
$myNumber = $fields["my_contact_number"];
$myMessage = $fields["myMessage"];
$myFormData = '[{"Attribute":"FirstName","Value":"'.$myName.'"},{"Attribute":"EmailAddress","Value":"'.$myEmail.'"},{"Attribute":"Phone","Value":"'.$myNumber.'"},{"Attribute":"Notes","Value":"'.$myMessage.'"},]';

$curl = curl_init('https://api-in21.leadsquared.com/v2/LeadManagement.svc/Lead.Create?accessKey=u$r9538ca002d0f679810a27e8f254a2f62&secretKey=e342f6d83be820cc15fb10378cc31e6c33e66843');
curl_setopt($curl, CURLOPT_CUSTOMREQUEST, "POST");
curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($curl, CURLOPT_HEADER, 0);
curl_setopt($curl, CURLOPT_POSTFIELDS, $myFormData);
curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);
curl_setopt($curl, CURLOPT_HTTPHEADER, array(
        "Content-Type:application/json",
        "Content-Length:".strlen($myFormData)));
 curl_exec($curl);
	
// $response = curl_exec($curl);
// print_r(json_decode($response));


}, 10, 2 );


// Redirect Directly to Checkout

add_filter('add_to_cart_redirect', 'lw_add_to_cart_redirect');
function lw_add_to_cart_redirect() {
 global $woocommerce;
 $lw_redirect_checkout = $woocommerce->cart->get_checkout_url();
 return $lw_redirect_checkout;
} 

// Clear cart and Add product and redirect to checkout
add_filter( 'woocommerce_add_to_cart_validation', 'one_cart_item_at_the_time', 10, 3 );
function one_cart_item_at_the_time( $passed, $product_id, $quantity ) {
    if( ! WC()->cart->is_empty())
        WC()->cart->empty_cart();
    return $passed;
}

// Hide Product has been added to your cart notification from cart page
add_filter( 'wc_add_to_cart_message_html', '__return_false' );


// Redirect user after checkout to Our SSO
add_action( 'woocommerce_thankyou', 'redirect_after_checkout');
 
function redirect_after_checkout( $order_id ){
 
    $order = wc_get_order( $order_id );
	$data  = $order->get_data();
 	$email = $data['billing']['email'];
    $url = 'https://staging.getkeel.com/sso?'.$email;
 
    if ( ! $order->has_status( 'failed' ) ) {
        wp_redirect( $url );
//   echo "<script> window.open(".$url.", '_blank') </script>";
        exit;
    }
 
}
