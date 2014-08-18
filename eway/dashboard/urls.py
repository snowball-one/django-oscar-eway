# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^eway/$',
        views.TransactionListView.as_view(), name='transaction-list'),
    url(r'^eway/transaction/(?P<pk>\d+)/$',
        views.TransactionDetailView.as_view(), name='transaction-detail'),
]
