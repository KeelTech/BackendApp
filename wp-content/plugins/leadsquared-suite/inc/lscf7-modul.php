<?php	
	function getMetadata() {
		$rest_api_keys = get_option(LSQFORM_REST_API_OPTION);
		$url  = 'https://'.get_option("leadsquared_api").'/v2/LeadManagement.svc/LeadsMetaData.Get?accessKey='.$rest_api_keys["access_key"].'&secretKey='.$rest_api_keys["secret_key"];
		$request = wp_remote_get($url);
		$response = wp_remote_retrieve_body( $request );
		$result = $response;
		return $result;
	}
    if(function_exists('wpcf7_add_tag_generator')) {
		$text = function_exists('wpcf7_add_meta_boxes') ? 'wpcf7_tg_pane_leadsquared_text' : 'wpcf7_tag_generator_leadsquared_text';
		$textarea = function_exists('wpcf7_add_meta_boxes') ? 'wpcf7_tg_pane_leadsquared_text' : 'wpcf7_tag_generator_leadsquared_textarea';
		$number = function_exists('wpcf7_add_meta_boxes') ? 'wpcf7_tg_pane_leadsquared_text' : 'wpcf7_tag_generator_leadsquared_number';
		$tel = function_exists('wpcf7_add_meta_boxes') ? 'wpcf7_tg_pane_leadsquared_text' : 'wpcf7_tag_generator_leadsquared_tel';
		$email = function_exists('wpcf7_add_meta_boxes') ? 'wpcf7_tg_pane_leadsquared_text' : 'wpcf7_tag_generator_leadsquared_email';
		$url = function_exists('wpcf7_add_meta_boxes') ? 'wpcf7_tg_pane_leadsquared_text' : 'wpcf7_tag_generator_leadsquared_url';
		$date = function_exists('wpcf7_add_meta_boxes') ? 'wpcf7_tg_pane_leadsquared_text' : 'wpcf7_tag_generator_leadsquared_date';
		$menu = function_exists('wpcf7_add_meta_boxes') ? 'wpcf7_tg_pane_leadsquared_text' : 'wpcf7_tag_generator_leadsquared_menu';
		$accept = function_exists('wpcf7_add_meta_boxes') ? 'wpcf7_tg_pane_leadsquared_text' : 'wpcf7_tag_generator_leadsquared_acceptance';
		wpcf7_add_tag_generator( 'leadsquared-text', 'Leadsquared Text', 'wpcf7-tg-pane-leadsquared-text',  $text  );
		wpcf7_add_tag_generator( 'leadsquared-textarea', 'Leadsquared Text area', 'wpcf7-tg-pane-leadsquared-textarea', $textarea );
		wpcf7_add_tag_generator( 'leadsquared-number', 'Leadsquared Number', 'wpcf7-tg-pane-leadsquared-number', $number );
		wpcf7_add_tag_generator( 'leadsquared-tele', 'Leadsquared Telephone number', 'wpcf7-tg-pane-leadsquared-number-tel', $tel );
		wpcf7_add_tag_generator( 'leadsquared-email', 'Leadsquared Email', 'wpcf7-tg-pane-leadsquared-email',$email );
		wpcf7_add_tag_generator( 'leadsquared-url', 'Leadsquared Url', 'wpcf7-tg-pane-leadsquared-url', $url );
		wpcf7_add_tag_generator( 'leadsquared-date', 'Leadsquared Date', 'wpcf7-tg-pane-leadsquared-date', $date );
		wpcf7_add_tag_generator( 'leadsquared-select', 'Leadsquared Drop-down', 'wpcf7-tg-pane-leadsquared-select', $menu );
		wpcf7_add_tag_generator( 'leadsquared-ys', 'Leadsquared Acceptance', 'wpcf7-tg-pane-leadsquared-ys', $accept );

	}

	function lsq_search($array, $key, $value)
		{
			$results = array();

			if (is_array($array)) {
				if (isset($array[$key]) && $array[$key] == $value) {
					$results[] = $array;
				}

				foreach ($array as $subarray) {
					$results = array_merge($results, lsq_search($subarray, $key, $value));
				}
			}

			return $results;
		}
		
	function wpcf7_tag_generator_leadsquared_text( $contact_form, $args = '' ) {
		 include_once(LSQFORM_PLUGIN_PATH.'inc/modules/text.php');
	}

	function wpcf7_tag_generator_leadsquared_textarea( $contact_form, $args = '' ) {
		include_once(LSQFORM_PLUGIN_PATH.'inc/modules/textarea.php');
	}
	function wpcf7_tag_generator_leadsquared_number( $contact_form, $args = '' ) {
		include_once(LSQFORM_PLUGIN_PATH.'inc/modules/number.php');
	}

	
	function wpcf7_tag_generator_leadsquared_tel( $contact_form, $args = '' ) {
		include_once(LSQFORM_PLUGIN_PATH.'inc/modules/tel.php');
	}
	
	
	
	function wpcf7_tag_generator_leadsquared_email( $contact_form, $args = '' ) {
		include_once(LSQFORM_PLUGIN_PATH.'inc/modules/email.php');
	}

	function wpcf7_tag_generator_leadsquared_url( $contact_form, $args = '' ) {
		include_once(LSQFORM_PLUGIN_PATH.'inc/modules/url.php');
	}


	function wpcf7_tag_generator_leadsquared_date( $contact_form, $args = '' ) {
		include_once(LSQFORM_PLUGIN_PATH.'inc/modules/date.php');
	}


	function wpcf7_tag_generator_leadsquared_menu( $contact_form, $args = '' ) {
		include_once(LSQFORM_PLUGIN_PATH.'inc/modules/menu.php');
	}

	function wpcf7_tag_generator_leadsquared_acceptance( $contact_form, $args = '' ) {
		include_once(LSQFORM_PLUGIN_PATH.'inc/modules/acceptance.php');
	}

	function wpcf7_tg_pane_leadsquared_text(){
		include_once(LSQFORM_PLUGIN_PATH.'inc/modules/legacy.php');
	}