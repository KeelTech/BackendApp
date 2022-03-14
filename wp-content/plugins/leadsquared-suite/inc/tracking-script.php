<?php	
	global $post;
	$lsq_tracking = get_post_meta($post->ID, 'lsq_tracking', true);
	$lsq_id = get_option("leadsquared_account_number");
	$leadsquared_tracking = get_option("leadsquared_tracking");
	if($leadsquared_tracking){
		$tracking_url = 'https://'.$leadsquared_tracking;
	} else {
		$tracking_url = 'https://web.mxradon.com';
	}
	if ( is_singular() ) {
		if($lsq_tracking)
		{
			if($lsq_tracking["tracking"] != "checked")
			{
				?>
					<script type="text/javascript" src="<?php echo $tracking_url; ?>/t/Tracker.js"></script>
					<script type="text/javascript">
						<?php if(!empty($lsq_tracking["score"])) { ?>
						<?php echo "Asc =".$lsq_tracking["score"]; ?>;
						<?php } ?>
						pidTracker('<?php echo $lsq_id; ?>');			
					</script>
				<?php 
			}
		}
		else
			{
				?>
					<script type="text/javascript" src="<?php echo $tracking_url; ?>/t/Tracker.js"></script>
					<script type="text/javascript">
						<?php if(!empty($lsq_tracking["score"])) { ?>
						<?php echo "Asc =".$lsq_tracking["score"]; ?>;
						<?php } ?>
						pidTracker('<?php echo $lsq_id; ?>');			
					</script>
				<?php 
			}
		} else {
?>
					<script type="text/javascript" src="<?php echo $tracking_url; ?>/t/Tracker.js"></script>
					<script type="text/javascript">
						pidTracker('<?php echo $lsq_id; ?>');			
					</script>
				<?php 
	}

