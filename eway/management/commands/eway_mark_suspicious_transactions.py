# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging

from datetime import timedelta
from optparse import make_option

from django.core.management.base import BaseCommand

from ... import utils

logger = logging.getLogger('eway')


class Command(BaseCommand):
    help = "Check dangling transaction for being suspicious."

    option_list = BaseCommand.option_list + (
        make_option(
            '--minimum-age',
            dest='minimum_age',
            type=int,
            help='Minimum age of transactions to be considered dangling.'),)

    def handle(self, *args, **options):
        minimum_age = options.get('minimum_age')

        if minimum_age:
            logger.info("Using minimum age: {0} hours".format(minimum_age))
            minimum_age = timedelta(hours=minimum_age)

        utils.check_dangling_transactions(minimum_age=minimum_age)
