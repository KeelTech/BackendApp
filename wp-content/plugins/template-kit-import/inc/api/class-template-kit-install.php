<?php
/**
 * Template Kit Import: Template Kits installs
 *
 * API for handling template kit installs
 *
 * @package Envato/Template_Kit_Import
 * @since 2.0.0
 */

namespace Template_Kit_Import\API;

use Template_Kit_Import\Backend\Template_Kits;
use Template_Kit_Import\Utils\Limits;

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly.
}


/**
 * API for handling template kit installs
 *
 * @since 2.0.0
 */
class Template_Kit_Install extends API {

	/**
	 * @param $request \WP_REST_Request
	 */
	public function upload_template_kit_zip_file( $request ) {

		Limits::get_instance()->raise_limits();

		$all_files = $request->get_file_params();
		if ( $all_files && ! empty( $all_files['file'] ) ) {
			if ( is_uploaded_file( $all_files['file']['tmp_name'] ) && ! $all_files['file']['error'] ) {
				// We've got a successful file upload!
				$temp_file_name           = $all_files['file']['tmp_name'];
				$error_or_template_kit_id = Template_Kits::get_instance()->process_zip_file( $temp_file_name );
				unlink( $temp_file_name );

				if ( is_wp_error( $error_or_template_kit_id ) ) {
					return $this->format_error(
						'uploadTemplateKitZipFile',
						'zip_failure',
						$error_or_template_kit_id->get_error_message()
					);
				}

				// If we get here we assume the kit installed correctly.
				return $this->format_success(
					array(
						'templateKitId' => $error_or_template_kit_id,
						'message'       => 'Zip installed successfully',
					)
				);
			}
		}

		return $this->format_error(
			'uploadTemplateKitZipFile',
			'zip_failure',
			'Failed to process ZIP file, please ensure the selected file is the correct Template Kit format.'
		);
	}

	/**
	 * Deletes the template kit.
	 *
	 * @param $request \WP_REST_Request
	 */
	public function delete_template_kit( $request ) {
		$template_kit_id = $request->get_param( 'templateKitId' );
		Template_Kits::get_instance()->delete_template_kit( $template_kit_id );

		return $this->format_success(
			array(
				'message' => 'Kit deleted successfully',
			)
		);
	}

	public function register_api_endpoints() {
		$this->register_endpoint( 'uploadTemplateKitZipFile', array( $this, 'upload_template_kit_zip_file' ) );
		$this->register_endpoint( 'deleteTemplateKit', array( $this, 'delete_template_kit' ) );
	}
}
