(function( $ ) {
	'use strict';

	/**
	 * All of the code for your public-facing JavaScript source
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

	$(function(){   
	 	/**
	 	*	Layout Position eg: Bottomm Left or buttom right
	 	*/
	 	var temp = trustify_popup_params.trustify_popup_position;
	 	var $sel = $('.popup_position');

	 	if( $sel.hasClass(temp) ) {						
	 		return;
	 	}
	 	
	 	if( $sel.hasClasses(['bottomLeft', 'bottomRight']) ) {
	 		$sel.removeClass('bottomLeft bottomRight ');
	 	}	
	 	
	 	$sel.addClass(temp);

	 	/**
	 	*	Layout Transition eg: FadeIn  Left or FadeOut right 
	 	*/
	 	var temp = trustify_popup_params.trustify_popup_transition;
	 	var $sel = $('.popup_template');	
	 	if( $sel.hasClass(temp) ) {						
	 		return;
	 	}
	 	
	 	if( $sel.hasClasses(['fadeInLeft', 'fadeInUp', 'fadeInRight', 'bounceInRight', 'bounceInLeft', 'bounceInUp', 'flipInX', 'zoomIn', 'shake','swing','rollIn']) ) {
	 		$sel.removeClass('fadeInLeft fadeInUp fadeInRight bounceInRight bounceInLeft bounceInUp flipInX zoomIn shake swing rollIn');
	 	}	 	
	 	$sel.addClass(temp);	 
	});


    //Trigger popup for the first time (after popup_start_time)
    setTimeout(function () { 
    	loadPopupBox(); 
    }, trustify_popup_params.trustify_popup_start_time * 1000 );
    	
    //Loads the popup
    function loadPopupBox() {
        var StayTime = trustify_popup_params.trustify_popup_stay * 1000,
            auto_enable = trustify_popup_params.trustify_notification_type,
            edd = trustify_popup_params.trustify_edd_notice,
            woo = trustify_popup_params.trustify_woo_notice;
        if(woo == 1){
			showWooPopUpData();
        }else if(edd == 1){
			showEddPopUpData();
        }else if(auto_enable==1){
        	showRandomPopUpDataAuto();      
        }else{
            showRandomPopUpData();
        }

        setTimeout(function() {
            unloadPopupBox();
        }, StayTime);

    }

	function unloadPopupBox() {
        var x = trustify_popup_params.trustify_popup_range_from * 1; //making sure that it is a number
        var y = trustify_popup_params.trustify_popup_range_to * 1;
        var PopRange= Math.floor((Math.random() * (y-x)) + x + 1) * 1000;

        hidePopUp();
	      setTimeout(function () {
	        $('#popup_template').html(''); 
	      }, PopRange);
        setTimeout(function(){
			loadPopupBox();
		}, PopRange);
	}

    function showRandomPopUpDataAuto() {
        $.ajax({
            url: trustify_popup_params.ajax_url,
            type: 'post',
            data: { 'action': 'trustify_get_auto_notice' },
            success: function(data) {
                $('#popup_template').html(data);
            },
            complete:function(data){
		      showPopUp();
		    }
        });
    }     	

    function showRandomPopUpData() {
    	var pageId = $('#trustifyWrapper').attr('data-trustify-page-id');
    	var pageType = $('#trustifyWrapper').attr('data-offset');
        $.ajax({
            url: trustify_popup_params.ajax_url,
            type: 'post',
            data: { 
            'action': 'trustify_get_notice',
            'page_id': pageId,
            'page_type': pageType
            },
            success: function(data) {
	            var currentId = $(data).attr('id');
	            setIdsCookie(currentId);
	            $('#popup_template').html(data);
	            if(data.length<2){
	            	$('#trustifyWrapper').hide();
	            }
            },
            complete:function(data){
		      showPopUp();
		    }
        });
    }

    function showWooPopUpData(){
        $.ajax({
            url: trustify_popup_params.ajax_url,
            type: 'post',
            data: { 'action': 'trustify_get_woo_notice' },
            success: function(data) {
                var currentId = $(data).filter('.popup-item').attr('data-id');
                setIdsCookie(currentId);
                $('#popup_template').html(data);
	            if(data.length<2){
	            	$('#trustifyWrapper').hide();
	            }
            },
            complete:function(data){
		      showPopUp();
		    }
        });
    } 	

    function showEddPopUpData(){
        $.ajax({
            url: trustify_popup_params.ajax_url,
            type: 'post',
            data: { 'action': 'trustify_get_edd_notice' },
            success: function(data) {
                //var currentId = $(data).filter('.popup-item').attr('data-id');
                //setIdsCookie(currentId);
                $('#popup_template').html(data);
	            if(data.length<2){
	            	$('#trustifyWrapper').hide();
	            }
            },
            complete:function(data){
		      showPopUp();
		    }
        });
    }

    function setIdsCookie(currentId) {
        var trustifyIds = [];
        if ($.cookie('trustify_ids')) {
        	trustifyIds = JSON.parse($.cookie('trustify_ids'));
        }

        if (currentId) {
            trustifyIds.push(currentId);
        }

        $.cookie(
        	'trustify_ids',
			JSON.stringify(trustifyIds),
			{
				expires: 1,
				path: '/'
			}
		);
    }

   	var animateClass = trustify_popup_params.trustify_popup_transition;
	if(animateClass=='fadeInLeft' || animateClass=='swing' || animateClass=='shake'){
		var hide = 'fadeOutLeft';
	}else if(animateClass=='fadeInRight'){
		var hide = 'fadeOutRight';
	}else if(animateClass=='fadeInUp'){
		var hide = 'fadeOutDown';
	}else if(animateClass=='bounceInLeft'){
		var hide = 'bounceOutLeft';
	}else if(animateClass=='bounceInRight'){
		var hide = 'bounceOutRight';
	}else if(animateClass=='bounceInUp'){
		var hide = 'bounceOutDown';
	}else if(animateClass=='flipInX'){
		var hide = 'flipOutX';
	}else if(animateClass=='zoomIn'){
		var hide = 'zoomOut';
	}else if(animateClass=='rollIn'){
		var hide = 'rollOut'
	}

    function showPopUp() {
    	$('#trustifyWrapper').show();
        $('#popup_template').show();
        $('#popup_template').addClass(animateClass);
        $('#popup_template').removeClass(hide); 
    }

    function hidePopUp() {
    	$('#popup_template').removeClass(animateClass);
        $('#popup_template').addClass(hide); 
        setTimeout(function() {
            $('#trustifyWrapper').hide();
        }, 3000);
    }

    $(document).mouseover(function(){
        $('.popup-item .popup_close').on('click',function(){
            hidePopUp();
        });
    });

    /* Click Track */
    $(document).ready(function(){
	    $('body').on('click','.popup-item.woo-content a',function(){
	    	var Pid = $(this).parents('.popup-item').data('pid');
	        $.ajax({
	            url: trustify_popup_params.ajax_url,
	            type: 'post',
	            data: { 
	            	'action': 'trustify_click_track',
	            	'product_id': Pid
	            },
	            success: function(data) {

	            }
	        });
	    });
    });


})( jQuery );