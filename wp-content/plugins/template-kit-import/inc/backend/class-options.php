<?php
/**
 * Template Kit Import: Options
 *
 * Making option management a bit easier for us.
 *
 * @package Envato/Template_Kit_Import
 * @since 2.0.0
 */

namespace Template_Kit_Import\Backend;

use Template_Kit_Import\Utils\Base;

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly.
}


/**
 * Option saving / getting
 *
 * @since 2.0.0
 */
class Options extends Base {

	const OPTION_KEY = 'template_kit_import_options';

	public function __construct() {
		add_action( 'admin_head', array( $this, 'print_admin_env_vars' ) );
		add_action( 'elementor/editor/before_enqueue_scripts', array( $this, 'print_admin_env_vars' ) );
		add_action( 'elementor/preview/enqueue_styles', array( $this, 'print_admin_env_vars' ) );
	}

	/**
	 * Prints some variables we can access from within React
	 */
	public function print_admin_env_vars() {
		$admin_options = array(
			'api_nonce'   => wp_create_nonce( 'wp_rest' ),
			// 'api_url'   => admin_url( 'admin-ajax.php?action=template_kit_import&endpoint=' ),
			'api_url'     => get_rest_url() . 'template-kit-import/v2/',
			'review_mode' => defined( 'ENVATO_TEMPLATE_KIT_IMPORT_DEV' ) && ENVATO_TEMPLATE_KIT_IMPORT_DEV,
		);
		?>
		<script>
	  var template_kit_import = <?php echo json_encode( $admin_options ); ?>;
		</script>
		<?php
	}

	/**
	 * @param bool $key
	 * @param bool $default
	 *
	 * @return array|bool|mixed|string|void
	 */
	public function get( $key = false, $default = false ) {

		$options = get_option( self::OPTION_KEY, array() );
		if ( ! $options || ! is_array( $options ) ) {
			$options = array();
		}
		$user_id = get_current_user_id();
		if ( $user_id ) {
			$user_options = isset( $options[ $user_id ] ) ? $options[ $user_id ] : array();
			if ( $key !== false ) {
				return isset( $user_options[ $key ] ) ? $user_options[ $key ] : $default;
			}

			return $user_options;
		} else {
			return $default;
		}
	}

	public function set( $key, $value ) {
		$options = get_option( self::OPTION_KEY, array() );
		if ( ! is_array( $options ) ) {
			$options = array();
		}
		$user_id = get_current_user_id();
		if ( $user_id ) {
			if ( ! isset( $options[ $user_id ] ) ) {
				$options[ $user_id ] = array();
			}
			$options[ $user_id ][ $key ] = $value;
			update_option( self::OPTION_KEY, $options );
		}
	}

	public function reset_user() {
		$options = get_option( self::OPTION_KEY, array() );
		$user_id = get_current_user_id();
		if ( $user_id ) {
			$options[ $user_id ] = array();
			update_option( self::OPTION_KEY, $options );
		}
	}

}
