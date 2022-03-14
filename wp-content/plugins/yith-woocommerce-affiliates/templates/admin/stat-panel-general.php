<?php
/**
 * General Stat Admin Panel
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

<h2><?php echo esc_html( $page_title ); ?></h2>

<div class="yith-affiliates-stats">
	<div class="tablenav top">
		<div class="alignleft">
			<input type="text" name="_from" placeholder="<?php esc_html_e( 'From:', 'yith-woocommerce-affiliates' ); ?>" value="<?php echo esc_attr( $from ); ?>" class="date-picker" />
			<input type="text" name="_to" placeholder="<?php esc_html_e( 'To:', 'yith-woocommerce-affiliates' ); ?>" value="<?php echo esc_attr( $to ); ?>" class="date-picker" />
			<input type="submit" name="filter_action" id="post-query-submit" class="button" value="<?php esc_html_e( 'Filter', 'yith-woocommerce-affiliates' ); ?>" />
			<?php if ( $need_reset ) : ?>
				<a href="<?php echo esc_url( $reset_link ); ?>" class="button"><?php esc_html_e( 'Reset', 'yith-woocommerce-affiliates' ); ?></a>
			<?php endif; ?>
		</div>
	</div>
	<table class="wc_status_table widefat">
		<thead>
		<tr>
			<th colspan="3">
				<?php esc_html_e( 'General stats', 'yith-woocommerce-affiliates' ); ?>
			</th>
		</tr>
		</thead>
		<tbody>
		<tr>
			<td><?php esc_html_e( 'Total commissions', 'yith-woocommerce-affiliates' ); ?></td>
			<td class="help">
				<a href="#" class="help_tip" data-tip="<?php esc_html_e( 'Sum of all confirmed commissions so far', 'yith-woocommerce-affiliates' ); ?>">[?]</a>
			</td>
			<td><?php echo wc_price( $total_amount ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></td>
		</tr>
		<tr>
			<td><?php esc_html_e( 'Total Paid', 'yith-woocommerce-affiliates' ); ?></td>
			<td class="help">
				<a href="#" class="help_tip" data-tip="<?php esc_html_e( 'Sum of all paid commissions so far', 'yith-woocommerce-affiliates' ); ?>">[?]</a>
			</td>
			<td><?php echo wc_price( $total_paid ); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></td>
		</tr>
		<tr>
			<td><?php esc_html_e( 'Number of hits', 'yith-woocommerce-affiliates' ); ?></td>
			<td class="help">
				<a href="#" class="help_tip" data-tip="<?php esc_html_e( 'Number of clicks', 'yith-woocommerce-affiliates' ); ?>">[?]</a>
			</td>
			<td><?php echo intval( $total_clicks ); ?></td>
		</tr>
		<tr>
			<td><?php esc_html_e( 'Number of conversions', 'yith-woocommerce-affiliates' ); ?></td>
			<td class="help">
				<a href="#" class="help_tip" data-tip="<?php esc_html_e( 'Number of conversions', 'yith-woocommerce-affiliates' ); ?>">[?]</a>
			</td>
			<td><?php echo esc_html( $total_conversions ); ?></td>
		</tr>
		<tr>
			<td><?php esc_html_e( 'Average conversion rate', 'yith-woocommerce-affiliates' ); ?></td>
			<td class="help">
				<a href="#" class="help_tip" data-tip="<?php esc_html_e( 'Average percent conversion rate', 'yith-woocommerce-affiliates' ); ?>">[?]</a>
			</td>
			<td><?php echo esc_html( $avg_conv_rate ); ?></td>
		</tr>
		</tbody>
	</table>
</div>
