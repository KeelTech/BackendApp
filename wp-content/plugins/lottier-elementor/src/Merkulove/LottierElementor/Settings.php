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

use Merkulove\LottierElementor;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
	header( 'Status: 403 Forbidden' );
	header( 'HTTP/1.1 403 Forbidden' );
	exit;
}

/**
 * Class used to implement plugin settings.
 **/
final class Settings {

	/**
	 * Plugin settings.
	 *
	 * @var array()
	 **/
	public $options = [];

	/**
	 * The one true Settings.
	 *
	 * @var Settings
	 **/
	private static $instance;

	/**
	 * Sets up a new Settings instance.
	 *
	 * @access public
	 **/
	private function __construct() {

		/** Get plugin settings. */
	    $this->get_options();

    }

	/**
	 * Render Tabs Headers.
	 *
	 * @param string $current - Selected tab key.
	 * @access public
	 **/
	public function render_tabs( $current = 'general' ) {

		/** Tabs array. */
		$tabs = SettingsFields::get_instance()->tabs;

		$tabs['status'] = [
			'icon' => 'info',
			'name' => esc_html__( 'Status', 'lottier-elementor' )
		];

		/** Activation tab enable only if plugin have Envato ID. */
		$plugin_id = EnvatoItem::get_instance()->get_id();
		if ( (int)$plugin_id > 0 ) {
			$tabs['activation'] = [
				'icon' => 'vpn_key',
				'name' => esc_html__( 'Activation', 'lottier-elementor' )
			];
        }

		$tabs['updates'] = [
			'icon' => 'update',
			'name' => esc_html__( 'Updates', 'lottier-elementor' )
		];

		$tabs['uninstall'] = [
			'icon' => 'delete_sweep',
			'name' => esc_html__( 'Uninstall', 'lottier-elementor' )
		];

		/** Render Tabs. */
		?>
        <aside class="mdc-drawer">
            <div class="mdc-drawer__content">
                <nav class="mdc-list">
                    <?php

                    $this->render_logo();

                    ?>
                    <hr class="mdc-plugin-menu">
                    <hr class="mdc-list-divider">
                    <h6 class="mdc-list-group__subheader"><?php echo esc_html__( 'Plugin settings', 'lottier-elementor' ) ?></h6>
					<?php

					foreach ( $tabs as $tab => $value ) {

						/** Prepare CSS classes. */
						$classes = [];
						$classes[] = 'mdc-list-item';

						/** Mark Active Tab. */
						if ( $tab === $current ) {
							$classes[] = 'mdc-list-item--activated';
						}

						/** Hide Developer tab before multiple clicks on logo. */
						if ( 'developer' === $tab ) {
							$classes[] = 'mdp-developer';
							$classes[] = 'mdc-hidden';
							$classes[] = 'mdc-list-item--activated';
						}

						/** Prepare link. */
						$link = '?page=mdp_lottier_elementor_settings&tab=' . $tab;

						?>
                        <a class="<?php esc_attr_e( implode( ' ', $classes ) ); ?>" href="<?php esc_attr_e( $link ); ?>">
                            <i class='material-icons mdc-list-item__graphic' aria-hidden='true'><?php esc_html_e( $value['icon'] ); ?></i>
                            <span class='mdc-list-item__text'><?php esc_html_e( $value['name'] ); ?></span>
                        </a>
						<?php

					}

					/** Helpful links. */
					$this->support_link();

					/** Activation Status. */
					PluginActivation::get_instance()->display_status();

					?>
                </nav>
            </div>
        </aside>
		<?php
	}

