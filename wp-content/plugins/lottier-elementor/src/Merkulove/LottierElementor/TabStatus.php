<?php
/**
 * Lottier for Elementor
 * Lottie animations in just a few clicks without writing a single line of code.
 * Exclusively on https://1.envato.market/lottier-elementor
 *
 * @encoding        UTF-8
 * @version         1.0.3
 * @copyright       (C) 2018 - 2020 Merkulove ( https://merkulov.design/ ). All rights reserved.
 * @license         Envato License https://1.envato.market/KYbje
 * @contributors    Vitaliy Nemirovskiy (nemirovskiyvitaliy@gmail.com), Dmitry Merkulov (dmitry@merkulov.design)
 * @support         help@merkulov.design
 * @license         Envato License https://1.envato.market/KYbje
 **/


namespace Merkulove\LottierElementor;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
	header( 'Status: 403 Forbidden' );
	header( 'HTTP/1.1 403 Forbidden' );
	exit;
}

/**
 * Class used to implement StatusTab tab on plugin settings page.
 **/
final class TabStatus {

	/**
	 * The one true StatusTab.
	 *
     * @var TabStatus
	 **/
	private static $instance;

	/**
	 * Generate Status Tab.
	 *
	 * @access public
     * @return void
	 **/
	public function add_settings() {

		/** Status Tab. */
		register_setting( 'LottierElementorStatusOptionsGroup', 'mdp_lottier_elementor_status_settings' );
		add_settings_section( 'mdp_lottier_elementor_settings_page_status_section', '', null, 'LottierElementorStatusOptionsGroup' );

	}

	/**
	 * Render form with all settings fields.
	 *
	 * @access public
     * @return void
	 **/
	public function render_form() {

	    /** Render "System Requirements". */
		$this->render_system_requirements();

		/** Render Privacy Notice. */
		$this->render_privacy_notice();

	}

	/**
	 * Render "System Requirements" field.
	 *
	 * @access public
     * @return void
	 **/
	public function render_system_requirements() {

	    $reports = [
            'server' => ServerReporter::get_instance(),
            'wordpress' => WordPressReporter::get_instance(),
        ]
		?>
		<div class="mdc-system-requirements">

			<?php foreach ( $reports as $key => $report ) : ?>
                <div class="mdp-status-<?php echo esc_attr( $key ); ?>">
                    <table class="mdc-system-requirements-table">
                        <thead>
                            <tr>
                                <th colspan="2"><?php echo esc_html( $report->get_title() ); ?></th>
                            </tr>
                        </thead>
                        <tbody>
                        <?php foreach ( $report->get_report() as $row ) : ?>
                            <tr>
                                <td><?php echo esc_html( $row['label'] ); ?>:</td>
                                <td><span class="mdc-system-value"><?php echo wp_kses_post( $row['value'] ); ?></span></td>
                                <th class="mdc-text-left">
                                    <?php if ( isset( $row['warning'] ) && $row['warning'] ) : ?>
                                        <i class="material-icons mdc-system-warn">warning</i>
                                        <?php echo ( isset( $row['recommendation'] ) ? esc_html( $row['recommendation'] ) : ''); ?>
                                    <?php endif; ?>
                                </th>
                            </tr>
                        <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            <?php endforeach; ?>

		</div><?php

	}

	/**
	 * Render Privacy Notice.
	 *
	 * @access public
     * @return void
     **/
	public function render_privacy_notice() {

	    ?>
        <div class="mdc-text-field-helper-line">
            <div class="mdc-text-field-helper-text mdc-text-field-helper-text--persistent">
                <?php esc_html_e( 'Some data will be sent to our server to verify purchase and to ensure that a plugin is compatible with your install. 
                We will never collect any confidential data. All data is stored anonymously.', 'lottier-elementor' ); ?>
            </div>
        </div>
        <?php

    }

	/**
	 * Main StatusTab Instance.
	 * Insures that only one instance of StatusTab exists in memory at any one time.
	 *
	 * @static
     * @return TabStatus
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;

	}

}
