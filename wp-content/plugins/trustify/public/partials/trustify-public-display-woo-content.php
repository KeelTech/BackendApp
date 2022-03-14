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

$options = get_option( 'trustify_woo_settings' );
$timeperiod = isset( $options['trustify_woonotice_timeperiod'] ) ? $options['trustify_woonotice_timeperiod'] : '60';

$args = array(
    'post_type' => 'shop_order',
    'post_status' => 'wc-on-hold, wc-completed, wc-pending, wc-processing',
    'date_query' => array(
      'after' => date('Y-m-d', strtotime('-'.$timeperiod.' days'))
    ),
    'orderby'=> 'rand',
);
//$args['post__not_in'] = $trustify_ids;

$posts = get_posts($args);

$products = array();
$version_is_before_3 = version_compare( WC()->version, '3.0', '<')?true:false;

foreach($posts as $post) {
    $order = new WC_Order($post->ID);
    $order_items = $order->get_items();
    //print_r($order_items);
    if(!empty($order_items)) {
        $first_item = array_values($order_items)[0];
        $product_id = $first_item['product_id'];
        $product = wc_get_product($product_id);
        if(!empty($product)){
            preg_match( '/src="(.*?)"/', $product->get_image('200x300'), $imgurl);
            array_push( $products, array(
              'p_id'  => $post->ID,
              'product_id' => $product_id,
              'id'    => $first_item['order_id'],
              'name'  => $product->get_title(),
              'url'   => $product->get_permalink(),
              'date'  => $post->post_date_gmt,
              'image' => count($imgurl) === 2 ? $imgurl[1] : null,
              'price' => get_woocommerce_currency_symbol() . ($version_is_before_3 ? $product->get_display_price() : wc_get_price_to_display($product)),
              'buyer' => createBuyerArray($order)
            ));
        }
    }
}


function createBuyerArray($order){
    $address = $order->get_address('billing');
    if(!isset($address['city']) || strlen($address['city']) == 0 )
        $address = $order->get_address('shipping');

    $buyer = array(
    'name' => isset($address['first_name']) && strlen($address['first_name']) > 0 ? ucfirst($address['first_name']) : 'someone',
    'city' => isset($address['city']) && strlen($address['city']) > 0 ? ucfirst($address['city']) : 'N/A',
    'state' => isset($address['state']) && strlen($address['state']) > 0 ? ucfirst($address['state']) : 'N/A',
    'country' =>  isset($address['country']) && strlen($address['country']) > 0 ? WC()->countries->countries[$address['country']] : 'N/A',
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
$options = get_option( 'trustify_woo_settings' );
$popup_contents = isset( $options['trustify_woonotice_content'] ) ? $options['trustify_woonotice_content'] : '';
 
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