	/**
	 * Displays useful links for an activated and non-activated plugin.
	 *
     * @return void
	 **/
	public function support_link() { ?>

        <hr class="mdc-list-divider">
        <h6 class="mdc-list-group__subheader"><?php echo esc_html__( 'Helpful links', 'lottier-elementor' ) ?></h6>

        <a class="mdc-list-item" href="https://docs.merkulov.design/tag/lottier" target="_blank">
            <i class="material-icons mdc-list-item__graphic" aria-hidden="true">collections_bookmark</i>
            <span class="mdc-list-item__text"><?php echo esc_html__( 'Documentation', 'lottier-elementor' ) ?></span>
        </a>

		<?php if ( PluginActivation::get_instance()->is_activated() ) : /** Activated. */ ?>
            <a class="mdc-list-item" href="https://1.envato.market/lottier-elementor-support" target="_blank">
                <i class="material-icons mdc-list-item__graphic" aria-hidden="true">mail</i>
                <span class="mdc-list-item__text"><?php echo esc_html__( 'Get help', 'lottier-elementor' ) ?></span>
            </a>
            <a class="mdc-list-item" href="https://1.envato.market/cc-downloads" target="_blank">
                <i class="material-icons mdc-list-item__graphic" aria-hidden="true">thumb_up</i>
                <span class="mdc-list-item__text"><?php echo esc_html__( 'Rate this plugin', 'lottier-elementor' ) ?></span>
            </a>
		<?php endif; ?>

        <a class="mdc-list-item" href="https://1.envato.market/cc-merkulove" target="_blank">
            <i class="material-icons mdc-list-item__graphic" aria-hidden="true">store</i>
            <span class="mdc-list-item__text"><?php echo esc_html__( 'More plugins', 'lottier-elementor' ) ?></span>
        </a>
		<?php

	}

	/**
	 * Add plugin settings page.
	 *
	 * @access public
	 **/
	public function add_settings_page() {

		add_action( 'admin_menu', [ $this, 'add_admin_menu' ], 1000 );
		add_action( 'admin_init', [ $this, 'settings_init' ] );

	}

	/**
	 * Generate Settings Page.
	 *
	 * @access public
	 **/
	public function settings_init() {

	    /** Custom tabs */
		SettingsFields::get_instance()->tabs();

		/** Status Tab. */
		TabStatus::get_instance()->add_settings();

		/** Updates Tab */
        TabUpdates::get_instance()->add_settings();

		/** Activation Tab. */
		PluginActivation::get_instance()->add_settings();

		/** Uninstall Tab. */
		UninstallTab::get_instance()->add_settings();

	}

	/**
	 * Add admin menu for plugin settings.
	 *
	 * @access public
	 **/
	public function add_admin_menu() {

        /** Check if Elementor installed and activated. */
        $parent = 'options-general.php';
        if ( did_action( 'elementor/loaded' ) ) {
            $parent = 'elementor';
        }

		add_submenu_page(
            $parent,
			esc_html__( 'Lottier Settings', 'lottier-elementor' ),
			esc_html__( 'Lottier for Elementor', 'lottier-elementor' ),
			'manage_options',
			'mdp_lottier_elementor_settings',
			[ $this, 'options_page' ]
		);

	}

	/**
	 * Plugin Settings Page.
	 *
	 * @access public
	 **/
	public function options_page() {

		/** User rights check. */
		if ( ! current_user_can( 'manage_options' ) ) { return; } ?>

        <!--suppress HtmlUnknownTarget -->
        <form action='options.php' method='post'>
            <div class="wrap">

				<?php
				$tab = 'status'; // Default tab
				if ( isset ( $_GET['tab'] ) ) { $tab = $_GET['tab']; }

				/** Render "Settings saved!" message. */
				$this->render_nags();

				/** Render Tabs Headers. */
				?><section class="mdp-aside"><?php $this->render_tabs( $tab ); ?></section><?php

				/** Render Tabs Body. */
				?><section class="mdp-tab-content mdp-tab-name-<?php echo esc_attr( $tab ) ?>"><?php

                    SettingsFields::get_instance()->tab_content( $tab );

                    /** Activation Tab. */
                    if ( $tab === 'activation' ) {
						settings_fields( 'LottierElementorActivationOptionsGroup' );
						do_settings_sections( 'LottierElementorActivationOptionsGroup' );
						PluginActivation::get_instance()->render_pid();

                    /** Status tab. */
					} elseif ( $tab === 'status' ) {
						echo '<h3>' . esc_html__( 'System Requirements', 'lottier-elementor' ) . '</h3>';
						TabStatus::get_instance()->render_form();

                    /** Updates Tab */
                    } elseif ( 'updates' === $tab ) {
                        TabUpdates::get_instance()->render_tab_content();

                    /** Uninstall Tab. */
					} elseif ( $tab === 'uninstall' ) {
						echo '<h3>' . esc_html__( 'Uninstall Settings', 'lottier-elementor' ) . '</h3>';
						UninstallTab::get_instance()->render_form();
					}

					?>

                </section>
            </div>
        </form>

		<?php
	}

