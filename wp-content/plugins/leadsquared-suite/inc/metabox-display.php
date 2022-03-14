<?php 
global $post;
wp_nonce_field( 'leadsquared_form_box', 'leadsquared_form_box_nonce' );
$lpc = get_post_meta( $post->ID, 'leadsquared-form-code', true );
?>
<div class="leadsquared-form-view">
	<?php if ($post->post_status == 'publish'){?>
		<div class="leadsquared-form-shortcode"><p><i>Copy this shortcode and paste it into your post, page, or text widget content:  </i><span style="background:#e6e6e6; padding:0 5px;">[leadsquared-form id="<?php echo $post->ID; ?>"]</span></p></div>
	
	<?php } ?>
	<input type="hidden" name="formcode" id="formcode" value="<?php  echo $lpc; ?>" />
	<div id="showresults">
		<?php echo htmlspecialchars_decode($lpc); ?>	
		<?php if( empty($lpc ) ) : ?><div style="border:1px dashed #e7e7e7;padding:20px;"> Choose your LeadSqaured form from the section on the right hand side </div><?php endif; ?>
	</div>
</div>