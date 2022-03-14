<?php
/**
 * Template Kit Import:
 *
 * Elements Welcome Page UI.
 *
 * @package Envato/Template_Kit_Import
 * @since 2.0.0
 */

namespace Template_Kit_Import\Backend;

use Template_Kit_Import\Utils\Base;

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Exit if accessed directly.
}


/**
 * Envato Elements Welcome Page UI.
 *
 * @since 2.0.0
 */
class Welcome extends Base {

	/**
	 * Registers our main "Elements" menu in the sidebar
	 */
	public function admin_menu() {

		$page = add_management_page(
			__( 'Template Kit Import', 'template-kit-import' ),
			'Template Kit',
			'edit_posts',
			ENVATO_TEMPLATE_KIT_IMPORT_SLUG,
			array( $this, 'admin_page_open' )
		);
		add_action( 'admin_print_scripts-' . $page, array( $this, 'admin_page_assets' ) );

		if ( defined( 'ENVATO_TEMPLATE_KIT_IMPORT_DEV' ) && ENVATO_TEMPLATE_KIT_IMPORT_DEV && isset( $_GET['template_kit_id'] ) ) {
			$page = add_menu_page(
				__( 'TK Review', 'template-kit-import' ),
				__( 'TK Review', 'template-kit-import' ),
				'edit_posts',
				'template-kit-review',
				array( $this, 'admin_page_review' ),
				'',
				30
			);
		}

	}

	/**
	 * Called when the plugin page is opened.
	 */
	public function admin_page_open() {
		?>
		<div id="template-kit-import-app-holder"></div>
		<script type="text/javascript">
			jQuery(function(){
		var appHolder = document.getElementById( 'template-kit-import-app-holder' );
		if (appHolder && 'undefined' !== typeof window.templateKitImport) {
					window.templateKitImport.initBackend( appHolder );
		}
	  })
		</script>
		<?php
	}

	/**
	 * Called when the review page is opened.
	 */
	public function admin_page_review() {

		$template_kit_id = isset( $_GET['template_kit_id'] ) ? (int) $_GET['template_kit_id'] : null;
		if ( $template_kit_id > 0 ) {
			require_once ENVATO_TEMPLATE_KIT_IMPORT_DIR . 'review/review.php';
		} else {
			wp_die( 'No template kit found to review' );
		}
	}

	/**
	 * Assets required for the admin page to render correctly (i.e. all our react stuff)
	 */
	public function admin_page_assets() {
		wp_enqueue_style( 'template-kit-import-admin', ENVATO_TEMPLATE_KIT_IMPORT_URI . 'assets/main.css', array(), filemtime( ENVATO_TEMPLATE_KIT_IMPORT_DIR . 'assets/main.css' ) );
		wp_enqueue_script( 'template-kit-import-admin', ENVATO_TEMPLATE_KIT_IMPORT_URI . 'assets/main.js', array(), filemtime( ENVATO_TEMPLATE_KIT_IMPORT_DIR . 'assets/main.js' ), true );
	}

}
