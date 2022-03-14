<?php
/**
 * Template Kit Import: Options
 *
 * Making option management a bit easier for us.
 *
 * @package Envato/Template_Kit_Import
 * @since 2.0.0
 */

namespace Template_Kit_Import\API;

use Template_Kit_Import\Utils\Base;

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly.
}


/**
 * API base class
 *
 * @since 2.0.0
 */
abstract class API extends Base {

	public function __construct() {
		$this->register_api_endpoints();
	}

	public function rest_permission_check( $request ) {
		return current_user_can( 'edit_posts' ) && current_user_can( 'upload_files' );
	}

	public function register_endpoint( $endpoint, $callback ) {
		register_rest_route(
			ENVATO_TEMPLATE_KIT_IMPORT_API_NAMESPACE,
			$endpoint,
			array(
				array(
					'methods'             => \WP_REST_Server::CREATABLE,
					'callback'            => $callback,
					'permission_callback' => array( $this, 'rest_permission_check' ),
					'args'                => array(),
				),
			)
		);
	}

	/**
	 * @param array $data
	 *
	 * @return \WP_REST_Response
	 */
	public function format_success( $data ) {
		return new \WP_REST_Response( $data, 200 );
	}

	/**
	 * @param $endpoint
	 * @param $error_code
	 * @param $error_message
	 * @param array         $additional_data
	 *
	 * @return \WP_REST_Response
	 */
	public function format_error( $endpoint, $error_code, $error_message, $additional_data = array() ) {
		return new \WP_REST_Response(
			array(
				'error' => array(
					'context' => $endpoint,
					'code'    => $error_code,
					'message' => $error_message,
					'data'    => $additional_data,
				),
			),
			500
		);
	}
}
