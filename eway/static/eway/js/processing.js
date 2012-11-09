(function () {
    var eway = eway || {};

    eway.processing = {
        init: function () {
            console.log('initialising');
            var form = $('#place-order-form');

            form.submit(function (ev) {
                ev.preventDefault();
                $(this).unbind('submit');
                eway.processing.processTransaction($("#eway-form")[0]);
            });
        },
        processTransaction: function (form) {
            // call eWAY to process the request
            eWAY.process(form, {
                autoRedirect: false,
                onComplete: function (data) {
                    // this is a callback to hook into when the requests completes
                    console.log('The JSONP request has completed\r\n\r\nCLick OK to redirect and complete the process');

                    $("#eway-form").remove();
                    var orderForm = $('#place-order-form');
                    $('input[name=access_code]', orderForm).val(data.AccessCode);
                    orderForm.submit();

                    //if (data.Is3DSecure) {
                    //    window.location.replace(data.RedirectUrl);
                    //}
                },
                onError: function (e) {
                    // this is a callback you can hook into when an error occurs
                    alert('There was an error processing the request\r\n\r\nClick OK to redirect to your result/query page');
                    //window.location.replace(urlToRedirectOnError);
                },
                onTimeout: function (e) {
                    // this is a callback you can hook into when the request times out
                    alert('The request has timed out\r\n\r\nClick OK to redirect to your result/query page.');
                    //window.location.replace(urlToRedirectOnError);
                }
            });
        }
    };

    eway.processing.init();
})();
