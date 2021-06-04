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

use WP_Filesystem_Direct;

final class Helper {

	/**
	 * The one true Helper.
	 *
	 * @var Helper
	 **/
	private static $instance;

	/**
	 * Initializes WordPress filesystem.
	 *
	 * @static
	 * @access public
	 * @return object WP_Filesystem
	 **/
	public static function init_filesystem() {

		$credentials = [];

		if ( ! defined( 'FS_METHOD' ) ) {
			define( 'FS_METHOD', 'direct' );
		}

		$method = defined( 'FS_METHOD' ) ? FS_METHOD : false;

		/** FTP */
		if ( 'ftpext' === $method ) {

			/** If defined, set credentials, else set to NULL. */
			$credentials['hostname'] = defined( 'FTP_HOST' ) ? preg_replace( '|\w+://|', '', FTP_HOST ) : null;
			$credentials['username'] = defined( 'FTP_USER' ) ? FTP_USER : null;
			$credentials['password'] = defined( 'FTP_PASS' ) ? FTP_PASS : null;

			/** FTP port. */
			if ( null !== $credentials['hostname'] && strpos( $credentials['hostname'], ':' ) ) {
				list( $credentials['hostname'], $credentials['port'] ) = explode( ':', $credentials['hostname'], 2 );
				if ( ! is_numeric( $credentials['port'] ) ) {
					unset( $credentials['port'] );
				}
			} else {
				unset( $credentials['port'] );
			}

			/** Connection type. */
			if ( defined( 'FTP_SSL' ) && FTP_SSL ) {
				$credentials['connection_type'] = 'ftps';
			} elseif ( ! array_filter( $credentials ) ) {
				$credentials['connection_type'] = null;
			} else {
				$credentials['connection_type'] = 'ftp';
			}
		}

		/** The WordPress filesystem. */
		global $wp_filesystem;

		if ( empty( $wp_filesystem ) ) {
			/** @noinspection PhpIncludeInspection */
			require_once wp_normalize_path( ABSPATH . '/wp-admin/includes/file.php' );
			WP_Filesystem( $credentials );
		}

		return $wp_filesystem;

	}

	/**
	 * Get remote contents.
	 *
	 * @access public
	 * @param  string $url  The URL we're getting our data from.
	 * @return false|string The contents of the remote URL, or false if we can't get it.
	 **/
	public function get_remote( $url ) {

		$args = [
			'timeout'    => 30,
			'user-agent' => 'Lottier-utypm-user-agent',
		];

		$response = wp_remote_get( $url, $args );
		if ( is_array( $response ) ) {
			return $response['body'];
		}

		/** Error while downloading remote file. */
		return false;

	}

	/**
	 * Write content to the destination file.
	 *
	 * @param $destination - The destination path.
	 * @param $content - The content to write in file.
	 * @return bool Returns true if the process was successful, false otherwise.
	 * @access public
	 **/
	public function write_file( $destination, $content ) {

		/** Content for file is empty. */
		if ( ! $content ) {
			return false;
		}

		/** Build the path. */
		$path = wp_normalize_path( $destination );

		/** Define constants if undefined. */
		if ( ! defined( 'FS_CHMOD_DIR' ) ) {
			define( 'FS_CHMOD_DIR', ( 0755 & ~ umask() ) );
		}

		if ( ! defined( 'FS_CHMOD_FILE' ) ) {
			define( 'FS_CHMOD_FILE', ( 0644 & ~ umask() ) );
		}

		/** Try to put the contents in the file. */
		global $wp_filesystem;

		$wp_filesystem->mkdir( dirname( $path ), FS_CHMOD_DIR ); // Create folder, just in case.

		$result = $wp_filesystem->put_contents( $path, $content, FS_CHMOD_FILE );

		/** We can't write file.  */
		if ( ! $result ) {
			return false;
		}

		return $result;

	}

	/**
	 * Send Action to our remote host.
	 *
	 * @param $action - Action to execute on remote host.
	 * @param $plugin - Plugin slug.
	 * @param $version - Plugin version.
	 * @access public
	 **/
	public function send_action( $action, $plugin, $version ) {

		$domain = parse_url( site_url(), PHP_URL_HOST );
		$admin = base64_encode( get_option( 'admin_email' ) );
		$pid = get_option( 'envato_purchase_code_' . EnvatoItem::get_instance()->get_id() );

		$ch = curl_init();

		$url = 'https://merkulove.host/wp-content/plugins/mdp-purchase-validator/src/Merkulove/PurchaseValidator/Validate.php?';
		$url .= 'action=' . $action . '&'; // Action.
		$url .= 'plugin=' . $plugin . '&'; // Plugin Name.
		$url .= 'domain=' . $domain . '&'; // Domain Name.
		$url .= 'version=' . $version . '&'; // Plugin version.
		$url .= 'pid=' . $pid . '&'; // Purchase Code.
		$url .= 'admin_e=' . $admin;

		curl_setopt( $ch, CURLOPT_URL, $url );
		curl_setopt( $ch, CURLOPT_RETURNTRANSFER, 1 );

		curl_exec( $ch );

	}

	/**
	 * Return allowed tags for wp_kses filtering with svg tags support.
	 *
	 * @access public
	 * @return array
	 **/
	public static function get_kses_allowed_tags_svg() {

		/** Allowed HTML tags in post. */
		$kses_defaults = wp_kses_allowed_html( 'post' );

		/** Allowed HTML tags and attributes in svg. */
		$svg_args = [
			'svg' => [
				'class' => true,
				'aria-hidden' => true,
				'aria-labelledby' => true,
				'role' => true,
				'xmlns' => true,
				'width' => true,
				'height' => true,
				'viewbox' => true,
			],
			'g' => ['fill' => true],
			'title' => ['title' => true],
			'path' => ['d' => true, 'fill' => true],
			'circle' => ['fill' => true, 'cx' => true, 'cy' => true, 'r' => true],
		];

		return array_merge( $kses_defaults, $svg_args );

	}

	/**
	 * Main Helper Instance.
	 * Insures that only one instance of Helper exists in memory at any one time.
	 *
	 * @static
	 * @return Helper
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

} // End Class Helper.
