from django.conf import settings

from oscar.core.loading import get_classes

from eway.rapid import gateway

PURCHASE = 'Purchase'


(RedirectRequired,
 UnableToTakePayment,
 PaymentError) = get_classes('payment.exceptions', [
     'RedirectRequired',
     'UnableToTakePayment',
     'PaymentError'
 ])


class Facade(object):

    def __init__(self):
        self.gateway = gateway.Gateway(
            getattr(settings, 'EWAY_API_KEY', gateway.EWAY_API_KEY),
            getattr(settings, 'EWAY_PASSWORD', gateway.EWAY_PASSWORD),
        )
        self.currency = getattr(
            settings,
            'EWAY_CURRENCY',
            gateway.EWAY_CURRENCY
        )

    def token_payment(self, order_number, total_incl_tax, redirect_url,
                            billing_address, token_customer_id=None,
                            shipping_address=None, customer_ip=None,
                            basket=None, **kwargs):
        response = self.gateway.token_payment(
            order_number=order_number,
            total_incl_tax=total_incl_tax,
            redirect_url=redirect_url,
            token_customer_id=token_customer_id,
            customer_ip=customer_ip,
            billing_address=billing_address,
            shipping_address=shipping_address,
            **kwargs
        )
        return response

    def get_access_code_result(self, access_code):
        return self.gateway.get_access_code_result(access_code)
