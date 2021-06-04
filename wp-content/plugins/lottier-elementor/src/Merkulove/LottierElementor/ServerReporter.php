<?php
/**
 * Lottier for Elementor
 * Lottie animations in just a few clicks without writing a single line of code.
 * Exclusively on https://1.envato.market/lottier-elementor
 *
 * @encoding        UTF-8
 * @version         1.0.3
 * @copyright       (C) 2018 - 2020 Merkulove ( https://merkulov.design/ ). All rights reserved.
 * @license         Envato License https://1.envato.market/KYbje
 * @contributors    Vitaliy Nemirovskiy (nemirovskiyvitaliy@gmail.com), Dmitry Merkulov (dmitry@merkulov.design)
 * @support         help@merkulov.design
 * @license         Envato License https://1.envato.market/KYbje
 **/


namespace Merkulove\LottierElementor;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
	header( 'Status: 403 Forbidden' );
	header( 'HTTP/1.1 403 Forbidden' );
	exit;
}

/**
 * SINGLETON: Used to implement System report handler class
 * responsible for generating a report for the server environment.
 **/
final class ServerReporter {

	/**
	 * The one true ServerReporter.
	 *
	 * @var ServerReporter
	 **/
	private static $instance;

	/**
	 * Sets up a new ServerReporter instance.
	 *
	 * @access public
	 **/
	private function __construct() {}

	/**
	 * Get server environment reporter title.
	 *
	 * @access public
	 * @return string Report title.
	 **/
	public function get_title() {
		return 'Server Environment';
	}

	/**
	 * Retrieve the required fields for the server environment report.
	 *
	 * @access public	 *
	 * @return array Required report fields with field ID and field label.
	 **/
	public function get_fields() {

		return [
			'os'                    => esc_html__( 'Operating System', 'lottier-elementor' ),
			'software'              => esc_html__( 'Software','lottier-elementor' ),
			'mysql_version'         => esc_html__( 'MySQL version','lottier-elementor' ),
			'php_version'           => esc_html__( 'PHP Version','lottier-elementor' ),
			'write_permissions'     => esc_html__( 'Write Permissions','lottier-elementor' ),
			'zip_installed'         => esc_html__( 'ZIP Installed','lottier-elementor' ),
			'curl_installed'        => esc_html__( 'cURL Installed','lottier-elementor' ),
			'elementor_installed'   => esc_html__( 'Elementor Installed','lottier-elementor' ),
			/** 'allow_url_fopen'        => esc_html__( 'allow_url_fopen','lottier-elementor' ), */
			/** 'dom_installed'         => esc_html__( 'DOM Installed','lottier-elementor' ), */
			/** 'xml_installed'         => esc_html__( 'XML Installed','lottier-elementor' ), */
			/** 'bcmath_installed'      => esc_html__( 'BCMath Installed','lottier-elementor' ), */
		];

	}

	/**
	 * Get allow_url_fopen enabled.
	 *
	 * @access public
	 * @return array {
	 *    Report data.
	 *
	 *    @type string $value   YES if the allow_url_fopen is enabled, NO otherwise.
	 *    @type bool   $warning Whether to display a warning. True if the allow_url_fopen is enabled, False otherwise.
	 * }
	 * @noinspection PhpUnused
	 **/
	public function get_allow_url_fopen() {

		$allow_url_fopen = ini_get( 'allow_url_fopen' );

		return [
			'value' => $allow_url_fopen ? '<i class="material-icons mdc-system-yes">check_circle</i>' . esc_html__( 'YES', 'lottier-elementor' ) : '<i class="material-icons mdc-system-no">error</i>' . esc_html__( 'NO', 'lottier-elementor' ),
			'warning' => ! $allow_url_fopen,
			'recommendation' => esc_html__( 'You must enable allow_url_fopen option in PHP. Contact the support service of your hosting provider. They know what to do.', 'lottier-elementor' )
		];

	}

	/**
	 * Get server operating system.
	 * Retrieve the server operating system.
	 *
	 * @access public
	 *
	 * @return array {
	 *    Report data.
	 *
	 *    @type string $value Server operating system.
	 * }
	 * @noinspection PhpUnused
	 **/
	public function get_os() {
		return [
			'value' => PHP_OS,
		];
	}

	/**
	 * Get server software.
	 * Retrieve the server software.
	 *
	 * @access public
	 *
	 * @return array {
	 *    Report data.
	 *
	 *    @type string $value Server software.
	 * }
	 *
	 * @noinspection PhpUnused
	 **/
	public function get_software() {
		return [
			'value' => $_SERVER['SERVER_SOFTWARE'],
		];
	}

