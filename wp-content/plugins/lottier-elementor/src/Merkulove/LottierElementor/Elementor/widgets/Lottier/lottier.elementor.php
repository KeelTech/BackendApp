<?php /** @noinspection PhpUndefinedClassInspection */
/**
 * Lottier for Elementor
 * Lottie animations in just a few clicks without writing a single line of code.
 * Exclusively on https://1.envato.market/lottier-elementor
 *
 * @encoding        UTF-8
 * @version         2.0.0
 * @copyright       (C) 2018 - 2021 Merkulove ( https://merkulov.design/ ). All rights reserved.
 * @license         Envato License https://1.envato.market/KYbje
 * @contributors    Vitaliy Nemirovskiy (nemirovskiyvitaliy@gmail.com), Cherviakov Vlad (vladchervjakov@gmail.com), Dmitry Merkulov (dmitry@merkulov.design)
 * @support         help@merkulov.design
 **/

namespace Merkulove\LottierElementor;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
    header( 'Status: 403 Forbidden' );
    header( 'HTTP/1.1 403 Forbidden' );
    exit;
}

use Exception;
use Elementor\Group_Control_Background;
use Elementor\Group_Control_Text_Shadow;
use Elementor\Group_Control_Typography;
use Elementor\Core\Schemes\Typography;
use Elementor\Core\Schemes\Color;
use Elementor\Utils;
use Elementor\Widget_Base;
use Elementor\Controls_Manager;
use Merkulove\LottierElementor\Unity\Plugin as UnityPlugin;

/** @noinspection PhpUnused */
/**
 * Lottier - Custom Elementor Widget.
 **/
class lottier_elementor extends Widget_Base {

    /**
     * Use this to sort widgets.
     * A smaller value means earlier initialization of the widget.
     * Can take negative values.
     * Default widgets and widgets from 3rd party developers have 0 $mdp_order
     **/
    public $mdp_order = 1;

    /**
     * Widget base constructor.
     * Initializing the widget base class.
     *
     * @access public
     * @throws Exception If arguments are missing when initializing a full widget instance.
     * @param array      $data Widget data. Default is an empty array.
     * @param array|null $args Optional. Widget default arguments. Default is null.
     *
     * @return void
     **/
    public function __construct( $data = [], $args = null ) {

        parent::__construct( $data, $args );

        wp_register_style( 'mdp-lottier-elementor-admin', UnityPlugin::get_url() . 'src/Merkulove/Unity/assets/css/elementor-admin' . UnityPlugin::get_suffix() . '.css', [], UnityPlugin::get_version() );
        wp_register_style( 'mdp-lottier-elementor', UnityPlugin::get_url() . 'css/lottier-elementor' . UnityPlugin::get_suffix() . '.css', [], UnityPlugin::get_version() );
	    wp_register_script( 'lottie-player', UnityPlugin::get_url() . 'js/lottie-player' . UnityPlugin::get_suffix() . '.js', [ 'jquery', 'elementor-frontend' ], UnityPlugin::get_version(), true );

    }

    /**
     * Return a widget name.
     *
     * @return string
     **/
    public function get_name() {

        return 'mdp-lottier-elementor';

    }

    /**
     * Return the widget title that will be displayed as the widget label.
     *
     * @return string
     **/
    public function get_title() {

        return esc_html__( 'Lottier', 'lottier-elementor' );

    }

    /**
     * Set the widget icon.
     *
     * @return string
     */
    public function get_icon() {

        return 'mdp-lottier-elementor-widget-icon';

    }

    /**
     * Set the category of the widget.
     *
     * @return array with category names
     **/
    public function get_categories() {

        return [ 'general' ];

    }

    /**
     * Get widget keywords. Retrieve the list of keywords the widget belongs to.
     *
     * @access public
     *
     * @return array Widget keywords.
     **/
    public function get_keywords() {

        return [ 'Merkulove', 'Lottier', 'Lottie', 'Player', 'Animation', 'Image' ];

    }

    /**
     * Get style dependencies.
     * Retrieve the list of style dependencies the widget requires.
     *
     * @access public
     *
     * @return array Widget styles dependencies.
     **/
    public function get_style_depends() {

        return [ 'mdp-lottier-elementor', 'mdp-lottier-elementor-admin' ];

    }

	/**
	 * Get script dependencies.
	 * Retrieve the list of script dependencies the element requires.
	 *
	 * @access public
     *
	 * @return array Element scripts dependencies.
	 **/
	public function get_script_depends() {

		return [ 'lottie-player' ];

    }

