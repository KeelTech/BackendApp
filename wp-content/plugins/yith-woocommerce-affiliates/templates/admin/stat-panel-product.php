<?php
/**
 * Products Stat Admin Panel
 *
 * @author  Your Inspiration Themes
 * @package YITH WooCommerce Affiliates
 * @version 1.0.0
 */

/*
 * This file belongs to the YIT Framework.
 *
 * This source file is subject to the GNU GENERAL PUBLIC LICENSE (GPL 3.0)
 * that is bundled with this package in the file LICENSE.txt.
 * It is also available through the world-wide-web at this URL:
 * http://www.gnu.org/licenses/gpl-3.0.txt
 */

if ( ! defined( 'YITH_WCAF' ) ) {
	exit;
} // Exit if accessed directly
?>

<h2><?php esc_html_e( 'Statistics per single product', 'yith-woocommerce-affiliates' ); ?></h2>
<div class="yith-affiliates-stats">
	<?php $product_table->display(); ?>
</div>
