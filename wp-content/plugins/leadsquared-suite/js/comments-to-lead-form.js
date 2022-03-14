jQuery('document').ready(function($){
    // Get Plugin url 
	var plugin_url      = object_name.plugin_url;
	/*************** Comment form captcha refresh ************************/
 	$("#comment-captcha").click(function(e) {
	e.preventDefault();
	var rand = Math.random();
	var id = $(this).attr("id");
	var captcha_id = $('#captcha_session').attr("id");
	$("#captcha-image").attr({src : plugin_url+'inc/captcha.php?uniqid='+rand,
	});
	$('#comments2lead_captcha').val(rand);
	});
	/******** End ********/
	$('input#email').blur(function (){
        $('input[name="ProspectID"]').val(MXCProspectId);
    });
	$('#commentform').submit(function(){
	    var captcha  = $('input[name="captcha"]').val();
		$('#comment-status').find('span').remove();
		if(!( captcha )) {
		    alert('Please enter the correct security code shown in the image above.');
			$( 'input[name="captcha"]' ).focus();
		    return false;  
        }
		else {
		    return true;
		}
    });
});


    