    /**
     * Style tab - Animation section
     */
    private function style_animation() {

        /** Animation content style. */
        $this->start_controls_section(
            'style_content',
            [
                'label' => esc_html__( 'Animation', 'lottier-elementor' ),
                'tab' => Controls_Manager::TAB_STYLE,
            ] );

        /** Margin. */
        $this->add_responsive_control(
            'lottier_svg_margin',
            [
                'label' => esc_html__( 'Margin', 'lottier-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px', '%', 'em' ],
                'devices' => [ 'desktop', 'tablet', 'mobile' ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-svg' => 'margin: {{top}}{{unit}} {{right}}{{unit}} {{bottom}}{{unit}} {{left}}{{unit}};',
                ],
                'toggle' => true,
            ]
        );

        /** Padding. */
        $this->add_responsive_control(
            'lottier_svg_padding',
            [
                'label' => esc_html__( 'Padding', 'lottier-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px', '%', 'em' ],
                'devices' => [ 'desktop', 'tablet', 'mobile' ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-svg' => 'padding: {{top}}{{unit}} {{right}}{{unit}} {{bottom}}{{unit}} {{left}}{{unit}};',
                ],
                'toggle' => true,
            ]
        );

        /** Width. */
        $this->add_responsive_control(
            'lottier_width_svg',
            [
                'label' => esc_html__( 'Width', 'lottier-elementor' ),
                'type'  => Controls_Manager::SLIDER,
                'size_units' => [ 'px', '%' ],
                'default' => [
                    'unit' => '%',
                    'size' => 100,
                ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-svg > div' => 'width: {{SIZE}}{{UNIT}};',
                ],
            ]
        );

        /** Height. */
        $this->add_responsive_control(
            'lottier_height_svg',
            [
                'label' => esc_html__( 'Height', 'lottier-elementor' ),
                'type'  => Controls_Manager::SLIDER,
                'size_units' => [ 'px', 'vh' ],
                'range' => [
                    'px' => [
                        'min' => 0,
                        'max' => 1000,
                        'step' => 1,
                    ],
                ],
                'default' => [
                    'unit' => 'px',
                    'size' => 500,
                ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-svg > div' => 'height: {{SIZE}}{{UNIT}};',
                    '{{WRAPPER}} .mdp-lottier-animation' => 'height: {{SIZE}}{{UNIT}};',
                ],
                'condition' => [ 'lottier_height_custom' => 'yes' ]
            ]
        );

        /** Custom height. */
        $this->add_control(
            'lottier_height_custom',
            [
                'label' => esc_html__( 'Custom height', 'lottier-elementor' ),
                'type' => Controls_Manager::SWITCHER,
                'label_on' => esc_html__( 'On', 'lottier-elementor' ),
                'label_off' => esc_html__( 'Off', 'lottier-elementor' ),
                'return_value' => 'yes',
                'default' => '',
                'separator' => 'after'
            ]
        );

        /** Background. */
        $this->add_group_control(
            Group_Control_Background::get_type(),
            [
                'name' => 'lottier_background',
                'label' => esc_html__( 'Background', 'lottier-elementor' ),
                'types' => [ 'classic', 'gradient' ],
                'selector' => '{{WRAPPER}} .mdp-lottier-animation',
            ]
        );

        /** Alignment. */
        $this->add_responsive_control(
            'lottier_align',
            [
                'label' => esc_html__( 'Alignment', 'lottier-elementor' ),
                'type' => Controls_Manager::CHOOSE,
                'options' => [
                    'flex-start' => [
                        'title' => esc_html__( 'Left', 'lottier-elementor' ),
                        'icon' => 'fa fa-align-left',
                    ],
                    'space-around' => [
                        'title' => esc_html__( 'Center', 'lottier-elementor' ),
                        'icon' => 'fa fa-align-center',
                    ],
                    'flex-end' => [
                        'title' => esc_html__( 'Right', 'lottier-elementor' ),
                        'icon' => 'fa fa-align-right',
                    ],
                ],
                'default' => 'space-around',
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-svg' => 'justify-content: {{lottier_align}};',
                ],
                'toggle' => true,
            ]
        );

