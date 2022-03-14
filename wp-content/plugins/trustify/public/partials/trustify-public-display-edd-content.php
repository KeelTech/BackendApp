<?php

/**
 * Provide a public-facing view for the plugin
 *
 * This file is used to markup the public-facing aspects of the plugin.
 *
 * @link       http://responsive-pixel.com/
 * @since      2.0
 *
 * @package    Trustify
 * @subpackage Trustify/public/partials
 */

$options = get_option( 'trustify_edd_settings' );
$timeperiod = isset( $options['trustify_eddnotice_timeperiod'] ) ? $options['trustify_eddnotice_timeperiod'] : '60';

$args = array(
    'post_type' => 'edd_payment',
    'post_status' => 'publish',
    'date_query' => array(
      'after' => date('Y-m-d', strtotime('-'.$timeperiod.' days'))
    ),
    'orderby'=> 'rand',
);
//$args['post__not_in'] = $trustify_ids;

$posts = get_posts($args);
$products = array();
foreach($posts as $post) {
  $order = new EDD_Payment($post->ID);
  $order_items = $order->downloads;

  if(!empty($order_items)) {
      $first_item = array_values($order_items)[0];
      $product_id = $first_item['id'];
      $product = edd_get_download($product_id);
      //print_r($product);
      if(!empty($product)){
            preg_match( '/src="(.*?)"/', get_the_post_thumbnail($product_id,'thumbnail'), $imgurl);
            array_push( $products, array(
              'p_id'  => $post->ID,
              'product_id' => $product_id,
              'id'    => $post->ID,
              'name'  => $product->post_title,
              'url'   => get_permalink($product_id),
              'date'  => $post->post_date_gmt,
              'image' => count($imgurl) === 2 ? $imgurl[1] : null,
              'price' => edd_price($product_id,false),
              'buyer' => createBuyerArray($order)
            ));
      }
  }    
}
//print_r($products);

function createBuyerArray($order){
    $address = $order->address;
    $fname = isset($order->first_name)?$order->first_name:'';
    $lname = isset($order->last_name)?$order->last_name:'';
    $countries = edd_get_country_list();
    $states = edd_get_shop_states($address['country']);

    $buyer = array(
    'name' => $fname.' '.$lname,
    'city' => isset($address['city']) && strlen($address['city']) > 0 ? ucfirst($address['city']) : 'N/A',
    'state' => isset($address['state']) && strlen($address['state']) > 0 ? $states[$address['state']] : 'N/A',
    'country' =>  isset($address['country']) && strlen($address['country']) > 0 ? $countries[$address['country']] : 'N/A',
    );

  return $buyer;
}

$p = $products[0];
$pid = isset($p['p_id']) ? $p['p_id'] : '';
$pr_id = isset($p['product_id']) ? $p['product_id'] : '';

//Image Position
$options = get_option( 'trustify_settings' );
$key = $options['trustify_popup_design'];
$image_position = $key['imgposition'];

//Popup Contents
$options = get_option( 'trustify_edd_settings' );
$popup_contents = isset( $options['trustify_eddnotice_content'] ) ? $options['trustify_eddnotice_content'] : '';
 
if($posts!=Null && $popup_contents){
    $image_url = isset($p['image']) ? $p['image'] : '';
    $date = strtotime($p['date']);
    $date = human_time_diff($date);
    
    $real_content  = strtr($popup_contents, array("[name]"=>$p['buyer']['name'], "[country]"=>$p['buyer']['country'], "[city]"=>$p['buyer']['city'], "[product]"=>$p['name'], "[time]"=>$date));
    ?>
    <div class="popup-item woo-content <?php echo esc_attr($image_position);?> <?php echo ($image_url == '') ? 'textOnly' : ''; ?> clearfix" data-id="<?php echo (int)$pid ?>" data-pid="<?php echo (int)$pr_id ?>">
        <div class="popup_close">X</div>
        <a target="_blank" href="<?php echo esc_url($p['url']);?>">
            <?php 
            if($image_url != ''){ 
            if($image_position !== 'textOnly'){ 
            ?>
            <figure class="woo-img <?php echo esc_attr($image_style);?>"><img src="<?php echo esc_url($image_url)?>"/></figure>
            <?php }}?>
            <div class="trustify-content-wrap">
                <?php echo $real_content;?>
                <br><small class="time"><?php echo esc_attr($date) . ' '; ?><?php echo esc_html__('ago','trustify'); ?></small>
            </div>
        </a>
    </div>
    <?php
}
 