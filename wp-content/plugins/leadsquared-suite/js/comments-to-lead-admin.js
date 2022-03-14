jQuery(document).ready(function($){
    // Get Plugin url 
	var plugin_url = object_name.plugin_url;
	
	//Add alt class to TR
	$('#comment-form-config-view tr:even').addClass('alt');
		
	// Initialise the second table specifying a dragClass and an onDrop function that will display an alert
	$("#comment-form-config-view").tableDnD({
	        onDrop: function(table, row) {
			    	},
		    dragHandle: ".dragHandle"
    });
	
	$("#comment-form-config-view tr").hover(function() {
	        $(this).addClass('lsdragcolor');
			$(this).attr('id', 'dragcolor-border'); 
	        $(this.cells[4]).addClass('showDragHandle');
    }, function() {
	        $(this).removeClass('lsdragcolor'); 
			$(this).removeAttr('id'); 
			$(this.cells[4]).removeClass('showDragHandle');
    });
		
	//add_field_type
	$("#add-field-type").live("change", function(){
	$("#add_field_type").html('<img src="'+plugin_url+'/images/wpspin_light.gif" />');
	var add_value = $(":selected", $(this)).val();
	var add_text  = $(":selected", $(this)).text();
	var data = {
		          action: 'load_field_ajax_request',
		          'add_text': add_text,
	             };
	  $.post(ajaxurl, data, function(response) {
		var str = response;
		var ret = str.split(",");
		$('#leads_field_type').val(ret[0]);
		$('#leads_schemaname').val(ret[1]);
		$("#add_field_type").html(ret[0]);
	});
	});
	
	$("#name-field-type").live("change", function(){
	var name_value = $(":selected", $(this)).val();
	var name_text  = $(":selected", $(this)).text();
	if(name_value == '') { alert("Please configure Security Credentials before you setup form field."); return false; }
	$("#name_field_type").html('<img src="'+plugin_url+'/images/wpspin_light.gif" />');
	var data = {
		          action: 'load_field_ajax_request',
		          'name_text': name_text,
	             };
	  $.post(ajaxurl, data, function(response) {
	    var str = response;
		var ret = str.split(",");
		$('#add_label_name').val(ret[0]);
		$('#leads_author_schemaname').val(ret[1]);
		$("#name_field_type").html(ret[0]);
	});
    });
	
	//
	$("#email-field-type").live("change", function(){
	var email_value = $(":selected", $(this)).val();
	var email_text  = $(":selected", $(this)).text();
	if(email_value == '') { alert("Please configure Security Credentials before you setup form field."); return false; }
	$("#email_field_type").html('<img src="'+plugin_url+'/images/wpspin_light.gif" />');
	var data = {
		          action: 'load_field_ajax_request',
		          'email_text': email_text,
	             };
	  $.post(ajaxurl, data, function(response) {
	    var str = response;
		var ret = str.split(",");
		$('#add_label_email').val(ret[0]);
		$('#leads_email_schemaname').val(ret[1]);
		$("#email_field_type").html(ret[0]);
	});
    });
	
	//
	$("#comment-field-type").change(function(){
	  var comment_value = $(":selected", $(this)).val();
	  var comment_text  = $(":selected", $(this)).text();
	  if(comment_value == '') { alert("Please configure Security Credentials before you setup form field."); return false; }
	  $("#comment_field_type").html('<img src="'+plugin_url+'/images/wpspin_light.gif" />');
	  var data = {
		          action: 'load_field_ajax_request',
		          'comment_text': comment_text,
	             };
	  $.post(ajaxurl, data, function(response) {
	    var str = response;
		var ret = str.split(",");
		$('#add_label_comment').val(ret[0]);
		$('#leads_comment_schemaname').val(ret[1]);
		$("#comment_field_type").html(ret[0]);
	});
    });
	//
	$(".dynamic-type-field").live("change", function(){
        var id = $(this).attr("id");
		var dynamic_value = $(":selected", $(this)).val();
	    var dynamic_text  = $(":selected", $(this)).text();
		if(dynamic_value == '') { alert("Please configure Security Credentials before you setup form field."); return false; }
		$("#ajax-field-"+id).html('<img src="'+plugin_url+'/images/wpspin_light.gif" />');
		var data = {
		          action: 'load_field_ajax_request',
		          'dynamic_files'      : dynamic_text,
	             };
		$.post(ajaxurl, data, function(response) {
		var str = response;
		var ret = str.split(",");
		$('#field-'+id).val(ret[0]);
		$('#schemaname-'+id).val(ret[1]);
		$("#ajax-field-"+id).html(ret[0]);
	});		 
    });
	//
	$(".delete-field a").click(function(e) {
	e.preventDefault();
	var id = $(this).attr("id");
	var a = confirm("Are you sure you wish to delete this?");		
	var data = {
		          action: 'load_field_ajax_request',
		          'delete_field'      : id,
	             };
	if(a) {
	          $.post(ajaxurl, data, function(response) {
			  window.location = $('.delete-field a').attr('href');
	});
	}
    });
	
	//cancel-add
	$("#cancel-add").click(function() {
		$("#add_field_type").text('--');
	});
	//
	$("#cancel").click(function() {
		$("#name_field_type").text('Text');
		$("#email_field_type").text('Email');
		$("#comment_field_type").text('Text');
		$(".field_dynamic_type_default").each(function(index, value) { 
		   	var field_id   = $(this).attr('id'); 
			var field_text = $(this).text(); 
			$("#ajax-field-dynamic-type-"+index).text(field_text);
			});
    });
	//
	$("#check_activity_status").click(function(){
	$("#activity_type").html('<img src="'+plugin_url+'/images/wpspin_light.gif" />');
	    if (!$(this).is(':checked')) {
            //return confirm("Are you sure?");
			$("#activity_type").html('');
        }
		else {
		     //activity_type
			 var data = {
		          action: 'load_prospect_activity_request',
		          'status': 1,
	             };
	         $.post(ajaxurl, data, function(response) {
			 $("#prospect_checkbox").css("width","210px");
		     $("#activity_type").html(response);
		     });
		}
	});
});