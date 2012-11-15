from django.contrib import admin
from django.db.models import get_model


Transaction = get_model('eway', 'Transaction')
ResponseCode = get_model('eway', 'ResponseCode')


class ErrorInline(admin.StackedInline):
    model = ResponseCode.transactions.through

class ResponseCodeAdmin(admin.ModelAdmin):
    inlines = [
        ErrorInline,
    ]
    exclude = ('transactions',)

class TransactionAdmin(admin.ModelAdmin):
    inlines = [
        ErrorInline,
    ]
    list_display = [
        'method',
        'transaction_id',
        'amount',
        'response_message',
        'token_customer_id',
        'date_created',
    ]
    readonly_fields = [
        'method',
        'request_url',
        'transaction_id',
        'amount',
        'response_code',
        'response_message',
        'token_customer_id',
        'date_created',
        'request_json',
        'response_json',
        'order_number',
    ]


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(ResponseCode)
