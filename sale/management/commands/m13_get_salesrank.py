# -*- coding: utf-8 -*-

import logging
import os

from django.core.management.base import BaseCommand

from sale.services.sales_rank import SalesRankFetchService

log = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):

        verbosity = options.get('verbosity')

        print("live from cmd")
        print(log.__dict__)

        if verbosity == 1:  # default
            log.setLevel(logging.WARN)
        if verbosity > 1:
            log.setLevel(logging.INFO)
        if verbosity > 2:
            log.setLevel(logging.DEBUG)

        log.debug("os.environ['AMAZON_USER_NAME']: {}".format(os.environ['AMAZON_USER_NAME']))
        log.debug("os.environ['AMAZON_PASSWORD']: {}".format(os.environ['AMAZON_PASSWORD']))

        sales_rank_fetch_service = SalesRankFetchService(log)
        sales_rank_fetch_service.login()
        sales_rank_fetch_service.get_all_salesranks()
