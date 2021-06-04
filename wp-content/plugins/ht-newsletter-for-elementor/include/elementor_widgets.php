<?php
namespace Elementor;

// Elementor Classes
use Elementor\Core\Schemes\Color as Scheme_Color;
use Elementor\Core\Schemes\Typography as Scheme_Typography;

if ( ! defined( 'ABSPATH' ) ) exit; // Exit if accessed directly

class HTMailChimpForm_Elementor_Widget extends Widget_Base {

    public function get_name() {
        return 'ht-mailchimpform-addons';
    }
    
    public function get_title() {
        return __( 'HT: Mailchimp For WP', 'ht-mailchimpform' );
    }

    public function get_icon() {
        return 'eicon-mail';
    }

    public function get_categories() {
        return [ 'general' ];
    }

    protected function _register_controls() {

        $this->start_controls_section(
            'mailchimpform_content',
            [
                'label' => __( 'Mail Chimp Form', 'ht-mailchimpform' ),
            ]
        );
            $this->add_control(
                'mail_chimp_form_id',
                [
                    'label'       => __( 'Mailchimp Form ID', 'ht-mailchimpform' ),
                    'type'        => Controls_Manager::TEXT,
                    'placeholder' => __( '290', 'ht-mailchimpform' ),
                    'description' => __( 'For show ID <a href="admin.php?page=mailchimp-for-wp-forms" target="_blank"> Click here </a>', 'ht-mailchimpform' ),
                    'label_block' => true,
                    'separator'   => 'before',
                ]
            );

        $this->end_controls_section();

        // Style tab section
        $this->start_controls_section(
            'ht_mailchimp_section_style',
            [
                'label' => __( 'Style', 'ht-mailchimpform' ),
                'tab' => Controls_Manager::TAB_STYLE,
            ]
        );
            
            $this->add_responsive_control(
                'ht_mailchimp_section_padding',
                [
                    'label' => __( 'Padding', 'ht-mailchimpform' ),
                    'type' => Controls_Manager::DIMENSIONS,
                    'size_units' => [ 'px', '%', 'em' ],
                    'selectors' => [
                        '{{WRAPPER}} .htformmailchimp-input-box' => 'padding: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};',
                    ],
                    'separator' =>'before',
                ]
            );

            $this->add_responsive_control(
                'ht_mailchimp_section_margin',
                [
                    'label' => __( 'Margin', 'ht-mailchimpform' ),
                    'type' => Controls_Manager::DIMENSIONS,
                    'size_units' => [ 'px', '%', 'em' ],
                    'selectors' => [
                        '{{WRAPPER}} .htformmailchimp-input-box' => 'margin: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};',
                    ],
                    'separator' =>'before',
                ]
            );

            $this->add_group_control(
                Group_Control_Background::get_type(),
                [
                    'name' => 'ht_mailchimp_section_background',
                    'label' => __( 'Background', 'ht-mailchimpform' ),
                    'types' => [ 'classic', 'gradient' ],
                    'selector' => '{{WRAPPER}} .htformmailchimp-input-box',
                ]
            );

            $this->add_responsive_control(
                'ht_mailchimp_section_align',
                [
                    'label' => __( 'Alignment', 'ht-mailchimpform' ),
                    'type' => Controls_Manager::CHOOSE,
                    'options' => [
                        'left' => [
                            'title' => __( 'Left', 'ht-mailchimpform' ),
                            'icon' => 'fa fa-align-left',
                        ],
                        'center' => [
                            'title' => __( 'Center', 'ht-mailchimpform' ),
                            'icon' => 'fa fa-align-center',
                        ],
                        'right' => [
                            'title' => __( 'Right', 'ht-mailchimpform' ),
                            'icon' => 'fa fa-align-right',
                        ],
                        'justify' => [
                            'title' => __( 'Justified', 'ht-mailchimpform' ),
                            'icon' => 'fa fa-align-justify',
                        ],
                    ],
                    'selectors' => [
                        '{{WRAPPER}} .htformmailchimp-input-box' => 'text-align: {{VALUE}};',
                    ],
                    'default' => 'left',
                    'separator' =>'before',
                ]
            );

        $this->end_controls_section();

        // Input Box style tab start
        $this->start_controls_section(
            'ht_mailchimp_input_style',
            [
                'label'     => __( 'Input Box', 'ht-mailchimpform' ),
                'tab'       => Controls_Manager::TAB_STYLE,
            ]
        );

            $this->add_control(
                'ht_input_box_height',
                [
                    'label' => __( 'Height', 'ht-mailchimpform' ),
                    'type'  => Controls_Manager::SLIDER,
                    'range' => [
                        'px' => [
                            'max' => 150,
                        ],
                    ],
                    'default' => [
                        'size' => 50,
                    ],
                    'selectors' => [
                        '{{WRAPPER}} .mc4wp-form input[type*="text"]'  => 'height: {{SIZE}}{{UNIT}};',
                        '{{WRAPPER}} .mc4wp-form input[type*="email"]' => 'height: {{SIZE}}{{UNIT}};',
                    ],
                ]
            );

            $this->add_group_control(
                Group_Control_Typography::get_type(),
                [
                    'name' => 'ht_input_box_typography',
                    'scheme' => Scheme_Typography::TYPOGRAPHY_1,
                    'selector' => '{{WRAPPER}} .mc4wp-form input[type*="email"]',
                ]
            );

            $this->add_control(
                'ht_input_box_background',
                [
                    'label'     => __( 'Background Color', 'ht-mailchimpform' ),
                    'type'      => Controls_Manager::COLOR,
                    'selectors' => [
                        '{{WRAPPER}} .mc4wp-form input[type*="text"]'         => 'background-color: {{VALUE}};',
                        '{{WRAPPER}} .mc4wp-form input[type*="email"]'        => 'background-color: {{VALUE}};',
                        '{{WRAPPER}} .mc4wp-form select[name*="_mc4wp_lists"]' => 'background-color: {{VALUE}};',
                    ],
                ]
            );

            $this->add_control(
                'ht_input_box_text_color',
                [
                    'label'     => __( 'Text Color', 'ht-mailchimpform' ),
                    'type'      => Controls_Manager::COLOR,
                    'selectors' => [
                        '{{WRAPPER}} .mc4wp-form input[type*="text"]'  => 'color: {{VALUE}};',
                        '{{WRAPPER}} .mc4wp-form input[type*="email"]' => 'color: {{VALUE}};',
                    ],
                ]
            );

            $this->add_control(
                'ht_input_box_placeholder_color',
                [
                    'label'     => __( 'Placeholder Color', 'ht-mailchimpform' ),
                    'type'      => Controls_Manager::COLOR,
                    'selectors' => [
                        '{{WRAPPER}} .mc4wp-form input[type*="text"]::-webkit-input-placeholder'  => 'color: {{VALUE}};',
                        '{{WRAPPER}} .mc4wp-form input[type*="text"]::-moz-placeholder'  => 'color: {{VALUE}};',
                        '{{WRAPPER}} .mc4wp-form input[type*="text"]:-ms-input-placeholder'  => 'color: {{VALUE}};',
                        '{{WRAPPER}} .mc4wp-form input[type*="email"]::-webkit-input-placeholder' => 'color: {{VALUE}};',
                        '{{WRAPPER}} .mc4wp-form input[type*="email"]::-moz-placeholder' => 'color: {{VALUE}};',
                        '{{WRAPPER}} .mc4wp-form input[type*="email"]:-ms-input-placeholder' => 'color: {{VALUE}};',
                        '{{WRAPPER}} .mc4wp-form select[name*="_mc4wp_lists"]'      => 'color: {{VALUE}};',
                    ],
                ]
            );

            $this->add_group_control(
                Group_Control_Border::get_type(),
                [
                    'name' => 'ht_input_box_border',
                    'label' => __( 'Border', 'ht-mailchimpform' ),
                    'selector' => '{{WRAPPER}} .mc4wp-form input[type*="email"]',
                ]
            );

            $this->add_responsive_control(
                'ht_input_box_border_radius',
                [
                    'label' => esc_html__( 'Border Radius', 'ht-mailchimpform' ),
                    'type' => Controls_Manager::DIMENSIONS,
                    'selectors' => [
                        '{{WRAPPER}} .mc4wp-form input[type*="text"]' => 'border-radius: {{TOP}}px {{RIGHT}}px {{BOTTOM}}px {{LEFT}}px;',
                        '{{WRAPPER}} .mc4wp-form input[type*="email"]' => 'border-radius: {{TOP}}px {{RIGHT}}px {{BOTTOM}}px {{LEFT}}px;',
                    ],
                    'separator' =>'before',
                ]
            );

            $this->add_responsive_control(
                'ht_input_box_padding',
                [
                    'label' => __( 'Padding', 'ht-mailchimpform' ),
                    'type' => Controls_Manager::DIMENSIONS,
                    'size_units' => [ 'px', '%', 'em' ],
                    'selectors' => [
                        '{{WRAPPER}} .mc4wp-form input[type*="text"]' => 'padding: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};',
                        '{{WRAPPER}} .mc4wp-form input[type*="email"]' => 'padding: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};',
                    ],
                    'separator' =>'before',
                ]
            );

            $this->add_responsive_control(
                'ht_input_box_margin',
                [
                    'label' => __( 'Margin', 'ht-mailchimpform' ),
                    'type' => Controls_Manager::DIMENSIONS,
                    'size_units' => [ 'px', '%', 'em' ],
                    'selectors' => [
                        '{{WRAPPER}} .mc4wp-form input[type*="text"]' => 'margin: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};',
                        '{{WRAPPER}} .mc4wp-form input[type*="email"]' => 'margin: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};',
                    ],
                    'separator' =>'before',
                ]
            );
           
        $this->end_controls_section(); // Input box style tab end

        // Input submit button style tab start
        $this->start_controls_section(
            'ht_mailchimp_inputsubmit_style',
            [
                'label'     => __( 'Button', 'ht-mailchimpform' ),
                'tab'       => Controls_Manager::TAB_STYLE,
            ]
        );
            
            $this->start_controls_tabs('ht_submit_style_tabs');

                // Button Normal tab start
                $this->start_controls_tab(
                    'ht_submit_style_normal_tab',
                    [
                        'label' => __( 'Normal', 'ht-mailchimpform' ),
                    ]
                );

                    $this->add_control(
                        'ht_input_submit_height',
                        [
                            'label' => __( 'Height', 'ht-mailchimpform' ),
                            'type'  => Controls_Manager::SLIDER,
                            'range' => [
                                'px' => [
                                    'max' => 150,
                                ],
                            ],
                            'default' => [
                                'size' => 40,
                            ],
                            'selectors' => [
                                '{{WRAPPER}} .mc4wp-form input[type*="submit"]' => 'height: {{SIZE}}{{UNIT}};',
                            ],
                        ]
                    );

                    $this->add_group_control(
                        Group_Control_Typography::get_type(),
                        [
                            'name' => 'ht_input_submit_typography',
                            'scheme' => Scheme_Typography::TYPOGRAPHY_1,
                            'selector' => '{{WRAPPER}} .mc4wp-form input[type*="submit"]',
                        ]
                    );

                    $this->add_control(
                        'ht_input_submit_text_color',
                        [
                            'label'     => __( 'Text Color', 'ht-mailchimpform' ),
                            'type'      => Controls_Manager::COLOR,
                            'selectors' => [
                                '{{WRAPPER}} .mc4wp-form input[type*="submit"]'  => 'color: {{VALUE}};',
                            ],
                        ]
                    );

                    $this->add_control(
                        'ht_input_submit_background_color',
                        [
                            'label'     => __( 'Background Color', 'ht-mailchimpform' ),
                            'type'      => Controls_Manager::COLOR,
                            'selectors' => [
                                '{{WRAPPER}} .mc4wp-form input[type*="submit"]'  => 'background-color: {{VALUE}};',
                            ],
                        ]
                    );

                    $this->add_responsive_control(
                        'ht_input_submit_padding',
                        [
                            'label' => __( 'Padding', 'ht-mailchimpform' ),
                            'type' => Controls_Manager::DIMENSIONS,
                            'size_units' => [ 'px', '%', 'em' ],
                            'selectors' => [
                                '{{WRAPPER}} .mc4wp-form input[type*="submit"]' => 'padding: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};',
                            ],
                            'separator' =>'before',
                        ]
                    );

                    $this->add_responsive_control(
                        'ht_input_submit_margin',
                        [
                            'label' => __( 'Margin', 'ht-mailchimpform' ),
                            'type' => Controls_Manager::DIMENSIONS,
                            'size_units' => [ 'px', '%', 'em' ],
                            'selectors' => [
                                '{{WRAPPER}} .mc4wp-form input[type*="submit"]' => 'margin: {{TOP}}{{UNIT}} {{RIGHT}}{{UNIT}} {{BOTTOM}}{{UNIT}} {{LEFT}}{{UNIT}};',
                            ],
                            'separator' =>'before',
                        ]
                    );

                    $this->add_group_control(
                        Group_Control_Border::get_type(),
                        [
                            'name' => 'ht_input_submit_border',
                            'label' => __( 'Border', 'ht-mailchimpform' ),
                            'selector' => '{{WRAPPER}} .mc4wp-form input[type*="submit"]',
                        ]
                    );

                    $this->add_responsive_control(
                        'ht_input_submit_border_radius',
                        [
                            'label' => esc_html__( 'Border Radius', 'ht-mailchimpform' ),
                            'type' => Controls_Manager::DIMENSIONS,
                            'selectors' => [
                                '{{WRAPPER}} .mc4wp-form input[type*="submit"]' => 'border-radius: {{TOP}}px {{RIGHT}}px {{BOTTOM}}px {{LEFT}}px;',
                            ],
                            'separator' =>'before',
                        ]
                    );

                    $this->add_group_control(
                        Group_Control_Box_Shadow::get_type(),
                        [
                            'name' => 'ht_input_submit_box_shadow',
                            'label' => __( 'Box Shadow', 'ht-mailchimpform' ),
                            'selector' => '{{WRAPPER}} .mc4wp-form input[type*="submit"]',
                        ]
                    );

                $this->end_controls_tab(); // Button Normal tab end

                // Button Hover tab start
                $this->start_controls_tab(
                    'ht_submit_style_hover_tab',
                    [
                        'label' => __( 'Hover', 'ht-mailchimpform' ),
                    ]
                );

                    $this->add_control(
                        'ht_input_submithover_text_color',
                        [
                            'label'     => __( 'Text Color', 'ht-mailchimpform' ),
                            'type'      => Controls_Manager::COLOR,
                            'selectors' => [
                                '{{WRAPPER}} .mc4wp-form input[type*="submit"]:hover'  => 'color: {{VALUE}};',
                            ],
                        ]
                    );

                    $this->add_control(
                        'ht_input_submithover_background_color',
                        [
                            'label'     => __( 'Background Color', 'ht-mailchimpform' ),
                            'type'      => Controls_Manager::COLOR,
                            'selectors' => [
                                '{{WRAPPER}} .mc4wp-form input[type*="submit"]:hover'  => 'background-color: {{VALUE}};',
                            ],
                        ]
                    );

                    $this->add_group_control(
                        Group_Control_Border::get_type(),
                        [
                            'name' => 'ht_input_submithover_border',
                            'label' => __( 'Border', 'ht-mailchimpform' ),
                            'selector' => '{{WRAPPER}} .mc4wp-form input[type*="submit"]:hover',
                        ]
                    );

                $this->end_controls_tab(); // Button Hover tab end

            $this->end_controls_tabs();

        $this->end_controls_section(); // Input submit button style tab end

        // Form Label Style
        $this->start_controls_section(
            'ht_mailchimp_label_style',
            [
                'label'     => __( 'Label', 'ht-mailchimpform' ),
                'tab'       => Controls_Manager::TAB_STYLE,
            ]
        );
            
            $this->add_control(
                'ht_mailchimp_label_text_color',
                [
                    'label'     => __( 'Color', 'ht-mailchimpform' ),
                    'type'      => Controls_Manager::COLOR,
                    'selectors' => [
                        '{{WRAPPER}} .mc4wp-form label'  => 'color: {{VALUE}};',
                    ],
                ]
            );

            $this->add_group_control(
                Group_Control_Typography::get_type(),
                [
                    'name' => 'ht_mailchimp_label_typography',
                    'scheme' => Scheme_Typography::TYPOGRAPHY_1,
                    'selector' => '{{WRAPPER}} .mc4wp-form label',
                ]
            );

        $this->end_controls_section(); // Label style tab end


    }

    protected function render( $instance = [] ) {

        $settings   = $this->get_settings_for_display();
        $id         = $this->get_id();

        $this->add_render_attribute( 'htmailchimp_attr', 'class', 'ht-mailchimp-form-wrapper' );

        $this->add_render_attribute( 'shortcode', 'id', $settings['mail_chimp_form_id'] );
        $shortcode = sprintf( '[mc4wp_form %s]', $this->get_render_attribute_string( 'shortcode' ) );

    ?>
            <div <?php echo $this->get_render_attribute_string('htmailchimp_attr'); ?> >
                <div class="htformmailchimp-input-box">
                    <?php
                        if( !empty( $settings['mail_chimp_form_id'] ) ){
                            echo do_shortcode( $shortcode ); 
                        }else{
                            echo '<div class="form_no_select">' .__('Please Enter the Mail chimp form id.','ht-mailchimpform'). '</div>';
                        }
                    ?>
                </div>
            </div>

        <?php
    }
}

Plugin::instance()->widgets_manager->register_widget_type( new HTMailChimpForm_Elementor_Widget() );