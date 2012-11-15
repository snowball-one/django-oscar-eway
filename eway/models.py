from django.db import models
from django.utils.translation import ugettext_lazy as _


class Transaction(models.Model):
    """
    A transaction log entry for communication with the eWay API server.
    This logs the request URL used in the transaction, the raw JSON
    request and response as well as additional data depending on the
    type of the transaction method
    """
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
        if errors:
            self.response_message = u'Successful'
            self.save()

        for error in errors:
            erc, __ = ResponseCode.objects.get_or_create(
                code=error.code,
                message=error.message,
            )
            erc.transactions.add(self)

    def save(self, *args, **kwargs):
        if not self.response_message and not self.transactions.count():
            self.response_message = u'Successful'
        super(Transaction, self).save(*args, **kwargs)

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
    """
    Error and response codes as defined in the eWay Rapid 3.0 specs
    linked to multiple transactions so that data does not have to 
    be replicated in each request.
    """
    code = models.CharField(_("Code"), unique=True, max_length=10)
    message = models.CharField(_("Message"), max_length=255)
    transactions = models.ManyToManyField(
        Transaction,
        related_name="response_messages"
    )

    def __unicode__(self):
        return "[%s] %s" % (self.code, self.message)
