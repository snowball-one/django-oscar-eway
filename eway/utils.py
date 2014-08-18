# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging

from datetime import timedelta

from django.utils.timezone import now
from django.db.models import get_model

from .rapid import facade

Transaction = get_model('eway', 'Transaction')

logger = logging.getLogger('eway')
eway_gw = facade.Facade()


def check_dangling_transactions(minimum_age=None):
    """
    Check for transactions that are currently in progress and are at least
    of *minimum_age*. If no minimum age is specified, a default timedelta
    of **2 hours** is used.

    In the process, the transaction might be updated with data retrieved from
    eWay. In addition, suspicious transactions are marked as such in the
    transaction status.

    :param minimum_age: Minimum age of dangling transaction as timedelta.
    :type minimum_age: timedelta or None
    """
    if not minimum_age:
        minimum_age = timedelta(hours=2)

    cutoff_date = now() - minimum_age

    logger.info("Looking up all eway transactions started before: {0}".format(
        cutoff_date.isoformat()))

    #get dangling transactions
    transactions = Transaction.objects.filter(
        date_created__lte=cutoff_date, status=Transaction.IN_PROGRESS)

    logger.info("Found {0} transactions that are in progress".format(
        len(transactions)))

    # check for suspicious transactions and mark them as such
    for transaction in transactions:
        if is_transaction_suspicious(transaction):
            transaction.status = transaction.SUSPICIOUS
            transaction.save()


def is_transaction_suspicious(transaction, check_eway=True):
    """
    Check if the *transaction* is suspicious. A transaction is considered to
    be suspicious if it doesn't have an **access code** assigned to it or if
    its order number doesn't correspond to an order in the system.

    :param transaction: an instance of the eway ``Transaction`` model.
    :returns: ``True`` if transaction is suspicious, ``False`` otherwise.
    """
    if not transaction.access_code:
        logger.error('could not find access code in transaction with '
                     'PK {0}'.format(transaction.id))
        return True

    if check_eway:
        # this updates the transaction with the latest details
        # retrieved from eWAY so we don't have to care about the
        # returned result
        eway_gw.get_access_code_result(transaction.access_code)

    if not transaction.order_number:
        logger.info(
            "ignoring transaction with PK {0}, no order number "
            "generated".format(transaction.id))
        return False

    if transaction.is_rejected and not transaction.order:
        logger.info(
            "transaction {0} was rejected and no order was generated. All "
            "good.".format(transaction.id))
        return False

    if transaction.is_approved and transaction.order:
        logger.info(
            "ignoring transaction with PK {0}, seems to be valid ".format(
                transaction.id))
        return False

    logger.error('transaction with PK {0} looks suspecious, flagging it '
                 'as suspicious.'.format(transaction.id))
    return True
