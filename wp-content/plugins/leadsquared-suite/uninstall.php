<?php
if ( ! defined( 'WP_UNINSTALL_PLUGIN' ) )
	exit();
	
function wplsdp_delete_plugin() {
	delete_option('_leadsquared_rest_api');
	delete_option('_comments2lead_form_fields');
	delete_option('_comments2lead_prospect_activity');
	delete_option('leadsquared_modules');

}
wplsdp_delete_plugin();
?>