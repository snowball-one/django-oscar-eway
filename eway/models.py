import re

from django.db import models
from django.utils.translation import ugettext_lazy as _


class EwayTransaction(models.Model):
    # Note we don't use a foreign key as the order hasn't been created
    # by the time the transaction takes place
    order_number = models.CharField(
        max_length=128,
        db_index=True,
        null=True
    )
    # the token ID that is used when an existing customer is trying
    # use a previously used card. This can be empty for anonymous
    # user's or if this is the first transaction
    token_customer_id = models.CharField(
        max_length=16,
        db_index=True,
        null=True
    )

    # Transaction type
    txn_url = models.CharField(max_length=800, null=True)
    txn_method = models.CharField(max_length=12, null=True)
    txn_ref = models.CharField(max_length=16, null=True)

    amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        blank=True,
        null=True
    )

    response_code = models.CharField(max_length=2, null=True)
    response_message = models.CharField(max_length=255, null=True)

    # For debugging purposes
    request_json = models.TextField()
    response_json = models.TextField(null=True)

    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    #def save(self, *args, **kwargs):
    #    if not self.pk:
    #        cc_regex = re.compile(r'\d{12}')
    #        self.request_xml = cc_regex.sub('XXXXXXXXXXXX', self.request_xml)
    #        ccv_regex = re.compile(r'<Cvc2>\d+</Cvc2>')

    #        self.request_xml = ccv_regex.sub('<Cvc2>XXX</Cvc2>',
    #                                         self.request_xml)

    #        pw_regex = re.compile(r'<PostPassword>.*</PostPassword>')
    #        self.request_xml = pw_regex.sub('<PostPassword>XXX</PostPassword>',
    #                                        self.request_xml)

    #    super(EwayTransaction, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s txn for order %s - ref: %s, message: %s' % (
            self.txn_method,
            self.order_number,
            self.txn_ref,
            self.response_message,
        )


class EwayResponseCode(models.Model):
    code = models.CharField(_("Code"), unique=True, max_length=10)
    message = models.CharField(_("Message"), max_length=255)
    transactions = models.ManyToManyField(
        EwayTransaction,
        related_name="response_messages"
    )

    def __unicode__(self):
        return "[%s] %s" % (self.code, self.message)
