(function () {
    var eway = eway || {};

    eway.rapid = {
        orderFormId: null,
        ewayFormId: null,
        init: function (options) {
            options = options || {};

            var ep = eway.rapid;

            ep.orderFormId = options.orderFormId || "#place-order-form";
            ep.ewayFormId = options.ewayFormId || "#eway-form";

            var form = $(ep.orderFormId);
            form.submit(function (ev) {
                ev.preventDefault();
                $(this).unbind('submit');
                eway.rapid.processTransaction($(ep.ewayFormId)[0]);
            });
        },
        processTransaction: function (form) {
            // call eWAY to process the request
            eWAY.process(form, {
                autoRedirect: false,
                onComplete: function (data) {
                    eway.rapid.handleResponse(data);
                },
                onError: function (e) {
                    eway.rapid.handleResponse(data);
                },
                onTimeout: function (e) {
                    eway.rapid.handleResponse(data);
                }
            });
        },
        handleResponse: function (data) {
            var ep = eway.rapid,
                orderForm = $(ep.orderFormId);

            $(ep.ewayFormId).remove();
            orderForm.submit();
        }
    };

    eway.rapid.init();
})();
