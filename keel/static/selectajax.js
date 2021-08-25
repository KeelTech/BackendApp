jQuery(function($){
    $(document).ready(function(){
        $("#id_country").change(function(){
            $.ajax({
                type:"POST",
                data:{'country': $(this).val(),},
                url:"/api/v1/core/get-states/",
                // headers: {'X-CSRFToken': csrftoken},
                success: function(results) {
                    cols = document.getElementById("id_state");
                    cols.options.length = 0;
                    results.forEach((result) =>
                        cols.options.add(new Option(result.state, result.id))
                    );
                },
                error: function(e){
                    console.error(JSON.stringify(e));
                },
            });
        });
    }); 
});
jQuery(function($){
    $(document).ready(function(){
        $("#id_state").change(function(){
            $.ajax({
                type:"POST",
                data:{'state': $(this).val(),},
                url:"/api/v1/core/get-cities/",
                // headers: {'X-CSRFToken': csrftoken},
                success: function(results) {
                    cols = document.getElementById("id_city");
                    cols.options.length = 0;
                    results.forEach((result) =>
                        cols.options.add(new Option(result.city, result.id))
                    );
                },
                error: function(e){
                    console.error(JSON.stringify(e));
                },
            });
        });
    }); 
});