	/**
	 * Get PHP version.
	 * Retrieve the PHP version.
	 *
	 * @access public
	 *
	 * @return array {
	 *    Report data.
	 *
	 *    @type string $value          PHP version.
	 *    @type string $recommendation Minimum PHP version recommendation.
	 *    @type bool   $warning        Whether to display a warning.
	 * }
	 *
	 * @noinspection PhpUnused
	 **/
	public function get_php_version() {
		$result = [
			'value' => PHP_VERSION,
		];

		if ( version_compare( $result['value'], '5.6', '<' ) ) {
			$result['recommendation'] = esc_html__( 'We recommend to use php 5.6 or higher', 'lottier-elementor' );

			$result['warning'] = true;
		}

		return $result;
	}

	/**
	 * Get ZIP installed.
	 * Whether the ZIP extension is installed.
	 *
	 * @access public
	 *
	 * @return array {
	 *    Report data.
	 *
	 *    @type string $value   Yes if the ZIP extension is installed, NO otherwise.
	 *    @type bool   $warning Whether to display a warning. True if the ZIP extension is installed, False otherwise.
	 * }
	 *
	 * @noinspection PhpUnused
	 **/
	public function get_zip_installed() {
		$zip_installed = extension_loaded( 'zip' );

		return [
			'value' => $zip_installed ? '<i class="material-icons mdc-system-yes">check_circle</i>' . esc_html__( 'YES', 'lottier-elementor') : '<i class="material-icons mdc-system-no">error</i>' . esc_html__( 'NO', 'lottier-elementor' ),
			'warning' => ! $zip_installed,
		];
	}

	/**
	 * Get cURL installed.
	 * Whether the cURL extension is installed.
	 *
	 * @access public
	 *
	 * @return array {
	 *    Report data.
	 *
	 *    @type string $value   YES if the cURL extension is installed, NO otherwise.
	 *    @type bool   $warning Whether to display a warning. True if the cURL extension is installed, False otherwise.
	 * }
	 **/
	public function get_curl_installed() {

		$curl_installed = extension_loaded( 'curl' );

		return [
			'value' => $curl_installed ? '<i class="material-icons mdc-system-yes">check_circle</i>' . esc_html__( 'YES', 'lottier-elementor' ) : '<i class="material-icons mdc-system-no">error</i>' . esc_html__( 'NO', 'lottier-elementor' ),
			'warning' => ! $curl_installed,
			'recommendation' => esc_html__( 'You must enable CURL (Client URL Library) in PHP. Contact the support service of your hosting provider. They know what to do.', 'lottier-elementor' )
		];

	}

	/**
	 * Get Elementor installed.
	 * Whether the Elementor builder is installed.
	 *
	 * @access public
	 * @return array Report data.
	 *          @type string $value   YES if the Elementor builder is installed, NO otherwise.
	 *          @type bool   $warning Whether to display a warning.
	 *
	 * @noinspection PhpUnused
	 **/
	public function get_elementor_installed() {

		/** Check if Elementor installed and activated. */
		$elementor_installed = did_action( 'elementor/loaded' );

		return [
			'value' => $elementor_installed ? '<i class="material-icons mdc-system-yes">check_circle</i>' . esc_html__( 'YES', 'lottier-elementor') : '<i class="material-icons mdc-system-no">error</i>' . esc_html__( 'NO', 'lottier-elementor' ),
			'warning' => ! $elementor_installed,
			'recommendation' => esc_html__( 'You need install and activate Elementor builder. Go to Elementor site (elementor.com) for details.', 'lottier-elementor' )
		];

	}

	/**
	 * Get DOM installed.
	 * Whether the DOM extension is installed.
	 *
	 * @access public
	 * @return array {
	 *    Report data.
	 *
	 *    @type string $value   YES if the DOM extension is installed, NO otherwise.
	 *    @type bool   $warning Whether to display a warning. True if the DOM extension is installed, False otherwise.
	 * }
	 **/
	public function get_dom_installed() {

		$dom_installed = extension_loaded( 'dom' );

		return [
			'value' => $dom_installed ? '<i class="material-icons mdc-system-yes">check_circle</i>' . esc_html__( 'YES', 'lottier-elementor') : '<i class="material-icons mdc-system-no">error</i>' . esc_html__( 'NO', 'lottier-elementor' ),
			'warning' => ! $dom_installed,
			'recommendation' => esc_html__(' You must enable DOM extension (Document Object Model) in PHP. It\'s used for HTML processing. Contact the support service of your hosting provider. They know what to do.', 'lottier-elementor' )
		];

	}

	/**
	 * Get XML installed.
	 * Whether the XML extension is installed.
	 *
	 * @access public
	 * @return array {
	 *    Report data.
	 *
	 *    @type string $value   YES if the XML extension is installed, NO otherwise.
	 *    @type bool   $warning Whether to display a warning. True if the XML extension is installed, False otherwise.
	 * }
	 **/
	public function get_xml_installed() {

		$xml_installed = extension_loaded( 'xml' );

		return [
			'value' => $xml_installed ? '<i class="material-icons mdc-system-yes">check_circle</i>' . esc_html__( 'YES', 'lottier-elementor' ) : '<i class="material-icons mdc-system-no">error</i>' . esc_html__( 'NO', 'lottier-elementor' ),
			'warning' => ! $xml_installed,
			'recommendation' => esc_html__( 'You must enable XML extension in PHP. It\'s used for XML processing. Contact the support service of your hosting provider. They know what to do.', 'lottier-elementor' )
		];

	}

