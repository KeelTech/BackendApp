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



//Image Position
 $options = get_option( 'trustify_settings' );
 $key = $options['trustify_popup_design'];
 $image_position = $key['imgposition'];

//Random name

$options = get_option( 'trustify_auto_settings' );
$key =  'trustify_autonotice_title';
$rand_name = $options[$key];

$text_array = $arr_history = explode(',',$rand_name);
$n_key = array_rand($text_array,1);
$name = $text_array[$n_key];

//Random country

$options = get_option( 'trustify_auto_settings' );
$key =  'trustify_autonotice_country';
$rand_country = $options[$key];

$country_array = explode(',',$rand_country);
$c_key = array_rand($country_array,1);
$country = $country_array[$c_key];

//Random Time

$time = mt_rand(1,15);
$mins =  esc_html__('mins','trustify');
$hours = esc_html__('hours','trustify');
$sec = esc_html__('secs','trustify');
$min_hr = [$mins,$hours,$sec];
$t_key = array_rand($min_hr,1);
$timespend = $time.' '.$min_hr[$t_key];

//Random products

$options = get_option('trustify_auto_settings');
$key = 'trustify_autonotice_product';
$product_array = ( isset( $options[$key] ) ) ? $options[$key] : '';  

$rand_product = array_rand($product_array['title'],1);
$image_url = $product_array['url'][$rand_product];
$product_name = $product_array['title'][$rand_product];


//Static Texts
$options = get_option('trustify_auto_settings');
$key = 'trustify_autonotice_static_texts';
$purchased = ( isset( $options[$key]['has'] ) ? $options[$key]['has'] : 'Has Purchased' );
$from = ( isset($options[$key]['from'] ) ? $options[$key]['from'] : 'From' );

$popup_contents = isset($options['trustify_autonotice_content']) ? $options['trustify_autonotice_content'] : '';

$auto_content  = strtr($popup_contents, array("[name]"=>$name, "[country]"=>$country, "[product]"=>$product_name, "[time]"=>$timespend));


?>

    <div class="popup-item <?php echo esc_attr($image_position);?> <?php echo ($image_url == '') ? 'textOnly' : ''; ?> clearfix">
        <div class="popup_close">X</div>
        <?php 
        if($image_url != ''){ 
        if($image_position !== 'textOnly'){ 
        ?>
        <figure><img src="<?php echo esc_url($image_url)?>"></figure>
        <?php }}?>
        <div class="trustify-content-wrap">
            <?php if(!$popup_contents){?>
                <?php echo esc_attr($name).' '.esc_attr($from).' '.esc_attr($country).' '.esc_attr($purchased).' <span class="t-product">'.esc_attr($product_name).'</span>'; ?>
                <small class="time"><?php echo esc_attr($timespend) . ' '; ?><?php echo esc_html__('ago','trustify'); ?></small>
                <?php 
            } else{ 
                echo $auto_content; 
                ?>
                <br><small class="time"><?php echo esc_attr($timespend) . ' '; ?><?php echo esc_html__('ago','trustify'); ?></small>
                <?php
            }
            ?>
        </div>
    </div>







