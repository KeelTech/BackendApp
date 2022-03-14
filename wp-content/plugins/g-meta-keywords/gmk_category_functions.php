<?php
	add_action('category_add_form_fields', 'category_metabox_add', 10, 1);
	add_action('category_edit_form_fields', 'category_metabox_edit', 10, 1);

	function category_metabox_add($tag) {
		$categoryMetaKeywords = get_term_meta($tag->term_id, 'gmk_field', true);
		?>
		<style type="text/css">
			#gmk_box_id { margin: 15px 0 0 0; }
			input#gmk_field { width: 100%; padding: 10px 15px; }
			h2.hndle { font-size: 14px; padding: 8px 12px; margin: 0; line-height: 1.4; }
			.inside { padding-bottom: 0 !important; }
		</style>
		<div id="gmk_box_id" class="postbox ">
			<h2 class="hndle ui-sortable-handle"><span>G Meta Keywords</span></h2>

			<div class="inside">
				<p><?php _e('Please add comma separated meta keywords to show for this content.', 'g-meta-keywords'); ?></p>
				<input name="gmk_field" id="gmk_field" type="text" value="<?= $categoryMetaKeywords ?>">
			</div>
		</div>
		<?php
	}

	function category_metabox_edit($tag) {
		$categoryMetaKeywords = get_term_meta($tag->term_id, 'gmk_field', true);
		?>
		<style type="text/css">
			#gmk_box_id { margin: 15px 0 0 0; }
			input#gmk_field { width: 100%; padding: 10px 15px; }
			h2.hndle { font-size: 14px; padding: 8px 12px; margin: 0; line-height: 1.4; }
			.inside { padding-bottom: 0 !important; }
		</style>
		<div id="gmk_box_id" class="postbox ">
			<h2 class="hndle ui-sortable-handle"><span>G Meta Keywords</span></h2>

			<div class="inside">
				<p><?php _e('Please add comma separated meta keywords to show for this content.', 'g-meta-keywords'); ?></p>
				<input name="gmk_field" id="gmk_field" type="text" value="<?= $categoryMetaKeywords ?>">
			</div>
		</div>
		<?php
	}

	add_action('created_category', 'save_category_metadata', 10, 1);
	add_action('edited_category', 'save_category_metadata', 10, 1);

	function save_category_metadata($term_id) {
		if (array_key_exists('gmk_field', $_POST)) {
			update_term_meta($term_id, 'gmk_field', sanitize_text_field($_POST['gmk_field']));
		}
	}

?>