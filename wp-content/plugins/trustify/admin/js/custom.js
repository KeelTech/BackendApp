jQuery(document).ready(function ($) {
    "use strict";
	//main tabs
	$(".trustify-settings-tab li").click(function (e) {
        e.preventDefault();
        var self = $(this);
        var dispstyle = self.attr("data-id");
        
        $(".tab-pane").hide();
        $(".trustify-settings-tab li").removeClass('active');
        self.closest('li').addClass('active');
        $("."+dispstyle+"").fadeIn();
    });

    //toggle for mannual post types
	$('.mifi-toggle-tab-header').on('click',function(){
	    $(this).toggleClass('mifi-toggle-active');
	    $(this).siblings('.mifi-toggle-tab-body').slideToggle();
	});

    /* Global Setting tabs toggle */

    $('body').on('click','.trustify-settings-tabs',function(){
      $('.trustify-settings-tabs').removeClass('toggle-active');
      $('.trustify-settings-wrap').slideUp();
      $(this).toggleClass('toggle-active');
      $(this).siblings('.trustify-settings-wrap').slideToggle();
    }); 

    /* Date Picker */
    $( 'input[name="DateFrom"]' ).datepicker({ dateFormat: "yy-mm-dd" }); 
    $( 'input[name="DateTo"]' ).datepicker({ dateFormat: "yy-mm-dd" });

    $('.trustify-date-filter #submit').on('click',function(){
      var from = $( 'input[name="DateFrom"]' ).val(),
          to = $( 'input[name="DateTo"]' ).val();
          if(from || to){
            document.location.href = 'edit.php?post_type=mifi&page=trustify-click-report&DateFrom='+from+'&DateTo='+to;
          }else{
            document.location.href = 'edit.php?post_type=mifi&page=trustify-click-report';
          }
    });

    //bg image
    var bg_image = $('.bg-image input').val();
    $('.popup_template').css('background-image', 'url(' + bg_image + ')');

    //Auto Notification Enable
    if ($('.auto-en-wrap input.chk-en').is(':checked')) {
    	$('.auto-en-wrap .notice').show();
    } 
    $('.auto-en-wrap .chk-en').click(function(){
    	$('.auto-en-wrap .notice').toggle();
    });

    $('.trustify-auto').hide();
    if ($('.auto-en-wrap input.chk-en').is(':checked')) {
      $('.trustify-auto').show();
    } 
    $('.auto-en-wrap .chk-en').click(function(){
      $('.trustify-auto').toggle();
    });

    //Woo Notification Enable
    if ($('.woo-en-wrap input.chk-en').is(':checked')) {
      $('.woo-en-wrap .notice').show();
    } 
    $(document).on('click','.woo-en-wrap .chk-en',function(){
      $('.woo-en-wrap .notice').toggle();
/*      if($('.edd-en-wrap .chk-en').hasClass('chkd')){
        $(this).prop("checked", false);
      }*/
    });

    //EDD Notification Enable
    if ($('.edd-en-wrap input.chk-en').is(':checked')) {
      $('.edd-en-wrap .notice').show();
    } 
    $(document).on('click','.edd-en-wrap .chk-en',function(){
      $('.edd-en-wrap .notice').toggle();
/*      if($('.woo-en-wrap .chk-en').hasClass('chkd')){
        $(this).prop("checked", false);
      }*/
    });

    //woo edd check
    $('.woo-edd').on('click',function(){
      $(this).toggleClass('chkd');
    });

   /* For repeater products */
    var tCount = $('#table_products_count').val();

    $('.docopy-table-product').click(function(){
        tCount++;
        $('.table-products-wrapper').append('<div class="single-product"><div class="single-section-title clearfix"><h4 class="product-title">Product '+tCount+' : </h4>'+
                                              '<div class="product-inputfield"><input type="text" name="trustify_auto_settings[trustify_autonotice_product][title]['+tCount+']" value="" required/></div>'+
                                              '<div class="product-imagefield clearfix"><input type="text" name="trustify_auto_settings[trustify_autonotice_product][url]['+tCount+']" placeholder="http://path/to/image.png" value="">'+
                                              '<span class="sme_galimg_ctrl"><a class="sme_add_galimg" href="#">Upload</a></span></div>'+
                                              '<div class="delete-table-product"><a href="javascript:void(0)" class="delete-product button">Delete Product</a></div>'+
                                              '</div></div>'
                                            );
        });
     $(document).on('click', '.delete-table-product > a', function(){
       $(this).parents('.single-product').remove();
    });   

     /** Upload Product Image **/
	$(document).on('click' , '.sme_galimg_ctrl .sme_add_galimg', function(e) {
      e.preventDefault();
        var $this = $(this);
      var image = wp.media({ 
        title: 'Upload Image',
        // mutiple: true if you want to upload multiple files at once
        multiple: false
      }).open()
      .on('select', function(e){
        // This will return the selected image from the Media Uploader, the result is an object
        var uploaded_image = image.state().get('selection').first();
        // We convert uploaded_image to a JSON object to make accessing it easier
        // Output to the console uploaded_image
        var image_url = uploaded_image.toJSON().url;
        // Let's assign the url value to the input field
        $this.parent('.sme_galimg_ctrl').prev('input').val(image_url);

        $this.parents('.trustify-main-settings').siblings('.trustify-backend-preview').find('.popup_template').css('background-image', 'url(' + image_url + ')');
      });
	});	

	//border enable live preview
    $('body').on('change','.chk-border',function(){       	
        $('.popup_template').toggleClass('border');
    });
    if ($('body .chk-border').is(':checked')) {
        $('.popup_template').removeClass('radius');
      $('body').on('change','.chk-border',function(){  
        $('.popup_template').toggleClass('b-radius');
      });
    }else{
      $('body').on('change','.chk-border',function(){  
        $('.popup_template').toggleClass('radius');
      });
    }

	//Border Color picker
	$("#popup_bordercolor").wpColorPicker(
		'option',
		'change',
		function (event, ui){
			var color = ui.color.toString();
			$('.popup_template').css('border-color', color);

		}
		);
	//on load
    var border_color = $('#popup_bordercolor').val();
    $('.popup_template.border').css('border-color', border_color);

  // Inner padding
  $('body').on('keyup','.trusify-inner-padding',function(){
    var place = $(this).data('place');
    var innerPadding = $(this).val();
    $('.popup-item').css("padding-"+place,innerPadding);
  });
  //on load
  $('.trusify-inner-padding').each(function(){
    var place = $(this).data('place');
    var inner_padding = $(this).val();
    $('.popup-item').css('padding-'+place,inner_padding); 
  });
    
    
  //Border Radius
	$('body').on('keyup','#trusify-border-radius',function(){
		var borderRadius = $(this).val();
		$('.popup_template.border').css( { "border-radius": borderRadius+"px" } );
	});
	//on load
    var border_radius = $('#trusify-border-radius').val();
    $('.popup_template.border').css( { "border-radius": border_radius+"px" } );
    
    //Border Width
	$('body').on('keyup','#trusify-border-width',function(){
		var borderWidth = $(this).val();
		$('.popup_template.border').css('border-width',borderWidth);
	});
	//on load
    var border_width = $('#trusify-border-width').val();
    $('.popup_template.border').css('border-width', border_width);

	//on load Border enable
    if ($('body .chk-border').is(':checked')) {
    	return;
    } else{
    	 $('.popup_template').removeClass('border');
    }



});

