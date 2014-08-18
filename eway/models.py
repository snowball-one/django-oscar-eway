# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging

from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from . import rapid

logger = logging.getLogger('eway')


class ModificationMixin(models.Model):
    date_created = models.DateTimeField(_("date created"))
    date_modified = models.DateTimeField(_("date modified"))

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.date_created:
            self.date_created = now
        self.date_modified = now
        return super(ModificationMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class Transaction(ModificationMixin):
    """
    A representation of a EWay transaction for a specific Oscar order.
    """
    IN_PROGRESS = 'in progress'
    COMPLETED = 'completed'
    SUSPICIOUS = 'suspicious'

    STATUSES = (
        (IN_PROGRESS, _("in progress")),
        (COMPLETED, _("completed")),
        (SUSPICIOUS, _("suspicious"))
    )

    access_code = models.CharField(
        _("access code"), max_length=255, blank=True)
    token_customer_id = models.CharField(
        _("token customer ID"), max_length=16, blank=True, default='')
    transaction_id = models.CharField(
        _("transaction ID"), max_length=100, blank=True, default='')

    amount = models.DecimalField(
        _("amount"), decimal_places=2, max_digits=12, blank=True, null=True)

    basket = models.ForeignKey(
        'basket.Basket', verbose_name=_("basket"),
        related_name='eway_transactions', null=True, on_delete=models.SET_NULL)

    # we use this to store the order number in case an order is deleted. This
    # is automatically populated when saving the model
    order_number = models.CharField(
        _("order number"), max_length=255, blank=True, default='')

    status = models.CharField(
        _("status"), max_length=255, default=IN_PROGRESS, choices=STATUSES)

    @cached_property
    def is_completed(self):
        return self.status == self.COMPLETED

    @cached_property
    def last_request_log(self):
        logs = self.request_logs.all()[:1]
        if len(logs):
            return logs[0]
        return None

    @cached_property
    def is_approved(self):
        log = self.last_request_log
        if not log:
            return False
        return log.response_code == rapid.TRANSACTION_APPROVED

    @cached_property
    def is_rejected(self):
        return not self.is_approved

    @cached_property
    def response_code(self):
        try:
            return self.last_request_log.response_code
        except AttributeError:
            return ''

    @cached_property
    def response_message(self):
        try:
            return self.last_request_log.response_message
        except AttributeError:
            return ''

    @cached_property
    def order(self):
        if not self.order_number:
            return

        Order = models.get_model('order', 'Order')
        try:
            return Order.objects.get(number=self.order_number)
        except Order.DoesNotExist:
            logger.info(
                "could not find order with number '{0}', not setting order "
                "on transaction: {1}".format(self.order_number, unicode(self)))
            return None

    def __unicode__(self):
        txn_id = self.transaction_id or self.access_code
        return "Transaction {0}".format(txn_id[:30])

    class Meta:
        ordering = ('-date_created',)
        verbose_name = _("transaction")
        verbose_name_plural = _("transactions")


class RequestLog(ModificationMixin):
    """
    Log entry for requests submitted to the EWay API.
    """
    transaction = models.ForeignKey(
        'eway.Transaction', verbose_name=_("transaction"),
        related_name="request_logs")

    url = models.TextField(_("request URL"), default='')
    method = models.CharField(_("request_method"), max_length=255, blank=True)

    request = models.TextField(_("request message"), blank=True)
    response = models.TextField(_("response message"), blank=True, default='')

    response_code = models.CharField(
        _("response code"), max_length=2, blank=True, default='')
    response_message = models.CharField(
        _("response message"), max_length=255, blank=True, default='')

    errors = models.TextField(_("errors"), blank=True, default='')

    def __unicode__(self):
        return "Request '{0}' for TXN {1}".format(
            self.method, self.transaction.transaction_id)

    class Meta:
        ordering = ('-date_created',)
        verbose_name = _("request log")
        verbose_name_plural = _("request logs")
