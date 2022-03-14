<?php

if(is_home() || is_front_page()){
	$var = 'front';
}elseif(is_single() || is_page()){
	$var = 'single';
}elseif(is_404()){
	$var = '404';
}elseif (is_search()) {
	$var = 'search';
}elseif (is_archive()) {
	$var = 'archive';
}else{
	$var = '';
}
/**
 * @since 1.1.0
 *
 **/
$options = get_option('trustify_settings');
$key = 'trustify_popup_additional';
$disable_loggedin = isset( $options[$key]['disable_loggedin'] ) ? $options[$key]['disable_loggedin'] : '';
if($disable_loggedin == 1 && is_user_logged_in()){
    return;
}
//Image Position
 $options = get_option( 'trustify_settings' );
 $key = $options['trustify_popup_design'];
 $image_view = $key['imageview'];
?>

<div id="trustifyWrapper" data-trustify-page-id="<?php echo get_the_ID(); ?>" data-offset=<?php echo esc_attr($var);?> class="col2" style="float: left">
    <div class="popup_position">
        <div class="popup_box">
            <div class="popup_template animated clearfix <?php echo esc_attr('image-'.$image_view);?>" id="popup_template" style="display: none;">
                <!-- Content will be loaded dynamically through ajax -->
            </div>
        </div>
    </div>
</div>