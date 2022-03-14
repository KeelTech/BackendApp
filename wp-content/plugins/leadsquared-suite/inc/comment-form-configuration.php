<?php
if(isset($_POST['submit'])) {
	//Update prospect activity option
if(isset($_POST['activity_status']) && $_POST['activity_status'] == 1) {
$prospect_activity_status = $_POST['activity_status'];
	if(isset($_POST['select_activity_type']) && $_POST['select_activity_type'] == '') {
	         $msg_prospect_status = '<div class = "updated"><p>Activity type should not be empty.</p></div>';
	}
	elseif(isset($_POST['select_activity_type']) && $_POST['select_activity_type'] != '') {
			$prospect_activity_type   = $_POST['select_activity_type'];
			$combined_prospect_activity_values = array($prospect_activity_status,$prospect_activity_type);
			update_option( LSQFORM_PROSPECT_ACTIVITY_OPTION, $combined_prospect_activity_values);
			unset($_POST['activity_status']);
			unset($_POST['select_activity_type']);
	}
}
else {
delete_option(LSQFORM_PROSPECT_ACTIVITY_OPTION);
}

$form_split_array = array_chunk($_POST, 3, true);
$fields_value_array = array();
$i=0;
foreach($form_split_array as $key => $value) {
        $form_array_split_value = array_values($value);
		$format_field_array = array();
		foreach($form_array_split_value as $s_key => $s_value) {
		          if($s_key === 0) {
				  $s_key = 'title';
				  }
                  elseif($s_key === 1) {
				  $s_key = 'data_name';
				  }
				  elseif($s_key === 2) {
				  $s_key = 'leads_schemaname';
				  }
   				  
		          $format_field_array[$s_key] = $s_value;
		}
		$fields_value_array[$i] = $format_field_array;
$i++;		
}
$count = count($fields_value_array);
unset($fields_value_array[$count-1]);
$update = update_option( LSQFORM_COMMENT_FORM_OPTION, $fields_value_array );
	$msg = '<div class = "updated"><p>Your form configuration settings have been <strong>Updated!</strong></p></div>';
}
/* Get LeadSquared Field from REST api*/
$restkeys = get_option(LSQFORM_REST_API_OPTION);
if(isset($restkeys['access_key']) && $restkeys['access_key'] != '' && isset($restkeys['secret_key']) && $restkeys['secret_key'] != '') {
		 $decode_json = json_decode($json, TRUE);
		 if($decode_json) {
		 $data_type = array();
			 foreach($decode_json as $key => $value) {
			   $data_type[$value['SchemaName']] = $value['DisplayName'];
			 }
		 $leadsquared_fied_type = array_unique($data_type);
		}
}
else {
        $key_empty_msg = '<div class = "updated"><p>You must configure <strong>Security Credentials</strong> before you can use Comments-to-Lead plugin</p></div>';
}
$lsqc2l = get_option(LSQFORM_COMMENT_FORM_OPTION);
if(!$lsqc2l){
	$lsqc2l = array( 
				array("title"=>"Name","data_name"=>"comment_author","leads_schemaname"=>"FirstName"),
				array("title"=>"Email","data_name"=>"comment_author_email","leads_schemaname"=>"EmailAddress"),
				array("title"=>"Website","data_name"=>"comment_author_url","leads_schemaname"=>"Website"),
				array("title"=>"Comment","data_name"=>"comment_content","leads_schemaname"=>"Notes"),
				);
}
?>
<div class="wrap">
	<div id="leadsquared-comment-form">
		<div class="icon32" id="icon-options-general"></div>
		<h2><?php _e('Comments to LeadSquared Configuration')  ?></h2>
		<p><?php _e('Track user active of your website on leadsquared') ?> </p>
	</div>
	<form method="post">
	
<h3><?php _e('Activity Setting')  ?></h3>
<p><?php _e('Select this option if you would like to track each comment post as a separate activity in LeadSquared') ?> </p>
<?php //wp_nonce_field('add-item','leadsquared-comment-form'); ?>
<!--- Prospect Activity --->
<?php
$leadsquare_prospect_activity = get_option(LSQFORM_PROSPECT_ACTIVITY_OPTION);
if($leadsquare_prospect_activity) {
if($leadsquare_prospect_activity[0] != '' && $leadsquare_prospect_activity[1] != '')  {
$prospect_status_option     = $leadsquare_prospect_activity[0]; 
$prospect_activity_option   = $leadsquare_prospect_activity[1];
 	$decode_activity_json = json_decode($activity_json, TRUE);
	if($decode_activity_json) {
		$activity_type = array();
			foreach($decode_activity_json as $key => $value) {
			   $activity_type[$value['ActivityEvent']] = $value['DisplayName'];
	  	    }
		$prospect_activity_type = array_unique($activity_type);
		$output = 'Activity Type: <select name="select_activity_type" id="select_activity_type">
        <option value="" selected="selected">-- SELECT --</option>';
        if(!empty($prospect_activity_type)) {
		asort($prospect_activity_type);
        foreach($prospect_activity_type as $activity_key => $activity_values) {
		   $select = ($prospect_activity_option == $activity_key) ? 'selected="selected"' : '';
		   $output .= '<option '.$select.' value="'.$activity_key.'">'.$activity_values.'</option>'; 
		} 
		}
$output .= '</select>';
} }
}
?>
<table class="ls_activity">
  <tbody>
      <tr>
        <td id="prospect_checkbox"><input id="check_activity_status" type="checkbox" name="activity_status" value="1"  <?php (isset($prospect_status_option) == 1) ? print 'checked="checked"' : print ''; ?> /><label for="check_activity_status">Track each comment as activity</label></td>
	  </tr>
	  
  </tbody>
</table>
<div id="activity_type"><?php if(isset($output)){ print $output; } ?></div>
<!--- End --->
<h3><?php _e('Comment Form Mapping')  ?></h3>
		<table class="widefat fixed" cellspacing="0">
			<thead>
				<tr>
					<th>Comments Field</th>
					<th>LeadSquared Field</th>
				</tr>
			</thead>
			<tbody id="patient_table">
				<?php foreach($lsqc2l as $value) { ?>
				
				<tr>
					<td>
						<input type="hidden" value="<?php echo $value['title']; ?>" name="<?php echo $value['title']; ?>">
						<input type="hidden" value="<?php echo $value['data_name']; ?>" name="<?php echo $value['data_name']; ?>">
						<?php echo $value['title']; ?></td>
					<td>
					<select name="<?php echo $value['data_name']; ?>-field-type" id="<?php echo $value['data_name']; ?>-field-type">
					<option value="" selected="selected">Map to LeadSquared fields</option>
								<?php
								if(!empty($leadsquared_fied_type)) {
									asort($leadsquared_fied_type);
									foreach($leadsquared_fied_type as $field_key => $field_values) {
										$select = ($field_key == $value['leads_schemaname']) ? 'selected="selected"' : '';
										print '<option '.$select.' value="'.$field_key.'">'.$field_values.'</option>'; 
									}
								} 
								?>
					</select>
					</td>
				</tr>
				<?php 	}?>
			</tbody>
		</table>
		<p class="submit">
			<input id="submit" class="button button-primary" type="submit" value="Save" name="submit">
			<input id="cancel" type="reset" name="reset" value="Cancel" class="button button-primary">
		</p>
	</form>
</div>
<div style="clear:both"></div>
<div class="powered-by"><a target="_blank" href="http://www.leadsquared.com"><img alt="LeadSquared Image" src="<?php print LSQFORM_PLUGIN_URL ?>images/powered_by.png"></a></div>