from oscar.apps.checkout.views import PaymentDetailsView as OscarPaymentDetailsView

from eway.rapid.mixins import EwayPaymentDetailMixin


class PaymentDetailsView(EwayPaymentDetailMixin, OscarPaymentDetailsView):
    template_name = 'checkout/payment_details.html'
