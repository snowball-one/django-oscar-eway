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

OrderNumberGenerator = get_class('order.utils', 'OrderNumberGenerator')
PaymentError = get_class('payment.exceptions', 'PaymentError')
CheckoutSessionData = get_class('checkout.utils', 'CheckoutSessionData')


class EwayPaymentDetailMixin(object):
    facade = Facade()

    def get_context_data(self, **kwargs):
        ctx = super(EwayPaymentDetailMixin, self).get_context_data(**kwargs)

        if self.preview:
            bankcard_form = forms.BankcardForm(self.request.POST)
        else:
            bankcard_form = forms.BankcardForm()

        ctx['bankcard_form'] = kwargs.get('bankcard_form', bankcard_form)
        ctx['payment_method'] = self.checkout_session.payment_method()

        if not 'form_action_url' in ctx:
            ctx['form_action_url'] = reverse('checkout:preview')

        return ctx

    def post(self, request, *args, **kwargs):
        """
        This method is designed to be overridden by subclasses which will
        validate the forms from the payment details page. If the forms are
        valid then the method can call submit().
        """
        error_response = self.get_error_response()
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
        if compat.USES_NEW_STRATEGY_PATTERN:
            total = self.get_order_totals(
                basket, self.get_shipping_method(basket))
            total_incl_tax = total.incl_tax
        else:
            total_incl_tax, __ = self.get_order_totals(basket)

        try:
            billing_address = self.get_billing_address()
        except AttributeError:
            billing_address = self.get_default_billing_address()

        if compat.USES_NEW_STRATEGY_PATTERN:
            shipping_address = self.get_shipping_address(basket)
        else:
            shipping_address = self.get_shipping_address()

        billing_address = billing_address or shipping_address

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
