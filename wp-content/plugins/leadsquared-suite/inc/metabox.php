<?php
if(isset($this->restkeys['access_key']) && $this->restkeys['access_key'] != '' && isset($this->restkeys['secret_key']) && $this->restkeys['secret_key'] != ''){

global $post;
wp_nonce_field( 'leadsquared_form_box', 'leadsquared_form_box_nonce' );
$lp = get_post_meta( $post->ID, 'leadsquared-form-settings' );
function lsqcurl($url,$data_string)
{
		$post_string = $data_string;

			
		$response = wp_remote_request( $url, array( 
				'method'  => 'POST',
				'headers' => array('Content-Type' => 'application/json','Content-Length' => strlen($post_string)),
				'body'    => $post_string,
				'timeout' => 20
		) );

			if ( is_wp_error( $response ) ) {
			   $error_message = $response->get_error_message();
				$json_decode = json_decode($response['body'], true);
			} else {
				$json_decode = json_decode($response['body'], true);
				
			}	
			
			return $json_decode;
}
$api_url_base = 'https://'.get_option("leadsquared_api").'/v2/LandingPage.svc';
$url = $api_url_base . '/Retrieve?accessKey=' . $this->restkeys["access_key"]. '&secretKey=' . $this->restkeys["secret_key"];
$data_string = '{
    "SearchParameters": {"SearchText":"", "StatusCode" : "1","StatusReason":"-1"},
    "Sorting": {"ColumnName":"ModifiedOn","Direction":"1"},
    "Paging": {"PageIndex":"1","PageSize":"1000"}
}
';
$lp_array = lsqcurl($url,$data_string);
if(isset($lp)){
	if ($lp[0]["landing_page_style"] == 'true' ) { $true = 'selected=""'; } else { $true = '';}
	if ($lp[0]["landing_page_style"] == 'false' ) { $false = 'selected=""'; } else { $false = '';}	
}
echo '<div class="submitbox" id="submitpost"><label for="lp" style="width:100%;padding:10px 0;"><strong>Landing Pages</strong></label>';
echo '<select id="lp-select" name="lp-select" style="width:100%;" >';
foreach($lp_array['List'] as $value){
	 if ($lp[0]["landing_page_id"] == $value['LandingPageId'] ) { $selected = 'selected=""'; } else { $selected = '';}
	echo '<option class="landing-page" value="'.$value['LandingPageId'].'"  '. $selected. '>'.$value['Name'].'</option>';
}
echo '</select>
<label for="lp" style="width:100%;padding:10px 0;"><strong>With Style</strong></label>
<select id="lpstyle" name="lpstyle" style="width:100%;" >
<option class="landing-page" value="true" '.$true.'>Yes</option>
<option class="landing-page" value="false" '.$false.'>No</option>
</select>
<div class="clear"></div>
<div id="major-publishing-actions" style="margin: 10px -12px -12px;">
<div id="publishing-action">
<span class="spinner"></span>
		<input type="button" name="load_lp" id="load_lp" class="button button-primary button-large" value="Load"></div>
<div class="clear"></div>
</div></div>';} else { 
print '<p>Couldn\'t fetch LeadSquared REST API fields, Please update valid Access and Secret Keys.</p>';
}
?>
<script>
(function( $ ) {
	$( "#load_lp" ).click(function() {
		var landing_page_id = $('#lp-select').val();
		var landing_page_style = $('#lpstyle').val();
		jQuery.ajax({
		data: {	action: 'leadsquared_form_get_form',
				landing_pid:landing_page_id,
				landing_pstyle:landing_page_style
		},
		type: 'POST',
		url: "<?php echo admin_url('admin-ajax.php'); ?>",
		success: function(data){
			console.log (data);
			 $("#showresults").replaceWith(data);
			 $("#formcode").val(data);
		}, 
			error: function(MLHttpRequest, textStatus, errorThrown){ 
				alert("there is an error"); 
			},
		  
		});	 
	});
})( jQuery );
</script>