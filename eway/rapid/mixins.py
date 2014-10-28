# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from oscar.core.loading import get_class

from . import forms
from . import gateway
from .facade import Facade
from .. import compat
from .. import PAYMENT_METHOD_EWAY


if compat.USES_NEW_STRATEGY_PATTERN:
    from eway.rapid.compat import OscarStrategyMixin as OscarPaymentMixin
else:
    from eway.rapid.compat import OscarPreStrategyMixin as OscarPaymentMixin


OrderNumberGenerator = get_class('order.utils', 'OrderNumberGenerator')
PaymentError = get_class('payment.exceptions', 'PaymentError')
CheckoutSessionData = get_class('checkout.utils', 'CheckoutSessionData')


class EwayPaymentDetailMixin(OscarPaymentMixin):
    facade = Facade()

    def get_context_data(self, **kwargs):
        ctx = super(EwayPaymentDetailMixin, self).get_context_data(**kwargs)

        if self.preview:
            bankcard_form = forms.BankcardForm(self.request.POST)
        else:
            bankcard_form = forms.BankcardForm()

        ctx['bankcard_form'] = kwargs.get('bankcard_form', bankcard_form)
        ctx['payment_method'] = self.checkout_session.payment_method()

        if 'form_action_url' not in ctx:
            ctx['form_action_url'] = reverse('checkout:preview')

        return ctx

    def post(self, request, *args, **kwargs):
        """
        This method is designed to be overridden by subclasses which will
        validate the forms from the payment details page. If the forms are
        valid then the method can call submit().
        """
        # get_error_response has been removed in Oscar 0.7 due to changes in
        # validating pre-conditions. This prevents failure in Oscar 0.7+
        try:
            error_response = self.get_error_response()
        except AttributeError:
            error_response = None

        if error_response:
            return error_response

        if self.preview:
            self.checkout_session.pay_by(PAYMENT_METHOD_EWAY)

            # We use a custom parameter to indicate if this is an attempt to
            # place an order. Without this, we assume a payment form is being
            # submitted from the payment-details page.
            if request.POST.get('action', '') == 'place_order':
                if compat.USES_NEW_STRATEGY_PATTERN:
                    return self.submit(**self.build_submission())
                else:
                    return self.submit(request.basket)

            return self.render_eway_preview(request)

        # Posting to payment-details isn't the right thing to do
        return self.get(request, *args, **kwargs)

    def render_eway_preview(self, request, **kwargs):
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
            request, form_action_url=response.form_action_url,
            bankcard_form=forms.BankcardForm(data))

    def get_eway_access_code(self, basket):
        order_number = self.generate_order_number(basket)

        shipping_address = self.get_shipping_address_COMPAT(basket)

        total_incl_tax = self.get_total_incl_tax_COMPAT(
            basket=basket, shipping_address=shipping_address)

        billing_address = self.get_billing_address_COMPAT(shipping_address)

        redirect_url = "http://%s%s" % (
            self.request.META['HTTP_HOST'], reverse('eway-rapid-response'))

        response = self.facade.token_payment(
            order_number, total_incl_tax, redirect_url=redirect_url,
            billing_address=billing_address, shipping_address=shipping_address)
        return response

    def generate_order_number(self, basket):
        if self.checkout_session.get_order_number():
            return self.checkout_session.get_order_number()

        generator = OrderNumberGenerator()
        order_number = generator.order_number(basket)
        self.checkout_session.set_order_number(order_number)
        return order_number
