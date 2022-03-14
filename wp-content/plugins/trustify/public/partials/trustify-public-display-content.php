<?php



/**
 * Provide a public-facing view for the plugin
 *
 * This file is used to markup the public-facing aspects of the plugin.
 *
 * @link       http://responsive-pixel.com/
 * @since      1.0.0
 *
 * @package    Trustify
 * @subpackage Trustify/public/partials
 */



global $post;

$main_id = isset($_POST['page_id']) ? $_POST['page_id'] : '';

$page_type = $_POST['page_type'];



//popup image option

//Image Position
 $options = get_option( 'trustify_settings' );
 $key = $options['trustify_popup_design'];
 $image_position = $key['imgposition'];

$current_date = current_time( 'Y-m-d' );

$args = [
    'post__not_in' => $trustify_ids,
    'post_type' => 'mifi',
    'posts_per_page' => -1,
    'orderby' => 'rand',
    'post_status' => 'publish',
    //'meta_query' => array($meta_query)
];

$loop = new WP_Query($args);
while ($loop->have_posts()) : $loop->the_post();

//Notification variables

$text = get_post_meta(get_the_ID(), 'mifi-time-text', TRUE);
$time = get_post_meta(get_the_ID(), 'mifi-time', TRUE);
$min_hr = get_post_meta(get_the_ID(), 'mifi-min-hr', TRUE);
$heading = get_post_meta(get_the_ID(), 'mifi-heading', TRUE);
$checkfields = get_post_meta(get_the_ID(), 'checkfield');
$from_date = get_post_meta(get_the_ID(), 'mifi-from-date', TRUE);
$end_date = get_post_meta( get_the_ID(), 'mifi-to-date', TRUE );
$current_date = current_time( 'Y-m-d' );


$chkfld_exp = explode(',',$checkfields[0]);

if(in_array($main_id, $chkfld_exp)){
    continue;
}

if($current_date==$end_date){
    continue;
}


if(in_array(('front_page'),$chkfld_exp)){ 
    if ( $page_type=='front' ) 
        continue;   
}



if(in_array('single_page',$chkfld_exp)){
    if($page_type=='single')
        continue;                 
}


if(in_array('404_page',$chkfld_exp)){
    if($page_type=='404')
        continue;
}

if(in_array('search_page',$chkfld_exp)){
    if($page_type=='search')
        continue;
}

if(in_array('archive_page',$chkfld_exp)){
    if($page_type=='archive')
        continue;
}  

if($from_date<=$current_date):          

    ?>

    <div id="<?php echo $id = get_the_ID(); ?>" class="popup-item <?php echo esc_attr($image_position);?> <?php echo (!has_post_thumbnail()) ? 'textOnly' : '';?> clearfix">
        <div class="popup_close">X</div>
        <?php if($image_position !== 'textOnly' && has_post_thumbnail()){ ?>
            <figure>
                <img src="<?php the_post_thumbnail_url(); ?>" alt="trustify-image">
            </figure>
        <?php } ?>
        <div class="trustify-content-wrap">
            <?php echo esc_attr($text); ?> <span class="t-product"><?php echo esc_attr($heading); ?> </span>
            <small class="time"><?php echo esc_attr($time) . ' ' . esc_attr($min_hr) . ' '; ?><?php echo esc_html__('ago','trustify'); ?></small>
        </div>
    </div>

    <?php

endif;
break;
endwhile;

wp_reset_postdata();

