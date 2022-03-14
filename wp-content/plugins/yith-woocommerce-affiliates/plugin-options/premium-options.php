<?php
/**
 * Premium tab
 *
 * @author  Your Inspiration Themes
 * @package YITH WooCommerce Affiliates
 * @version 1.0.0
 */

if ( ! defined( 'YITH_WCAF' ) ) {
	exit;
} // Exit if accessed directly

return apply_filters(
	'yith_wcaf_premium_settings',
	array(
		'premium' => array(
			'premium_tab' => array(
				'type' => 'custom_tab',
				'action' => 'yith_wcaf_premium_tab',
				'hide_sidebar' => true
			)
		)
	)
);