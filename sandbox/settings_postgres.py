# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from settings import *  # noqa


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'devdb',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost'}}
