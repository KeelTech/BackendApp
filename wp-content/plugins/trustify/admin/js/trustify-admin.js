(function( $ ) {
	'use strict';

	/**
	 * All of the code for your admin-facing JavaScript source
	 * should reside in this file.
	 *
	 * Note: It has been assumed you will write jQuery code here, so the
	 * $ function reference has been prepared for usage within the scope
	 * of this function.
	 *
	 * This enables you to define handlers, for when the DOM is ready:
	 *
	 * $(function() {
	 *
	 * });
	 *
	 * When the window is loaded:
	 *
	 * $( window ).load(function() {
	 *
	 * });
	 *
	 * ...and/or other possibilities.
	 *
	 * Ideally, it is not considered best practise to attach more than a
	 * single DOM-ready or window-load handler for a particular page.
	 * Although scripts in the WordPress core, Plugins and Themes may be
	 * practising this, we should strive to set a better example in our own work.
	 */
	 
	 $.fn.extend({
	 	hasClasses: function (selectors) {
	 		var self = this;
	 		for (var i in selectors) {
	 			if ($(self).hasClass(selectors[i])) 
	 				return true;
	 		}
	 		return false;
	 	}
	 });

	//Transitation effect
	$(function(){

        //border enable
        $('.trustify-border').hide();
        if ($('body .chk-border').is(':checked')) {
        	$('.trustify-border').show();
        } 
        $('body').on('click','.chk-border',function(){
        	$('.trustify-border').toggle();
        });
     	
		$('#transition_style').on('change', function() {
			var val = $(this).val();
			var $sel = $('#popup_template');
			if( $sel.hasClass(val) ) {
				return;
			}
			if( $sel.hasClasses(['fadeInLeft', 'fadeInUp', 'fadeInRight', 'bounceInRight', 'bounceInLeft', 'bounceInUp', 'flipInX', 'zoomIn', 'shake', 'swing', 'rollIn']) ) {
				$sel.removeClass('fadeInLeft fadeInUp fadeInRight bounceInRight bounceInLeft bounceInUp flipInX zoomIn shake swing rollIn');
			}
			$sel.addClass(val);
		});

		 // colorpicker
		 $('.color-picker').wpColorPicker();

		// datepicker
		$('.mifi_pick').datepicker({
			dateFormat: 'yy-mm-dd'
		});

		//Background Color picker
		$("#popup_bgcolor").wpColorPicker(
			'option',
			'change',
			function(event, ui) {	
				var color = ui.color.toString();	  
				var $destination = $('.popup_template'); 
				$destination.css('background-color', color);
			}
			);
		//on load
        var bg_color = $('#popup_bgcolor').val();
        $('.popup_template').css('background-color', bg_color);

		//Text Color picker
		$("#popup_textcolor").wpColorPicker(
			'option',
			'change',
			function (event, ui){
				var color = ui.color.toString();
				$('.popup_template').css('color', color);

			}
			);
        //on load
        var text_color = $('#popup_textcolor').val();
        $('.popup_template').css('color', text_color);

        //Text Font Size
		$('body').on('keyup','#popup_font_size',function(){
			var fontSize = $(this).val();
			$('.popup-item > p').css( { "font-size": fontSize+"px" } );
		});
		//on load        
        var font_size = $('#popup_font_size').val();
        $('.popup-item > p').css( { "font-size": font_size+"px" } );

        //Text Transform
        $('#popup_text_tnsfrm').on('change', function() {
        	var textTsm = $(this).val();
            $('.popup-item > p').css( { "text-transform": textTsm } );
        });
        //on load
        var text_tsm = $('#popup_text_tnsfrm option:selected').val();
        $('.popup-item > p').css( { "text-transform": text_tsm } );

		//Layout Style eg:image/ without image
		$('#template_layout').on('change', function() {
			var val = $(this).val();
			var $sel = $('#popup_template');
			if( $sel.hasClass(val) ) {
				return;
			}
			if( $sel.hasClasses(['imageOnLeft', 'imageOnRight', 'textOnly']) ) {
				$sel.removeClass('imageOnLeft imageOnRight textOnly');
			}
			$sel.addClass(val);
			
		});
		// on load
		var val = $('#template_layout option:selected').val();
		var $sel = $('#popup_template');
		if( $sel.hasClass(val) ) {
			return;
		}
		if( $sel.hasClasses(['imageOnLeft', 'imageOnRight', 'textOnly']) ) {
			$sel.removeClass('imageOnLeft imageOnRight textOnly');
		}
		$sel.addClass(val);


  		//Image view
	  	$('body').on('change','#image-view',function(){
	    	var view = $(this).val();
			if( $sel.hasClasses(['img-square', 'img-circle']) ) {
				$sel.removeClass('img-square img-circle');
			}
	    	$('.popup_template').addClass( 'img-'+view );
	  	});
	    //on load
	    var view = $('#image-view').val();
	    $('.popup_template').addClass( 'img-'+view );

		//Layout Position eg: Bottomm Left or buttom right 
		$('#template_position').on('change', function() {
			var val = $(this).val();
			var $sel = $('.popup_position');
			if( $sel.hasClass(val) ) {
				return;
			}
			if( $sel.hasClasses(['bottomLeft', 'bottomRight','topLeft', 'topRight']) ) {
				$sel.removeClass('bottomLeft bottomRight topLeft topRight ');
			}
			$sel.addClass(val);

		});
		//on load
		var val1 = $('#template_position option:selected').val();
		var $sel1 = $('.popup_position');
		if( $sel1.hasClass(val1) ) {
			return;
		}		
        if( $sel1.hasClasses(['bottomLeft', 'bottomRight','topLeft', 'topRight']) ) {
			$sel1.removeClass('bottomLeft bottomRight topLeft topRight ');
		}
		$sel1.addClass(val1);



	});
})( jQuery );

