<?php
	function gmk_html($post) {
		$postMetaKeywords = get_post_meta($post->ID, '_gmk', true);
		?>
		<style type="text/css">
			input#gmk_field {
				width: 100%;
				padding: 10px 15px;
			}
		</style>
		<p><?php _e('Please add comma separated meta keywords to show for this content.', 'g-meta-keywords'); ?></p>
		<input name="gmk_field" id="gmk_field" type="text" value="<?= $postMetaKeywords ?>">
		<?php
	}

	add_action('add_meta_boxes', 'gmk_add_custom_box');

	function gmk_add_custom_box() {
		$post_type = trim(get_option('post_type'));
		$post_type = explode("\n", $post_type);
		$post_type = array_filter($post_type, 'trim');

		$screens = ['post', 'page', 'category', 'tag', 'taxonomy', 'attachment', 'term', 'taxonomies'];

		foreach ($post_type as $line) {
			array_push($screens, $line);
		}

		foreach ($screens as $screen) {
			add_meta_box('gmk_box_id', 'G Meta Keywords', 'gmk_html', $screen);
		}

	}

	add_action('save_post', 'gmk_save_postdata');

	function gmk_save_postdata($post_id) {
		if (array_key_exists('gmk_field', $_POST)) {
			update_post_meta($post_id, '_gmk', sanitize_text_field($_POST['gmk_field']));
		}
	}

	require 'gmk_category_functions.php';
?>