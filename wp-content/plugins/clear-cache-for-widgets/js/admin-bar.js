jQuery(function($) {
    var in_progress = false;
    $('#wp-admin-bar-ccfm-link').on('click', function(e){
        e.preventDefault();
        if (in_progress) {
            return;
        }
        in_progress = true;
        var link = $(this);
        $.post(
            ccfm.ajax_url, {
                action: 'ccfm-ajax-ccfm',
                nonce: ccfm.nonce
            },
            function (json) {
                in_progress = false;
                if (json.success) {
                    link.append('<div class="ccfm-admin-bar-msg" style="background: rgba(0, 166, 0, .9);text-align: center;color: #fff;border-bottom-left-radius: 5px;border-bottom-right-radius: 5px;">Success!</div>');
                }
                else {
                    link.append('<div class="ccfm-admin-bar-msg" style="background: rgba(166, 0, 0, .9);text-align: center;color: #fff;border-bottom-left-radius: 5px;border-bottom-right-radius: 5px;">Failed</div>');
                }
                $('.ccfm-admin-bar-msg:last', link.closest('#wp-admin-bar-ccfm-link')).fadeOut(2000, function() {
                    $(this).remove();
                });
            }
        );
    });

});