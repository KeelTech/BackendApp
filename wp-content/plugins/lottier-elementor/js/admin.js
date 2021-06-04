( function ( $ ) { // TODO: Make vanilla and modular

    "use strict";

    $(document).ready(function () {

        let mdpLottierElementor = window.mdpLottierElementor

        /** Subscribe form. */
        let $subscribeBtn = $('#mdp-subscribe');
        $subscribeBtn.on( 'click', function (e) {

            e.preventDefault();

            let mail = $('#mdp-subscribe-mail').val();
            let name = $('#mdp-subscribe-name').val();
            let plugin = 'lottier-elementor';
            let mailIndex = $('#mdp-subscribe-mail').parent().data('mdc-index');

            if (mail.length > 0 && window.MerkulovMaterial[mailIndex].valid) {

                $('#mdp-subscribe-name').prop("disabled", true);
                $('#mdp-subscribe-mail').prop("disabled", true);
                $('#mdp-subscribe').prop("disabled", true);

                $.ajax({
                    type: "GET",
                    url: "https://merkulove.host/wp-content/plugins/mdp-purchase-validator/esputnik/subscribe.php",
                    crossDomain: true,
                    data: 'name=' + name + '&mail=' + mail + '&plugin=' + plugin,
                    success: function (data) {

                        if (true === data) {
                            alert('We received your Subscription request. Now you need to confirm your subscription. Please check your inbox for an email from us.');
                        }

                    },
                    error: function (err) {
                        alert(err);
                    }
                });

            } else {
                window.MerkulovMaterial[mailIndex].valid = false;
            }

        });

        /** Check for Updates. */
        let $checkUpdatesBtn = $( '#mdp-updates-btn' );
        $checkUpdatesBtn.on( 'click', function ( e ) {

            e.preventDefault();

            /** Disable button and show process. */
            $checkUpdatesBtn.attr( 'disabled', true ).addClass( 'mdp-spin' ).find( '.material-icons' ).text( 'refresh' );

            /** Prepare data for AJAX request. */
            let data = {
                action: 'check_updates',
                nonce: mdpLottierElementor.nonce,
                checkUpdates: true
            };

            /** Do AJAX request. */
            $.post( mdpLottierElementor.ajaxURL, data, function( response ) {

                if ( response ) {
                    console.info( 'Latest version information updated.' );
                    location.reload();
                } else {
                    console.warn( response );
                }

            }, 'json' ).fail( function( response ) {

                /** Show Error message if returned some data. */
                console.error( response );
                alert( 'Looks like an Error has occurred. Please try again later.' );

            } ).always( function() {

                /** Enable button again. */
                $checkUpdatesBtn.attr( 'disabled', false ).removeClass( 'mdp-spin' ).find( '.material-icons' ).text( 'autorenew' );

            } );

        } );

    })

} ( jQuery ) );