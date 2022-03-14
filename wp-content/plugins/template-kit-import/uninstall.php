<?php
// If uninstall not called from WordPress exit
if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) ) {
	exit();
}

delete_option( 'template_kit_import_tracker_notice' );
delete_option( 'template_kit_import_version' );
delete_option( 'template_kit_import_install_time' );
delete_option( '_template_kit_import_installed_time' );
delete_option( 'template_kit_import_license_code' );
delete_option( 'template_kit_import_options' );
delete_option( 'template_kit_import_photo_imports' );

// Remove the scheduled task.
wp_clear_scheduled_hook( 'template_kit_import_cron' );
