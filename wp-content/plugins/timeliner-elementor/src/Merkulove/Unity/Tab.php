<?php
/**
 * Timeliner for Elementor
 * Beautiful graphical representation of a period of time for Elementor
 * Exclusively on https://1.envato.market/timeliner-elementor
 *
 * @encoding        UTF-8
 * @version         1.0.0
 * @copyright       (C) 2018 - 2021 Merkulove ( https://merkulov.design/ ). All rights reserved.
 * @license         Envato License https://1.envato.market/KYbje
 * @contributors    Nemirovskiy Vitaliy (nemirovskiyvitaliy@gmail.com), Dmitry Merkulov (dmitry@merkulov.design)
 * @support         help@merkulov.design
 **/

namespace Merkulove\TimelinerElementor\Unity;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
    header( 'Status: 403 Forbidden' );
    header( 'HTTP/1.1 403 Forbidden' );
    exit;
}

/**
 * Base methods for Tabs Classes.
 *
 * @since 1.0.0
 *
 **/
abstract class Tab {

    /**
     * Check if tab exist and enabled.
     *
     * @param string $tab_slug - Slug of tub to check.
     *
     * @since  1.0.0
     * @access protected
     *
     * @return bool - True if Tab is enabled, false otherwise.
     **/
    protected function is_enabled( $tab_slug = null ) {

        /** Foolproof. */
        if ( null === $tab_slug ) { return false; }

        /** Get all tabs and settings. */
        $tabs = Plugin::get_tabs();

        /** Check if status tab exist. */
        if ( ! isset( $tabs[ $tab_slug ] ) ) { return false; }

        /** Check if 'enabled' field of status tab exist. */
        if ( ! isset( $tabs[ $tab_slug ][ 'enabled' ] ) ) { return false; }

        /** Check if status tab is enabled. */
        return true === $tabs[ $tab_slug ][ 'enabled' ];

    }

    /**
     * Render tab title.
     *
     * @param string $tab_slug - Slug of tub to check.
     *
     * @since  1.0.0
     * @access protected
     *
     * @return void
     **/
    protected function render_title( $tab_slug = null ) {

        /** Foolproof. */
        if ( null === $tab_slug ) { return; }

        /** Get all tabs and settings. */
        $tabs = Plugin::get_tabs();

        /** Get selected to process tab. */
        $tab = $tabs[ $tab_slug ];

        /** If title enabled. */
        if ( true ===  $tab[ 'show_title' ] ) {

            /** Render Title. */
            echo '<h3>' . esc_html__( $tab[ 'title' ] ) . '</h3>';

        }

    }

    /**
     * Output nonce, action, and option_page fields for a settings page.
     * Prints out all settings sections added to a particular settings page
     *
     * @param string $tab_slug - Slug of tub to check.
     *
     * @since  1.0.0
     * @access protected
     *
     * @return void
     **/
    protected function do_settings_base( $tab_slug = null ) {

        /** Foolproof. */
        if ( null === $tab_slug ) { return; }

        settings_fields( 'TimelinerElementor' . $tab_slug . 'OptionsGroup' );
        do_settings_sections( 'TimelinerElementor' . $tab_slug. 'OptionsGroup' );

    }

    /**
     * Registers a setting and its data.
     * Add a new section to a settings page.
     *
     * @param string $tab_slug - Slug of tub to check.
     *
     * @since  1.0.0
     * @access protected
     *
     * @return void
     **/
    protected function add_settings_base( $tab_slug = null ) {

        /** Foolproof. */
        if ( null === $tab_slug ) { return; }

        /** Status Tab. */
        register_setting( 'TimelinerElementor' . $tab_slug . 'OptionsGroup', 'mdp_timeliner_elementor_' . $tab_slug . '_settings' );
        add_settings_section( 'mdp_timeliner_elementor_' . $tab_slug . '_page_status_section', '', null, 'TimelinerElementor' . $tab_slug . 'OptionsGroup' );

    }

    /**
     * Check if tab is enabled by tab slug.
     *
     * @param string $tab_slug - Tab slug.
     *
     * @since  1.0.0
     * @access private
     *
     * @return bool
     **/
    public static function is_tab_enabled( $tab_slug ) {

        /** Get all tabs and settings. */
        $tabs = Plugin::get_tabs();

        return isset( $tabs[ $tab_slug ][ 'enabled' ] ) && $tabs[ $tab_slug ][ 'enabled' ];

    }

}
