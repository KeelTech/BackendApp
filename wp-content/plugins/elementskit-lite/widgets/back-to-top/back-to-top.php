<?php
namespace Elementor;

use \Elementor\ElementsKit_Widget_Back_To_Handler as Handler;
use \ElementsKit_Lite\Modules\Controls\Controls_Manager as ElementsKit_Controls_Manager;

if (! defined( 'ABSPATH' ) ) exit;

class ElementsKit_Back_To extends Widget_Base {
    use \ElementsKit_Lite\Widgets\Widget_Notice;

    public $base;

    public function get_name() {
        return Handler::get_name();
    }

    public function get_title() {
        return Handler::get_title();
    }

    public function get_icon() {
        return Handler::get_icon();
    }

    public function get_categories() {
        return Handler::get_categories();
    }
    
    public function get_help_url() {
        return '';
    }

  

    protected function register_controls() {

      
   }

   protected function render( ) {
    echo '<div class="ekit-wid-con" >';
        echo 'testing';
    echo '</div>';
   }

}
