<?php 
global $post;
wp_nonce_field( 'leadsquared_tracking', 'leadsquared_tracking_nonce' );
$lsq_tracking = get_post_meta( $post->ID, 'lsq_tracking', true);

?>
<div class="leadsquared-tracking">
	<p>You can stop tracking this page in LeadSquared </p>
	<p class="meta-options"><label for="leadsquared_tracking" class="selectit"><input name="tracking_status" type="checkbox" id="tracking_status" value="checked"  <?php if($lsq_tracking){ if ( $lsq_tracking["tracking"] == "checked" ) { ?> checked="checked" <?php }} ?> > Stop Tracking.</label></p>
	<p>You can give custom scoring to this page</p>
	<p class="meta-options"><label for="leadsquared_score" class="selectit"><input type="number" id="lsq_score" name="lsq_score" size="13" value="<?php if($lsq_tracking){ echo $lsq_tracking['score']; }  ?>" style="width: 80px;margin-right: 10px;"/>Page Scoring</label></p>
</div>