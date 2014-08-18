# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.conf import settings

from oscar.core.loading import get_classes

from eway.rapid import gateway
from eway import PURCHASE  # noqa


(RedirectRequired, UnableToTakePayment, PaymentError) = get_classes(
    'payment.exceptions',
    ['RedirectRequired', 'UnableToTakePayment', 'PaymentError'])


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class Facade(object):

    def __init__(self):
        self.gateway = gateway.Gateway(
            getattr(settings, 'EWAY_API_KEY', gateway.EWAY_API_KEY),
            getattr(settings, 'EWAY_PASSWORD', gateway.EWAY_PASSWORD))

        self.currency = getattr(
            settings, 'EWAY_CURRENCY', gateway.EWAY_CURRENCY)

    def token_payment(self, order_number, total_incl_tax, redirect_url,
                      billing_address, token_customer_id=None,
                      shipping_address=None, customer_ip=None,
                      basket=None, options=None, **kwargs):
        #TODO extract items from basket

        response = self.gateway.token_payment(
            order_number=order_number,
            total_incl_tax=total_incl_tax,
            redirect_url=redirect_url,
            token_customer_id=token_customer_id,
            customer_ip=customer_ip,
            billing_address=billing_address,
            #TODO We need to get the actual shipping address created
            # and provide it to the token_payment method
            #NOTE this is the shipping address used in Rapid NOT the
            # Oscar shipping address
            shipping_address=shipping_address,
            #TODO We need to get the actual basket items created
            # and provide it to the token_payment method
            items=None,
            options=options,
            **kwargs)
        return response

    def get_access_code_result(self, access_code):
        return self.gateway.get_access_code_result(access_code)
