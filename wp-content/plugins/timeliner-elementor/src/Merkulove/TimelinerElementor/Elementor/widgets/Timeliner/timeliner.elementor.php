<?php /** @noinspection PhpUndefinedClassInspection */
/**
 * Timeliner for Elementor
 * Beautiful graphical representation of a period of time for Elementor
 * Exclusively on https://1.envato.market/timeliner-elementor
 *
 * @encoding        UTF-8
 * @version         1.0.0
 * @copyright       (C) 2018 - 2021 Merkulove ( https://merkulov.design/ ). All rights reserved.
 * @license         Envato License https://1.envato.market/KYbje
 * @contributors    Nemirovskiy Vitaliy (nemirovskiyvitaliy@gmail.com)
 * @support         help@merkulov.design
 **/

namespace Merkulove\TimelinerElementor;

/** Exit if accessed directly. */
if ( ! defined( 'ABSPATH' ) ) {
    header( 'Status: 403 Forbidden' );
    header( 'HTTP/1.1 403 Forbidden' );
    exit;
}

use Exception;
use Elementor\Plugin;
use Elementor\Widget_Base;
use Elementor\Controls_Manager;
use Elementor\Repeater;
use Elementor\Utils;
use Elementor\Group_Control_Background;
use Elementor\Group_Control_Text_Shadow;
use Elementor\Group_Control_Typography;
use Elementor\Core\Schemes\Typography;
use Elementor\Core\Schemes\Color;
use Elementor\Controls_Stack;
use Elementor\Group_Control_Border;
use Elementor\Group_Control_Box_Shadow;
use Elementor\Group_Control_Css_Filter;
use Merkulove\TimelinerElementor\Unity\Plugin as UnityPlugin;
use Merkulove\TimelinerElementor\Unity\ElementorControls;

/** @noinspection PhpUnused */
/**
 * Timeliner - Custom Elementor Widget.
 **/
class timeliner_elementor extends Widget_Base {

    /**
     * Use this to sort widgets.
     * A smaller value means earlier initialization of the widget.
     * Can take negative values.
     * Default widgets and widgets from 3rd party developers have 0 $mdp_order
     **/
    public $mdp_order = 1;

    /**
     * Stores a unique identifier for the extension.
     */
    private static $addonID;

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

        wp_register_style( 'mdp-timeliner-elementor-admin', UnityPlugin::get_url() . 'src/Merkulove/Unity/assets/css/elementor-admin' . UnityPlugin::get_suffix() . '.css', [], UnityPlugin::get_version() );

        wp_register_style( 'timeline', UnityPlugin::get_url() . 'css/timeline.min' .  '.css', [], UnityPlugin::get_version() );

        wp_register_style( 'timeliner-elementor', UnityPlugin::get_url() . 'css/timeliner-elementor' . UnityPlugin::get_suffix() . '.css', [], UnityPlugin::get_version() );

