# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__version__ = VERSION = (0, 1, 1)

PURCHASE = 'Purchase'
PAYMENT_METHOD_EWAY = "eWay"


def get_version():
    return '.'.join([str(i) for i in VERSION[:3]])


# Only used by Django 1.7+, ignored otherwise
default_app_config = 'eway.apps.DjangoEwayConfig'
