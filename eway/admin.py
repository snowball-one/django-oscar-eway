# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.db.models import get_model


class RequestLogInline(admin.TabularInline):
    model = get_model('eway', 'RequestLog')
    readonly_fields = (
        'method', 'response_code', 'response_message',
        'errors', 'date_created', 'date_modified')
    exclude = ('url', 'request', 'response')
    extra = 0
    can_delete = False


class TransactionAdmin(admin.ModelAdmin):
    search_fields = (
        'access_code', 'transaction_id', 'token_customer_id', 'order_number')
    list_display = (
        'access_code', 'transaction_id', 'amount', 'token_customer_id',
        'order_number')

    inlines = [RequestLogInline]


class RequestLogAdmin(admin.ModelAdmin):
    search_fields = ('request', 'response')
    list_display = (
        'transaction', 'method', 'url', 'response_code', 'response_message')
    readonly_fields = (
        'transaction', 'url', 'method', 'request', 'response', 'response_code',
        'response_message', 'errors', 'date_created', 'date_modified')


admin.site.register(get_model('eway', 'Transaction'), TransactionAdmin)
admin.site.register(get_model('eway', 'RequestLog'), RequestLogAdmin)
