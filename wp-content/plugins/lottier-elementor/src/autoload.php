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


/** Register plugin custom autoloader. */
spl_autoload_register( static function ( $class ) {

	$namespace = 'Merkulove\\';

	/** Bail if the class is not in our namespace. */
	if ( 0 !== strpos( $class, $namespace ) ) {
		return;
	}

	/** Build the filename. */
	$file = realpath( __DIR__ );
	$file .= DIRECTORY_SEPARATOR . str_replace( '\\', DIRECTORY_SEPARATOR, $class ) . '.php';

	/** If the file exists for the class name, load it. */
	if ( file_exists( $file ) ) {

		/** @noinspection PhpIncludeInspection */
		include( $file );

	}

} );
