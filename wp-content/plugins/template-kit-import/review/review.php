<?php

namespace Envato_Template_Kit_Import;

if ( ! defined( 'ABSPATH' ) || ! isset( $template_kit_id ) ) {
	exit; // Exit if accessed directly.
}

$template_kit = envato_template_kit_import_get_builder( $template_kit_id );

if ( ! $template_kit ) {
	wp_die( 'Invalid Template Kit ID' );
}

$manifest         = $template_kit->get_manifest_data();
$required_plugins = $template_kit->get_required_plugins();
$templates        = $template_kit->get_available_templates();

?>
<div>
	<h2>Kit Details:</h2>
	<ul>
		<li>Kit Name: <strong><?php echo esc_html( $manifest['title'] ); ?></strong></li>
		<li>Builder: <strong><?php echo esc_html( $manifest['page_builder'] ); ?></strong></li>
		<li>Author Kit Version: <strong><?php echo esc_html( $manifest['kit_version'] ); ?></strong></li>
		<li>Export Plugin Version: <strong><?php echo esc_html( $manifest['manifest_version'] ); ?></strong></li>
		<li>Templates: <strong><?php echo count( $manifest['templates'] ); ?></strong></li>
		<li>Plugins: <strong><?php echo count( $manifest['required_plugins'] ); ?></strong></li>
		<li>Images: <strong><?php echo count( $manifest['images'] ); ?></strong></li>
	</ul>
</div>
<div>
	<h2>Required Plugins:</h2>
	<ul>
		<?php
		foreach ( $required_plugins as $required_plugin ) {
			?>
			<li>
			<?php echo '<strong>' . esc_html( $required_plugin['name'] . ' - ' . $required_plugin['slug'] ) . '</strong>' . esc_html__( ' - Version ' . $required_plugin['version'] . ' (' . ( ! empty( $required_plugin['author'] ) ? $required_plugin['author'] . ' / ' : '' ) . $required_plugin['file'] . ')' ); ?>
			</li>
		<?php } ?>
	</ul>
</div>
<div>
	<h2>JSON Audit:</h2>
	<?php
	$template_errors = array();

	foreach ( $templates as $template ) {

		$template_kit_folder_name = $template_kit->get_template_kit_temporary_folder();
		$template_json_file       = $template_kit_folder_name . $template['source'];

		$elementor_meta = json_decode( file_get_contents( $template_json_file ), true );
		if ( $elementor_meta ) {
			$iterator     = new \RecursiveIteratorIterator( new \RecursiveArrayIterator( $elementor_meta ) );
			$element_type = 'widget';
			foreach ( $iterator as $key => $val ) {
				if ( 'elType' === $key ) {
					$element_type = $val;
				}
				if ( 'custom_css' === $key && strlen( $val ) > 0 ) {
					// Look for any Custom CSS coming in from Elementor Pro:
					$template_errors[] = 'Please remove Custom CSS from the ' . $element_type . ' in template: ' . $template['name'];
				} elseif ( '_element_id' === $key && strlen( $val ) > 0 ) {
					// Error if the user has set a custom element ID on any element
					$template_errors[] = 'Please remove Custom ID value "' . $val . '" from the ' . $element_type . ' in template: ' . $template['name'];
				} elseif ( '_css_classes' === $key && strlen( $val ) > 0 ) {
					// Error if hte user has set a custom classname on any element
					$template_errors[] = 'Please remove Custom Class value "' . $val . '" from the ' . $element_type . ' in template: ' . $template['name'];
				} elseif ( preg_match_all( '#(https?://[\w\d\-./]+)+#', $val, $matches ) ) {
					// a basic white list of allowed external urls here:
					foreach ( $matches[1] as $match ) {
						if ( ! strpos( $match, 'youtube.com' )
							 && ! strpos( $match, 'wp-content/uploads/' )
							 && ! strpos( $match, 'vimeo.com' )
						) {
							$template_errors[] = 'Please remove external URL "' . $match . '" from the ' . $element_type . ' in template: ' . $template['name'];
						}
					}
				}
				// Hunt for mailto links:
				if ( preg_match_all( '#mailto:\w+#', $val, $matches ) ) {
					foreach ( $matches[0] as $match ) {
						$template_errors[] = 'Please remove the Email link "' . $match . '" from the ' . $element_type . ' in template: ' . $template['name'];
					}
				}
				// Hunt for inline styles:
				if ( preg_match_all( '#style=[\'"]([^\'"]+)[\'"]#imsU', $val, $matches ) ) {
					foreach ( $matches[1] as $match ) {
						$template_errors[] = 'Please remove any inline style="' . esc_html( $match ) . '" from ' . $template['name'];
					}
				}
				// Hunt for inline class names
				if ( preg_match_all( '#class=[\'"]([^\'"]+)[\'"]#imsU', $val, $matches ) ) {
					$allowed_built_in_classes = array(
						'size-',
						'wp-image',
						'align',
					);
					foreach ( $matches[1] as $match ) {
						if ( str_replace( $allowed_built_in_classes, '', $match ) === $match ) {
							$template_errors[] = 'Please remove any inline class="' . esc_html( $match ) . '" from ' . $template['name'];
						}
					}
				}
				// Hunt for onclick event handlers:
				if ( preg_match_all( '#(on\w+)=[\'"]([^\'"]+)[\'"]#imsU', $val, $matches ) ) {
					foreach ( $matches[1] as $onclick ) {
						$template_errors[] = 'No ' . esc_html( $onclick ) . ' allowed in: ' . $template['name'];
					}
				}
				if ( preg_match_all( '#<script[^>]*>(.*)<#imsU', $val, $matches ) ) {
					foreach ( $matches[1] as $match ) {
						$template_errors[] = 'No script tags allowed in: ' . $template['name'];
					}
				}
				if ( preg_match_all( '/<(link|meta|div|span|table)[^>]*>/', $val, $matches ) ) {
					foreach ( $matches[0] as $match ) {
						if ( strlen( $match ) > 1 ) {
							$template_errors[] = 'Please remove any custom HTML tags: ' . esc_html( $match ) . ': ' . $template['name'];
						}
					}
				}
			}
		}
	}

	?>
	<ul>
		<?php
		foreach ( $template_errors as $template_error ) {
			?>
			<li>
			<?php echo '<strong>ERROR:</strong> ' . esc_html( $template_error ); ?>
			</li>
		<?php } ?>
	</ul>
