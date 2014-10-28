# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import


class OscarStrategyMixin(object):
    """
    Oscar versions: >=0.6 and <0.8

    Implement specific functionality for the ``PaymentDetailView`` in Oscar's
    ``checkout`` app. This implementation relies on the new strategy pattern
    introduced in version 0.6 of Oscar.
    """

    def get_total_incl_tax_COMPAT(self, basket, shipping_address):
        shipping_method = self.get_shipping_method(
            basket=basket, shipping_address=shipping_address)

        # Oscar 0.8 introduced a new (thread-safe) implementation of the
        # shipping methods that requires a slightly different calculation
        # of the shipping costs. We try the *new* way first and fall back
        # to the old way
        try:
            shipping_charge = shipping_method.calculate(basket)
        except AttributeError:
            shipping_charge = shipping_method

        total = self.get_order_totals(basket, shipping_charge)
        return total.incl_tax

    def get_shipping_address_COMPAT(self, basket):
        return self.get_shipping_address(basket)

    def get_billing_address_COMPAT(self, shipping_address):
        try:
            billing_address = self.get_billing_address(shipping_address)
        except AttributeError:
            billing_address = self.get_default_billing_address()
        return billing_address or shipping_address


class OscarPreStrategyMixin(object):
    """
    Oscar versions: <0.6

    This implements Oscar-specific functionality in the ``PaymentDetailView``
    for version of Oscar that **don't** implement the strategy pattern
    introduced in version 0.6.
    """

    def get_total_incl_tax_COMPAT(self, basket, shipping_address):
        total_incl_tax, __ = self.get_order_totals(basket)
        return total_incl_tax

    def get_shipping_address_COMPAT(self, basket):
        return self.get_shipping_address()

    def get_billing_address_COMPAT(self, shipping_address):
        billing_address = self.get_default_billing_address()
        return billing_address or shipping_address
