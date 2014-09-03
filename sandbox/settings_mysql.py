# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from settings import *  # noqa


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'devdb',  # noqa
        'USER': 'travis',  # noqa
        'PASSWORD': '',
        'HOST': '127.0.0.1'}}