</div>
<div>
	<h2>Large Images:</h2>
	<?php
	$bad_images = array();
	foreach ( $manifest['images'] as $image ) {
		if ( ! empty( $image['dimensions'] ) ) {
			if ( $image['dimensions'][0] > 3000 ) {
				$bad_images[] = 'Image ' . $image['filename'] . ' is ' . $image['dimensions'][0] . 'px wide, it probably doesn\'t need to be this big.';
			}
			if ( $image['dimensions'][1] > 3000 ) {
				$bad_images[] = 'Image ' . $image['filename'] . ' is ' . $image['dimensions'][1] . 'px tall, it probably doesn\'t need to be this big.';
			}
		} else {
			$bad_images[] = 'Image ' . $image['filename'] . ' has no dimensions, author needs to re-export kit in latest Export plugin.';
		}
		if ( ! empty( $image['filesize'] ) ) {
			if ( $image['filesize'] > 900000 ) {
				$bad_images[] = 'Image ' . $image['filename'] . ' is ' . number_format( $image['filesize'] / 1048576, 2 ) . 'MB, it probably doesn\'t need to be this big.';
			}
		} else {
			$bad_images[] = 'Image ' . $image['filename'] . ' has no file size, author needs to re-export kit in latest Export plugin.';
		}
	}
	if ( ! $bad_images ) {
		echo 'None found, yay!';
	} else {
		?>
		<ul>
			<?php foreach ( $bad_images as $bad_image ) { ?>
				<li><?php echo esc_html( $bad_image ); ?></li>
			<?php } ?>
		</ul>
		<?php
	}
	?>
</div>
<div>
	<h2>Templates:</h2>
	<table class="widefat striped">
		<thead>
		<tr>
			<th>Template Name</th>
			<th>Screenshot</th>
			<th>Author Demo URL</th>
			<th>Review</th>
		</tr>
		</thead>
		<tbody>
			<?php
			foreach ( $templates as $template ) {
				?>
				<tr>
					<td>
						<?php echo esc_html( $template['name'] ); ?>
					</td>
					<td>
						<div style="max-height: 200px; overflow: hidden;">
						<a href="<?php echo esc_url( $template['screenshot_url'] ); ?>" target="_blank" rel="nofollow noreferrer">
							<img width="200" src="<?php echo esc_url( $template['screenshot_url'] ); ?>" alt="<?php echo esc_attr( $template['name'] ); ?>" />
						</a>
						</div>
					</td>
					<td>
						<a href="<?php echo esc_url( $template['preview_url'] ); ?>" target="_blank" rel="nofollow noreferrer"><?php echo esc_html( $template['preview_url'] ); ?></a>
					</td>
					<td>
						<ul>
							<li>Pro Required: <strong><?php echo ! empty( $template['elementor_pro_required'] ) ? 'YES' : 'No'; ?></strong></li>
							<li>Elementor Type: <strong><?php echo esc_html( $template['type'] ); ?></strong></li>
							<?php if ( ! empty( $template['metadata'] ) && is_array( $template['metadata'] ) ) { ?>
								<li>Author Type: <strong><?php echo esc_html( $template['metadata']['template_type'] ); ?></strong></li>
								<?php if ( ! empty( $template['metadata']['additional_template_information'] ) ) { ?>
									<?php foreach ( $template['metadata']['additional_template_information'] as $message ) { ?>
									<li>Message: <strong><?php echo esc_html( $message ); ?></strong></li>
									<?php } ?>
								<?php } ?>
								<?php if ( ! empty( $template['metadata']['elementor_pro_conditions'] ) ) { ?>
									<?php foreach ( $template['metadata']['elementor_pro_conditions'] as $message ) { ?>
									<li>Pro Display Condition: <strong><?php echo esc_html( $message ); ?></strong></li>
									<?php } ?>
								<?php } ?>
							<?php } ?>
						</ul>
					</td>
				</tr>
			<?php } ?>
		</tbody>
	</table>