	/**
	 * Render "Settings Saved" nags.
     *
     * @return void
	 **/
	public function render_nags() {

		if ( ! isset( $_GET['settings-updated'] ) ) { return; }

		if ( strcmp( $_GET['settings-updated'], "true" ) === 0 ) {

			/** Render "Settings Saved" message. */
			UI::get_instance()->render_snackbar( esc_html__( 'Settings saved!', 'lottier-elementor' ) );

		}

		if ( ! isset( $_GET['tab'] ) ) { return; }

		if ( strcmp( $_GET['tab'], "activation" ) === 0 ) {

			if ( PluginActivation::get_instance()->is_activated() ) {

				/** Render "Activation success" message. */
				UI::get_instance()->render_snackbar( esc_html__( 'Plugin activated successfully.', 'lottier-elementor' ), 'success', 5500 );

			} else {

				/** Render "Activation failed" message. */
				UI::get_instance()->render_snackbar( esc_html__( 'Invalid purchase code.', 'lottier-elementor' ), 'error', 5500 );

			}

		}

	}

	/**
	 * Render logo and Save changes button in plugin settings.
	 *
	 * @access private
	 * @return void
	 **/
	private function render_logo() {

		?>
        <div class="mdc-drawer__header mdc-plugin-fixed">
            <!--suppress HtmlUnknownAnchorTarget -->
            <a class="mdc-list-item mdp-plugin-title" href="#wpwrap">
                <i class="mdc-list-item__graphic" aria-hidden="true">
                    <img src="<?php echo esc_attr( LottierElementor::$url . 'images/logo-color.svg' ); ?>" alt="<?php echo esc_html__( 'LottierElementor', 'lottier-elementor' ) ?>">
                </i>
                <span class="mdc-list-item__text"><?php echo esc_html__( 'Lottier', 'lottier-elementor' ) ?></span>
                <span class="mdc-list-item__text"><sup><?php echo esc_html__( 'v.', 'lottier-elementor' ) . esc_html( LottierElementor::$version ); ?></sup></span>
            </a>
            <button type="submit" name="submit" id="submit"
                    class="mdc-button mdc-button--dense mdc-button--raised">
                <span class="mdc-button__label"><?php echo esc_html__( 'Save changes', 'lottier-elementor' ) ?></span>
            </button>
        </div>
		<?php

	}

	/**
	 * Get plugin settings with default values.
	 *
	 * @access public
	 * @return void
	 **/
	public function get_options() {

		/** General Tab Options. */
		$options = get_option( 'mdp_lottier_elementor_settings' );
		$results = wp_parse_args( $options, SettingsFields::get_instance()->defaults );

		$this->options = $results;

	}

	/**
	 * Main Settings Instance.
	 * Insures that only one instance of Settings exists in memory at any one time.
	 *
	 * @static
	 * @return Settings
	 **/
	public static function get_instance() {

		if ( ! isset( self::$instance ) && ! ( self::$instance instanceof self ) ) {

			self::$instance = new self;

		}

		return self::$instance;
	}

}