	/**
	 * Get BCMath installed.
	 * Whether the BCMath extension is installed.
	 *
	 * @access public
	 * @return array {
	 *    Report data.
	 *
	 *    @type string $value   YES if the BCMath extension is installed, NO otherwise.
	 *    @type bool   $warning Whether to display a warning. True if the BCMath extension is installed, False otherwise.
	 * }	 *
	 * @noinspection PhpUnused
	 **/
	public function get_bcmath_installed() {

		$bcmath_installed = extension_loaded( 'bcmath' );

		return [
			'value' => $bcmath_installed ? '<i class="material-icons mdc-system-yes">check_circle</i>' . esc_html__( 'YES', 'lottier-elementor' ) : '<i class="material-icons mdc-system-no">error</i>' . esc_html__( 'NO', 'lottier-elementor' ),
			'warning' => ! $bcmath_installed,
			'recommendation' => esc_html__( 'You must enable BCMath extension (Arbitrary Precision Mathematics) in PHP. Contact the support service of your hosting provider. They know what to do.', 'lottier-elementor' )
		];

	}

	/**
	 * Get MySQL version.
	 * Retrieve the MySQL version.
	 *
	 * @access public
	 * @return array {
	 *    Report data.
	 *
	 *    @type string $value MySQL version.
	 * }
	 * @noinspection PhpUnused
	 **/
	public function get_mysql_version() {

		global $wpdb;

		$db_server_version = $wpdb->get_results( "SHOW VARIABLES WHERE `Variable_name` IN ( 'version_comment', 'innodb_version' )", OBJECT_K );

		return [
			'value' => $db_server_version['version_comment']->Value . ' v' . $db_server_version['innodb_version']->Value,
		];

	}

	/**
	 * Get write permissions.
	 * Check whether the required folders has writing permissions.
	 *
	 * @access public
	 * @return array {
	 *    Report data.
	 *
	 *    @type string $value   Writing permissions status.
	 *    @type bool   $warning Whether to display a warning. True if some required
	 *                          folders don't have writing permissions, False otherwise.
	 * }
	 * @noinspection PhpUnused
	 **/
	public function get_write_permissions() {

		$paths_to_check = [
			ABSPATH => esc_html__( 'WordPress root directory', 'lottier-elementor' )
		];

		$write_problems = [];

		$wp_upload_dir = wp_upload_dir();

		if ( $wp_upload_dir[ 'error' ] ) {
			$write_problems[] = esc_html__( 'WordPress root uploads directory', 'lottier-elementor' );
		}

		$htaccess_file = ABSPATH . '/.htaccess';

		if ( file_exists( $htaccess_file ) ) {
			$paths_to_check[ $htaccess_file ] = esc_html__( '.htaccess file', 'lottier-elementor' );
		}

		foreach ( $paths_to_check as $dir => $description ) {

			if ( ! is_writable( $dir ) ) {
				$write_problems[] = $description;
			}
		}

		if ( $write_problems ) {

			$value = '<i class="material-icons mdc-system-no">error</i>' . esc_html__( 'There are some writing permissions issues with the following directories/files:', 'lottier-elementor' ) . "<br> &nbsp;&nbsp;&nbsp;&nbsp;– ";
			$value .= implode( "<br> &nbsp;&nbsp;&nbsp;&nbsp;– ", $write_problems );

		} else {

			$value = '<i class="material-icons mdc-system-yes">check_circle</i>' . esc_html__( 'All right', 'lottier-elementor' );

		}

		return [
			'value' => $value,
			'warning' => (bool) $write_problems,
		];

	}

	/**
	 * Get report.
	 * Retrieve the report with all it's containing fields.
	 *
	 * @access public
	 * @return array {
	 *    Report fields.
	 *
	 *    @type string $name Field name.
	 *    @type string $label Field label.
	 * }
	 * @noinspection PhpUnused
	 **/
	public function get_report() {

		$result = [];

		foreach ( $this->get_fields() as $field_name => $field_label ) {

			$method = 'get_' . $field_name;

			$reporter_field = [
				"name" => $field_name,
				'label' => $field_label,
			];

			/** @noinspection SlowArrayOperationsInLoopInspection */
			$reporter_field        = array_merge( $reporter_field, $this->$method() );
			$result[ $field_name ] = $reporter_field;

		}

		return $result;

	}

	/**
	 * Main ServerReporter Instance.
	 *
	 * Insures that only one instance of ServerReporter exists in memory at any one time.
	 *
	 * @static
	 * @return ServerReporter
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

} // End Class ServerReporter.
