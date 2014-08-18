# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url

from eway.rapid import views


urlpatterns = [
    url(r'^preview/$',
        views.RapidResponseView.as_view(preview=True),
        name='eway-rapid-response'),
]