        /** End animation content style. */
        $this->end_controls_section();

    }

    /**
     * Add the widget controls.
     *
     * @since 1.0.0
     * @access protected
     *
     * @return void with category names
     **/
    protected function _register_controls() {

        /** Start section properties. */
        $this->start_controls_section(
            'content_properties',
            [
                'label' => esc_html__( 'Properties', 'lottier-elementor' ),
                'tab' => Controls_Manager::TAB_CONTENT,
            ]
        );

        /** Animation speed. */
        $this->add_control(
            'animation_speed',
            [
                'label' => esc_html__( 'Animation speed', 'lottier-elementor' ),
                'type'  => Controls_Manager::SLIDER,
                'range' => [
                    'px' => [
                        'min' => 0.1,
                        'max' => 10,
                        'step' => 0.1,
                    ],
                ],
                'default' => [
                    'unit' => 'px',
                    'size' => 1,
                ],
            ]
        );

        /** Play animation. */
        $this->add_control(
            'play_animation',
            [
                'label' => esc_html__( 'Playback', 'lottier-elementor' ),
                'type' => Controls_Manager::SELECT,
                'default' => 'autoplay',
                'options' => [
                    'autoplay' => esc_html__( 'Auto play', 'lottier-elementor' ),
                    'hover'    => esc_html__( 'SVG hover', 'lottier-elementor' ),
                    'section'  => esc_html__( 'Section hover', 'lottier-elementor' ),
                    'click'    => esc_html__( 'On click', 'lottier-elementor' ),
                ],
            ]
        );

        /** Play mode. */
        $this->add_control(
            'play_mode',
            [
                'label' => esc_html__( 'Play mode', 'lottier-elementor' ),
                'type' => Controls_Manager::SELECT,
                'default' => 'normal',
                'options' => [
                    'normal'  => esc_html__( 'Normal', 'lottier-elementor' ),
                    'bounce' => esc_html__( 'Bounce', 'lottier-elementor' ),
                ],
                'condition' => ['animation_loop' => 'yes']
            ]
        );

        /** Loop Animation. */
        $this->add_control(
            'animation_loop',
            [
                'label' => esc_html__( 'Loop', 'lottier-elementor' ),
                'type' => Controls_Manager::SWITCHER,
                'label_on' => esc_html__( 'On', 'lottier-elementor' ),
                'label_off' => esc_html__( 'Off', 'lottier-elementor' ),
                'return_value' => 'yes',
                'default' => 'yes',
            ]
        );

        /** Show controls. */
        $this->add_control(
            'show_controls',
            [
                'label' => esc_html__( 'Controls', 'lottier-elementor' ),
                'type' => Controls_Manager::SWITCHER,
                'label_on' => esc_html__( 'Show', 'lottier-elementor' ),
                'label_off' => esc_html__( 'Hide', 'lottier-elementor' ),
                'return_value' => 'yes',
            ]
        );

        /** Show header. */
        $this->add_control(
            'show_header',
            [
                'label' => esc_html__( 'Header', 'lottier-elementor' ),
                'type' => Controls_Manager::SWITCHER,
                'label_on' => esc_html__( 'Show', 'lottier-elementor' ),
                'label_off' => esc_html__( 'Hide', 'lottier-elementor' ),
                'return_value' => 'yes',
                'default' => '',
            ]
        );

        /** Show description. */
        $this->add_control(
            'show_description',
            [
                'label' => esc_html__( 'Description', 'lottier-elementor' ),
                'type' => Controls_Manager::SWITCHER,
                'label_on' => esc_html__( 'Show', 'lottier-elementor' ),
                'label_off' => esc_html__( 'Hide', 'lottier-elementor' ),
                'return_value' => 'yes',
                'default' => '',
            ]
        );

        /** Enable link. */
        $this->add_control(
            'show_link',
            [
                'label' => esc_html__( 'Enable link', 'lottier-elementor' ),
                'type' => Controls_Manager::SWITCHER,
                'label_on' => esc_html__( 'Show', 'lottier-elementor' ),
                'label_off' => esc_html__( 'Hide', 'lottier-elementor' ),
                'return_value' => 'yes',
            ]
        );

        /** End section properties. */
        $this->end_controls_section();

        /** Start section header. */
        $this->start_controls_section(
            'content_header',
            [
                'label' => esc_html__( 'Header', 'lottier-elementor' ),
                'tab' => Controls_Manager::TAB_CONTENT,
                'condition' => [ 'show_header' => 'yes' ],
            ]
        );

        /** Header. */
        $this->add_control(
            'lottier_header',
            [
                'label' => esc_html__( 'Header', 'lottier-elementor' ),
                'type' => Controls_Manager::TEXT,
                'default' => esc_html__( 'Header', 'lottier-elementor' ),
                'placeholder' => esc_html__( 'Header', 'lottier-elementor' ),
            ]
        );

        /** HTML Tag. */
        $this->add_control(
            'lottier_tag',
            [
                'label' => esc_html__( 'HTML Tag', 'lottier-elementor' ),
                'type' => Controls_Manager::SELECT,
                'options' => [
                    'h1' => 'H1',
                    'h2' => 'H2',
                    'h3' => 'H3',
                    'h4' => 'H4',
                    'h5' => 'H5',
                    'h6' => 'H6',
                    'div' => 'div',
                    'span' => 'span',
                    'p' => 'p',
                ],
                'default' => 'h2',
            ]
        );

        /** Show Subheader. */
        $this->add_control(
            'show_subheader',
            [
                'label' => esc_html__( 'Show Subheader', 'lottier-elementor' ),
                'type' => Controls_Manager::SWITCHER,
                'label_on' => esc_html__( 'Show', 'lottier-elementor' ),
                'label_off' => esc_html__( 'Hide', 'lottier-elementor' ),
                'return_value' => 'yes',
            ]
        );

        /** Subheader Position. */
        $this->add_control(
            'subheader_position',
            [
                'label' => esc_html__( 'Subheader Position', 'lottier-elementor' ),
                'type' => Controls_Manager::SELECT,
                'options' => [
                    'top' => 'Top',
                    'bottom' => 'Bottom',
                ],
                'default' => 'bottom',
                'condition'   => ['show_subheader' => 'yes']
            ]
        );

        /** Subheader. */
        $this->add_control(
            'lottier_sub_name',
            [
                'label' => esc_html__( 'Subheader', 'lottier-elementor' ),
                'type' => Controls_Manager::TEXT,
                'default' => esc_html__( 'Subheader', 'lottier-elementor' ),
                'placeholder' => esc_html__( 'Subheader', 'lottier-elementor' ),
                'condition'   => ['show_subheader' => 'yes']
            ]
        );

        /** End section header. */
        $this->end_controls_section();

        /** Start section description. */
        $this->start_controls_section(
            'content_description',
            [
                'label' => esc_html__( 'Description', 'lottier-elementor' ),
                'tab' => Controls_Manager::TAB_CONTENT,
                'condition' => [ 'show_description' => 'yes' ],
            ]
        );

        /** Description Position. */
        $this->add_control(
            'description_position',
            [
                'label' => esc_html__( 'Description Position', 'lottier-elementor' ),
                'type' => Controls_Manager::SELECT,
                'options' => [
                    'header' => esc_html__( 'After header', 'lottier-elementor' ),
                    'footer' => esc_html__( 'Footer','lottier-elementor' )
                ],
                'default' => 'footer',
            ]
        );

        /** HTML Tag. */
        $this->add_control(
            'description_tag',
            [
                'label' => esc_html__( 'HTML Tag', 'lottier-elementor' ),
                'type' => Controls_Manager::SELECT,
                'options' => [
                    'div' => 'div',
                    'span' => 'span',
                    'p' => 'p',
                ],
                'default' => 'p',
            ]
        );

        /** Description. */
        $this->add_control(
            'lottier_description',
            [
                'label' => esc_html__( 'Description', 'lottier-elementor' ),
                'type' => Controls_Manager::TEXTAREA,
                'rows' => 10,
                'default' => esc_html__( 'Description', 'lottier-elementor' ),
                'placeholder' => esc_html__( 'Description', 'lottier-elementor' ),
            ]
        );

        /** End section description. */
        $this->end_controls_section();

        /** Start section link. */
        $this->start_controls_section(
            'content_link',
            [
                'label' => esc_html__( 'Link', 'lottier-elementor' ),
                'tab' => Controls_Manager::TAB_CONTENT,
                'condition' => [ 'show_link' => 'yes' ],
            ]
        );

        /** Link Position. */
        $this->add_control(
            'link_position',
            [
                'label' => esc_html__( 'Link Position', 'lottier-elementor' ),
                'type' => Controls_Manager::SELECT,
                'options' => [
                    'svg' => esc_html__( 'SVG', 'lottier-elementor' ),
                    'box' => esc_html__( 'Box', 'lottier-elementor' ),
                ],
                'default' => 'svg'
            ]
        );

        /** URL link. */
        $this->add_control(
            'lottier_url',
            [
                'label' => esc_html__( 'URL', 'lottier-elementor' ),
                'type' => Controls_Manager::URL,
                'placeholder' => esc_html__( 'https://codecanyon.net/user/merkulove', 'lottier-elementor' ),
            ]
        );

        /** End section link. */
        $this->end_controls_section();

        /** Start section animation content. */
        $this->start_controls_section(
            'content_section',
            [
                'label' => esc_html__( 'Animation content', 'lottier-elementor' ),
                'tab' => Controls_Manager::TAB_CONTENT,
            ]
        );

        /** Data type. */
        $this->add_control(
            'data_type',
            [
                'label' => esc_html__( 'Source', 'lottier-elementor' ),
                'type' => Controls_Manager::SELECT,
                'default' => 'url',
                'options' => [
                    'media' => esc_html__( 'Media library', 'lottier-elementor' ),
                    'url'  => esc_html__( 'URL', 'lottier-elementor' ),
                    'json' => esc_html__( 'JSON', 'lottier-elementor' ),
                ],
                'description' => esc_html__( 'Choose animation on ', 'lottier-elementor' ).
                    '<a href="https://lottiefiles.com/" target="_blank">(lottiefiles.com)</a>' .
                    esc_html__( ' and import it as JSON or URL.', 'lottier-elementor' )
            ]
        );

        /** URL. */
        $this->add_control(
            'data_type_url',
            [
                'label' => esc_html__( 'URL', 'lottier-elementor' ),
                'type' => Controls_Manager::URL,
                'placeholder' => esc_html__( 'https://lottiefiles.com/...', 'lottier-elementor' ),
                'default' => [
                    'url' => 'https://assets3.lottiefiles.com/datafiles/3DjbupK8MPRIC89/data.json',
                    'is_external' => false,
                    'nofollow' => false,
                ],
                'condition' => [ 'data_type' => 'url' ],
            ]
        );

        /** JSON. */
        $this->add_control(
            'data_type_json',
            [
                'label' => esc_html__( 'JSON', 'lottier-elementor' ),
                'type' => Controls_Manager::CODE,
                'language' => 'json',
                'rows' => 10,
                'condition' => [ 'data_type' => 'json' ],
            ]
        );

        /** MEDIA  */
        $this->add_control(
            'data_type_media',
            [
                'label' => __( 'Choose Image', 'lottier-elementor' ),
                'type' => Controls_Manager::MEDIA,
                'default' => [
                    'url' => Utils::get_placeholder_image_src(),
                ],
                'condition' => [ 'data_type' => 'media' ],
            ]
        );

        /** End section content. */
        $this->end_controls_section();

        /** Header style. */
        $this->start_controls_section( 'style_header',
            [
                'label' => esc_html__( 'Header', 'lottier-elementor' ),
                'tab' => Controls_Manager::TAB_STYLE,
                'condition' => [ 'show_header' => 'yes' ],
            ] );

        /** Margin. */
        $this->add_responsive_control(
            'lottier_margin_header',
            [
                'label' => esc_html__( 'Margin', 'lottier-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px', '%', 'em' ],
                'devices' => [ 'desktop', 'tablet', 'mobile' ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-heading' => 'margin: {{top}}{{unit}} {{right}}{{unit}} {{bottom}}{{unit}} {{left}}{{unit}};',
                ],
                'toggle' => true,
            ]
        );

        /** Padding. */
        $this->add_responsive_control(
            'lottier_padding_header',
            [
                'label' => esc_html__( 'Padding', 'lottier-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px', '%', 'em' ],
                'devices' => [ 'desktop', 'tablet', 'mobile' ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-heading' => 'padding: {{top}}{{unit}} {{right}}{{unit}} {{bottom}}{{unit}} {{left}}{{unit}};',
                ],
                'toggle' => true,
            ]
        );

        /** Color. */
        /** @noinspection PhpUndefinedClassInspection */
        $this->add_control(
            'color_header',
            [
                'label' => esc_html__( 'Color', 'lottier-elementor' ),
                'type' => Controls_Manager::COLOR,
                'scheme' => [
                    'type' => Color::get_type(),
                    'value' => Color::COLOR_3,
                ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-header' => 'color: {{VALUE}}',
                ],
            ]
        );

        /** Typography. */
        /** @noinspection PhpUndefinedClassInspection */
        $this->add_group_control(
            Group_Control_Typography::get_type(),
            [
                'name' => 'header_typography',
                'label' => esc_html__( 'Typography', 'lottier-elementor' ),
                'scheme' => Typography::TYPOGRAPHY_1,
                'selector' => '{{WRAPPER}} .mdp-lottier-header',
            ]
        );

        /** Shadow. */
        $this->add_group_control(
            Group_Control_Text_Shadow::get_type(),
            [
                'name' => 'header_shadow',
                'label' => esc_html__( 'Shadow', 'lottier-elementor' ),
                'selector' => '{{WRAPPER}} .mdp-lottier-header',
            ]
        );

        /** Background */
        $this->add_group_control(
            Group_Control_Background::get_type(),
            [
                'name' => 'header_background',
                'label' => esc_html__( 'Background', 'lottier-elementor' ),
                'types' => [ 'classic', 'gradient' ],
                'selector' => '{{WRAPPER}} .mdp-lottier-heading',
            ]
        );

        /** Alignment. */
        $this->add_responsive_control(
            'header_align',
            [
                'label' => esc_html__( 'Alignment', 'lottier-elementor' ),
                'type' => Controls_Manager::CHOOSE,
                'options' => [
                    'left' => [
                        'title' => esc_html__( 'Left', 'lottier-elementor' ),
                        'icon' => 'fa fa-align-left',
                    ],
                    'center' => [
                        'title' => esc_html__( 'Center', 'lottier-elementor' ),
                        'icon' => 'fa fa-align-center',
                    ],
                    'right' => [
                        'title' => esc_html__( 'Right', 'lottier-elementor' ),
                        'icon' => 'fa fa-align-right',
                    ],
                ],
                'default' => 'center',
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-heading' => 'text-align: {{header_align}};',
                ],
                'toggle' => true,
            ]
        );

        /** Subheader. */
        $this->add_control(
            'text_animation_header',
            [
                'label' => esc_html__( 'Subheader', 'lottier-elementor' ),
                'type' => Controls_Manager::HEADING,
                'separator' => 'before',
                'condition'   => ['show_subheader' => 'yes']
            ]
        );

        /** Margin. */
        $this->add_responsive_control(
            'lottier_margin_subheader',
            [
                'label' => esc_html__( 'Margin', 'lottier-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px', '%', 'em' ],
                'devices' => [ 'desktop', 'tablet', 'mobile' ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-subheader' => 'margin: {{top}}{{unit}} {{right}}{{unit}} {{bottom}}{{unit}} {{left}}{{unit}};',
                ],
                'toggle' => true,
                'condition'   => ['show_subheader' => 'yes']
            ]
        );

        /** Padding. */
        $this->add_responsive_control(
            'lottier_padding_subheader',
            [
                'label' => esc_html__( 'Padding', 'lottier-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px', '%', 'em' ],
                'devices' => [ 'desktop', 'tablet', 'mobile' ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-subheader' => 'padding: {{top}}{{unit}} {{right}}{{unit}} {{bottom}}{{unit}} {{left}}{{unit}};',
                ],
                'toggle' => true,
                'condition'   => ['show_subheader' => 'yes']
            ]
        );

        /** Color. */
        /** @noinspection PhpUndefinedClassInspection */
        $this->add_control(
            'color_subheader',
            [
                'label' => esc_html__( 'Color', 'lottier-elementor' ),
                'type' => Controls_Manager::COLOR,
                'scheme' => [
                    'type' => Color::get_type(),
                    'value' => Color::COLOR_3,
                ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-subheader' => 'color: {{VALUE}}',
                ],
                'condition'   => ['show_subheader' => 'yes']
            ]
        );

        /** Typography. */
        /** @noinspection PhpUndefinedClassInspection */
        $this->add_group_control(
            Group_Control_Typography::get_type(),
            [
                'name' => 'subheader_typography',
                'label' => esc_html__( 'Typography', 'lottier-elementor' ),
                'scheme' => Typography::TYPOGRAPHY_1,
                'selector' => '{{WRAPPER}} .mdp-lottier-subheader',
                'condition'   => ['show_subheader' => 'yes']
            ]
        );

        /** Shadow. */
        $this->add_group_control(
            Group_Control_Text_Shadow::get_type(),
            [
                'name' => 'subheader_shadow',
                'label' => esc_html__( 'Shadow', 'lottier-elementor' ),
                'selector' => '{{WRAPPER}} .mdp-lottier-subheader',
                'condition'   => ['show_subheader' => 'yes']
            ]
        );

        /** End header style. */
        $this->end_controls_section();

        /** Description style. */
        $this->start_controls_section( 'style_description',
            [
                'label' => esc_html__( 'Description', 'lottier-elementor' ),
                'tab' => Controls_Manager::TAB_STYLE,
                'condition' => [ 'show_description' => 'yes' ],
            ] );

        /** Margin. */
        $this->add_responsive_control(
            'lottier_margin_description',
            [
                'label' => esc_html__( 'Margin', 'lottier-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px', '%', 'em' ],
                'devices' => [ 'desktop', 'tablet', 'mobile' ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-description' => 'margin: {{top}}{{unit}} {{right}}{{unit}} {{bottom}}{{unit}} {{left}}{{unit}};',
                ],
                'toggle' => true,
            ]
        );

        /** Padding. */
        $this->add_responsive_control(
            'lottier_padding_description',
            [
                'label' => esc_html__( 'Padding', 'lottier-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px', '%', 'em' ],
                'devices' => [ 'desktop', 'tablet', 'mobile' ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-description' => 'padding: {{top}}{{unit}} {{right}}{{unit}} {{bottom}}{{unit}} {{left}}{{unit}};',
                ],
                'toggle' => true,
            ]
        );

        /** Color. */
        /** @noinspection PhpUndefinedClassInspection */
        $this->add_control(
            'color_description',
            [
                'label' => esc_html__( 'Color', 'lottier-elementor' ),
                'type' => Controls_Manager::COLOR,
                'scheme' => [
                    'type' => Color::get_type(),
                    'value' => Color::COLOR_3,
                ],
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-description' => 'color: {{VALUE}}',
                ],
            ]
        );

        /** Typography. */
        /** @noinspection PhpUndefinedClassInspection */
        $this->add_group_control(
            Group_Control_Typography::get_type(),
            [
                'name' => 'description_typography',
                'label' => esc_html__( 'Typography', 'lottier-elementor' ),
                'scheme' => Typography::TYPOGRAPHY_1,
                'selector' => '{{WRAPPER}} .mdp-lottier-description',
            ]
        );

        /** Shadow. */
        $this->add_group_control(
            Group_Control_Text_Shadow::get_type(),
            [
                'name' => 'description_shadow',
                'label' => esc_html__( 'Shadow', 'lottier-elementor' ),
                'selector' => '{{WRAPPER}} .mdp-lottier-description',
            ]
        );

        /** Background */
        $this->add_group_control(
            Group_Control_Background::get_type(),
            [
                'name' => 'description_background',
                'label' => esc_html__( 'Background', 'lottier-elementor' ),
                'types' => [ 'classic', 'gradient' ],
                'selector' => '{{WRAPPER}} .mdp-lottier-description',
            ]
        );

        /** Alignment. */
        $this->add_responsive_control(
            'description_align',
            [
                'label' => esc_html__( 'Alignment', 'lottier-elementor' ),
                'type' => Controls_Manager::CHOOSE,
                'options' => [
                    'left' => [
                        'title' => esc_html__( 'Left', 'lottier-elementor' ),
                        'icon' => 'fa fa-align-left',
                    ],
                    'center' => [
                        'title' => esc_html__( 'Center', 'lottier-elementor' ),
                        'icon' => 'fa fa-align-center',
                    ],
                    'right' => [
                        'title' => esc_html__( 'Right', 'lottier-elementor' ),
                        'icon' => 'fa fa-align-right',
                    ],
                    'justify' => [
                        'title' => esc_html__( 'Justify', 'lottier-elementor' ),
                        'icon' => 'fa fa-align-justify',
                    ],
                ],
                'default' => 'center',
                'selectors' => [
                    '{{WRAPPER}} .mdp-lottier-description' => 'text-align: {{header_align}};',
                ],
                'toggle' => true,
            ]
        );

        /** End description style. */
        $this->end_controls_section();

        /** Style Tab - Animation Section */
        $this->style_animation();

    }

    /**
     * Render Frontend Output. Generate the final HTML on the frontend.
     *
     * @since 1.0.0
     * @access protected
     **/
    protected function render() {

        /** We get all the values from the admin panel. */
        $settings = $this->get_settings_for_display();

        /** Section id. */
        $idSection = $this->get_id();

        /** We save the data into a variable depending on the selected data type. */
        $src = '';
        if ( $settings['data_type'] === 'media' ){
            $src = $settings['data_type_media']['url'];
        }
        if( $settings['data_type'] === 'url' ){
            $src = $settings['data_type_url']['url'];
        }
        if ( $settings['data_type'] === 'json' ){
            $src = $settings['data_type_json'];
        }

        /** Sub Header. */
        $this->add_render_attribute(
            [
                'lottier_sub_name' => [
                    'class' => [ 'mdp-lottier-subheader' ]
                ],
            ]
        );

        /** Header */
        $this->add_render_attribute(
            [
                'lottier_header' => [
                    'class' => [ 'mdp-lottier-header' ]
                ],
            ]
        );

        /** Description. */
        $this->add_render_attribute(
            [
                'lottier_description' => [
                    'class' => [ 'mdp-lottier-description' ]
                ],
            ]
        );

        echo '<div id="mdp-lottier-box-' . esc_attr($idSection) . '">';

        if( $settings['show_header'] === 'yes' ){

            echo '<' . esc_attr( $settings['lottier_tag'] ) . ' class="mdp-lottier-heading">';

            /** Display the subheader above the title. */
            if( $settings['show_subheader'] === 'yes' and $settings['subheader_position'] === 'top' ){
                $this->add_inline_editing_attributes( 'lottier_sub_name', 'basic' );
                echo '<span ' . $this->get_render_attribute_string( 'lottier_sub_name' ) . '>' . wp_kses_post( $settings['lottier_sub_name'] ). '</span>';
            }

            /** Display the header. */
            $this->add_inline_editing_attributes( 'lottier_header', 'basic' );
            echo '<span ' . $this->get_render_attribute_string( 'lottier_header' ) . '>' . wp_kses_post( $settings['lottier_header'] ) . '</span>';

            /** Display the subheader. */
            if($settings['show_subheader'] === 'yes' and $settings['subheader_position'] === 'bottom' ){
                $this->add_inline_editing_attributes( 'lottier_sub_name', 'basic' );
                echo '<span ' . $this->get_render_attribute_string( 'lottier_sub_name' ) . ' >' . wp_kses_post( $settings['lottier_sub_name'] ) . '</span>';
            }

            echo '</' . esc_attr( $settings['lottier_tag'] ) . '>';

        }

        /** We display a brief description if you want to display it after the title. */
        if ( $settings['description_position'] === 'header' and $settings['show_description'] === 'yes' ) {
            $this->add_inline_editing_attributes( 'lottier_description', 'basic' );
            echo '<' . esc_attr( $settings['description_tag'] ) . ' ' . $this->get_render_attribute_string( 'lottier_description' ) . ' >' . wp_kses_post( $settings['lottier_description'] ) . '</' . esc_attr( $settings['description_tag'] ) . '>';
        }

        $target = isset($settings['lottier_url']['is_external']) ? ' target="_blank"' : '';
        $nofollow = isset($settings['lottier_url']['nofollow']) ? ' rel="nofollow"' : '';
        ?>

        <?php if( $settings['show_link'] === 'yes' and $settings['link_position'] === 'svg' ): ?>
        <a href="<?php echo esc_attr($settings['lottier_url']['url']); ?>" <?php echo esc_attr( $target ) .' '. esc_attr($nofollow);  ?>>
            <?php endif; ?>
            <div class="mdp-lottier-svg">
                <div class="mdp-lottier-player">
                    <!--suppress HtmlUnknownTag -->
                    <lottie-player id="mdp-lottier-<?php echo esc_attr($idSection); ?>" class="mdp-lottier-animation" src='<?php echo esc_attr($src); ?>'></lottie-player>
                </div>
            </div>
            <?php if( $settings['show_link'] === 'yes' and $settings['link_position'] === 'svg' ): ?>
        </a>
    <?php endif; ?>

        <?php
        /** We display a short description if you want to display it at the end of the section. */
        if ( $settings['description_position'] === 'footer' and $settings['show_description'] === 'yes' ) {
            $this->add_inline_editing_attributes( 'lottier_description', 'basic' );
            echo '<' . esc_attr( $settings['description_tag'] ) . ' ' . $this->get_render_attribute_string( 'lottier_description' ) . '>' . wp_kses_post( $settings['lottier_description'] ) . '</' . esc_attr( $settings['description_tag'] ) . '>';
        }
        ?>

        <?php if( $settings['show_link'] === 'yes' and $settings['link_position'] === 'box' ): ?>
            <a href="<?php echo esc_attr( $settings['lottier_url']['url'] ); ?>" class="mdp-link-max" <?php echo esc_attr( $target ) .' '. esc_attr( $nofollow );  ?> ></a>
        <?php endif; ?>

        </div>

        <script>
            var player_<?php echo esc_attr($idSection); ?> = document.querySelector("#mdp-lottier-<?php echo esc_attr($idSection); ?>");

            player_<?php echo esc_attr($idSection); ?>.background = 'transporant';
            <?php
            echo $settings['play_animation'] === 'autoplay' ? 'player_'.esc_attr($idSection).'.autoplay = true;' : '';
            echo ( $settings['play_animation'] === 'hover' or $settings['play_animation'] === 'section' ) ? 'player_'.esc_attr($idSection).'.hover = true;' : '';
            ?>
            player_<?php echo esc_attr($idSection); ?>.mode = '<?php echo esc_attr( $settings['play_mode'] ); ?>';
            player_<?php echo esc_attr($idSection); ?>.controls = <?php echo $settings['show_controls'] === 'yes' ? 'true' : 'false'; ?>;
            player_<?php echo esc_attr($idSection); ?>.loop = <?php echo $settings['animation_loop'] === 'yes' ? 'true' : 'false'; ?>;
            player_<?php echo esc_attr($idSection); ?>.speed = <?php echo esc_attr( $settings['animation_speed']['size'] ); ?>;

            <?php if( $settings['play_animation'] === 'section' ): ?>
            var boxLink_<?php echo esc_attr($idSection); ?> = document.querySelector("#mdp-lottier-box-<?php echo esc_attr($idSection); ?>");

            boxLink_<?php echo esc_attr($idSection); ?>.addEventListener("mouseover", function () {
                player_<?php echo esc_attr($idSection); ?>.play();
            });

            boxLink_<?php echo esc_attr($idSection); ?>.addEventListener("mouseout", function () {
                player_<?php echo esc_attr($idSection); ?>.pause();
            });

            <?php endif; ?>

            <?php if( $settings['play_animation'] === 'click' ): ?>
            var startPlay = 0;

            player_<?php echo esc_attr($idSection); ?>.addEventListener("click", function () {
                if (startPlay === 0) {
                    player_<?php echo esc_attr($idSection); ?>.play();
                    startPlay = 1;
                } else {
                    player_<?php echo esc_attr($idSection); ?>.pause();
                    startPlay = 0;
                }
            });

            <?php endif; ?>

        </script>

        <?php
    }

    /**
     * Return link for documentation.
     *
     * Used to add stuff after widget.
     *
     * @since 1.0.0
     * @access public
     **/
    public function get_custom_help_url() {
        return 'https://docs.merkulov.design/category/lottier-elementor/';
    }

}