jQuery(document).ready(function() {
    jQuery("input[placeholder*='name']").on("input", function(){
     var name = jQuery(this).val()
     console.log('in');
     console.log(name);
    })
    console.log('out');
    var email = jQuery("input[name='email']").val()
    var age = jQuery("input[id*='age']").val()
    var education = jQuery("input[id*='education']").val()
    var canadian_educational_credential = jQuery("input[id*='Canadian educational credential']").val()
    var language_test = jQuery("input[id*='language_test']").val()
    var work_experince = jQuery("input[id*='work_experince']").val()
    var certificate_of_qualification = jQuery("input[id*='certificate of qualification']").val()
    var job_offer = jQuery("input[id*='job offer']").val()
    var job_skill_type = jQuery("input[id*='job_skill_type']").val()

    jQuery.ajax({
        type : 'POST',
        url : 'api/v1/eligibility/eligibility_calculator',
        data : {
            'name' : name,
            'email' : email,
            'age' : age,
            'education' : education,
            'canadian_educational_credential' : canadian_educational_credential,
            'language_test' : language_test,
            'work_experince' : work_experince,
            'certificate_of_qualification' : certificate_of_qualification,
            'job_offer' : job_offer,
            'job_skill_type' : job_skill_type,
        },
        //dataType : 'json',
        //headers : {},

        success : function(response) 
        {
            console.log('success');
        },
        
        error : function() {
            //alert error message
        }
});
});
