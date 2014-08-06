# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.views import generic
from django.db.models import get_model

Transaction = get_model('eway', 'Transaction')


class TransactionListView(generic.ListView):
    model = Transaction
    context_object_name = 'transactions'
    template_name = 'eway/dashboard/transaction_list.html'
    paginate_by = 20


class TransactionDetailView(generic.DetailView):
    model = Transaction
    context_object_name = 'transaction'
    template_name = 'eway/dashboard/transaction_detail.html'