</div>
<div>
	<h2>Images:</h2>
	<table class="widefat striped">
		<thead>
		<tr>
			<th>File Name &amp; Sizes</th>
			<th>Author Preview URL</th>
			<th>Used On Templates</th>
			<th>Image Source</th>
			<th>Person or Place</th>
			<th>Image URLs</th>
		</tr>
		</thead>
		<tbody>
			<?php
			foreach ( $manifest['images'] as $image ) {
				?>
				<tr>
					<td>
						<?php echo esc_html( $image['filename'] ); ?>
						<br/>
						<br/>
						(<?php echo esc_html( $image['dimensions'][0] . 'x' . $image['dimensions'][1] . 'px @ ' . number_format( $image['filesize'] / 1048576, 2 ) . ' MB' ); ?>)
					</td>
					<td>
						<div style="max-height: 200px; max-width: 300px; overflow: hidden; text-align: center">
							<a href="<?php echo esc_url( $image['thumbnail_url'] ); ?>" target="_blank" rel="nofollow noreferrer">
								<?php echo esc_html( $image['thumbnail_url'] ); ?> <br/>
								<img width="200" src="<?php echo esc_url( $image['thumbnail_url'] ); ?>" alt="<?php echo esc_attr( $image['filename'] ); ?>" />
							</a>
						</div>
					</td>
					<td>
						<ul>
						<?php
						if ( ! empty( $image['templates'] ) && is_array( $image['templates'] ) ) {
							foreach ( $image['templates'] as $image_template ) {
								?>
								<li>
									<?php echo esc_html( $image_template['name'] ); ?>
								</li>
								<?php
							}
						}
						?>
						</ul>
					</td>
					<td>
						<?php echo esc_html( $image['image_source'] ); ?>
					</td>
					<td>
						<?php echo esc_html( $image['person_or_place'] ); ?>
					</td>
					<td>
						<?php echo esc_html( $image['image_urls'] ); ?>
					</td>
				</tr>
			<?php } ?>
		</tbody>
	</table>
</div>
<div>
	<h2>Item Page Markup:</h2>
	<?php
	// extract any envato elements images from all our images
	function generate_item_page_markup( $all_images, $market ) {
		$template_kit_import_images = array_filter(
			$all_images,
			function ( $image ) {
				return ! empty( $image['image_source'] ) && ! empty( $image['image_urls'] ) && $image['image_source'] === 'template_kit_import';
			}
		);
		if ( $template_kit_import_images ) {
			$output  = 'This Template Kit uses demo images from Envato Elements. You will need to license these images from Envato Elements to use them on your website, or you can substitute them with your own.';
			$output .= ( $market === 'elements' ) ? "\n" : "<br/><br/>\n";
			// Start a list item of images:
			$output .= ( $market === 'elements' ) ? '' : "<ul>\n";
			foreach ( $template_kit_import_images as $image ) {
				$output .= ( $market === 'elements' ) ? '* ' : '<li>';
				$output .= $image['image_urls'];
				$output .= ( $market === 'elements' ) ? "\n" : "</li>\n";
			}
			// End the list:
			$output .= ( $market === 'elements' ) ? "\n" : "</ul>\n";

			return $output;
		} else {
			return '(no Envato Elements images found, not generating default markup)';
		}
	}
	?>
	<p>
		<strong>ThemeForest item page HTML:</strong>
		<br/>
		<textarea name="themeforest_markup" style="width: 100%" onclick="this.focus();this.select()" readonly="readonly"><?php echo esc_textarea( generate_item_page_markup( $manifest['images'], 'themeforest' ) ); ?></textarea>
	</p>
	<p>
		<strong>Envato Elements item page markdown:</strong>
		<br/>
		<textarea name="elements_markup" style="width: 100%" onclick="this.focus();this.select()" readonly="readonly"><?php echo esc_textarea( generate_item_page_markup( $manifest['images'], 'elements' ) ); ?></textarea>
	</p>
</div>
