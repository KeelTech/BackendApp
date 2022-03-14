<?php
if(isset($_POST['submit'])) {
$api_keys = array(
                   'access_key' => $_POST['access_key'],
				   'secret_key' => $_POST['secret_key']
                 );

$auth_url = LSQFORM_AUTH.'accessKey='.$_POST['access_key'].'&secretKey='.$_POST['secret_key'];



$response = wp_remote_get($auth_url,array('timeout'     => 120));

if ( is_array( $response ) && ! is_wp_error( $response ) ) {
    $body    = $response['body']; 

	$json_decode = json_decode($body,true);
	if(!isset($json_decode['Status'])){
		update_option( LSQFORM_REST_API_OPTION, $api_keys );
		update_option("leadsquared_account_number",$json_decode['OrgShortCode']);	
		update_option("leadsquared_api",$json_decode['LSQCommonServiceURLs']['api']);
		update_option("leadsquared_tracking",$json_decode['LSQCommonServiceURLs']['tracking']);
		$message = '<div class = "updated"><p>Your settings have been <strong>Updated!</strong></p></div>';
	}	else {
		$message = '<div class = "error"><p>Please Provide valid Access Key and Secret Key</p></div>';	
	}
	
} else {
	$message = '<div class = "error"><p>There was an error!</p></div>';	
}
	 
}
else
{
	$message = '';
}
$restkeys = get_option(LSQFORM_REST_API_OPTION);
$modules = get_option("leadsquared_modules");
?>
<div class="wrap">
<div id="leadsquared-setting-form">
<div class="icon32" id="icon-options-general"></div>
<h2><?php _e('LeadSquared API Security Credentials') ?></h2>
<?php print (!$message) ? '': $message; ?>
<p><?php _e('Update your access key, secret key and account number here') ?>:</p>
<form id="leadsquare-api-key" name="leadsquare-api-key" method="post" action="">
<table class="form-table">
  <tbody>
	<?php  
	if($this->lsqoption['lsqform'] == '1' or $this->lsqoption['cf72lsq'] =='1' or $this->lsqoption['lsqc2l'] == '1' or $this->lsqoption['lsqts'] == '1' ) { ?> 
      <tr class="form-field">
        <th scope="row"><label for="access_key">LeadSquared API Access Key :</label></th>
        <td><input id="access_key" type="text" name="access_key" value="<?php print $restkeys ? $restkeys['access_key'] : '';  ?>" /></td>
      </tr class="form-field">
      <tr>
        <th scope="row"><label for="access_key">LeadSquared API Secret Key :</label></th>
        <td><input id="secret_key" type="text" name="secret_key" value="<?php print $restkeys ? $restkeys['secret_key'] : '';  ?>" /></td>
     </tr>
	<?php }  ?>
  </tbody>
</table>
<?php submit_button('Update Keys'); ?>
</form>
<p>You will find your API access key and security key in your Settings page of your LeadSquared Account. For more information, check our <a href="http://help.leadsquared.com/how-do-i-obtain-api-access-keys-in-leadsquared/" target="_blank"><?php _e('help article here') ?></a>.</p>
<p><b>LeadSquared Account Number</b> You can find it in the <em>footer</em> of <b>LeadSquared Application</b> on the right side</p>
</div></div>
<div class="powered-by"><a target="_blank" href="http://www.leadsquared.com"><img alt="LeadSquared Image" src="<?php print LSQFORM_PLUGIN_URL ?>images/powered_by.png"></a></div>