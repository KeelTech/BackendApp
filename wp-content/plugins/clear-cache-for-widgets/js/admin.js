jQuery(function($) {
  $( document ).on( 'click', '.ccfm-notice-hosting .notice-dismiss', function ( e ) {
    e.preventDefault();
    var notice = $(this).closest('.ccfm-notice-hosting');
    $.post( ajaxurl, {
        action: 'ccfm-notice-response',
        nonce: ccfm_admin.nonce,
      }, function( data ){
        notice.hide();
      }, 'json' );
  } );
});