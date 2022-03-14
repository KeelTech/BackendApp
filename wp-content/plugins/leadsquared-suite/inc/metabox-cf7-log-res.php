<?php 
global $post;
$lsqres = get_post_meta( $post->ID, 'leadsquared-cf7-log-response', true );
?>
<div class="leadsquared-form-view">
	<?php echo $lsqres; ?>
</div>