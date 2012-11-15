from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from oscar.core.loading import get_class
from oscar.apps.checkout.views import PaymentDetailsView as OscarPaymentDetailsView
from oscar.apps.payment.models import SourceType, Source

from eway.rapid import forms, gateway, facade

OrderNumberGenerator = get_class('order.utils', 'OrderNumberGenerator')
PaymentError = get_class('payment.exceptions', 'PaymentError')


class PaymentDetailsView(OscarPaymentDetailsView):
    template_name = 'checkout/payment_details.html'
    facade = facade.Facade()

    def get_context_data(self, **kwargs):
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        if self.preview:
            bankcard_form = forms.BankcardForm(self.request.POST)
        else:
            bankcard_form = forms.BankcardForm()
        ctx['bankcard_form'] = kwargs.get('bankcard_form', bankcard_form)
        return ctx

    def post(self, request, *args, **kwargs):
        """
        This method is designed to be overridden by subclasses which will
        validate the forms from the payment details page. If the forms are valid
        then the method can call submit()
        """
        error_response = self.get_error_response()
        if error_response:
            return error_response

        if self.preview:
            # We use a custom parameter to indicate if this is an attempt to place an order.
            # Without this, we assume a payment form is being submitted from the
            # payment-details page
            if request.POST.get('action', '') == 'place_order':
                return self.submit(request.basket)

            try:
                response = self.get_eway_access_code(request.basket)
            except gateway.RapidError:
                messages.error(
                    self.request,
                    "invalid payment details. please try again"
                )
                return HttpResponseRedirect(reverse('checkout:payment-details'))

            data = self.request.POST.copy()
            data['EWAY_ACCESSCODE'] = response.access_code
            return self.render_preview(
                request,
                form_action_url=response.form_action_url,
                bankcard_form=forms.BankcardForm(data),
            )

        # Posting to payment-details isn't the right thing to do
        return self.get(request, *args, **kwargs)

    def get_eway_access_code(self, basket):
        order_number = self.generate_order_number(basket)
        total_incl_tax, total_excl_tax = self.get_order_totals(basket)

        try:
            billing_address = self.get_billing_address()
        except AttributeError:
            billing_address = self.get_default_billing_address()

        shipping_address = self.get_shipping_address()
        billing_address = billing_address or shipping_address

        redirect_url = "http://%s%s" % (
            self.request.META['HTTP_HOST'],
            reverse('checkout:preview'),
        )

        response = self.facade.start_token_payment(
            order_number,
            total_incl_tax,
            redirect_url=redirect_url,
            #token_customer_id=token_customer_id,
            billing_address=billing_address,
            shipping_address=shipping_address,
        )
        return response

    def handle_payment(self, order_number, total_incl_tax,
                       token_customer_id=None, **kwargs):

        response = self.facade.get_access_code_result(
            self.request.POST.get('access_code')
        )

        if not response.transaction_status:
            raise PaymentError(
                "received error(s) '%s' from eway for transaction #%s" % (
                    [(c.code, c.message) for c in response.response_message],
                    response.transaction_id,
                )
            )

        #TODO store token_customer_id with user
        response.token_customer_id
        #TODO store transaction number

        # Request was successful - record the "payment source".  As this
        # request was a 'pre-auth', we set the 'amount_allocated' - if we had
        # performed an 'auth' request, then we would set 'amount_debited'.
        source_type, _ = SourceType.objects.get_or_create(name='Eway')
        source = Source(
            source_type=source_type,
            currency=settings.EWAY_CURRENCY,
            amount_debited=total_incl_tax,
            reference=response.transaction_id,
        )
        self.add_payment_source(source)

        # Also record payment event
        self.add_payment_event('debited', total_incl_tax)

    def generate_order_number(self, basket):
        if self.checkout_session.get_order_number():
            return self.checkout_session.get_order_number()

        generator = OrderNumberGenerator()
        order_number = generator.order_number(basket)
        self.checkout_session.set_order_number(order_number)
        return order_number
