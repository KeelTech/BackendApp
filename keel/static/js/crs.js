$(document).ready(function () {
    var name = $("input[id*='name']")
    var email = $("input[name='email']")
    var age = $("input[id*='age']")
    var education = $("input[id*='education']")
    var canadian_educational_credential = $("input[id*='Canadian educational credential']")
    var language_test = $("input[id*='language_test']")
    var work_experince = $("input[id*='work_experince']")
    var certificate_of_qualification = $("input[id*='certificate of qualification']")
    var job_offer = $("input[id*='job offer']")
    var job_skill_type = $("input[id*='job_skill_type']")

    .ajax({
        type : 'POST',
        url : '/eligibility_calculator',
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
        dataType : 'json',
        headers : {'X-CSRFToken': csrftoken},

        success : function(response) {
            //return response
        },
        
        error : function() {
            //alert error message
        }
    })
})