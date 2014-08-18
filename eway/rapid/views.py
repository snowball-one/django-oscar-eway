# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from oscar.core.loading import get_class

from .facade import Facade
from .. import compat
from .. import PURCHASE, PAYMENT_METHOD_EWAY


BankcardModel = get_model('payment', 'Bankcard')
PaymentDetailsView = get_class('checkout.views', 'PaymentDetailsView')

PaymentError = get_class('payment.exceptions', 'PaymentError')
SourceType = get_model('payment', 'SourceType')
Source = get_model('payment', 'Source')


class RapidResponseView(PaymentDetailsView):
    facade = Facade()

    def get(self, request, *args, **kwargs):
        self.access_code = request.GET.get('AccessCode', None)

        if compat.USES_NEW_STRATEGY_PATTERN:
            return self.submit(**self.build_submission())
        else:
            return self.submit(request.basket)

    def get_bankcard_details(self):
        kwargs = self.checkout_session._get('bankcard', 'bankcard_fields')
        if not kwargs:
            return {}
        expiry_date = datetime.strptime(kwargs.get('expiry_date'), "%m/%Y").date()
        kwargs['expiry_date'] = expiry_date
        return kwargs

    def set_bankcard_details(self, bankcard_kwargs):
        self.checkout_session._unset('bankcard', 'bankcard_fields')
        self.checkout_session._set('bankcard', 'bankcard_fields', bankcard_kwargs)

    def store_bankcard(self, token_customer_id):
        kwargs = self.get_bankcard_details()

        if not kwargs:
            return

        kwargs.update({
            'user': self.request.user,
            'partner_reference': token_customer_id,
        })

        try:
            bankcard = BankcardModel.objects.get(
                user=self.request.user,
                partner_reference=token_customer_id,
            )
        except BankcardModel.DoesNotExist:
            bankcard = BankcardModel.objects.create(**kwargs)
        else:
            BankcardModel.objects.filter(pk=bankcard.id).update(**kwargs)

    def handle_payment(self, order_number, total, **kwargs):
        response = self.facade.get_access_code_result(self.access_code)

        # this is required because the new strategy pattern introduced in
        # Oscar 0.6 changes the data passed into this method. This is purely
        # for backwards-compatibility
        try:
            total_incl_tax = total.incl_tax
        except AttributeError:
            total_incl_tax = total

        if not response.transaction_status:
            messages.error(
                self.request,
                _("We experienced a problem while processing your payment. "
                  "Please check your card details and try again. If the "
                  "problem persists, please contact us."))
            raise PaymentError(
                "received error(s) '%s' from eway for transaction #%s" % (
                    [(c.code, c.message) for c in response.response_message],
                    response.transaction_id,
                )
            )

        if self.request.user.is_authenticated():
            self.store_bankcard(response.token_customer_id)

        # Request was successful - record the "payment source".  As this
        # request was a 'pre-auth', we set the 'amount_allocated' - if we had
        # performed an 'auth' request, then we would set 'amount_debited'.
        source_type, __ = SourceType.objects.get_or_create(
            name=PAYMENT_METHOD_EWAY
        )
        source = Source(
            source_type=source_type,
            currency=settings.EWAY_CURRENCY,
            amount_allocated=total_incl_tax,
            amount_debited=total_incl_tax,
            reference=response.transaction_id
        )
        self.add_payment_source(source)

        # Also record payment event
        self.add_payment_event(PURCHASE, total_incl_tax)

    def render_to_response(self, context, **response_kwargs):
        if 'error' in context:
            return HttpResponseRedirect(reverse('checkout:payment-details'))
        return super(RapidResponseView, self).render_to_response(
            context,
            **response_kwargs
        )