        wp_register_script( 'timeline', UnityPlugin::get_url() . 'js/timeline' . UnityPlugin::get_suffix() . '.js', [ 'jquery', 'elementor-frontend' ], UnityPlugin::get_version(), true);

    }

    /**
     * Return a widget name.
     *
     * @return string
     **/
    public function get_name() {

        return 'mdp-timeliner-elementor';

    }

    /**
     * Return the widget title that will be displayed as the widget label.
     *
     * @return string
     **/
    public function get_title() {

        return esc_html__( 'Timeliner', 'timeliner-elementor' );

    }

    /**
     * Set the widget icon.
     *
     * @return string
     */
    public function get_icon() {

        return 'mdp-timeliner-elementor-widget-icon';

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

        return [ 'Merkulove', 'Timeliner', 'time', 'line', 'process', 'period' ];

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

        return [ 'timeline', 'timeliner-elementor', 'mdp-timeliner-elementor-admin' ];

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

		return [ 'timeline' ];

    }

    /**
     * Group controllers for setting styles.
     *
     * @param $name_Section - The name of the styles section.
     * @param string $css_class - Specifies one or more class names for an element.
     * @param array $condition - Interconnected controllers.
     * @param array $display - Determines which controllers to display. {
     *      @type $key 'margin'                 => (boolean) - Use margin.
     *      @type $key 'padding'                => (boolean) - Use padding.
     *      @type $key 'color'                  => (boolean) - Use color.
     *      @type $key 'typography'             => (boolean) - Use typography.
     *      @type $key 'text-shadow'            => (boolean) - Use text shadow.
     *      @type $key 'alignment'              => (boolean) - Use alignment.
     *      @type $key 'alignment-justify'      => (boolean) - Use alignment justify.
     *      @type $key 'alignment-horizontal'   => (boolean) - Use alignment horizontal.
     *      @type $key 'alignment-vertical'     => (boolean) - Use alignment vertical.
     *      @type $key 'background'             => (boolean) - Use background.
     *      @type $key 'border'                 => (boolean) - Use border.
     *      @type $key 'border-radius'          => (boolean) - Use border radius.
     *      @type $key 'box-shadow'             => (boolean) - Use box shadow.
     *      @type $key 'css-filter'             => (boolean) - Use css filter.
     *
     * }
     *  @param $separator
     *
     * @since 1.0.0
     * @access public
     *
     * @return void
     */
    public function get_settings_style_group( $name_Section,
                                              $css_class,
                                              $condition = [],
                                              $display = [], $separator = [ 'after', 'before', 'before', 'before'] ) {

        /** Margin. */
        if ( isset($display['margin']) && $display['margin'] === true ) {
            $this->add_responsive_control(
                'timeliner_' . $name_Section . '_margin',
                [
                    'label'      => esc_html__( 'Margin', 'timeliner-elementor' ),
                    'type'       => Controls_Manager::DIMENSIONS,
                    'size_units' => [ 'px', '%', 'em' ],
                    'selectors'  => [
                        '{{WRAPPER}} ' . $css_class => 'margin: {{top}}{{unit}} {{right}}{{unit}} {{bottom}}{{unit}} {{left}}{{unit}};',
                    ],
                    'toggle'     => true,
                    'condition'  => $condition,
                ]
            );
        }

        /** Padding. */
        if ( isset($display['padding']) && $display['padding'] === true ) {
            $this->add_responsive_control(
                'timeliner_' . $name_Section . '_padding',
                [
                    'label'      => esc_html__( 'Padding', 'timeliner-elementor' ),
                    'type'       => Controls_Manager::DIMENSIONS,
                    'size_units' => [ 'px', '%', 'em' ],
                    'selectors'  => [
                        '{{WRAPPER}} ' . $css_class => 'padding: {{top}}{{unit}} {{right}}{{unit}} {{bottom}}{{unit}} {{left}}{{unit}};',
                    ],
                    'toggle'     => true,
                    'separator'  => $separator[0],
                    'condition'  => $condition,
                ]
            );
        }

        /** Text Color. */
        if ( isset($display['color']) && $display['color'] === true ) {
            $this->add_control(
                'timeliner_' . $name_Section . '_text_color',
                [
                    'label'     => esc_html__( 'Color', 'timeliner-elementor' ),
                    'type'      => Controls_Manager::COLOR,
                    'selectors' => [
                        '{{WRAPPER}} ' . $css_class => 'color: {{VALUE}}',
                    ],
                    'condition' => $condition,
                ]
            );
        }

        /** Typography */
        if ( isset($display['typography']) && $display['typography'] === true ) {
            $this->add_group_control(
                Group_Control_Typography::get_type(),
                [
                    'name'      => 'timeliner_' . $name_Section . '_typography',
                    'label'     => esc_html__( 'Typography', 'timeliner-elementor' ),
                    'scheme'    => Typography::TYPOGRAPHY_1,
                    'selector'  => '{{WRAPPER}} ' . $css_class,
                    'condition' => $condition,
                ]
            );
        }

        /** Text Shadow. */
        if ( isset($display['text-shadow']) && $display['text-shadow'] === true ) {
            $this->add_group_control(
                Group_Control_Text_Shadow::get_type(),
                [
                    'name'      => 'timeliner_' . $name_Section . '_text_shadow',
                    'label'     => esc_html__( 'Text Shadow', 'timeliner-elementor' ),
                    'selector'  => '{{WRAPPER}} ' . $css_class,
                    'condition' => $condition,
                ]
            );
        }

        /** Alignment horizontal. */
        if ( isset($display['alignment-horizontal']) && $display['alignment-horizontal'] === true ) {
            $this->add_responsive_control(
                'timeliner_' . $name_Section . '_horizontal_align',
                [
                    'label'     => esc_html__( 'Horizontal Position', 'timeliner-elementor' ),
                    'type'      => Controls_Manager::CHOOSE,
                    'options'   => [
                        'flex-start'    => [
                            'title' => esc_html__( 'Left', 'timeliner-elementor' ),
                            'icon'  => 'eicon-h-align-left',
                        ],
                        'center'  => [
                            'title' => esc_html__( 'Center', 'timeliner-elementor' ),
                            'icon'  => 'eicon-h-align-center',
                        ],
                        'flex-end'   => [
                            'title' => esc_html__( 'Right', 'timeliner-elementor' ),
                            'icon'  => 'eicon-h-align-right',
                        ],
                    ],
                    'default'   => '',
                    'selectors' => [
                        '{{WRAPPER}} ' . $css_class => 'justify-content: {{header_align}};',
                        '{{WRAPPER}} .mdp-timeliner-box-content' => 'width: 65%;',
                    ],
                    'toggle'    => true,
                    'condition' => $condition,
                ]
            );
        }

        /** Alignment vertical. */
        if ( isset($display['alignment-vertical']) && $display['alignment-vertical'] === true ) {
            $this->add_responsive_control(
                'timeliner_' . $name_Section . '_vertical_align',
                [
                    'label'     => esc_html__( 'Vertical Position', 'timeliner-elementor' ),
                    'type'      => Controls_Manager::CHOOSE,
                    'options'   => [
                        'flex-start'    => [
                            'title' => esc_html__( 'Top', 'timeliner-elementor' ),
                            'icon'  => 'eicon-v-align-top',
                        ],
                        'center'  => [
                            'title' => esc_html__( 'Center', 'timeliner-elementor' ),
                            'icon'  => 'eicon-v-align-middle',
                        ],
                        'flex-end'   => [
                            'title' => esc_html__( 'Bottom', 'timeliner-elementor' ),
                            'icon'  => 'eicon-v-align-bottom',
                        ],
                    ],
                    'default'   => 'center',
                    'selectors' => [
                        '{{WRAPPER}} ' . $css_class => 'align-items: {{value}};',
                    ],
                    'toggle'    => true,
                    'condition' => $condition,
                ]
            );
        }

        /** Alignment. */
        if ( isset($display['alignment']) && $display['alignment'] === true ) {
            $this->add_responsive_control(
                'timeliner_' . $name_Section . '_align',
                [
                    'label'     => esc_html__( 'Alignment', 'timeliner-elementor' ),
                    'type'      => Controls_Manager::CHOOSE,
                    'options'   => [
                        'left'    => [
                            'title' => esc_html__( 'Left', 'timeliner-elementor' ),
                            'icon'  => 'fa fa-align-left',
                        ],
                        'center'  => [
                            'title' => esc_html__( 'Center', 'timeliner-elementor' ),
                            'icon'  => 'fa fa-align-center',
                        ],
                        'right'   => [
                            'title' => esc_html__( 'Right', 'timeliner-elementor' ),
                            'icon'  => 'fa fa-align-right',
                        ],
                    ],
                    'default'   => 'center',
                    'selectors' => [
                        '{{WRAPPER}} ' . $css_class => 'text-align: {{header_align}};',
                    ],
                    'toggle'    => true,
                    'condition' => $condition,
                ]
            );
        }

        /** Alignment justify. */
        if ( isset($display['alignment-justify']) && $display['alignment-justify'] === true ) {
            $this->add_responsive_control(
                'timeliner_' . $name_Section . '_align_justify',
                [
                    'label'     => esc_html__( 'Alignment', 'timeliner-elementor' ),
                    'type'      => Controls_Manager::CHOOSE,
                    'options'   => [
                        'left'    => [
                            'title' => esc_html__( 'Left', 'timeliner-elementor' ),
                            'icon'  => 'fa fa-align-left',
                        ],
                        'center'  => [
                            'title' => esc_html__( 'Center', 'timeliner-elementor' ),
                            'icon'  => 'fa fa-align-center',
                        ],
                        'right'   => [
                            'title' => esc_html__( 'Right', 'timeliner-elementor' ),
                            'icon'  => 'fa fa-align-right',
                        ],
                        'justify' => [
                            'title' => esc_html__( 'Justify', 'timeliner-elementor' ),
                            'icon'  => 'fa fa-align-justify',
                        ],
                    ],
                    'default'   => 'center',
                    'selectors' => [
                        '{{WRAPPER}} ' . $css_class => 'text-align: {{header_align}};',
                    ],
                    'toggle'    => true,
                    'condition' => $condition,
                ]
            );
        }

        /** Background. */
        if ( isset($display['background']) && $display['background'] === true ) {
            $this->add_group_control(
                Group_Control_Background::get_type(),
                [
                    'name'      => 'timeliner_' . $name_Section . '_background',
                    'label'     => esc_html__( 'Background', 'timeliner-elementor' ),
                    'types'     => [ 'classic', 'gradient'],
                    'separator'  => $separator[1],
                    'selector'  => '{{WRAPPER}} ' . $css_class,
                    'condition' => $condition,
                ]
            );
        }

        /** Border. */
        if ( isset($display['border']) && $display['border'] === true ) {
            $this->add_group_control(
                Group_Control_Border::get_type(),
                [
                    'name'      => 'timeliner_' . $name_Section . '_border',
                    'label'     => esc_html__( 'Border', 'timeliner-elementor' ),
                    'selector'  => '{{WRAPPER}} ' . $css_class,
                    'separator'  => $separator[2],
                    'condition' => $condition,
                ]
            );
        }

        /** Border Radius. */
        if ( isset($display['border-radius']) && $display['border-radius'] === true ) {
            $this->add_responsive_control(
                'timeliner_' . $name_Section . '_border_radius',
                [
                    'label'      => esc_html__( 'Border Radius', 'timeliner-elementor' ),
                    'type'       => Controls_Manager::DIMENSIONS,
                    'size_units' => [ 'px', '%', 'em' ],
                    'selectors'  => [
                        '{{WRAPPER}} ' . $css_class => 'border-radius: {{top}}{{unit}} {{right}}{{unit}} {{bottom}}{{unit}} {{left}}{{unit}};',
                    ],
                    'separator'  => $separator[3],
                    'toggle'     => true,
                    'condition'  => $condition,
                ]
            );
        }

        /** Box Shadow. */
        if ( isset($display['box-shadow']) && $display['box-shadow'] === true ) {
            $this->add_group_control(
                Group_Control_Box_Shadow::get_type(),
                [
                    'name'      => 'timeliner_' . $name_Section . '_box_shadow',
                    'label'     => esc_html__( 'Box Shadow', 'timeliner-elementor' ),
                    'selector'  => '{{WRAPPER}} ' . $css_class,
                    'separator'  => 'before',
                    'condition' => $condition,
                ]
            );
        }

        /** CSS filter. */
        if ( isset($display['css-filter']) && $display['css-filter'] === true ) {
            $this->add_group_control(
                Group_Control_Css_Filter::get_type(),
                [
                    'name'     => 'timeliner_' . $name_Section . '_css_filter',
                    'label'    => esc_html__( 'CSS filter', 'timeliner-elementor' ),
                    'selector' => '{{WRAPPER}} ' . $css_class,
                    'condition' => $condition,
                ]
            );
        }

    }

    /**
     * Add the widget controls.
     *
     * @access protected
     * @return void with category names
     **/
    protected function register_controls() {

        /** Content Tab. */
        $this->tab_content();

        /** Style Tab. */
        $this->tab_style();

    }

    /**
     * Add widget controls on Content tab.
     *
     * @since 1.0.0
     * @access private
     *
     * @return void
     **/
    private function tab_content() {

        /** General */
        $this->general_section_content();

        /** Layout */
        $this->layout_section_content();

        /** Content */
        $this->content_section_content();

    }

    /**
     * Add widget controls on Style tab.
     *
     * @since 1.0.0
     * @access private
     *
     * @return void
     **/
    private function tab_style() {

        /** Grid item */
        $this->grid_item_section_styles();

        /** Title */
        $this->title_section_styles();

        /** Description */
        $this->description_section_styles();

        /** Image */
        $this->image_section_styles();

        /** Button */
        $this->button_section_styles();

        /** Navigation Arrows */
        $this->navigation_section_styles();

    }

    /**
     *  TAB: Content.
     */

    /**
     *  General tab.
     */
    public function general_section_content()
    {

        $this->start_controls_section( 'general_content', [
            'label' => esc_html__( 'General', 'timeliner-elementor' ),
            'tab'   => Controls_Manager::TAB_CONTENT
        ] );

            /** Mode */
            $this->add_control(
                'general_mode',
                [
                    'label'     => esc_html__( 'Mode', 'timeliner-elementor' ),
                    'type'      => Controls_Manager::SELECT,
                    'options'   => [
                        'horizontal'    => esc_html__( 'Horizontal', 'timeliner-elementor' ),
                        'vertical'    => esc_html__( 'Vertical', 'timeliner-elementor' ),
                    ],
                    'default'   => 'vertical',
                ]
            );

            /** Force vertical mode */
            $this->add_control(
                'general_force_vertical_mode',
                [
                    'label'           => esc_html__( 'Force vertical mode (px)', 'timeliner-elementor' ),
                    'type'            => Controls_Manager::SLIDER,
                    'size_units'      => [ 'px' ],
                    'range'           => [
                        'px' => [
                            'min'  => 1,
                            'step' => 1,
                        ],
                    ],
                    'default' => [
                        'unit' => 'px',
                        'size' => 800,
                    ],
                    'description' => esc_html__( 'When using the timeline in horizontal mode, define at which viewport width it should revert to vertical mode.', 'timeliner-elementor' ),
                    'condition' => [ 'general_mode' => 'horizontal']
                ]
            );

            /** Horizontal start position */
            $this->add_control(
                'general_horizontal_start_position',
                [
                    'label'     => esc_html__( 'Horizontal start position', 'timeliner-elementor' ),
                    'type'      => Controls_Manager::SELECT,
                    'options'   => [
                        'top'    => esc_html__( 'Top', 'timeliner-elementor' ),
                        'bottom'    => esc_html__( 'Bottom', 'timeliner-elementor' ),
                    ],
                    'default'   => 'top',
                    'condition' => [ 'general_mode' => 'horizontal' ]
                ]
            );

            /** Vertical start position */
            $this->add_control(
                'general_vertical_start_position',
                [
                    'label'     => esc_html__( 'Vertical start position', 'timeliner-elementor' ),
                    'type'      => Controls_Manager::SELECT,
                    'options'   => [
                        'left'    => esc_html__( 'Left', 'timeliner-elementor' ),
                        'right'    => esc_html__( 'Right', 'timeliner-elementor' ),
                    ],
                    'default'   => 'left',
                    'condition' => [ 'general_mode' => 'vertical' ]
                ]
            );

            /** Move Items */
            $this->add_control(
                'general_move_items',
                [
                    'label'           => esc_html__( 'Move Items', 'timeliner-elementor' ),
                    'type'            => Controls_Manager::SLIDER,
                    'size_units'      => [ 'px' ],
                    'range'           => [
                        'px' => [
                            'min'  => 1,
                            'step' => 1,

                        ],
                    ],
                    'default' => [
                        'unit' => 'px',
                        'size' => 1,
                    ],
                    'condition' => [ 'general_mode' => 'horizontal' ]
                ]
            );

            /** RTL mode */
            $this->add_control(
                'general_rtl',
                [
                    'label' => esc_html__( 'RTL mode', 'timeliner-elementor' ),
                    'type' => Controls_Manager::SWITCHER,
                    'label_on' => esc_html__( 'Yes', 'timeliner-elementor' ),
                    'label_off' => esc_html__( 'No', 'timeliner-elementor' ),
                    'description' => esc_html__( 'When using the timeline in horizontal mode, this defines whether the 
                                            timeline should start from the right. This overrides the startIndex setting.',
                                    'timeliner-elementor' ),
                    'return_value' => 'yes',
                    'condition' => [ 'general_mode' => 'horizontal' ]
                ]
            );

            /** Start index */
            $this->add_control(
                'general_start_index',
                [
                    'label'           => esc_html__( 'Start index', 'timeliner-elementor' ),
                    'type'            => Controls_Manager::SLIDER,
                    'size_units'      => [ 'px' ],
                    'range'           => [
                        'px' => [
                            'min'  => 1,
                            'step' => 1,

                        ],
                    ],
                    'default' => [
                        'unit' => 'px',
                        'size' => 1,
                    ],
                    'condition' => [ 'general_mode' => 'horizontal' ]
                ]
            );

            /** Vertical trigger */
            $this->add_control(
                'general_vertical_trigger',
                [
                    'label'           => esc_html__( 'Vertical trigger', 'timeliner-elementor' ),
                    'type'            => Controls_Manager::SLIDER,
                    'size_units'      => [ 'px', '%'],
                    'range'           => [
                        'px' => [
                            'min'  => 1,
                            'step' => 1,

                        ],
                    ],
                    'default' => [
                        'unit' => 'px',
                        'size' => 150,
                    ],
                    'description' => esc_html__( 'Define the distance from the bottom of the screen, in percent 
                                                       or pixels, that the items slide into view.',
                                               'timeliner-elementor' ),
                    'condition' => [ 'general_mode' => 'vertical' ]
                ]
            );

            /** Visible items. */
            $this->add_control(
                'general_visible_items',
                [
                    'label'           => esc_html__( 'Visible items', 'timeliner-elementor' ),
                    'type'            => Controls_Manager::SLIDER,
                    'size_units'      => [ 'px' ],
                    'range'           => [
                        'px' => [
                            'min'  => 1,
                            'step' => 1,
                        ],
                    ],
                    'default' => [
                        'unit' => 'px',
                        'size' => 3,
                    ],
                    'condition' => [ 'general_mode' => 'horizontal' ]
                ]
            );

        $this->end_controls_section();

    }

    /**
     *  Layout tab.
     */
    public function layout_section_content()
    {

        $this->start_controls_section( 'layout_content', [
            'label' => esc_html__( 'Layout', 'timeliner-elementor' ),
            'tab'   => Controls_Manager::TAB_CONTENT,
        ] );

            $layout = new Repeater();

                /** Item. */
                $layout->add_control(
                    'layout_item',
                    [
                        'label'   => esc_html__( 'Item', 'timeliner-elementor' ),
                        'type'    => Controls_Manager::SELECT,
                        'default' => 'title',
                        'options' => [
                            'image'       => esc_html__( 'Image', 'timeliner-elementor' ),
                            'title'       => esc_html__( 'Title', 'timeliner-elementor' ),
                            'description' => esc_html__( 'Description', 'timeliner-elementor' ),
                            'button'      => esc_html__( 'Button', 'timeliner-elementor' ),
                        ],
                    ]
                );

                /** Title Tag. */
                $layout->add_control(
                    'layout_tag_title',
                    [
                        'label' => esc_html__( 'Title tag', 'timeliner-elementor' ),
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
                        'default' => 'h3',
                        'condition' => [ 'layout_item' => 'title' ]
                    ]
                );

                /** Before title text */
                $layout->add_control(
                    'layout_before_title',
                    [
                        'label' => esc_html__( 'Before title text', 'timeliner-elementor' ),
                        'type' => Controls_Manager::TEXT,
                        'dynamic' => ['active' => true],
                        'placeholder' => esc_html__( 'Before title text', 'timeliner-elementor' ),
                        'label_block' => true,
                        'condition' => [ 'layout_item' => 'title' ]
                    ]
                );

                /** After title text */
                $layout->add_control(
                    'layout_after_title',
                    [
                        'label' => esc_html__( 'After title text', 'timeliner-elementor' ),
                        'type' => Controls_Manager::TEXT,
                        'dynamic' => ['active' => true],
                        'placeholder' => esc_html__( 'After title text', 'timeliner-elementor' ),
                        'label_block' => true,
                        'condition' => [ 'layout_item' => 'title' ]
                    ]
                );

                /** Before description text */
                $layout->add_control(
                    'layout_before_description',
                    [
                        'label' => esc_html__( 'Before description text', 'timeliner-elementor' ),
                        'type' => Controls_Manager::TEXT,
                        'dynamic' => ['active' => true],
                        'placeholder' => esc_html__( 'Before description text', 'timeliner-elementor' ),
                        'label_block' => true,
                        'condition' => [ 'layout_item' => 'description' ]
                    ]
                );

                /** After description text */
                $layout->add_control(
                    'layout_after_description',
                    [
                        'label' => esc_html__( 'After description text', 'timeliner-elementor' ),
                        'type' => Controls_Manager::TEXT,
                        'dynamic' => ['active' => true],
                        'placeholder' => esc_html__( 'After description text', 'timeliner-elementor' ),
                        'label_block' => true,
                        'condition' => [ 'layout_item' => 'description' ]
                    ]
                );

            /** Priority. */
            $this->add_control(
                'layout_priority',
                [
                    'label'       => esc_html__( 'Priority', 'timeliner-elementor' ),
                    'type'        => Controls_Manager::REPEATER,
                    'fields'      => $layout->get_controls(),
                    'default'     => [
                        [ 'layout_item' => 'image' ],
                        [ 'layout_item' => 'title', 'layout_tag_title' => 'h3'],
                        [ 'layout_item' => 'description' ],
                    ],
                    'title_field' => 'Layout item  - {{{layout_item}}}'
                ]
            );

        $this->end_controls_section();

    }

    /**
     *  Content tab.
     */
    public function content_section_content()
    {

        $this->start_controls_section( 'content_content', [
            'label' => esc_html__( 'Content', 'timeliner-elementor' ),
            'tab'   => Controls_Manager::TAB_CONTENT,
        ] );

        $timeliner = new Repeater();

            /** Title. */
            $timeliner->add_control(
                'content_title',
                [
                    'label' => esc_html__( 'Title', 'timeliner-elementor' ),
                    'type' => Controls_Manager::TEXT,
                    'dynamic' => ['active' => true],
                    'placeholder' => esc_html__( 'Title', 'timeliner-elementor' ),
                    'label_block' => true
                ]
            );

            /** Image */
            $timeliner->add_control(
                'content_image',
                [
                    'label' => esc_html__( 'Choose Image', 'timeliner-elementor' ),
                    'type' => Controls_Manager::MEDIA,
                    'default' => [
                        'url' => Utils::get_placeholder_image_src(),
                    ],
                ]
            );

            /** Description. */
            $timeliner->add_control(
                'content_description',
                [
                    'label' => esc_html__( 'Description', 'timeliner-elementor' ),
                    'type' => Controls_Manager::WYSIWYG,
                    'placeholder' => esc_html__( 'Description', 'timeliner-elementor' ),
                ]
            );

            /** Button Text. */
            $timeliner->add_control(
                'content_button_text',
                [
                    'label' => esc_html__( 'Button Text', 'timeliner-elementor' ),
                    'type' => Controls_Manager::TEXT,
                    'dynamic' => ['active' => true],
                    'placeholder' => esc_html__( 'Button Text', 'timeliner-elementor' ),
                    'label_block' => true
                ]
            );

            /** Link. */
            $timeliner->add_control(
                'content_link',
                [
                    'label' => esc_html__( 'Link', 'timeliner-elementor' ),
                    'type' => Controls_Manager::URL,
                    'placeholder' => esc_html__( 'https://codecanyon.net/user/merkulove', 'timeliner-elementor' ),
                    'show_external' => true,
                    'default' => [
                        'url' => '',
                        'is_external' => true,
                        'nofollow' => true,
                    ],
                ]
            );

        $this->add_control(
            'content_items',
            [
                'label'       => esc_html__( 'Item', 'timeliner-elementor' ),
                'type'        => Controls_Manager::REPEATER,
                'fields'      => $timeliner->get_controls(),
                'default'     => [
                    [
                        'content_title' => esc_html__( 'Item 1', 'timeliner-elementor' ),
                        'content_description' => esc_html__( 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.', 'timeliner-elementor' ),
                        'content_button_text' => esc_html__( 'More', 'timeliner-elementor' ),
                    ],
                    [
                        'content_title' => esc_html__( 'Item 2', 'timeliner-elementor' ),
                        'content_description' => esc_html__( 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.', 'timeliner-elementor' ),
                        'content_button_text' => esc_html__( 'More', 'timeliner-elementor' ),
                    ],
                    [
                        'content_title' => esc_html__( 'Item 3', 'timeliner-elementor' ),
                        'content_description' => esc_html__( 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.', 'timeliner-elementor' ),
                        'content_button_text' => esc_html__( 'More', 'timeliner-elementor' ),
                    ]
                ],
                'title_field' => 'Item - {{{ content_title }}}',
            ]
        );

        $this->end_controls_section();

    }

    /**
     * TAB: Style.
     */

    /**
     * Item style tab.
     */
    public function grid_item_section_styles()
    {
        $this->start_controls_section( 'section_grid_item_style', [
            'label' => esc_html__( 'Item', 'timeliner-elementor' ),
            'tab'   => Controls_Manager::TAB_STYLE,
        ] );

        /** Left item indent. */
        $this->add_responsive_control(
            'item_left_item_indent',
            [
                'label' => esc_html__( 'Left item indent', 'timeliner-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px' ],
                'default' => [
                    'top' => '0',
                    'right' => '50',
                    'bottom' => '0',
                    'left' => '0',
                    'unit' => 'px',
                ],
                'tablet_default' => [
                    'top' => '0',
                    'right' => '30',
                    'bottom' => '0',
                    'left' => '0',
                    'unit' => 'px',
                ],
                'mobile_default' => [
                    'top' => '0',
                    'right' => '20',
                    'bottom' => '0',
                    'left' => '30',
                    'unit' => 'px',
                ],
                'selectors' => [
                    '{{WRAPPER}} .timeline__item--left' => 'padding: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};'
                ],
                'condition' => [ 'general_mode' => 'vertical']
            ]
        );

        /** Right item indent. */
        $this->add_responsive_control(
            'item_right_item_indent',
            [
                'label' => esc_html__( 'Right item indent', 'timeliner-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px' ],
                'default' => [
                    'top' => '0',
                    'right' => '0',
                    'bottom' => '0',
                    'left' => '50',
                    'unit' => 'px',
                ],
                'tablet_default' => [
                    'top' => '0',
                    'right' => '0',
                    'bottom' => '0',
                    'left' => '30',
                    'unit' => 'px',
                ],
                'mobile_default' => [
                    'top' => '0',
                    'right' => '0',
                    'bottom' => '0',
                    'left' => '0',
                    'unit' => 'px',
                ],
                'selectors' => [
                    '{{WRAPPER}} .timeline__item--right' => 'padding: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};',
                ],
                'condition' => [ 'general_mode' => 'vertical']
            ]
        );

        /** Top item indent. */
        $this->add_responsive_control(
            'item_top_item_indent',
            [
                'label' => esc_html__( 'Top item indent', 'timeliner-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px' ],
                'default' => [
                    'top' => '0',
                    'right' => '0',
                    'bottom' => '50',
                    'left' => '0',
                    'unit' => 'px',
                ],
                'tablet_default' => [
                    'top' => '0',
                    'right' => '0',
                    'bottom' => '0',
                    'left' => '0',
                    'unit' => 'px',
                ],
                'mobile_default' => [
                    'top' => '0',
                    'right' => '0',
                    'bottom' => '0',
                    'left' => '0',
                    'unit' => 'px',
                ],
                'selectors' => [
                    '{{WRAPPER}} .timeline__item--top' => 'padding: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};'
                ],
                'condition' => [ 'general_mode' => 'horizontal']
            ]
        );

        /** Bottom item indent. */
        $this->add_responsive_control(
            'item_bottom_item_indent',
            [
                'label' => esc_html__( 'Bottom item indent', 'timeliner-elementor' ),
                'type' => Controls_Manager::DIMENSIONS,
                'size_units' => [ 'px' ],
                'default' => [
                    'top' => '50',
                    'right' => '0',
                    'bottom' => '0',
                    'left' => '0',
                    'unit' => 'px',
                ],
                'tablet_default' => [
                    'top' => '0',
                    'right' => '0',
                    'bottom' => '0',
                    'left' => '0',
                    'unit' => 'px',
                ],
                'mobile_default' => [
                    'top' => '0',
                    'right' => '0',
                    'bottom' => '0',
                    'left' => '0',
                    'unit' => 'px',
                ],
                'selectors' => [
                    '{{WRAPPER}} .timeline__item--bottom' => 'padding: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};',
                ],
                'condition' => [ 'general_mode' => 'horizontal']
            ]
        );

        $this->add_control(
            'item_header',
            [
                'type' => Controls_Manager::HEADING,
                'separator' => 'before',
            ]
        );

        /** Compact layout. */
        $this->add_responsive_control(
            'item_compact_layout',
            [
                'label' => esc_html__( 'Compact layout', 'timeliner-elementor' ),
                'type' => Controls_Manager::SLIDER,
                'size_units' => [ 'px'],
                'range' => [
                    'px' => [
                        'min' => -350,
                        'max' => 350,
                        'step' => 1,
                    ],
                ],
                'default' => [
                    'unit' => 'px',
                    'size' => 0,
                ],
                'tablet_default' => [
                    'unit' => 'px',
                    'size' => 30,
                ],
                'mobile_default' => [
                    'unit' => 'px',
                    'size' => 30,
                ],
                'selectors' => [
                    '{{WRAPPER}} .timeline__item:not(:first-child)' => 'margin-top: {{SIZE}}{{UNIT}};',
                ],
                'condition' => [ 'general_mode' => 'vertical']
            ]
        );

        /** Horizontal compact layout. */
        $this->add_responsive_control(
            'item_horizontal_compact_layout',
            [
                'label' => esc_html__( 'Compact layout', 'timeliner-elementor' ),
                'type' => Controls_Manager::SLIDER,
                'size_units' => [ 'px'],
                'range' => [
                    'px' => [
                        'min' => -350,
                        'max' => 350,
                        'step' => 1,
                    ],
                ],
                'default' => [
                    'unit' => 'px',
                    'size' => 0,
                ],
                'tablet_default' => [
                    'unit' => 'px',
                    'size' => 30,
                ],
                'mobile_default' => [
                    'unit' => 'px',
                    'size' => 30,
                ],
                'selectors' => [
                    '{{WRAPPER}} @media (max-width: {{general_force_vertical_mode.size}}px) .timeline__item:not(:first-child)' => 'margin-left: {{SIZE}}{{UNIT}};',
                ],
                'condition' => [ 'general_mode' => 'horizontal']
            ]
        );

        $this->get_settings_style_group(
            'item_style',
            '.timeline__content',
            [],
            [
                'padding' => true,
            ]
        );

        $this->get_settings_style_group(
            'item_style',
            '.mdp-timeliner-title, ' .
                     '{{WRAPPER}} .mdp-timeliner-description, ' .
                     '{{WRAPPER}} .mpd-timeliner-button, {{WRAPPER}} .timeline__content',
            [],
            [
                'typography' => true,
                'alignment' => true,
            ]
        );

        /** Сolor lines & dots. */
        $this->add_control(
            'item_line_color',
            [
                'label' => esc_html__( 'Сolor lines & dots', 'timeliner-elementor' ),
                'type' => Controls_Manager::COLOR,
                'default' => '#ddd',
                'selectors' => [
                    '{{WRAPPER}} .timeline:not(.timeline--horizontal):before' => 'background-color: {{VALUE}} !important',
                    '{{WRAPPER}} .timeline__item:after' => 'border: 4px solid {{VALUE}} !important',
                    '{{WRAPPER}} .timeline--horizontal .timeline-divider' => 'background-color: {{VALUE}} !important',
                ],
            ]
        );

        /** Point background color */
        $this->add_control(
            'item_point_background_color',
            [
                'label' => esc_html__( 'Point background color', 'timeliner-elementor' ),
                'type' => Controls_Manager::COLOR,
                'default' => '#fff',
                'selectors' => [
                    '{{WRAPPER}} .timeline__item:after' => 'background-color: {{VALUE}} !important',
                ],
            ]
        );

        $this->start_controls_tabs( 'tabs_timeliner_item_panel' );

            /** Content tab. */
            $this->start_controls_tab(
                'tab_normal_item',
                [
                    'label' => esc_html__('NORMAL', 'timeliner-elementor')
                ]
            );

                $this->get_settings_style_group(
                    'item_style_normal',
                    '.timeline__content, {{WRAPPER}} .mpd-timeliner-button',
                    [],
                    [
                        'color' => true,
                    ]
                );

                $this->add_group_control(
                   Group_Control_Background::get_type(),
                    [
                        'name' => 'timeliner_item_style_normal_background',
                        'label' => esc_html__( 'Background', 'timeliner-elementor' ),
                        'types' => [ 'classic', 'gradient' ],
                        'selector' => '{{WRAPPER}} .timeline__content',
                    ]
                );

                $this->get_settings_style_group(
                    'item_style_normal',
                    '.timeline__content, {{WRAPPER}} .timeline__content a',
                    [],
                    [
                        'border' => true,
                        'border-radius' => true,
                        'box-shadow' => true,
                    ]
                );

            $this->end_controls_tab();

            /** Content tab. */
            $this->start_controls_tab(
                'tab_hover_item',
                [
                    'label' => esc_html__('HOVER', 'timeliner-elementor')
                ]
            );

                $this->get_settings_style_group(
                    'item_style_hover',
                    '.timeline__content:hover',
                    [],
                    [
                        'color' => true,
                    ]
                );

                $this->add_group_control(
                    Group_Control_Background::get_type(),
                    [
                        'name' => 'timeliner_item_style_hover_background',
                        'label' => esc_html__( 'Background', 'timeliner-elementor' ),
                        'types' => [ 'classic'],
                        'selector' => '{{WRAPPER}} .timeline__content:hover',
                    ]
                );

                $this->get_settings_style_group(
                    'item_style_hover',
                    '.timeline__content:hover',
                    [],
                    [
                        'border' => true,
                        'border-radius' => true,
                        'box-shadow' => true,
                    ]
                );

            $this->end_controls_tab();

        $this->end_controls_tabs();

        $this->end_controls_section();

    }

    /**
     * Title style tab.
     */
    public function title_section_styles()
    {

        $this->start_controls_section( 'section_title_style', [
            'label' => esc_html__( 'Title', 'timeliner-elementor' ),
            'tab'   => Controls_Manager::TAB_STYLE,
        ] );

            /** Width. */
            $this->add_control(
                'title_width',
                [
                    'label'           => esc_html__( 'Width', 'timeliner-elementor' ),
                    'type'            => Controls_Manager::SLIDER,
                    'size_units'      => [ '%', 'px' ],
                    'range'           => [
                        '%' => [
                            'min'  => 1,
                            'step' => 1,
                        ],
                    ],
                    'default' => [
                        'unit' => '%',
                        'size' => 100,
                    ],
                    'selectors'  => [ '{{WRAPPER}} .mdp-timeliner-title' => 'width: {{size}}{{unit}}' ]
                ]
            );

            $this->get_settings_style_group(
                'title_style',
                '.mdp-timeliner-title',
                [],
                [
                    'margin' => true,
                    'padding' => true,
                    'color' => true,
                    'typography' => true,
                    'text-shadow' => true,
                    'alignment' => true,
                    'background' => true,
                    'border' => true,
                    'border-radius' => true,
                    'box-shadow' => true,
                ]
            );

        $this->end_controls_section();

    }

    /**
     *  Description style tab.
     */
    public function description_section_styles()
    {

        $this->start_controls_section( 'section_description_style', [
            'label' => esc_html__( 'Description', 'timeliner-elementor' ),
            'tab'   => Controls_Manager::TAB_STYLE,
        ] );

            /** Width. */
            $this->add_control(
                'description_width',
                [
                    'label'           => esc_html__( 'Width', 'timeliner-elementor' ),
                    'type'            => Controls_Manager::SLIDER,
                    'size_units'      => [ '%', 'px' ],
                    'range'           => [
                        '%' => [
                            'min'  => 1,
                            'step' => 1,
                        ],
                    ],
                    'default' => [
                        'unit' => '%',
                        'size' => 100,
                    ],
                    'selectors'  => [ '{{WRAPPER}} .mdp-timeliner-description' => 'width: {{size}}{{unit}}' ]
                ]
            );

            $this->get_settings_style_group(
                'description_style',
                '.mdp-timeliner-description',
                [],
                [
                    'margin' => true,
                    'padding' => true,
                    'color' => true,
                    'typography' => true,
                    'text-shadow' => true,
                    'alignment-justify' => true,
                    'background' => true,
                    'border' => true,
                    'border-radius' => true,
                    'box-shadow' => true,
                ]
            );

        $this->end_controls_section();

    }

    /**
     * Image style tab.
     */
    public function image_section_styles()
    {

        $this->start_controls_section( 'section_image_style', [
            'label' => esc_html__( 'Image', 'timeliner-elementor' ),
            'tab'   => Controls_Manager::TAB_STYLE
        ] );

            /** Width. */
            $this->add_control(
                'image_width',
                [
                    'label'           => esc_html__( 'Width', 'timeliner-elementor' ),
                    'type'            => Controls_Manager::SLIDER,
                    'size_units'      => [ '%', 'px' ],
                    'range'           => [
                        '%' => [
                            'min'  => 1,
                            'step' => 1,
                        ],
                    ],
                    'default' => [
                        'unit' => '%',
                        'size' => 100,
                    ],
                    'selectors'  => [ '{{WRAPPER}} .mdp-timeliner-image' => 'width: {{size}}{{unit}}' ]
                ]
            );

            $this->get_settings_style_group(
                'image_style',
                '.mdp-timeliner-image',
                [],
                [
                    'margin' => true,
                    'padding' => true,
                ]
            );

            $this->add_control(
                'timeliner_image_style_horizontal_align',
                [
                    'label'     => esc_html__( 'Alignment', 'timeliner-elementor' ),
                    'type'      => Controls_Manager::CHOOSE,
                    'options'   => [
                        'left'    => [
                            'title' => esc_html__( 'Left', 'timeliner-elementor' ),
                            'icon'  => 'eicon-h-align-left',
                        ],
                        'right'   => [
                            'title' => esc_html__( 'Right', 'timeliner-elementor' ),
                            'icon'  => 'eicon-h-align-right',
                        ],
                    ],
                    'default'   => 'left',
                    'selectors' => [ '{{WRAPPER}} .mdp-timeliner-image' => 'float: {{VALUE}};'],
                    'toggle'    => true,
                ]
            );

            $this->get_settings_style_group(
                'image_style',
                '.mdp-timeliner-image',
                [],
                [
                    'background' => true,
                    'border' => true,
                    'border-radius' => true,
                    'box-shadow' => true,
                    'css-filter' => true
                ]
            );

        $this->end_controls_section();

    }

    /**
     * Button style tab.
     */
    public function button_section_styles()
    {

        $this->start_controls_section( 'section_button_style', [
            'label' => esc_html__( 'Button', 'timeliner-elementor' ),
            'tab'   => Controls_Manager::TAB_STYLE,
        ] );

        /** Width. */
        $this->add_control(
            'button_width',
            [
                'label'           => esc_html__( 'Width', 'timeliner-elementor' ),
                'type'            => Controls_Manager::SLIDER,
                'size_units'      => [ '%', 'px' ],
                'range'           => [
                    '%' => [
                        'min'  => 1,
                        'step' => 1,
                    ],
                ],
                'default' => [
                    'unit' => '%',
                    'size' => 100,
                ],
                'selectors'  => [ '{{WRAPPER}} .mpd-timeliner-button' => 'width: {{size}}{{unit}}' ]
            ]
        );

        $this->get_settings_style_group(
            'button_style',
            '.mpd-timeliner-button',
            [],
            [
                'margin' => true,
                'padding' => true,
                'typography' => true,
                'text-shadow' => true,
                'alignment' => true,
            ]
        );

        $this->start_controls_tabs( 'tabs_timeliner_button_panel' );

            /** Content tab. */
            $this->start_controls_tab(
                'tab_normal_button',
                [
                    'label' => esc_html__('NORMAL', 'timeliner-elementor')
                ]
            );

                $this->get_settings_style_group(
                    'button_style_normal',
                    '.mpd-timeliner-button',
                    [],
                    [
                        'color' => true,
                        'background' => true,
                        'border' => true,
                        'border-radius' => true,
                        'box-shadow' => true,
                    ]
                );

            $this->end_controls_tab();

            /** Content tab. */
            $this->start_controls_tab(
                'tab_hover_button',
                [
                    'label' => esc_html__('HOVER', 'timeliner-elementor')
                ]
            );

                $this->get_settings_style_group(
                    'button_style_hover',
                    '.mpd-timeliner-button:hover',
                    [],
                    [
                        'color' => true,
                        'background' => true,
                        'border' => true,
                        'border-radius' => true,
                        'box-shadow' => true,
                    ]
                );

            $this->end_controls_tab();

        $this->end_controls_tabs();

        $this->end_controls_section();

    }

    /**
     * Navigation style tab.
     */
    public function navigation_section_styles()
    {
        $this->start_controls_section( 'section_navigation_style', [
            'label' => esc_html__( 'Navigation Arrows', 'timeliner-elementor' ),
            'tab'   => Controls_Manager::TAB_STYLE,
            'condition' => [ 'general_mode' => 'horizontal']
        ] );

        $this->get_settings_style_group(
            'navigation_style',
            '.timeline-nav-button',
            [],
            [
                'padding' => true,
            ],
            [ 'none', 'none', 'none', 'none']
        );

        $this->add_control(
            'navigation_item_header',
            [
                'type' => Controls_Manager::HEADING,
                'separator' => 'before',
            ]
        );

        $this->start_controls_tabs( 'tabs_timeliner_navigation_panel' );

            /** Content tab. */
            $this->start_controls_tab(
                'tab_normal_navigation',
                [
                    'label' => esc_html__('NORMAL', 'timeliner-elementor')
                ]
            );

                $this->get_settings_style_group(
                    'navigation_style_normal',
                    '.timeline-nav-button',
                    [],
                    [
                        'background' => true,
                        'border' => true,
                        'border-radius' => true,
                        'box-shadow' => true,
                    ],
                    [ 'none', 'before', 'before', 'before' ]
                );

            $this->end_controls_tab();

            /** Content tab. */
            $this->start_controls_tab(
                'tab_hover_navigation',
                [
                    'label' => esc_html__('HOVER', 'timeliner-elementor')
                ]
            );

                $this->get_settings_style_group(
                    'navigation_style_hover',
                    '.timeline-nav-button:hover',
                    [],
                    [
                        'background' => true,
                        'border' => true,
                        'border-radius' => true,
                        'box-shadow' => true,
                    ]
                );

            $this->end_controls_tab();

        $this->end_controls_tabs();

        $this->end_controls_section();
    }

    /**
     * We return an array with the names of the layouts.
     *
     * @param $settings - we get an array with all the data.
     *
     * @return array
     */
    private function get_LayoutSortable( $settings ) {

        /** We get all the data on the lists of layouts. */
        $layout = $settings['layout_priority'];

        /** An array in which the names of the layouts and their width will be stored. */
        $res = array();

        /** We write the names of the layouts and their width into an array. */
        foreach ($layout as $key => $val){

            $res[] = [ 'name' => $val['layout_item'] ];
        }

        return $res;

    }

    /**
     * Displays image
     *
     * @param $settings -  we get an array with all the data.
     */
    public function get_custom_image( $settings ) {

        if( ! isset($settings['content_image']['url']) ) { return; } ?>

        <img src="<?php echo esc_url( $settings['content_image']['url'] ); ?>"
             class="mdp-timeliner-image"
             alt=""/>

        <?php
    }

    /**
     * @param $options
     * @param $type_data
     *
     * @return array
     */
    public function getBeforeAfter( $options, $type_data ){

        /** We get all the data on the lists of layouts. */
        $layout = $options['layout_priority'];

        /** An array in which the names of the layouts and their width will be stored. */
        $res = array();

        /** We write the names of the layouts and their width into an array. */

        if ( $type_data === 'title' ) {
            foreach ( $layout as $key => $val ) {
                if ( ! empty( $val[ 'layout_before_' . $type_data ] )
                    || ! empty( $val[ 'layout_after_' . $type_data ] )
                    || ! empty( $val[ 'layout_tag_' . $type_data ] )) {
                    $res = [
                        'before' => $val[ 'layout_before_' . $type_data ],
                        'after' => $val[ 'layout_after_' . $type_data ],
                        'html-tag' => $val[ 'layout_tag_' . $type_data ]
                    ];
                }
            }
        } else {
            foreach ( $layout as $key => $val ) {
                if ( ! empty( $val[ 'layout_before_' . $type_data ] ) || ! empty( $val[ 'layout_after_' . $type_data ] ) ) {
                    $res = [
                        'before' => $val[ 'layout_before_' . $type_data ],
                        'after' => $val[ 'layout_after_' . $type_data ],
                    ];
                }
            }
        }

        return $res;
    }

    /**
     * Displays title
     *
     * @param $settings -  we get an array with all the data.
     * @param $options
     */
    public function get_custom_title( $settings, $options ) {

        $res = $this->getBeforeAfter( $options, 'title');
    ?>
        <<?php echo !empty($res['html-tag']) ? esc_attr($res['html-tag']) : ''; ?> class="mdp-timeliner-title">
            <span><?php echo !empty($res['before']) ? esc_html($res['before']) : ''; ?></span>
            <?php echo esc_html($settings['content_title']); ?>
            <span><?php echo !empty($res['after']) ? esc_html($res['after']) : ''; ?></span>
        </<?php echo !empty($res['html-tag']) ? esc_attr($res['html-tag']) : ''; ?>>
    <?php
    }

    /**
     * Displays description
     *
     * @param $settings -  we get an array with all the data.
     * @param $options
     */
    public function get_custom_description( $settings, $options ){
        $allowed_html = array(
            'a' => array(
                'href'  => true,
                'title' => true,
            ),
            'br'     => array(),
            'em'     => array(),
            'strong' => array(),
            'span' => array(
                'style' => array()
            ),
            'img' => array(
                'alt' => array(),
                'src' => array()
            ),
        );

        $res = $this->getBeforeAfter( $options, 'description');
        ?>
        <p class="mdp-timeliner-description">
            <span><?php echo !empty($res['before']) ? esc_html($res['before']) : ''; ?></span>
            <?php echo wp_kses( $settings['content_description'], $allowed_html ); ?>
            <span><?php echo !empty($res['after']) ? esc_html($res['after']) : ''; ?></span>
        </p>
    <?php
    }

    /**
     * Displays button.
     *
     * @param $settings -  we get an array with all the data.
     */
    public function get_custom_button( $settings ){

        $target = $settings['content_link']['is_external'] ? ' target="_blank"' : '';
        $nofollow = $settings['content_link']['nofollow'] ? ' rel="nofollow"' : '';
        $tagLink = !empty( $settings['content_link']['url'] ) ? 'a' : 'span';
        $linkURL = !empty( $settings['content_link']['url'] ) ?
            'href=' . esc_url($settings['content_link']['url']). $target . $nofollow : '';
    ?>
        <<?php echo esc_attr( $tagLink ) . ' ' .
            esc_attr($linkURL); ?> class="mpd-timeliner-button">
            <?php echo esc_html($settings['content_button_text']); ?>
        </<?php echo esc_attr( $tagLink ); ?>>
    <?php
    }

    /**
     *  Display custom content
     *
     * @param $settings - User entered data.
     * @param $LayoutSortable - An array of user-mapped layouts.
     * @param $options - Setting for displaying custom items.
     */
    public function get_custom_timeliner_box( $settings, $LayoutSortable,  $options ) {

    ?>

       <div class="timeline__item">
            <div class="timeline__content">
                <?php
                    /** We list the layouts in the given order. */
                    foreach ( $LayoutSortable as $val ) {

                        switch ( $val['name'] ) {
                            case 'image':
                                $this->get_custom_image( $settings );
                                break;
                            case 'title':
                                $this->get_custom_title( $settings, $options);
                                break;
                            case 'description':
                                $this->get_custom_description( $settings, $options);
                                break;
                            case 'button':
                                $this->get_custom_button( $settings );
                                break;
                            default:
                                echo esc_html__('You have not added any items to the layout.', 'timeliner-elementor');
                        }

                    }
                ?>
          </div>
       </div>

    <?php
    }

    /**
     * Displays all custom item.
     *
     * @param $settings - Settings for displaying custom item.
     * @param $LayoutSortable - An array of user-mapped layouts.
     */
    public function get_custom_info( $settings, $LayoutSortable ) {

        /** Count the number. */
        $quantity_custom = count( $settings['content_items'] ) - 1;

        /** We display imagebox item in a cycle. */
        for ( $i = 0; $i <= $quantity_custom; $i++) {
            $this->get_custom_timeliner_box( $settings['content_items'][$i], $LayoutSortable, $settings );
        }

    }

    /**
     * Render Frontend Output. Generate the final HTML on the frontend.
     *
     * @access protected
     *
     * @return void
     **/
    protected function render() {

        /** Get all the values from the admin panel. */
        $settings = $this->get_settings_for_display();

        /** We return an array with the names of the layouts and their width. */
        $LayoutSortable = $this->get_LayoutSortable( $settings );

        self::$addonID = $this->get_id();
        ?>

        <!-- Start Timeliner WordPress Plugin -->

        <div id="mdp-timeline-<?php echo $this->get_id(); ?>" class="timeline mdp-timeline-<?php echo $this->get_id(); ?>">
            <div class="timeline__wrap">
                <div class="timeline__items">
                    <?php $this->get_custom_info( $settings, $LayoutSortable ); ?>
                </div>
            </div>
        </div>

        <script>
            <?php if( Plugin::$instance->editor->is_edit_mode() !== true ): ?>
            document.addEventListener("DOMContentLoaded", function() {
            <?php endif; ?>

            window.MDPTimeliner_<?php echo $this->get_id(); ?> = function () {
                <?php if( $settings[ 'general_mode' ] === 'vertical' ) : ?>
                jQuery('#mdp-timeline-<?php echo $this->get_id(); ?>').timeline({
                    verticalStartPosition: '<?php echo esc_attr( $settings[ 'general_vertical_start_position' ] ); ?>',
                    verticalTrigger: '<?php echo esc_attr( $settings[ 'general_vertical_trigger' ][ 'size' ] ) . esc_attr( $settings[ 'general_vertical_trigger' ][ 'unit' ] ); ?>'
                } );
                <?php endif; ?>

                <?php if( $settings[ 'general_mode' ] === 'horizontal' ) : ?>
                jQuery('#mdp-timeline-<?php echo $this->get_id(); ?>').timeline({
                    mode: 'horizontal',
                    horizontalStartPosition: '<?php echo esc_attr( $settings[ 'general_horizontal_start_position' ] ); ?>',
                    moveItems: '<?php echo esc_attr( $settings[ 'general_move_items' ][ 'size' ] ); ?>',
                    rtlMode: <?php if ( $settings[ 'general_rtl' ] === 'yes' ) {
                        echo 'true';
                    } else {
                        echo 'false';
                    } ?>,
                    startIndex: <?php echo esc_attr( $settings[ 'general_start_index' ][ 'size' ] - 1 ); ?>,
                    forceVerticalMode: <?php echo esc_attr( $settings[ 'general_force_vertical_mode' ][ 'size' ] ); ?>,
                    visibleItems: <?php echo esc_attr( $settings[ 'general_visible_items' ][ 'size' ] ); ?>,
                } );
                <?php endif; ?>
            }

            window.MDPTimeliner_<?php echo $this->get_id(); ?>();

            <?php if( Plugin::$instance->editor->is_edit_mode() !== true ): ?>
            } );
            <?php endif; ?>
        </script>

        <!-- End Timeliner WordPress Plugin -->

	    <?php

    }

    /**
     *
     */
    protected function _content_template() {
        $addon_id = self::$addonID;
        ?>
        <#
        /** Empty. */
        function isEmpty(str) {

            if (str.trim() == ''){
                return true;
            }

            return false;
        }

        /** We return an array with the names of the layouts. */
        function layoutSortable() {

            let res = [];

            if( settings.layout_priority ){
                _.each( settings.layout_priority, function( item, index ) {
                    res.push( item.layout_item );
                });
            }

            return res;

        }

        /** Tag Title */
        function getTagTitle( settings ){
            let res;

            if( settings.layout_priority ){
                _.each( settings.layout_priority, function( item, index ) {
                    if( !isEmpty(item.layout_tag_title) ){
                        res = item.layout_tag_title;
                    }
                });
            }

            return res;
        }

        /** After Title */
        function getAfterTitle( settings ){
            let res;

            if( settings.layout_priority ){
                _.each( settings.layout_priority, function( item, index ) {
                    if( !isEmpty(item.layout_after_title) ){
                        res = item.layout_after_title;
                    }
                });
            }

            return res;
        }

        /** Before Title */
        function getBeforeTitle( settings ){
        let res;

        if( settings.layout_priority ){
            _.each( settings.layout_priority, function( item, index ) {
                if( !isEmpty(item.layout_before_title) ){
                    res = item.layout_before_title;
                }
            });
        }

        return res;
        }

        /** Description before. */
        function getBeforeDescription( settings ){
            let res;

            if( settings.layout_priority ){
                _.each( settings.layout_priority, function( item, index ) {
                    if( !isEmpty(item.layout_before_description) ){
                        res = item.layout_before_description;
                    }
                });
            }

            return res;
        }

        /** Description after. **/
        function getAfterDescription( settings ){
            let res;

            if( settings.layout_priority ){
                _.each( settings.layout_priority, function( item, index ) {
                    if( !isEmpty(item.layout_after_description) ){
                        res = item.layout_after_description;
                    }
                });
            }

            return res;
        }

        /** Displays title. */
        function customTitle( itemContent, settings ){

            let AfterTitle = getAfterTitle( settings );
            let BeforeTitle = getBeforeTitle( settings );
            let TagTitle = getTagTitle( settings );
        #>
            <{{{TagTitle}}} class="mdp-timeliner-title">
                <span>{{{BeforeTitle}}}</span>
                    {{{itemContent.content_title}}}
                <span>{{{AfterTitle}}}</span>
            </{{{TagTitle}}}>
        <#
        }

        /** Displays description. */
        function customDescription( itemContent, settings ){
        let BeforeDescription = getBeforeDescription( settings );
        let AfterDescription = getAfterDescription( settings );
        #>
            <p class="mdp-timeliner-description">
                <span>{{{BeforeDescription}}}</span>
                    {{{itemContent.content_description}}}
                <span>{{{AfterDescription}}}</span>
            </p>
        <#
        }

        /** Displays image. */
        function customImage( itemContent ){
        #>
            <img src="{{{itemContent}}}" class="mdp-timeliner-image" alt=""/>
        <#
        }

        /** Displays button. */
        function customButton( itemContent ){
        #>
           <a href="{{{itemContent.content_link.url}}}" class="mpd-timeliner-button">
               {{{itemContent.content_button_text}}}
           </a>
        <#
        }

        /** Display custom content. */
        function customContainer( itemContent, layoutSortable, settings){
        #>
            <div class="timeline__item">
                <div class="timeline__content">
                    <#
                        _.each( layoutSortable, function( item, index ) {
                            switch ( item ) {
                                case 'image':
                                    customImage( itemContent.content_image.url );
                                    break;
                                case 'title':
                                    customTitle( itemContent, settings);
                                    break;
                                case 'description':
                                    customDescription( itemContent, settings);
                                    break;
                                case 'button':
                                    customButton( itemContent );
                                    break;
                                default:
                                    console.log('Sorry');
                            }
                        });
                    #>
                </div>
            </div>
        <#
        }

        /** Custom: We transfer data to create a slider. */
        function customInfo( layoutSortable ) {

            /** Count the number. */
            let quantityCustom = settings.content_items.length - 1;

            for(let i = 0; i <= quantityCustom; i++){
                customContainer( settings.content_items[i], layoutSortable, settings );
            }

        }

        #>

        <div id="mdp-timeline-<?php echo esc_attr( $addon_id ); ?>" class="timeline mdp-timeline-<?php echo esc_attr( $addon_id ); ?>">
            <div class="timeline__wrap">
                <div class="timeline__items">
                    <# customInfo( layoutSortable() ); #>
                </div>
            </div>
        </div>

        <script>
        window.MDPTimeliner_<?php esc_attr_e( $addon_id ); ?> = function () {
            if( '{{{settings.general_mode}}}' === 'vertical' ) {
                jQuery('#mdp-timeline-<?php esc_attr_e( $addon_id ); ?>').timeline({
                    verticalStartPosition: '{{{settings.general_vertical_start_position}}}',
                    verticalTrigger: '{{{settings.general_vertical_trigger.size}}}{{{settings.general_vertical_trigger.unit}}}'
                } );
            }

            if( '{{{settings.general_mode}}}' === 'horizontal' ) {
                jQuery('#mdp-timeline-<?php esc_attr_e( $addon_id ); ?>').timeline({
                    mode: 'horizontal',
                    horizontalStartPosition: '{{{settings.general_horizontal_start_position}}}',
                    moveItems: '{{{settings.general_move_items.size}}}',
                    rtlMode: '{{{settings.general_rtl}}}' === 'yes' ? true : false,
                    startIndex: {{{settings.general_start_index.size}}} - 1,
                    forceVerticalMode: {{{settings.general_force_vertical_mode.size}}},
                    visibleItems: {{{settings.general_visible_items.size}}},
                } );
            }
        }

        window.MDPTimeliner_<?php esc_attr_e( $addon_id ); ?>();
        </script>

        <?php
    }

    /**
     * Return link for documentation
     * Used to add stuff after widget
     *
     * @access public
     *
     * @return string
     **/
    public function get_custom_help_url() {

        return 'https://docs.merkulov.design/tag/timeliner';

    }

}
