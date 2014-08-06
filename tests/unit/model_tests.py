# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import get_model

try:
    from oscar.test.factories import create_order
except ImportError:
    from oscar_testsupport.factories import create_order

Transaction = get_model('eway', 'Transaction')


def test_can_set_order_from_number(transactional_db):
    order = create_order()

    transaction = Transaction.objects.create(access_code='imaginary-code')
    assert transaction.order_number == ''
    assert transaction.order is None

    transaction.order_number = order.number
    transaction.save()

    new_transaction = Transaction.objects.get(id=transaction.id)
    assert new_transaction.order_number == unicode(order.number)
    assert new_transaction.order == order
    assert new_transaction.status == new_transaction.IN_PROGRESS
