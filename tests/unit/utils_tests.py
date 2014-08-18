# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from mock import patch

from django.db.models import get_model

from eway.utils import is_transaction_suspicious

try:
    from oscar.test.factories import create_order
except ImportError:
    from oscar_testsupport.factories import create_order

Transaction = get_model('eway', 'Transaction')
RequestLog = get_model('eway', 'RequestLog')


def test_check_transaction_without_access_code(transactional_db):
    transaction = Transaction(access_code='')
    assert is_transaction_suspicious(transaction) is True


@patch('eway.utils.eway_gw')
def test_check_transaction_without_order_number(eway_gw, transactional_db):
    transaction = Transaction(
        access_code='valid-access-code', order_number='')
    assert is_transaction_suspicious(transaction) is False


@patch('eway.utils.eway_gw')
def test_check_transaction_with_valid_order(eway_gw, transactional_db):
    order = create_order()
    transaction = Transaction.objects.create(
        access_code='valid-access-code', order_number=order.number)
    RequestLog.objects.create(transaction=transaction, response_code='00')
    assert is_transaction_suspicious(transaction) is False


@patch('eway.utils.eway_gw')
def test_check_transaction_without_valid_order(eway_gw, transactional_db):
    transaction = Transaction.objects.create(
        access_code='valid-access-code', order_number='12345678')
    RequestLog.objects.create(transaction=transaction, response_code='00')
    assert is_transaction_suspicious(transaction) is True


@patch('eway.utils.eway_gw')
def test_check_transaction_rejected_by_eway(eway_gw, transactional_db):
    transaction = Transaction.objects.create(
        access_code='valid-access-code', order_number='12345678')
    RequestLog.objects.create(transaction=transaction, response_code='99')
    assert is_transaction_suspicious(transaction) is False
