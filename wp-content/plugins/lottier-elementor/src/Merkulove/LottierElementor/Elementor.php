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

use Elementor\Plugin;
use Merkulove\LottierElementor;
use RecursiveDirectoryIterator;
use RecursiveIteratorIterator;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
	header( 'Status: 403 Forbidden' );
	header( 'HTTP/1.1 403 Forbidden' );
	exit;
}

/**
 * Class to implement Elementor Widget.
 **/
final class Elementor {

	/**
	 * The one true Elementor.
	 *
	 * @var Elementor
	 **/
	private static $instance;

	/**
	 * Sets up a new Elementor instance.
	 *
	 * @access public
	 **/
	public function __construct() {

		/** Check for basic requirements. */
		$this->initialization();

		/** Elementor widget Editor CSS. */
		add_action( 'elementor/editor/before_enqueue_styles', [$this, 'editor_styles'] );

	}

	/**
	 * Add our css to admin editor.
	 *
	 * @access public
	 **/
	public function editor_styles() {

		wp_enqueue_style( 'mdp-lottier-elementor-admin', LottierElementor::$url . 'css/elementor-admin' . LottierElementor::$suffix . '.css', [], LottierElementor::$version );

	}

	/**
	 * The init process check for basic requirements and then then run the plugin logic.
	 *
	 * @access public
	 **/
	public function initialization() {

		/** Check if Elementor installed and activated. */
		if ( ! did_action( 'elementor/loaded' ) ) { return; }

		/** Register custom widgets. */
		add_action( 'elementor/widgets/widgets_registered', [$this, 'register_widgets'] );

	}

	/**
	 * Register new Elementor widgets.
	 *
	 * @access public
	 **/
	public function register_widgets() {

		/** Load and register Elementor widgets. */
		$path = LottierElementor::$path . 'src/Merkulove/LottierElementor/Elementor/widgets/';

		/**  Will store a list of chart file names. */
		$nameChart = array();

		foreach ( new RecursiveIteratorIterator( new RecursiveDirectoryIterator( $path ) ) as $filename ) {

			if ( substr( $filename, -4 ) === '.php' ) {

				/** @noinspection PhpIncludeInspection */
				require_once $filename;

				/** Prepare class name from file. */
				$widget_class = $filename->getBasename( '.php' );
				$widget_class = str_replace( '.', '_', $widget_class );

				/** We write all the file names to the array. */
				$nameChart[] = $widget_class;

			}

		}

		/** We sort the array with the names of the widgets. */
		sort( $nameChart );

		/** Register chart widget . */
		foreach ( $nameChart as $chart ) {

			$chart = '\\' .substr( $chart, 3 );
			Plugin::instance()->widgets_manager->register_widget_type( new $chart() );

		}

	}

	/**
	 * Main Elementor Instance.
	 *
	 * Insures that only one instance of Elementor exists in memory at any one time.
	 *
	 * @static
	 * @return Elementor
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

}