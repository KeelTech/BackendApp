<?php
	/*
		Plugin Name: G Meta Keywords
		Plugin URI: https://demo.grana.com.tr/web/wordpress/plugin/g-meta-keywords/
		Description: G Meta Keywords (GMK) is a simple but useful WordPress add-on that allows you to easily add the keyword insertion field removed from many Search Engine Optimization (SEO) enhancements for WordPress to all your content again.
		Version: 1.4
		Author: Sinan Yorulmaz
		Author URI: https://sinanyorulmaz.com
		License: GNU
	*/

	require 'gmk_functions.php';
	require 'gmk_options.php';

	function gmk_head() {
		$postMetaKeywords = get_post_meta(get_the_ID(), '_gmk', true);
		$categoryMetaKeywords = get_term_meta(get_query_var('cat'), 'gmk_field', true);


		if (!empty($postMetaKeywords) && !is_category()) {
			?>
			<meta name="keywords" content="<?= $postMetaKeywords ?>">
			<?php
		}

		if (!empty($categoryMetaKeywords) && is_category()) {
			?>
			<meta name="keywords" content="<?= $categoryMetaKeywords ?>">
			<?php
		}
	}

	add_action('wp_head', 'gmk_head');
?>