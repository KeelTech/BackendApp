<?php 
global $post;
$lsqdata = get_post_meta( $post->ID, 'leadsquared-cf7-log-data', true );
?>
<div class="leadsquared-form-view">
	<?php echo $lsqdata;?>
</div>