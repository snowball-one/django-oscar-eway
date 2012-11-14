from django.db import models
from django.utils.translation import ugettext_lazy as _


class Transaction(models.Model):
    # Note we don't use a foreign key as the order hasn't been created
    # by the time the transaction takes place
    order_number = models.CharField(max_length=128, db_index=True, null=True)
    # the token ID that is used when an existing customer is trying
    # use a previously used card. This can be empty for anonymous
    # user's or if this is the first transaction
    token_customer_id = models.CharField(
        max_length=16,
        db_index=True,
        null=True
    )

    # Transaction type
    request_url = models.CharField(max_length=800, null=True)
    method = models.CharField(max_length=100, null=True)
    transaction_id = models.CharField(max_length=100, null=True)

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

    def add_response_codes(self, errors):
        for error in errors:
            erc, __ = ResponseCode.objects.get_or_create(
                code=error.code,
                message=error.message,
            )
            erc.transactions.add(self)

    class Meta:
        ordering = ('-date_created',)

    def __unicode__(self):
        return u'%s txn for order %s - ref: %s, message: %s' % (
            self.method,
            self.order_number,
            self.transaction_id,
            self.response_message,
        )


class ResponseCode(models.Model):
    code = models.CharField(_("Code"), unique=True, max_length=10)
    message = models.CharField(_("Message"), max_length=255)
    transactions = models.ManyToManyField(
        Transaction,
        related_name="response_messages"
    )

    def __unicode__(self):
        return "[%s] %s" % (self.code, self.message)
