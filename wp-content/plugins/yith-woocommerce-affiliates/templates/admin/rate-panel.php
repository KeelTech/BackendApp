<?php
/**
 * Rate Admin Panel
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

$max = apply_filters( 'yith_wcaf_max_rate_value', 100 );

?>

<div id="yith_wcaf_panel_rate">
	<form id="plugin-fw-wc" class="general-rate-table" method="post">
		<div class="yith-users-new-commission">
			<h4><?php esc_html_e( 'Add new user commission', 'yith-woocommerce-affiliates' ); ?></h4>
			<?php
			yit_add_select2_fields(
				array(
					'class'            => 'yith-users-select wc-product-search',
					'name'             => 'yith_new_affiliate_rate[affiliate]',
					'data-action'      => 'json_search_affiliates',
					'data-placeholder' => __( 'Search for an affiliate&hellip;', 'yith-woocommerce-affiliates' ),
					'style'            => 'min-width: 300px;',
					'value'            => '',
				)
			);
			?>
			<input type="number" name="yith_new_affiliate_rate[rate]" class="yith-users-commission" min="0" max="<?php echo esc_attr( $max ); ?>" step="any" value="" style="max-width: 50px;"/>
			<input type="submit" class="yith-users-commission-submit button button-primary" value="<?php echo esc_attr( __( 'Add Commission', 'yith-woocommerce-affiliates' ) ); ?>"/>
		</div>

		<h2><?php esc_html_e( 'User rates', 'yith-woocommerce-affiliates' ); ?></h2>

		<div class="yith-affiliates-rates">
			<?php $user_rates_table->display(); ?>
		</div>

		<div class="clear separator"></div>

		<div class="yith-products-new-commission">
			<h4><?php esc_html_e( 'Add new product commission', 'yith-woocommerce-affiliates' ); ?></h4>
			<?php
			yit_add_select2_fields(
				array(
					'class'            => 'yith-products-select wc-product-search',
					'name'             => 'yith_new_product_rate[product]',
					'data-placeholder' => __( 'Search for a product&hellip;', 'yith-woocommerce-affiliates' ),
					'style'            => 'min-width: 300px;',
					'value'            => '',
				)
			);
			?>
			<input type="number" name="yith_new_product_rate[rate]" class="yith-products-commission" min="0" max="<?php echo esc_attr( $max ); ?>" step="any" value="" style="max-width: 50px;"/>
			<input type="submit" class="yith-products-commission-submit button button-primary" value="<?php echo esc_attr( __( 'Add Commission', 'yith-woocommerce-affiliates' ) ); ?>"/>
		</div>

		<h2><?php esc_html_e( 'Product rates', 'yith-woocommerce-affiliates' ); ?></h2>
		<div class="yith-affiliates-rates">
			<?php $product_rates_table->display(); ?>
		</div>

	</form>
</div>
